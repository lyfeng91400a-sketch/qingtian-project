#!/usr/bin/env python3
"""Verify all BUG fixes."""
import json
import httpx

BASE = "http://localhost:8000"

# Register a test user
resp = httpx.post(f"{BASE}/api/auth/register", json={
    "email": "verify@test.com",
    "name": "Verifier",
    "password": "test123456"
})
print(f"[SETUP] Register: {resp.status_code}")
token = resp.json().get("access_token", "")
headers = {"Authorization": f"Bearer {token}"}

# ===== BUG-1: name="" should NOT cause 500 =====
resp = httpx.post(f"{BASE}/api/auth/register", json={
    "email": "bug1@test.com",
    "name": "",
    "password": "123456"
})
print(f"\nBUG-1 (name=''): {resp.status_code} (expect 422) => {'✅ PASS' if resp.status_code == 422 else '❌ FAIL'}")

# ===== BUG-5: email="" should NOT be accepted =====
resp = httpx.post(f"{BASE}/api/auth/register", json={
    "email": "",
    "name": "test",
    "password": "123456"
})
print(f"BUG-5 (email=''): {resp.status_code} (expect 422) => {'✅ PASS' if resp.status_code == 422 else '❌ FAIL'}")

# ===== BUG-4: project name="" should NOT be accepted =====
resp = httpx.post(f"{BASE}/api/projects", json={"name": ""}, headers=headers)
print(f"BUG-4 (project name=''): {resp.status_code} (expect 422) => {'✅ PASS' if resp.status_code == 422 else '❌ FAIL'}")

# ===== Get a project to create tasks =====
resp = httpx.get(f"{BASE}/api/projects", headers=headers)
projects = resp.json()
if not projects:
    # Create one
    resp = httpx.post(f"{BASE}/api/projects", json={"name": "Test Project"}, headers=headers)
    projects = [resp.json()]
pid = projects[0]["id"]
print(f"\n[SETUP] Using project: {pid}")

# ===== BUG-2: invalid task status should get 422 =====
resp = httpx.post(f"{BASE}/api/projects/{pid}/tasks", json={
    "title": "test",
    "status": "cancelled"
}, headers=headers)
print(f"BUG-2 (status='cancelled'): {resp.status_code} (expect 422) => {'✅ PASS' if resp.status_code == 422 else '❌ FAIL'}")

# ===== BUG-3: assignee_id="" should not cause 500 =====
# First create a task with an assignee
resp = httpx.post(f"{BASE}/api/projects/{pid}/tasks", json={
    "title": "test-assignee-clear",
    "assignee_id": "some-id"
}, headers=headers)
task_id = resp.json().get("id", "")
print(f"\n[SETUP] Created task: {task_id}")

# Now clear the assignee
resp = httpx.put(f"{BASE}/api/tasks/{task_id}", json={
    "assignee_id": ""
}, headers=headers)
print(f"BUG-3 (assignee_id=''): {resp.status_code} (expect 200) => {'✅ PASS' if resp.status_code == 200 else '❌ FAIL'}")

if resp.status_code == 200:
    task = resp.json()
    print(f"  assignee_id: {task.get('assignee_id')!r} (expect None) => {'✅ PASS' if task.get('assignee_id') is None else '❌ FAIL'}")

print("\n===== All BUG verifications complete =====")
