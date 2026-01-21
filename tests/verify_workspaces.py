import requests
import json
import sys

BASE_URL = "http://localhost:8000"

def print_result(name, passed, details=""):
    status = "PASS" if passed else "FAIL"
    print(f"[{status}] {name}")
    if not passed and details:
        print(f"  Error: {details}")

def test_workspaces_logic():
    print("Testing Workspaces API...")
    
    headers = {"Authorization": "Bearer test_token"}

    # 1. List Workspaces
    try:
        resp = requests.get(f"{BASE_URL}/workspaces", headers=headers)
        if resp.status_code != 200:
            print_result("List Workspaces", False, f"Status {resp.status_code}: {resp.text}")
            return
        data = resp.json().get("data", [])
        if not isinstance(data, list):
             print_result("List Workspaces structure", False, f"Data is not list: {data}")
             return
        print_result("List Workspaces", True, f"Found {len(data)} workspaces")
    except Exception as e:
        print_result("List Workspaces", False, str(e))
        return

    # 2. Create Workspace
    new_gid = None
    try:
        payload = {
            "data": {
                "name": "New Test Workspace"
            }
        }
        resp = requests.post(f"{BASE_URL}/workspaces", json=payload, headers=headers)
        if resp.status_code != 200:
             print_result("Create Workspace", False, f"Status {resp.status_code}: {resp.text}")
             return
        
        ws_data = resp.json().get("data")
        if ws_data["name"] != "New Test Workspace":
             print_result("Create Workspace Name Match", False, f"Name mismatch: {ws_data['name']}")
             return
        
        new_gid = ws_data["gid"]
        print_result("Create Workspace", True, f"Created {new_gid}")
    except Exception as e:
        print_result("Create Workspace", False, str(e))
        return

    if not new_gid:
        print("Skipping dependent tests due to creation failure")
        return

    # 3. Get Workspace (Check for extended fields)
    try:
        resp = requests.get(f"{BASE_URL}/workspaces/{new_gid}", headers=headers)
        if resp.status_code != 200:
            print_result("Get Workspace", False, f"Status {resp.status_code}: {resp.text}")
        else:
            ws_data = resp.json().get("data")
            # Check fields
            if "email_domains" in ws_data and "is_organization" in ws_data:
                print_result("Get Workspace Fields", True)
            else:
                print_result("Get Workspace Fields", False, f"Missing fields (email_domains, is_organization). Keys: {ws_data.keys()}")
    except Exception as e:
        print_result("Get Workspace", False, str(e))

    # 4. Update Workspace
    try:
        payload = {
            "data": {
                "name": "Updated Workspace Name"
            }
        }
        resp = requests.put(f"{BASE_URL}/workspaces/{new_gid}", json=payload, headers=headers)
        if resp.status_code != 200:
            print_result("Update Workspace", False, f"Status {resp.status_code}: {resp.text}")
        else:
            ws_data = resp.json().get("data")
            if ws_data["name"] == "Updated Workspace Name":
                print_result("Update Workspace", True)
            else:
                 print_result("Update Workspace", False, f"Name not updated: {ws_data['name']}")
    except Exception as e:
        print_result("Update Workspace", False, str(e))

    # 6. Remove User
    try:
        payload = {
            "data": {
                "user": "me"
            }
        }
        resp = requests.post(f"{BASE_URL}/workspaces/{new_gid}/removeUser", json=payload, headers=headers)
        if resp.status_code != 200:
            print_result("Remove User", False, f"Status {resp.status_code}: {resp.text}")
        else:
            resp_data = resp.json().get("data")
            if resp_data == {} or resp_data is None: # Empty response often allows empty dict or null
                 print_result("Remove User", True)
            else:
                 print_result("Remove User", False, f"Expected empty data, got: {resp_data}")
    except Exception as e:
        print_result("Remove User", False, str(e))

if __name__ == "__main__":
    test_workspaces_logic()
