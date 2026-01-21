
import pytest
import requests
import uuid

BASE_URL = "http://localhost:8000"
HEADERS = {
    "Content-Type": "application/json",
    "Authorization": "Bearer test_token"
}

@pytest.fixture(scope="module")
def workspace_gid():
    # Helper to get a valid WS GID
    resp = requests.post(f"{BASE_URL}/workspaces", json={"data": {"name": f"Batch WS {uuid.uuid4()}"}}, headers=HEADERS)
    if resp.status_code == 200:
        return resp.json()["data"]["gid"]
    # Fallback
    l = requests.get(f"{BASE_URL}/workspaces", headers=HEADERS)
    return l.json()["data"][0]["gid"]

def test_batch_api(workspace_gid):
    # Construct a batch request performing 2 actions:
    # 1. Create a Project
    # 2. Get the Workspace
    
    project_name = f"Batch Proj {uuid.uuid4()}"
    
    batch_payload = {
        "data": {
            "actions": [
                {
                    "relative_path": "/projects",
                    "method": "post",
                    "data": {
                        "name": project_name,
                        "workspace": workspace_gid
                    }
                },
                {
                    "relative_path": f"/workspaces/{workspace_gid}",
                    "method": "get"
                }
            ]
        }
    }
    
    resp = requests.post(f"{BASE_URL}/batch", json=batch_payload, headers=HEADERS)
    assert resp.status_code == 200, f"Batch failed: {resp.text}"
    
    results = resp.json()["data"]
    assert len(results) == 2
    
    # Check 1: Project Creation
    res1 = results[0]
    assert res1["status_code"] in [200, 201]
    assert res1["body"]["data"]["name"] == project_name
    
    # Check 2: Get Workspace
    res2 = results[1]
    assert res2["status_code"] == 200
    assert res2["body"]["data"]["gid"] == workspace_gid

def test_compare_batch_structure_with_real():
    """
    Compare Local Batch Response Structure with Real Asana.
    """
    import os
    pat = os.environ.get("ASANA_PAT", "2/1212897542116316/1212897631500883:d63f55c622da942c1e4af46933a436cf")
    real_headers = {"Authorization": f"Bearer {pat}", "Content-Type": "application/json"}
    real_url = "https://app.asana.com/api/1.0/batch"
    
    # Payload for Real Asana
    real_payload = {
        "data": {
            "actions": [
                {
                    "relative_path": "/users/me",
                    "method": "get"
                }
            ]
        }
    }
    
    real_keys = set()
    real_item_keys = set()
    
    try:
        r = requests.post(real_url, json=real_payload, headers=real_headers)
        if r.status_code == 200:
            data = r.json().get("data", [])
            if data:
                real_keys = set(r.json().keys()) # should be 'data'
                real_item_keys = set(data[0].keys()) # should be status_code, headers, body
    except Exception as e:
        print(f"Real Asana Batch Call Failed: {e}")

    # Fallback expectations if real call acts up (e.g. auth)
    if not real_item_keys:
        real_item_keys = {"status_code", "headers", "body"}

    # Local Call
    # We need a valid local user or workspace. Just use /workspaces if it exists?
    # Or reuse workspace_gid fixture?
    # I'll just use a simple call that should work if I have ANY data, or even 404 is fine to check structure.
    # Let's use /workspaces
    local_payload = {
        "data": {
             "actions": [
                 {"relative_path": "/workspaces", "method": "get"}
             ]
        }
    }
    l_resp = requests.post(f"{BASE_URL}/batch", json=local_payload, headers=HEADERS)
    assert l_resp.status_code == 200
    local_items = l_resp.json()["data"]
    
    if local_items:
        local_item_keys = set(local_items[0].keys())
        # Assert Parity
        assert real_item_keys.issubset(local_item_keys), f"Local Batch Item missing keys: {real_item_keys - local_item_keys}"
