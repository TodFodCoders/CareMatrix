"""
CareMatrix API - Usage Examples and Testing
Demonstrates how to use all API endpoints

Run this file to test API endpoints:
    python test_api.py

Or use curl commands from the command line
"""

import requests
import json
from datetime import datetime

# Base URL - change if server runs on different host/port
BASE_URL = "http://localhost:8000/api/v1"
DEMO_MODE = True  # Set to False to actually send requests

def print_header(title):
    """Print formatted header"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def print_request(method, endpoint, data=None):
    """Print request details"""
    print(f"\n📨 REQUEST: {method} {BASE_URL}{endpoint}")
    if data:
        print(f"📦 DATA: {json.dumps(data, indent=2)}")

def print_response(response):
    """Print response details"""
    try:
        print(f"✅ RESPONSE ({response.status_code}):")
        print(json.dumps(response.json(), indent=2))
        return response.json()
    except:
        print(f"❌ Response: {response.text}")
        return None

def print_curl(method, endpoint, data=None):
    """Print curl command"""
    curl_cmd = f'curl -X {method} "{BASE_URL}{endpoint}"'
    if data:
        curl_cmd += f' -H "Content-Type: application/json" -d \'{json.dumps(data)}\''
    print(f"\n🔌 CURL: {curl_cmd}")


# ==================== 1. HEALTH CHECK ====================
def test_health_check():
    """Test health check endpoint"""
    print_header("1. Health Check")
    endpoint = "/health"
    print_request("GET", endpoint)
    print_curl("GET", "/health")
    
    if DEMO_MODE:
        print("\n✅ DEMO MODE - Expected response:")
        demo_response = {"status": "healthy", "service": "CareMatrix API", "version": "1.0.0"}
        print(json.dumps(demo_response, indent=2))
    else:
        response = requests.get(f"{BASE_URL}{endpoint}")
        print_response(response)


# ==================== 2. CREATE HOSPITAL ====================
def test_create_hospital():
    """Test hospital creation"""
    print_header("2. Create Hospital")
    endpoint = "/hospitals/"
    
    data = {
        "name": "Central Hospital",
        "location": "Downtown District",
        "total_beds": 100,
        "total_icu_beds": 20
    }
    
    print_request("POST", endpoint, data)
    print_curl("POST", endpoint, data)
    
    if DEMO_MODE:
        print("\n✅ DEMO MODE - Expected response:")
        demo_response = {
            "hospital_id": 1,
            **data,
            "created_at": datetime.now().isoformat()
        }
        print(json.dumps(demo_response, indent=2))
    else:
        response = requests.post(f"{BASE_URL}{endpoint}", json=data)
        print_response(response)


# ==================== 3. CREATE SECOND HOSPITAL ====================
def test_create_second_hospital():
    """Test creating second hospital"""
    print_header("3. Create Second Hospital")
    endpoint = "/hospitals/"
    
    data = {
        "name": "Medical City",
        "location": "North District",
        "total_beds": 150,
        "total_icu_beds": 30
    }
    
    print_request("POST", endpoint, data)
    print_curl("POST", endpoint, data)
    
    if DEMO_MODE:
        print("\n✅ DEMO MODE - Expected response:")
        demo_response = {
            "hospital_id": 2,
            **data,
            "created_at": datetime.now().isoformat()
        }
        print(json.dumps(demo_response, indent=2))
    else:
        response = requests.post(f"{BASE_URL}{endpoint}", json=data)
        print_response(response)


# ==================== 4. CREATE PATIENT ====================
def test_create_patient():
    """Test patient creation"""
    print_header("4. Create Patient")
    endpoint = "/patients/"
    
    data = {
        "full_name": "John Doe",
        "age": 45,
        "contact": "9876543210",
        "blood_group": "O+"
    }
    
    print_request("POST", endpoint, data)
    print_curl("POST", endpoint, data)
    
    if DEMO_MODE:
        print("\n✅ DEMO MODE - Expected response:")
        demo_response = {
            "patient_id": 1,
            **data,
            "created_at": datetime.now().isoformat()
        }
        print(json.dumps(demo_response, indent=2))
    else:
        response = requests.post(f"{BASE_URL}{endpoint}", json=data)
        print_response(response)


# ==================== 5. GET HOSPITALS ====================
def test_list_hospitals():
    """Test listing hospitals"""
    print_header("5. List All Hospitals")
    endpoint = "/hospitals/"
    print_request("GET", endpoint)
    print_curl("GET", endpoint)
    
    if DEMO_MODE:
        print("\n✅ DEMO MODE - Expected response:")
        demo_response = [
            {"hospital_id": 1, "name": "Central Hospital", "location": "Downtown District", "total_beds": 100, "total_icu_beds": 20},
            {"hospital_id": 2, "name": "Medical City", "location": "North District", "total_beds": 150, "total_icu_beds": 30}
        ]
        print(json.dumps(demo_response, indent=2))
    else:
        response = requests.get(f"{BASE_URL}{endpoint}")
        print_response(response)


# ==================== 6. CREATE ADMISSION ====================
def test_create_admission():
    """Test patient admission"""
    print_header("6. Admit Patient to Hospital")
    endpoint = "/admissions/"
    
    data = {
        "patient_id": 1,
        "hospital_id": 1,
        "priority": "high",
        "patient_condition": "Severe Pneumonia",
        "department": "General Ward"
    }
    
    print_request("POST", endpoint, data)
    print_curl("POST", endpoint, data)
    
    if DEMO_MODE:
        print("\n✅ DEMO MODE - Expected response:")
        demo_response = {
            "admission_id": 1,
            **data,
            "admission_time": datetime.now().isoformat(),
            "discharge_time": None
        }
        print(json.dumps(demo_response, indent=2))
    else:
        response = requests.post(f"{BASE_URL}{endpoint}", json=data)
        print_response(response)


# ==================== 7. GET ACTIVE ADMISSIONS ====================
def test_get_active_admissions():
    """Test getting active admissions"""
    print_header("7. Get Active Admissions")
    endpoint = "/admissions/active"
    print_request("GET", endpoint)
    print_curl("GET", endpoint)
    
    if DEMO_MODE:
        print("\n✅ DEMO MODE - Expected response:")
        demo_response = [
            {
                "admission_id": 1,
                "patient_id": 1,
                "hospital_id": 1,
                "priority": "high",
                "patient_condition": "Severe Pneumonia",
                "department": "General Ward",
                "admission_time": datetime.now().isoformat(),
                "discharge_time": None
            }
        ]
        print(json.dumps(demo_response, indent=2))
    else:
        response = requests.get(f"{BASE_URL}{endpoint}")
        print_response(response)


# ==================== 8. HOSPITAL LOAD ANALYTICS ====================
def test_hospital_load():
    """Test hospital load analytics - KEY FEATURE"""
    print_header("8. 🎯 Analytics: Hospital Patient Load (KEY FEATURE)")
    endpoint = "/analytics/hospital-load"
    print_request("GET", endpoint)
    print_curl("GET", endpoint)
    
    print("\n📊 Description:")
    print("  Returns current patient load for each hospital")
    print("  - Active patient count")
    print("  - Bed occupancy percentage")
    print("  - ICU occupancy percentage")
    print("  - Alert status (normal/warning/critical)")
    print("  - Auto-generates alerts if occupancy > 85%")
    
    if DEMO_MODE:
        print("\n✅ DEMO MODE - Expected response:")
        demo_response = [
            {
                "hospital_id": 1,
                "hospital_name": "Central Hospital",
                "active_patients": 1,
                "total_beds": 100,
                "bed_occupancy_percentage": 1.0,
                "total_icu_beds": 20,
                "icu_occupancy_percentage": 0.0,
                "alert_status": "normal"
            },
            {
                "hospital_id": 2,
                "hospital_name": "Medical City",
                "active_patients": 0,
                "total_beds": 150,
                "bed_occupancy_percentage": 0.0,
                "total_icu_beds": 30,
                "icu_occupancy_percentage": 0.0,
                "alert_status": "normal"
            }
        ]
        print(json.dumps(demo_response, indent=2))
    else:
        response = requests.get(f"{BASE_URL}{endpoint}")
        print_response(response)


# ==================== 9. RESOURCE STATUS ====================
def test_resource_status():
    """Test resource status analytics"""
    print_header("9. Analytics: Resource Status")
    endpoint = "/analytics/resource-status"
    print_request("GET", endpoint)
    print_curl("GET", endpoint)
    
    if DEMO_MODE:
        print("\n✅ DEMO MODE - Expected response:")
        demo_response = [
            {
                "hospital_id": 1,
                "hospital_name": "Central Hospital",
                "available_beds": 50,
                "total_beds": 100,
                "available_icu_beds": 15,
                "total_icu_beds": 20,
                "ventilators": 8,
                "oxygen_units": 50,
                "updated_at": datetime.now().isoformat()
            }
        ]
        print(json.dumps(demo_response, indent=2))
    else:
        response = requests.get(f"{BASE_URL}{endpoint}")
        print_response(response)


# ==================== 10. LOAD BALANCING ====================
def test_load_balance():
    """Test load balancing recommendation - KEY FEATURE"""
    print_header("10. 🎯 Analytics: Load Balancing (KEY FEATURE)")
    endpoint = "/analytics/load-balance"
    print_request("GET", endpoint)
    print_curl("GET", endpoint)
    
    print("\n📊 Description:")
    print("  Recommends the hospital with LOWEST patient load")
    print("  Use this to decide which hospital should accept a new patient")
    print("  Returns:")
    print("  - recommended_hospital_id: Best hospital for admission")
    print("  - current_load: Active patients in that hospital")
    print("  - available_beds: Available beds")
    print("  - bed_occupancy_percentage: Current occupancy %")
    
    if DEMO_MODE:
        print("\n✅ DEMO MODE - Expected response:")
        demo_response = {
            "recommended_hospital_id": 2,
            "recommended_hospital_name": "Medical City",
            "current_load": 0,
            "available_beds": 150,
            "bed_occupancy_percentage": 0.0,
            "reason": "Hospital with lowest occupancy (0.0%) and 150 available beds"
        }
        print(json.dumps(demo_response, indent=2))
    else:
        response = requests.get(f"{BASE_URL}{endpoint}")
        print_response(response)


# ==================== 11. ANALYTICS SUMMARY ====================
def test_analytics_summary():
    """Test analytics summary"""
    print_header("11. Analytics: Overall Summary")
    endpoint = "/analytics/summary"
    print_request("GET", endpoint)
    print_curl("GET", endpoint)
    
    if DEMO_MODE:
        print("\n✅ DEMO MODE - Expected response:")
        demo_response = {
            "total_hospitals": 2,
            "total_active_patients": 1,
            "average_bed_occupancy": 0.5,
            "critical_alerts_count": 0,
            "timestamp": datetime.now().isoformat()
        }
        print(json.dumps(demo_response, indent=2))
    else:
        response = requests.get(f"{BASE_URL}{endpoint}")
        print_response(response)


# ==================== 12. DISCHARGE PATIENT ====================
def test_discharge_patient():
    """Test patient discharge"""
    print_header("12. Discharge Patient")
    endpoint = "/admissions/1/discharge"
    print_request("POST", endpoint)
    print_curl("POST", endpoint)
    
    if DEMO_MODE:
        print("\n✅ DEMO MODE - Expected response:")
        demo_response = {
            "admission_id": 1,
            "patient_id": 1,
            "hospital_id": 1,
            "priority": "high",
            "patient_condition": "Severe Pneumonia",
            "department": "General Ward",
            "admission_time": datetime.now().isoformat(),
            "discharge_time": datetime.now().isoformat()
        }
        print(json.dumps(demo_response, indent=2))
    else:
        response = requests.post(f"{BASE_URL}{endpoint}")
        print_response(response)


# ==================== MAIN ====================
def main():
    """Run all tests"""
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + " "*58 + "║")
    print("║" + "  CareMatrix API - Testing Guide".center(58) + "║")
    print("║" + "  Predictive Hospital Flow System".center(58) + "║")
    print("║" + " "*58 + "║")
    print("╚" + "="*58 + "╝")
    
    print(f"\n🔗 Base URL: {BASE_URL}")
    print(f"📖 API Docs: http://localhost:8000/docs")
    print(f"🧪 Demo Mode: {DEMO_MODE}")
    
    # Run all tests
    test_health_check()
    test_create_hospital()
    test_create_second_hospital()
    test_create_patient()
    test_list_hospitals()
    test_create_admission()
    test_get_active_admissions()
    test_hospital_load()
    test_resource_status()
    test_load_balance()
    test_analytics_summary()
    test_discharge_patient()
    
    # Print summary
    print_header("Summary")
    print("\n✅ Testing Guide Complete!")
    print("\nKey Endpoints to Remember:")
    print("  • POST   /patients - Create patient")
    print("  • POST   /hospitals - Create hospital")
    print("  • POST   /admissions - Admit patient")
    print("  • GET    /admissions/active - Get active admissions")
    print("  • GET    /analytics/hospital-load - Hospital load analytics")
    print("  • GET    /analytics/load-balance - Load balancing recommendation 🎯")
    print("  • GET    /analytics/summary - Overall summary")
    print("\n📖 For more details: http://localhost:8000/docs")
    print("\n" + "="*60 + "\n")


if __name__ == "__main__":
    main()
