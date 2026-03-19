import random
import sqlite3
import time
import uuid
from datetime import datetime

import PridictionModel.core as coree
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel


class Hospital(BaseModel):
    name: str
    hospital_id: str
    lat: float
    lng: float


class HospitalRegister(BaseModel):
    name: str
    lat: float
    lng: float


class PridictData(BaseModel):
    hospital_id: str
    date: str


class CapacityUpdate(BaseModel):
    hospital_id: str
    department: str
    total: int
    available: int


class PatientRequest(BaseModel):
    department: str
    priority: str
    lat: float
    lng: float


class HospitalResponse(BaseModel):
    patient_id: str
    hospital_id: str
    status: str


class PatientSelect(BaseModel):
    patient_id: str
    hospital_id: str


class ResourceRequest(BaseModel):
    hospital_id: str
    resource_type: str
    quantity: int


class ResourceResponse(BaseModel):
    request_id: str
    hospital_id: str
    status: str


class ResourceSelect(BaseModel):
    request_id: str
    hospital_id: str


class HospitalRegisterWithId(BaseModel):
    hospital_id: str
    name: str
    lat: float
    lng: float


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_PATH = "carematrix.db"

_patients: dict = {}
_responses: list = []
_assignments: list = []
_response_counter = 0


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn, conn.cursor()


_conn = sqlite3.connect(DB_PATH)
_conn.executescript("""
CREATE TABLE IF NOT EXISTS hospitals (
  id TEXT PRIMARY KEY, name TEXT, lat REAL, lng REAL, status TEXT
);
CREATE TABLE IF NOT EXISTS capacity (
  hospital_id TEXT, department TEXT, total INTEGER, available INTEGER,
  PRIMARY KEY (hospital_id, department)
);
CREATE TABLE IF NOT EXISTS resource_requests (
  id TEXT PRIMARY KEY, requester_hospital_id TEXT, resource_type TEXT,
  quantity INTEGER, status TEXT DEFAULT 'open', timestamp INTEGER
);
CREATE TABLE IF NOT EXISTS resource_responses (
  id INTEGER PRIMARY KEY AUTOINCREMENT, request_id TEXT,
  provider_hospital_id TEXT, status TEXT, timestamp INTEGER
);
CREATE TABLE IF NOT EXISTS resources (
  hospital_id TEXT, resource_type TEXT, available INTEGER,
  PRIMARY KEY (hospital_id, resource_type)
);
""")
_conn.commit()
_conn.close()

KNOWN_HOSPITALS = {
    "hospital123": {
        "name": "Sarvodya General Hospital",
        "location": "Farrukh Nagar, Gurugram",
        "lat": 28.4450,
        "lng": 76.9970,
        "short": "SGH",
    },
    "hospital321": {
        "name": "Global Care Medical Centre",
        "location": "Connaught Place, New Delhi",
        "lat": 28.6329,
        "lng": 77.2195,
        "short": "GCMC",
    },
}


def _seed_known():
    conn, cursor = get_db()
    for hid, info in KNOWN_HOSPITALS.items():
        cursor.execute(
            "INSERT INTO hospitals (id, name, lat, lng, status) VALUES (?, ?, ?, ?, 'online') ON CONFLICT(id) DO UPDATE SET name=excluded.name, lat=excluded.lat, lng=excluded.lng, status='online'",
            (hid, info["name"], info["lat"], info["lng"]),
        )
    conn.commit()
    conn.close()


_seed_known()

