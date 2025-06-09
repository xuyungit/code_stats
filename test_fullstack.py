#!/usr/bin/env python3
"""
Full-stack integration test for Code Stats application.
Tests the complete workflow from user registration to repository statistics.

This file serves as a regression test to ensure the entire application stack
continues working after code changes. Run with:
    python test_fullstack.py

Prerequisites:
- Server must be running on http://127.0.0.1:8002
- Start server with: uv run uvicorn backend.app.main:app --reload --port 8002
"""

import requests
import time

BASE_URL = "http://127.0.0.1:8002"

def test_api_health():
    """Test that the API is responding."""
    response = requests.get(f"{BASE_URL}/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}
    print("✓ API health check passed")

def test_frontend_serving():
    """Test that the Vue frontend is served."""
    response = requests.get(f"{BASE_URL}/")
    assert response.status_code == 200
    assert "<!DOCTYPE html>" in response.text
    assert "Vue" in response.text or "app" in response.text
    print("✓ Frontend serving working")

def test_user_registration():
    """Test user registration."""
    import time
    timestamp = int(time.time())
    user_data = {
        "username": f"testuser_{timestamp}",
        "email": f"test_{timestamp}@example.com", 
        "password": "testpassword123"
    }
    
    response = requests.post(f"{BASE_URL}/api/auth/register", json=user_data)
    assert response.status_code == 200
    print("✓ User registration successful")
    return user_data

def test_user_login(user_data):
    """Test user login and get token."""
    login_data = {
        "username": user_data["username"],
        "password": user_data["password"]
    }
    
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json=login_data
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    print("✓ User login successful")
    return token

def test_authenticated_endpoints(token):
    """Test authenticated endpoints."""
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test /auth/me
    response = requests.get(f"{BASE_URL}/api/auth/me", headers=headers)
    assert response.status_code == 200
    user_info = response.json()
    assert "username" in user_info
    print("✓ User info retrieval successful")
    
    # Test repositories list (should be empty initially)
    response = requests.get(f"{BASE_URL}/api/repositories/", headers=headers)
    assert response.status_code == 200
    repos = response.json()
    assert isinstance(repos, list)
    print("✓ Repository list retrieval successful")
    
    return user_info

def test_repository_management(token):
    """Test repository CRUD operations."""
    headers = {"Authorization": f"Bearer {token}"}
    
    # Add a repository
    repo_data = {
        "name": "Test Repo",
        "local_path": "/Users/xuyun/AI/code_stats",  # Use current project
        "description": "Test repository for integration testing"
    }
    
    response = requests.post(f"{BASE_URL}/api/repositories/", json=repo_data, headers=headers)
    assert response.status_code == 200
    repo = response.json()
    assert repo["name"] == repo_data["name"]
    repo_id = repo["id"]
    print("✓ Repository creation successful")
    
    # Get repository details
    response = requests.get(f"{BASE_URL}/api/repositories/{repo_id}", headers=headers)
    assert response.status_code == 200
    print("✓ Repository retrieval successful")
    
    return repo_id

def test_repository_analysis(token, repo_id):
    """Test repository analysis functionality."""
    headers = {"Authorization": f"Bearer {token}"}
    
    # Trigger analysis
    analysis_request = {"days": 30, "force_refresh": True}
    response = requests.post(f"{BASE_URL}/api/repositories/{repo_id}/analyze", json=analysis_request, headers=headers)
    assert response.status_code == 200
    print("✓ Repository analysis triggered successfully")
    
    # Wait a moment for analysis to complete
    time.sleep(2)
    
    # Check statistics
    response = requests.get(f"{BASE_URL}/api/repositories/{repo_id}/stats/period?days=7", headers=headers)
    assert response.status_code == 200
    stats = response.json()
    assert "commits_count" in stats
    print("✓ Repository statistics retrieval successful")
    print(f"  - Found {stats['commits_count']} commits")
    print(f"  - Found {stats['added_lines']} lines added")
    
    return stats

def main():
    """Run the full integration test suite."""
    print("🚀 Starting full-stack integration tests...\n")
    
    try:
        # Test basic connectivity
        test_api_health()
        test_frontend_serving()
        
        # Test user management
        user_data = test_user_registration()
        token = test_user_login(user_data)
        user_info = test_authenticated_endpoints(token)
        
        # Test repository management
        repo_id = test_repository_management(token)
        stats = test_repository_analysis(token, repo_id)
        
        print(f"\n🎉 All tests passed! The full-stack application is working correctly.")
        print(f"   User: {user_info['username']} ({user_info['email']})")
        print(f"   Repository: ID {repo_id} with {stats['commits_count']} commits analyzed")
        
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        return 1
    except requests.exceptions.RequestException as e:
        print(f"\n❌ Connection error: {e}")
        print("   Make sure the server is running on http://127.0.0.1:8002")
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())