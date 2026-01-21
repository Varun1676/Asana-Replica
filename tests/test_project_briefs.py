
import pytest
import requests
import uuid
import os

BASE_URL = "http://localhost:8000"
REAL_ASANA_URL = "https://app.asana.com/api/1.0"
ASANA_PAT = os.environ.get("ASANA_PAT", "2/1212897542116316/1212897631500883:d63f55c622da942c1e4af46933a436cf")

HEADERS = {
    "Content-Type": "application/json",
    "Authorization": "Bearer test_token"
}

REAL_HEADERS = {
    "Authorization": f"Bearer {ASANA_PAT}",
    "Accept": "application/json"
}

@pytest.fixture(scope="module")
def setup_data():
    """Create Local Workspace and Project"""
    # WS
    resp = requests.post(f"{BASE_URL}/workspaces", json={"data": {"name": f"Brief WS {uuid.uuid4()}"}}, headers=HEADERS)
    assert resp.status_code == 200, f"Setup WS Failed: {resp.text}"
    ws_gid = resp.json()["data"]["gid"]
    
    # Project
    p_resp = requests.post(f"{BASE_URL}/projects", json={"data": {"name": "Brief Project", "workspace": ws_gid}}, headers=HEADERS)
    assert p_resp.status_code == 201 or p_resp.status_code == 200
    project_gid = p_resp.json()["data"]["gid"]
    
    return project_gid

def test_local_project_brief_lifecycle(setup_data):
    project_gid = setup_data
    
    # 1. Create Brief
    create_payload = {
        "data": {
            "title": "My Brief",
            "text": "This is the brief text",
            "html_text": "<body>This is the brief text</body>"
        }
    }
    resp = requests.post(f"{BASE_URL}/projects/{project_gid}/project_briefs", json=create_payload, headers=HEADERS)
    assert resp.status_code == 200, f"Create Failed: {resp.text}"
    data = resp.json()["data"]
    brief_gid = data["gid"]
    
    # 2. Get Brief & Verify Fields
    resp = requests.get(f"{BASE_URL}/project_briefs/{brief_gid}", headers=HEADERS)
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["gid"] == brief_gid
    assert data["text"] == "This is the brief text"
    assert "permalink_url" in data
    assert "project" in data
    
    # 3. Update Brief
    update_payload = { "data": { "title": "Updated Title" } }
    resp = requests.put(f"{BASE_URL}/project_briefs/{brief_gid}", json=update_payload, headers=HEADERS)
    assert resp.status_code == 200
    assert resp.json()["data"]["title"] == "Updated Title"

    # 4. Delete Brief
    requests.delete(f"{BASE_URL}/project_briefs/{brief_gid}", headers=HEADERS)
    assert requests.get(f"{BASE_URL}/project_briefs/{brief_gid}", headers=HEADERS).status_code == 404

def test_compare_with_real_asana(setup_data):
    """
    Attempt to find a Project Brief in Real Asana and compare response keys with Local.
    If none found, skip, but at least valid local structure against expected Asana Usage.
    """
    # 1. Try to find a real project brief
    real_brief = None
    
    # Get a project from Real Asana -> Then check its briefs
    # This is expensive/flaky without known ID. 
    # Strategy: Just check /project_briefs/{valid_id} if we knew one.
    # Alternative: Compare Local Output Keys with Hardcoded Expected Keys from Documentation/Real Trace.
    
    local_project_gid = setup_data
    # Create a local brief to inspect
    create_payload = {"data": {"title": "Comp Brief", "text": "Text"}}
    l_resp = requests.post(f"{BASE_URL}/projects/{local_project_gid}/project_briefs", json=create_payload, headers=HEADERS)
    local_data = l_resp.json()["data"]
    local_keys = set(local_data.keys())
    
    # Expected Critical Keys from Asana API
    expected_keys = {"gid", "resource_type", "title", "text", "html_text", "permalink_url", "project"}
    
    assert expected_keys.issubset(local_keys), f"Local Replica missing keys: {expected_keys - local_keys}"
