import sqlite3
import tempfile
import unittest
from pathlib import Path
from tools.reconcile_web_task import reconcile

class QueryOnly:
    async def query(self, task):
        return {'taskId':task,'status':'SUCCESS'}

class ReconcileTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.folder=tempfile.TemporaryDirectory()
        self.db=Path(self.folder.name)/'tasks.sqlite3'
        with sqlite3.connect(self.db) as conn:
            conn.execute('CREATE TABLE jobs (id TEXT PRIMARY KEY,state TEXT,task TEXT,checked REAL)')
            conn.execute("INSERT INTO jobs VALUES('local','uncertain',NULL,0)")
    async def asyncTearDown(self):
        self.folder.cleanup()
    async def test_verified_task_resumes_without_submit(self):
        await reconcile(self.db,'local','remote',QueryOnly())
        with sqlite3.connect(self.db) as conn:
            self.assertEqual(conn.execute('SELECT state,task FROM jobs').fetchone(),('tracking','remote'))
    async def test_wrong_id_keeps_uncertain(self):
        class Wrong:
            async def query(self, task): return {'taskId':'other','status':'SUCCESS'}
        with self.assertRaises(ValueError): await reconcile(self.db,'local','remote',Wrong())
        with sqlite3.connect(self.db) as conn:
            self.assertEqual(conn.execute('SELECT state,task FROM jobs').fetchone(),('uncertain',None))
    async def test_reused_remote_id_rejected(self):
        with sqlite3.connect(self.db) as conn: conn.execute("INSERT INTO jobs VALUES('other','succeeded','remote',0)")
        with self.assertRaises(ValueError): await reconcile(self.db,'local','remote',QueryOnly())
    async def test_cannot_replace_confirmed_task(self):
        await reconcile(self.db,'local','remote',QueryOnly())
        with self.assertRaises(ValueError): await reconcile(self.db,'local','different',QueryOnly())
