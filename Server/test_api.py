import requests
import time

BASE_URL = "http://127.0.0.1:8000"

def print_result(name, success):
    print(f"{name}: {'✅ PASS' if success else '❌ FAIL'}")


def test_hospital_register():
    res = requests.post(f"{BASE_URL}/api/hospital/register", json={
        "name": "City Hospital",
        "lat": 28.6,
        "lng": 77.2
    })
    data = res.json()
    return data.get("id")


def test_capacity(hospital_id):
    res = requests.post(f"{BASE_URL}/api/hospital/capacity", json={
        "hospital_id": hospital_id,
        "department": "ICU",
        "total": 10,
        "available": 5
    })
    return res.json().get("status") == "ok"


def test_patient_request(hospital_id):
    res = requests.post(f"{BASE_URL}/api/request", json={
        "hospital_id": hospital_id,
        "department": "ICU",
        "priority": "high",
        "lat": 28.61,
        "lng": 77.21
    })
    return res.json().get("patient_id")


def test_poll(hospital_id):
    res = requests.get(f"{BASE_URL}/api/hospital/poll", params={
        "hospital_id": hospital_id
    })
    return isinstance(res.json(), list)


def test_accept(patient_id, hospital_id):
    res = requests.post(f"{BASE_URL}/api/accept", json={
        "patient_id": patient_id,
        "hospital_id": hospital_id
    })
    return res.json().get("status") == "accepted"


def test_get_result(patient_id):
    res = requests.get(f"{BASE_URL}/api/getResult", params={
        "patient_id": patient_id
    })
    return res.json().get("status") in ["assigned", "pending"]


def test_heatmap():
    res = requests.get(f"{BASE_URL}/api/heatmap")
    return isinstance(res.json(), list)


def test_debug():
    res = requests.get(f"{BASE_URL}/api/debug/state")
    data = res.json()
    return "hospitals" in data and "patients" in data


# =========================
# RUN ALL TESTS
# =========================

if __name__ == "__main__":
    print("🚀 Running API Tests...\n")

    hospital_id = test_hospital_register()
    print_result("Hospital Register", hospital_id is not None)

    capacity_ok = test_capacity(hospital_id)
    print_result("Capacity Update", capacity_ok)

    patient_id = test_patient_request(hospital_id)
    print_result("Patient Request", patient_id is not None)

    poll_ok = test_poll(hospital_id)
    print_result("Poll Patients", poll_ok)

    accept_ok = test_accept(patient_id, hospital_id)
    print_result("Accept Patient", accept_ok)

    # wait for DB consistency
    time.sleep(1)

    result_ok = test_get_result(patient_id)
    print_result("Get Result", result_ok)

    heatmap_ok = test_heatmap()
    print_result("Heatmap", heatmap_ok)

    debug_ok = test_debug()
    print_result("Debug State", debug_ok)

    print("\n✅ Testing Completed")