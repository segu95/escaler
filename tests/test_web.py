import tempfile
import unittest
import uuid
from pathlib import Path
import httpx
from web.app import create_app

PNG = b'\x89PNG\r\n\x1a\n' + b'\0\0\0\rIHDR' + (32).to_bytes(4,'big')*2 + b'\x08\x02\0\0\0'

class FakeProvider:
    def __init__(self): self.submits=0; self.ambiguous=False
    async def upload(self,path,mime): return 'image.png'
    async def submit(self,reference,quality):
        self.submits+=1
        if self.ambiguous: raise TimeoutError()
        return {'taskId':'external-123'}
    async def query(self,task):
        return {'taskId':task,'status':'SUCCESS','results':[{'nodeId':'168','url':'https://example.com/result.png'}]}

class WebTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.temp=tempfile.TemporaryDirectory();self.provider=FakeProvider()
        self.app=create_app(self.temp.name,'test-access',self.provider)
        self.client=httpx.AsyncClient(transport=httpx.ASGITransport(app=self.app),base_url='http://test',headers={'Authorization':'Bearer test-access'})
    async def asyncTearDown(self):
        await self.client.aclose();self.temp.cleanup()
    async def submit(self,id=None,body=PNG,mime='image/png'):
        return await self.client.post('/api/jobs?quality=4k',content=body,headers={'Idempotency-Key':id or str(uuid.uuid4()),'Content-Type':mime})
    async def test_access_required(self):
        r=await self.client.get('/api/jobs',headers={'Authorization':'Bearer wrong'})
        self.assertEqual(r.status_code,401)
    async def test_success_duplicate_and_cleanup(self):
        key=str(uuid.uuid4());a=await self.submit(key);b=await self.submit(key)
        self.assertEqual(a.status_code,200);self.assertEqual(b.status_code,200)
        self.assertEqual(self.provider.submits,1)
        self.assertFalse(list(Path(self.temp.name).glob('input-*')))
        r=await self.client.get('/api/jobs/'+key)
        self.assertEqual(r.json()['state'],'succeeded')
        self.assertEqual(r.json()['result'],'https://example.com/result.png')
    async def test_ambiguous_submission_blocks_rebilling(self):
        self.provider.ambiguous=True
        key=str(uuid.uuid4());await self.submit(key);await self.submit(key)
        state=await self.client.get('/api/jobs/'+key)
        self.assertEqual(state.json()['state'],'uncertain')
        self.assertEqual((await self.submit()).status_code,409)
        self.assertEqual(self.provider.submits,1)
        create_app(self.temp.name,'test-access',self.provider)
        self.assertEqual((await self.submit()).status_code,409)
    async def test_invalid_image_does_not_call_provider(self):
        self.assertEqual((await self.submit(body=b'not an image')).status_code,400)
        self.assertEqual((await self.submit(mime='image/jpeg')).status_code,400)
        self.assertEqual(self.provider.submits,0)
    async def test_size_limit(self):
        self.assertEqual((await self.submit(body=PNG+b'0'*(10*1024*1024))).status_code,413)
        self.assertFalse(list(Path(self.temp.name).glob('input-*')))
    async def test_wrong_provider_task_does_not_complete_job(self):
        key=str(uuid.uuid4());await self.submit(key)
        async def wrong(task): return {'taskId':'other','status':'SUCCESS'}
        self.provider.query=wrong
        response=await self.client.get('/api/jobs/'+key)
        self.assertEqual(response.status_code,502)
        self.assertNotIn('other',response.text)
    async def test_preview_without_credentials(self):
        with tempfile.TemporaryDirectory() as folder:
            app=create_app(folder,'')
            async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app),base_url='http://test') as client:
                self.assertFalse((await client.get('/api/config')).json()['ready'])
                self.assertEqual((await client.get('/')).status_code,200)