STATIC_HOSPITALS = [
    {
        "id": "h_aiims",
        "name": "AIIMS New Delhi",
        "lat": 28.5672,
        "lng": 77.2100,
        "total": 2500,
        "base_load": 88,
    },
    {
        "id": "h_safdarjung",
        "name": "Safdarjung Hospital",
        "lat": 28.5683,
        "lng": 77.2032,
        "total": 1531,
        "base_load": 82,
    },
    {
        "id": "h_rml",
        "name": "Ram Manohar Lohia Hospital",
        "lat": 28.6226,
        "lng": 77.1986,
        "total": 1500,
        "base_load": 76,
    },
    {
        "id": "h_gtb",
        "name": "GTB Hospital Shahdara",
        "lat": 28.6721,
        "lng": 77.3042,
        "total": 1150,
        "base_load": 91,
    },
    {
        "id": "h_apollo",
        "name": "Apollo Hospital Sarita Vihar",
        "lat": 28.5498,
        "lng": 77.2826,
        "total": 710,
        "base_load": 64,
    },
    {
        "id": "h_medanta",
        "name": "Medanta The Medicity Gurugram",
        "lat": 28.4388,
        "lng": 77.0292,
        "total": 1250,
        "base_load": 71,
    },
    {
        "id": "h_fortis_ggn",
        "name": "Fortis Memorial Gurugram",
        "lat": 28.4595,
        "lng": 77.0266,
        "total": 320,
        "base_load": 55,
    },
    {
        "id": "h_max_skt",
        "name": "Max Hospital Saket",
        "lat": 28.5270,
        "lng": 77.2140,
        "total": 500,
        "base_load": 68,
    },
    {
        "id": "h_sir_ganga",
        "name": "Sir Ganga Ram Hospital",
        "lat": 28.6406,
        "lng": 77.1887,
        "total": 675,
        "base_load": 73,
    },
    {
        "id": "h_holy_family",
        "name": "Holy Family Hospital Okhla",
        "lat": 28.5623,
        "lng": 77.2714,
        "total": 395,
        "base_load": 48,
    },
    {
        "id": "h_ddumc",
        "name": "DDU Government Hospital",
        "lat": 28.6358,
        "lng": 77.1019,
        "total": 860,
        "base_load": 85,
    },
    {
        "id": "h_bses",
        "name": "BSES MG Hospital Dwarka",
        "lat": 28.5921,
        "lng": 77.0460,
        "total": 300,
        "base_load": 59,
    },
]


def _live_demand(base_load: int) -> int:
    hour = datetime.now().hour
    if 8 <= hour <= 11:
        factor = 1.12
    elif 17 <= hour <= 21:
        factor = 1.08
    elif 0 <= hour <= 5:
        factor = 0.82
    else:
        factor = 1.0
    noise = random.uniform(-4, 4)
    return min(99, max(10, round(base_load * factor + noise)))


_SURGE_POOL = [
    {
        "id": "sa_weather_1",
        "level": "HIGH",
        "code": "WEATHER_SURGE",
        "message": "Dense fog advisory active — expect 18–22% rise in respiratory and trauma admissions over next 6 hours.",
        "source": "IMD Weather Integration",
    },
    {
        "id": "sa_trend_2",
        "level": "MODERATE",
        "code": "SEASONAL_TREND",
        "message": "Dengue season peak detected. Vector-borne cases trending +31% vs. 4-week average in your catchment zone.",
        "source": "NVBDCP Trend Monitor",
    },
    {
        "id": "sa_event_3",
        "level": "MODERATE",
        "code": "MASS_EVENT",
        "message": "Large public gathering (est. 40,000 attendees) within 3 km radius this evening. Trauma & cardiac standby recommended.",
        "source": "Civic Event Feed",
    },
    {
        "id": "sa_heat_4",
        "level": "HIGH",
        "code": "HEAT_STRESS",
        "message": "Heat index 42 °C forecast for afternoon. Historical data predicts 25–30% spike in heat-stroke and dehydration cases.",
        "source": "IMD Thermal Index",
    },
    {
        "id": "sa_flu_5",
        "level": "LOW",
        "code": "ILI_TREND",
        "message": "Influenza-like illness reports up 9% this week. OPD load may increase by 12–15 patients/hour by evening.",
        "source": "IDSP Surveillance",
    },
    {
        "id": "sa_network_6",
        "level": "HIGH",
        "code": "NETWORK_OVERFLOW",
        "message": "GTB Hospital (Shahdara) at 91% capacity — patient redistribution likely. Prepare 4–6 additional beds.",
        "source": "CareMatrix Network",
    },
    {
        "id": "sa_air_7",
        "level": "MODERATE",
        "code": "AQI_ALERT",
        "message": "AQI 'Very Poor' (index 312). Predicted 20% surge in COPD/asthma emergency presentations within 8 hours.",
        "source": "CPCB Air Quality Feed",
    },
    {
        "id": "sa_weekend_8",
        "level": "LOW",
        "code": "WEEKEND_PATTERN",
        "message": "Weekend admission pattern active. ED walk-ins historically 14% higher Saturday–Sunday; plan staffing accordingly.",
        "source": "Historical Pattern Model",
    },
]

