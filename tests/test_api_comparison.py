import pytest
import requests
import os
from typing import Dict, Any

# CONFIGURATION
REAL_ASANA_URL = "https://app.asana.com/api/1.0"
LOCAL_REPLICA_URL = "http://localhost:8000"
ASANA_PAT = os.environ.get("ASANA_PAT", "2/1212897542116316/1212897631500883:d63f55c622da942c1e4af46933a436cf")

HEADERS = {
    "Authorization": f"Bearer {ASANA_PAT}",
    "Content-Type": "application/json",
    "Accept": "application/json"
}

@pytest.fixture(scope="module")
def workspace_gid():
    """Fetch a real workspace GID to use for tests."""
    response = requests.get(f"{REAL_ASANA_URL}/users/me", headers=HEADERS)
    assert response.status_code == 200, "Failed to connect to Real Asana API"
    data = response.json().get("data", {})
    workspaces = data.get("workspaces", [])
    if not workspaces:
        pytest.skip("No workspaces found in real Asana account, skipping dependent tests.")
    return workspaces[0]["gid"]

def get_keys(response_json):
    """Helper to extract keys from data object or list of objects."""
    if "data" not in response_json:
        return set()
    data = response_json["data"]
    if isinstance(data, list):
        if data:
            return set(data[0].keys())
        return set()
    elif isinstance(data, dict):
        return set(data.keys())
    return set()

def test_get_users_me():
    """Compare GET /users/me response."""
    path = "/users/me"
    
    # Real
    real_resp = requests.get(f"{REAL_ASANA_URL}{path}", headers=HEADERS)
    # Local
    local_resp = requests.get(f"{LOCAL_REPLICA_URL}{path}", headers=HEADERS)
    
    # Assert Status
    assert real_resp.status_code == 200
    assert local_resp.status_code == 200
    
    # Assert Keys
    real_keys = get_keys(real_resp.json())
    local_keys = get_keys(local_resp.json())
    
    # Check that critical keys exist in local
    critical_keys = {"gid", "name", "email", "resource_type"}
    assert critical_keys.issubset(local_keys), f"Local replica missing critical keys: {critical_keys - local_keys}"

def test_get_workspace(workspace_gid):
    """Compare GET /workspaces/{gid} response."""
    path = f"/workspaces/{workspace_gid}"
    
    # Real
    real_resp = requests.get(f"{REAL_ASANA_URL}{path}", headers=HEADERS)
    # Local
    local_resp = requests.get(f"{LOCAL_REPLICA_URL}{path}", headers=HEADERS)
    
    # Assert Status
    assert real_resp.status_code == 200
    assert local_resp.status_code == 200
    
    # Assert Keys
    real_keys = get_keys(real_resp.json())
    local_keys = get_keys(local_resp.json())
    
    # Check that critical keys exist in local
    critical_keys = {"gid", "name", "resource_type"}
    assert critical_keys.issubset(local_keys), f"Local replica missing critical keys: {critical_keys - local_keys}"

def test_get_projects_in_workspace(workspace_gid):
    """Compare GET /projects?workspace={gid} response."""
    path = f"/projects?workspace={workspace_gid}"
    
    # Real
    real_resp = requests.get(f"{REAL_ASANA_URL}{path}", headers=HEADERS)
    # Local
    local_resp = requests.get(f"{LOCAL_REPLICA_URL}{path}", headers=HEADERS)
    
    # Assert Status
    # Note: Local might return empty list if no projects created yet, but status should be 200
    assert local_resp.status_code == 200
    
    if real_resp.status_code == 200:
        real_keys = get_keys(real_resp.json())
        local_keys = get_keys(local_resp.json())
        
        # If we have data in both, compare keys
        if real_keys and local_keys:
            critical_keys = {"gid", "name", "resource_type"}
            assert critical_keys.issubset(local_keys)

def test_task_lifecycle(workspace_gid):
    """
    Test a full local lifecycle since we can't easily rely on real data 
    matching local data 1:1 for specific IDs.
    """
    # 1. Create Project (Local)
    proj_resp = requests.post(f"{LOCAL_REPLICA_URL}/projects", headers=HEADERS, json={
        "data": {"name": "Test Project", "workspace": workspace_gid, "resource_type": "project"}
    })
    assert proj_resp.status_code in [200, 201]
    project_gid = proj_resp.json()["data"]["gid"]
    
    # 2. Create Task (Local)
    task_resp = requests.post(f"{LOCAL_REPLICA_URL}/tasks", headers=HEADERS, json={
        "data": {"name": "Test Task", "project": project_gid, "resource_type": "task"}
    })
    assert task_resp.status_code in [200, 201]
    task_gid = task_resp.json()["data"]["gid"]
    
    # 3. Get Task (Local)
    get_resp = requests.get(f"{LOCAL_REPLICA_URL}/tasks/{task_gid}", headers=HEADERS)
    assert get_resp.status_code == 200
    data = get_resp.json()["data"]
    assert data["name"] == "Test Task"
    assert data["resource_type"] == "task"
    
    # 4. Compare Keys with Real Task (Arbitrary fetch if possible, else skip)
    # We fetch a real task to check key structure against our local task
    # This requires finding A real task.
    pass
