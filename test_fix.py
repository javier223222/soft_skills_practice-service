#!/usr/bin/env python3
"""
Test script para verificar el endpoint de simulación por soft skill
"""

import requests
import json

# Configuración
BASE_URL = 'http://localhost:8001'

def test_start_softskill_simulation():
    """Test del endpoint de inicio de simulación por soft skill"""
    
    # Datos de prueba
    test_data = {
        "user_id": "test_user_001",
        "skill_type": "communication",
        "difficulty_preference": 3,
        "tecnical_specialization": "Backend Developer",
        "seniority_level": "Senior"
    }
    
    print("🚀 Testing POST /simulation/softskill/start/")
    print(f"Request data: {json.dumps(test_data, indent=2)}")
    print("-" * 50)
    
    try:
        response = requests.post(
            f"{BASE_URL}/simulation/softskill/start/",
            json=test_data,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ SUCCESS!")
            print(f"Session ID: {result.get('session_id', 'N/A')}")
            print(f"Scenario Title: {result.get('scenario', {}).get('title', 'N/A')}")
            print(f"Message: {result.get('message', 'N/A')}")
            return result
        else:
            print("❌ ERROR!")
            print(f"Response: {response.text}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection Error: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"❌ JSON Decode Error: {e}")
        return None

def test_health_check():
    """Test básico de health check"""
    print("🔍 Testing GET /health")
    
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Service is healthy")
            return True
        else:
            print("❌ Service is not healthy")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection Error: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Soft Skills Practice Service")
    print("=" * 60)
    
    # Test 1: Health check
    if test_health_check():
        print("\n")
        # Test 2: Start simulation
        test_start_softskill_simulation()
    else:
        print("❌ Service not available. Make sure it's running on localhost:8001")
    
    print("\n" + "=" * 60)
    print("🏁 Test completed")