_RESOURCE_POOL = [
    {
        "hospital": "Medanta The Medicity",
        "hospital_id": "h_medanta",
        "distance_km": 8.2,
        "resources": [
            {"type": "Ventilators", "available": 4, "icon": "🫁"},
            {"type": "Oxygen Cylinders", "available": 12, "icon": "🫧"},
            {"type": "Blood Units O+", "available": 8, "icon": "🩸"},
        ],
    },
    {
        "hospital": "Max Hospital Saket",
        "hospital_id": "h_max_skt",
        "distance_km": 12.5,
        "resources": [
            {"type": "Defibrillators", "available": 2, "icon": "⚡"},
            {"type": "Saline Bottles", "available": 40, "icon": "🧴"},
            {"type": "Blood Units A+", "available": 5, "icon": "🩸"},
        ],
    },
    {
        "hospital": "Fortis Memorial Gurugram",
        "hospital_id": "h_fortis_ggn",
        "distance_km": 15.1,
        "resources": [
            {"type": "Oxygen Cylinders", "available": 6, "icon": "🫧"},
            {"type": "Syringes (×100)", "available": 200, "icon": "💉"},
            {"type": "Gloves (×100)", "available": 150, "icon": "🧤"},
        ],
    },
    {
        "hospital": "Sir Ganga Ram Hospital",
        "hospital_id": "h_sir_ganga",
        "distance_km": 9.7,
        "resources": [
            {"type": "Ventilators", "available": 2, "icon": "🫁"},
            {"type": "Wheelchairs", "available": 5, "icon": "♿"},
            {"type": "Blood Units B+", "available": 6, "icon": "🩸"},
        ],
    },
]

HOSPITAL_CSV = {
    "hospital123": "./PridictionModel/data/hospital123.csv",
    "hospital321": "./PridictionModel/data/hospital321.csv",
}


@app.post("/api/hospital/predict")
def predict_capacity(data: PridictData):
    path = HOSPITAL_CSV.get(data.hospital_id)
    if not path:
        raise HTTPException(
            status_code=404,
            detail=f"No prediction data for hospital '{data.hospital_id}'",
        )
    coree.run_training(csv_path=path)
    result = coree.predict_one(date_str=data.date)
    return result


