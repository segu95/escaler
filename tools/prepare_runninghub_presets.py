"""Generate reviewable API-format graphs from the supplied workflow; no API calls."""

import argparse
import copy
import hashlib
import json
from pathlib import Path


def references(node):
    for value in node["inputs"].values():
        if (isinstance(value, list) and len(value) == 2
                and isinstance(value[0], str) and isinstance(value[1], int)):
            yield value[0]


def validate(graph):
    visited, active = set(), set()

    def visit(node_id):
        if node_id in active:
            raise ValueError(f"Cycle at {node_id}")
        if node_id in visited:
            return
        if node_id not in graph:
            raise ValueError(f"Missing node {node_id}")
        active.add(node_id)
        for dependency in references(graph[node_id]):
            visit(dependency)
        active.remove(node_id)
        visited.add(node_id)

    for node_id in graph:
        visit(node_id)
    if graph["168"]["inputs"]["images"] != ["125", 0]:
        raise ValueError("Unexpected output connection")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    raw = args.source.read_bytes()
    source = json.loads(raw)
    expected = {"123": "LoadImage", "142": "ImageScaleBy",
                "172": "ImageResize+", "168": "SaveImage",
                "128": "SeedVR2VideoUpscaler"}
    for node_id, class_type in expected.items():
        if source[node_id]["class_type"] != class_type:
            raise ValueError(f"Unexpected class for node {node_id}")
    validate(source)

    # Retain only dependencies of SaveImage. This removes the comparison node
    # and its old signed preview URLs, and an unused dimensions node.
    needed = set()

    def retain(node_id):
        if node_id not in needed:
            needed.add(node_id)
            for dependency in references(source[node_id]):
                retain(dependency)

    retain("168")
    base = {key: copy.deepcopy(value) for key, value in source.items() if key in needed}
    base["123"]["inputs"]["image"] = "REPLACE_WITH_UPLOADED_IMAGE_REFERENCE"
    args.output.mkdir(parents=True, exist_ok=True)

    def save(name, data):
        (args.output / name).write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")

    validate(base)
    save("original-sanitized_api.json", base)
    for label, factor in (("4k", 4), ("6k", 6), ("8k", 8)):
        graph = copy.deepcopy(base)
        graph["142"]["inputs"]["scale_by"] = factor
        # The original condition does not enlarge tiny inputs to the 1024 base.
        # Always fitting to 1024 ensures a nominal longest side of 1024*factor.
        graph["172"]["inputs"]["condition"] = "always"
        graph["168"]["inputs"]["filename_prefix"] = f"segutools_{label}"
        validate(graph)
        save(f"{label}_api.json", graph)
        save(f"{label}_request-template.json", {
            "addMetadata": False,
            "nodeInfoList": [
                {"nodeId": "123", "fieldName": "image",
                 "fieldValue": "REPLACE_WITH_UPLOADED_IMAGE_REFERENCE"},
                {"nodeId": "142", "fieldName": "scale_by", "fieldValue": str(factor)},
                {"nodeId": "172", "fieldName": "condition", "fieldValue": "always"},
            ],
        })
    save("provenance.json", {
        "source_sha256": hashlib.sha256(raw).hexdigest(),
        "source_nodes": len(source),
        "retained_nodes": len(base),
        "removed_nodes": sorted(set(source) - needed),
        "validation": "JSON, graph references and cycles only; no GPU or API execution",
        "status": "candidate presets; provider acceptance and output sizes untested",
    })
    print(f"Prepared 3 candidate presets; retained {len(base)}/{len(source)} nodes.")


if __name__ == "__main__":
    main()
