#!/usr/bin/env python3
"""Verify BUG-3 specifically: assignee_id='' should not cause 500."""
import json
import httpx

BASE = "http://localhost:8000"

# Login
resp = httpx.post(f"{BASE}/api/auth/login", json={
    "email": "verify@test.com",
    "password": "test123456"
})
print(f"[SETUP] Login: {resp.status_code}")
token = resp.json().get("access_token", "")
headers = {"Authorization": f"Bearer {token}"}

# Get a project
resp = httpx.get(f"{BASE}/api/projects", headers=headers)
projects = resp.json()
pid = projects[0]["id"]
print(f"[SETUP] Using project: {pid}")

# Create a task without assignee
resp = httpx.post(f"{BASE}/api/projects/{pid}/tasks", json={
    "title": "test-assignee-clear"
}, headers=headers)
print(f"[SETUP] Create task: {resp.status_code}")
task = resp.json()
task_id = task.get("id", "")
print(f"[SETUP] Task ID: {task_id}")

# Now clear the assignee (it's already None, but the code path needs to handle "")
resp = httpx.put(f"{BASE}/api/tasks/{task_id}", json={
    "assignee_id": ""
}, headers=headers)
print(f"BUG-3 (assignee_id=''): {resp.status_code} (expect 200) => {'✅ PASS' if resp.status_code == 200 else '❌ FAIL'}")

if resp.status_code == 200:
    task = resp.json()
    print(f"  assignee_id: {task.get('assignee_id')!r} (expect None) => {'✅ PASS' if task.get('assignee_id') is None else '❌ FAIL'}")

print("\n✅ BUG-3 verification complete")