@app.get("/api/hospital/info/{hospital_id}")
def hospital_info(hospital_id: str):
    info = KNOWN_HOSPITALS.get(hospital_id)
    if info:
        return {
            "id": hospital_id,
            "name": info["name"],
            "location": info["location"],
            "short": info["short"],
        }
    conn, cursor = get_db()
    cursor.execute("SELECT id, name FROM hospitals WHERE id=?", (hospital_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {
            "id": row[0],
            "name": row[1],
            "location": "",
            "short": row[0][:8].upper(),
        }
    return {
        "id": hospital_id,
        "name": hospital_id,
        "location": "",
        "short": hospital_id[:8].upper(),
    }


@app.get("/api/surge-alerts")
def surge_alerts(hospital_id: str = "hospital123"):
    hour = datetime.now().hour
    day = datetime.now().weekday()
    seed_val = hour // 3 + day * 8
    random.seed(seed_val)
    indices = random.sample(range(len(_SURGE_POOL)), k=3)
    selected = [_SURGE_POOL[i] for i in sorted(indices)]
    if not any(a["code"] == "NETWORK_OVERFLOW" for a in selected):
        selected.append(_SURGE_POOL[5])
    return selected[:4]


@app.get("/api/resource/pool")
def resource_pool(hospital_id: str = "hospital123"):
    return _RESOURCE_POOL


@app.post("/api/hospital/register")
def register_hospital(data: HospitalRegister):
    conn, cursor = get_db()
    hospital_id = str(uuid.uuid4())
    cursor.execute(
        "INSERT INTO hospitals VALUES (?, ?, ?, ?, 'online')",
        (hospital_id, data.name, data.lat, data.lng),
    )
    conn.commit()
    conn.close()
    return {"id": hospital_id}


@app.post("/api/hospital/capacity")
def update_capacity(data: CapacityUpdate):
    conn, cursor = get_db()
    cursor.execute(
        "INSERT INTO capacity VALUES (?, ?, ?, ?) ON CONFLICT(hospital_id, department) DO UPDATE SET total=excluded.total, available=excluded.available",
        (data.hospital_id, data.department, data.total, data.available),
    )
    conn.commit()
    conn.close()
    return {"status": "ok"}


@app.get("/api/hospital/open-requests")
def open_requests(department: str = None):
    result = [p for p in _patients.values() if p["status"] == "open"]
    if department:
        result = [p for p in result if p["department"] == department]
    return [tuple(p.values()) for p in result]


@app.post("/api/hospital/respond")
def hospital_respond(data: HospitalResponse):
    global _response_counter
    _response_counter += 1
    _responses.append(
        {
            "id": _response_counter,
            "patient_id": data.patient_id,
            "hospital_id": data.hospital_id,
            "status": data.status,
            "timestamp": int(time.time()),
        }
    )
    return {"status": "recorded"}


@app.post("/api/request")
def create_request(data: PatientRequest):
    patient_id = str(uuid.uuid4())
    _patients[patient_id] = {
        "id": patient_id,
        "department": data.department,
        "priority": data.priority,
        "lat": data.lat,
        "lng": data.lng,
        "assigned": 0,
        "status": "open",
    }
    return {"patient_id": patient_id}


@app.get("/api/patient/responses")
def get_responses(patient_id: str):
    accepted = [
        r
        for r in _responses
        if r["patient_id"] == patient_id and r["status"] == "accepted"
    ]
    result = []
    conn, cursor = get_db()
    for r in accepted:
        cursor.execute(
            "SELECT id, name, lat, lng FROM hospitals WHERE id=?", (r["hospital_id"],)
        )
        h = cursor.fetchone()
        if h:
            result.append((h[0], h[1], h[2], h[3]))
    conn.close()
    return result


@app.post("/api/patient/select")
def select_hospital(data: PatientSelect):
    resp = next(
        (
            r
            for r in _responses
            if r["patient_id"] == data.patient_id
            and r["hospital_id"] == data.hospital_id
            and r["status"] == "accepted"
        ),
        None,
    )
    if not resp:
        return {"status": "invalid_selection"}

    p = _patients.get(data.patient_id)
    if not p or p["assigned"] == 1:
        return {"status": "already_assigned"}

    conn, cursor = get_db()
    cursor.execute(
        "SELECT * FROM capacity WHERE hospital_id=? AND department=?",
        (data.hospital_id, p["department"]),
    )
    cap = cursor.fetchone()
    if not cap or cap[3] <= 0:
        conn.close()
        return {"status": "no_capacity"}

    p["assigned"] = 1
    p["status"] = "assigned"
    _assignments.append(
        {
            "patient_id": data.patient_id,
            "hospital_id": data.hospital_id,
            "timestamp": int(time.time()),
        }
    )

    cursor.execute(
        "UPDATE capacity SET available=available-1 WHERE hospital_id=? AND department=?",
        (data.hospital_id, p["department"]),
    )
    conn.commit()
    conn.close()
    return {"status": "assigned"}


@app.get("/api/getResult")
def get_result(patient_id: str):
    assignment = next((a for a in _assignments if a["patient_id"] == patient_id), None)
    if not assignment:
        return {"status": "pending"}
    conn, cursor = get_db()
    cursor.execute("SELECT * FROM hospitals WHERE id=?", (assignment["hospital_id"],))
    h = cursor.fetchone()
    conn.close()
    return {"status": "assigned", "hospital": tuple(h) if h else None}


@app.post("/api/resource/request")
def create_resource_request(data: ResourceRequest):
    conn, cursor = get_db()
    request_id = str(uuid.uuid4())
    cursor.execute(
        "INSERT INTO resource_requests VALUES (?, ?, ?, ?, 'open', ?)",
        (
            request_id,
            data.hospital_id,
            data.resource_type,
            data.quantity,
            int(time.time()),
        ),
    )
    conn.commit()
    conn.close()
    return {"request_id": request_id}


@app.get("/api/resource/open")
def get_open_resource_requests():
    conn, cursor = get_db()
    cursor.execute("SELECT * FROM resource_requests WHERE status='open'")
    rows = cursor.fetchall()
    conn.close()
    return [tuple(r) for r in rows]


@app.post("/api/resource/respond")
def respond_resource(data: ResourceResponse):
    conn, cursor = get_db()
    cursor.execute(
        "INSERT INTO resource_responses (request_id, provider_hospital_id, status, timestamp) VALUES (?, ?, ?, ?)",
        (data.request_id, data.hospital_id, data.status, int(time.time())),
    )
    conn.commit()
    conn.close()
    return {"status": "recorded"}


@app.get("/api/resource/responses")
def get_resource_responses(request_id: str):
    conn, cursor = get_db()
    cursor.execute(
        "SELECT r.provider_hospital_id, h.name, h.lat, h.lng FROM resource_responses r JOIN hospitals h ON r.provider_hospital_id = h.id WHERE r.request_id=? AND r.status='accepted'",
        (request_id,),
    )
    rows = cursor.fetchall()
    conn.close()
    return [tuple(r) for r in rows]


@app.post("/api/resource/select")
def select_resource_provider(data: ResourceSelect):
    conn, cursor = get_db()
    cursor.execute(
        "SELECT * FROM resource_responses WHERE request_id=? AND provider_hospital_id=? AND status='accepted'",
        (data.request_id, data.hospital_id),
    )
    if not cursor.fetchone():
        conn.close()
        return {"status": "invalid_selection"}
    cursor.execute(
        "UPDATE resource_requests SET status='fulfilled' WHERE id=?", (data.request_id,)
    )
    conn.commit()
    conn.close()
    return {"status": "fulfilled"}


@app.get("/api/heatmap")
def heatmap():
    result = []
    for sh in STATIC_HOSPITALS:
        demand = _live_demand(sh["base_load"])
        available = max(0, round(sh["total"] * (1 - demand / 100)))
        result.append(
            {
                "id": sh["id"],
                "name": sh["name"],
                "lat": sh["lat"],
                "lng": sh["lng"],
                "total": sh["total"],
                "available": available,
                "demand": demand,
            }
        )
    conn, cursor = get_db()
    cursor.execute(
        "SELECT h.id, h.name, h.lat, h.lng, SUM(c.total), SUM(c.available) FROM hospitals h LEFT JOIN capacity c ON h.id=c.hospital_id GROUP BY h.id"
    )
    rows = cursor.fetchall()
    conn.close()
    static_ids = {sh["id"] for sh in STATIC_HOSPITALS}
    for r in rows:
        if r[0] in static_ids:
            continue
        total = r[4] if r[4] else 0
        available = r[5] if r[5] else 0
        demand = round((1 - available / total) * 100) if total else 0
        result.append(
            {
                "id": r[0],
                "name": r[1],
                "lat": r[2],
                "lng": r[3],
                "total": total,
                "available": available,
                "demand": demand,
            }
        )
    return result


@app.post("/api/hospital/register-with-id")
def register_hospital_with_id(data: HospitalRegisterWithId):
    conn, cursor = get_db()
    cursor.execute(
        "INSERT INTO hospitals (id, name, lat, lng, status) VALUES (?, ?, ?, ?, 'online') ON CONFLICT(id) DO UPDATE SET name=excluded.name, lat=excluded.lat, lng=excluded.lng, status='online'",
        (data.hospital_id, data.name, data.lat, data.lng),
    )
    conn.commit()
    conn.close()
    return {"status": "ok"}


@app.delete("/api/patient/{patient_id}")
def delete_patient(patient_id: str):
    global _responses
    _patients.pop(patient_id, None)
    _responses = [r for r in _responses if r["patient_id"] != patient_id]
    return {"status": "deleted"}


@app.get("/api/debug/state")
def debug_state():
    conn, cursor = get_db()
    data = {
        "hospitals": [
            tuple(r) for r in cursor.execute("SELECT * FROM hospitals").fetchall()
        ],
        "patients": list(_patients.values()),
        "responses": _responses,
        "assignments": _assignments,
    }
    conn.close()
    return data


class PatientDenyResponse(BaseModel):
    patient_id: str
    hospital_id: str


@app.post("/api/patient/deny-response")
def deny_response(data: PatientDenyResponse):
    for r in _responses:
        if (
            r["patient_id"] == data.patient_id
            and r["hospital_id"] == data.hospital_id
            and r["status"] == "accepted"
        ):
            r["status"] = "denied_by_source"
    return {"status": "denied"}


@app.get("/api/patient/acceptance-status")
def acceptance_status(patient_id: str, hospital_id: str):
    assignment = next((a for a in _assignments if a["patient_id"] == patient_id), None)
    if assignment:
        if assignment["hospital_id"] == hospital_id:
            return {"status": "confirmed"}
        return {"status": "denied_by_source"}

    matching = [
        r
        for r in _responses
        if r["patient_id"] == patient_id and r["hospital_id"] == hospital_id
    ]
    if not matching:
        return {"status": "pending"}
    latest = max(matching, key=lambda x: x["id"])
    if latest["status"] == "denied_by_source":
        return {"status": "denied_by_source"}
    return {"status": "pending"}


class HospitalInit(BaseModel):
    hospital_id: str
    name: str = ""
    lat: float = 0.0
    lng: float = 0.0


@app.post("/api/hospital/init")
def init_hospital(data: HospitalInit):
    conn, cursor = get_db()

    cursor.execute(
        "SELECT id, name, lat, lng FROM hospitals WHERE id=?",
        (data.hospital_id,),
    )
    row = cursor.fetchone()

    if row:
        conn.close()
        return {
            "id": row[0],
            "name": row[1],
            "lat": row[2],
            "lng": row[3],
            "status": "existing",
        }

    cursor.execute(
        "INSERT INTO hospitals (id, name, lat, lng, status) VALUES (?, ?, ?, ?, 'online')",
        (
            data.hospital_id,
            data.name or data.hospital_id,
            data.lat,
            data.lng,
        ),
    )

    conn.commit()
    conn.close()

    return {
        "id": data.hospital_id,
        "name": data.name or data.hospital_id,
        "lat": data.lat,
        "lng": data.lng,
        "status": "created",
    }


@app.post("/api/register/hospitals")
def store_hospital(data: Hospital):
    conn, cursor = get_db()

    cursor.execute(
        """
        INSERT INTO hospitals (id, name, lat, lng, status)
        VALUES (?, ?, ?, ?, 'online')
        ON CONFLICT(id) DO UPDATE SET
            name = excluded.name,
            status = 'online'
        """,
        (data.hospital_id, data.name, data.lat, data.lng),
    )

    conn.commit()
    conn.close()

    return {"status": "stored"}
