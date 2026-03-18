from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
import uuid
import time
from pydantic import BaseModel

class HospitalRegister(BaseModel):
    name: str
    lat: float
    lng: float


class CapacityUpdate(BaseModel):
    hospital_id: str
    department: str
    total: int
    available: int


class PatientRequest(BaseModel):
    hospital_id: str
    department: str
    priority: str
    lat: float
    lng: float


class AcceptRequest(BaseModel):
    patient_id: str
    hospital_id: str


app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# DB connection
conn = sqlite3.connect("carematrix.db", check_same_thread=False)
cursor = conn.cursor()

# =========================
# DB INIT
# =========================

cursor.executescript("""
CREATE TABLE IF NOT EXISTS hospitals (
  id TEXT PRIMARY KEY,
  name TEXT,
  lat REAL,
  lng REAL,
  status TEXT
);

CREATE TABLE IF NOT EXISTS capacity (
  hospital_id TEXT,
  department TEXT,
  total INTEGER,
  available INTEGER,
  PRIMARY KEY (hospital_id, department)
);

CREATE TABLE IF NOT EXISTS patients (
  id TEXT PRIMARY KEY,
  hospital_id TEXT,
  department TEXT,
  priority TEXT,
  lat REAL,
  lng REAL,
  assigned INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS assignments (
  patient_id TEXT,
  hospital_id TEXT,
  timestamp INTEGER
);
""")
conn.commit()

# =========================
# HOSPITAL ROUTES
# =========================

@app.post("/api/hospital/register")
def register_hospital(data: HospitalRegister):
    hospital_id = str(uuid.uuid4())

    cursor.execute(
        "INSERT INTO hospitals VALUES (?, ?, ?, ?, 'online')",
        (hospital_id, data.name, data.lat, data.lng)
    )
    conn.commit()

    return {"id": hospital_id}

@app.post("/api/hospital/capacity")
def update_capacity(data: CapacityUpdate):
    cursor.execute("""
        INSERT INTO capacity VALUES (?, ?, ?, ?)
        ON CONFLICT(hospital_id, department)
        DO UPDATE SET total=?, available=?
    """, (
        data.hospital_id,
        data.department,
        data.total,
        data.available,
        data.total,
        data.available
    ))
    conn.commit()

    return {"status": "ok"}


# =========================
# PATIENT ROUTES
# =========================

@app.post("/api/request")
def create_request(data: PatientRequest):
    patient_id = str(uuid.uuid4())

    cursor.execute("""
        INSERT INTO patients VALUES (?, ?, ?, ?, ?, ?, 0)
    """, (
        patient_id,
        data.hospital_id,
        data.department,
        data.priority,
        data.lat,
        data.lng
    ))
    conn.commit()

    return {"patient_id": patient_id}


# =========================
# POLLING
# =========================

@app.get("/api/hospital/poll")
def poll_patients(hospital_id: str):
    cursor.execute("""
        SELECT * FROM patients
        WHERE assigned=0 AND hospital_id=?
    """, (hospital_id,))

    rows = cursor.fetchall()
    return rows


# =========================
# ACCEPT
# =========================

@app.post("/api/accept")
def accept_patient(data: AcceptRequest):

    cursor.execute("SELECT * FROM patients WHERE id=?", (data.patient_id,))
    p = cursor.fetchone()

    if not p or p[6] == 1:
        return {"status": "invalid"}

    if p[1] != data.hospital_id:
        return {"status": "not_authorized"}

    cursor.execute("""
        SELECT * FROM capacity
        WHERE hospital_id=? AND department=?
    """, (data.hospital_id, p[2]))

    cap = cursor.fetchone()

    if not cap or cap[3] <= 0:
        return {"status": "no_capacity"}

    cursor.execute("UPDATE patients SET assigned=1 WHERE id=?", (data.patient_id,))

    cursor.execute("""
        INSERT INTO assignments VALUES (?, ?, ?)
    """, (
        data.patient_id,
        data.hospital_id,
        int(time.time())
    ))

    cursor.execute("""
        UPDATE capacity SET available=available-1
        WHERE hospital_id=? AND department=?
    """, (data.hospital_id, p[2]))

    conn.commit()

    return {"status": "accepted"}


# =========================
# RESULT
# =========================

@app.get("/api/getResult")
def get_result(patient_id: str):
    cursor.execute("""
        SELECT * FROM assignments WHERE patient_id=?
    """, (patient_id,))
    a = cursor.fetchone()

    if not a:
        return {"status": "pending"}

    cursor.execute("""
        SELECT * FROM hospitals WHERE id=?
    """, (a[1],))
    h = cursor.fetchone()

    return {
        "status": "assigned",
        "hospital": h
    }


# =========================
# HEATMAP
# =========================

@app.get("/api/heatmap")
def heatmap():
    cursor.execute("""
        SELECT h.id, h.name, h.lat, h.lng,
               SUM(c.total), SUM(c.available)
        FROM hospitals h
        LEFT JOIN capacity c ON h.id=c.hospital_id
        GROUP BY h.id
    """)

    rows = cursor.fetchall()

    result = []
    for r in rows:
        total = r[4] if r[4] else 0
        available = r[5] if r[5] else 0

        demand = round((1 - available / total) * 100) if total else 0

        result.append({
            "id": r[0],
            "name": r[1],
            "lat": r[2],
            "lng": r[3],
            "total": total,
            "available": available,
            "demand": demand
        })

    return result


# =========================
# DEBUG
# =========================

@app.get("/api/debug/state")
def debug_state():
    return {
        "hospitals": cursor.execute("SELECT * FROM hospitals").fetchall(),
        "patients": cursor.execute("SELECT * FROM patients").fetchall(),
        "assignments": cursor.execute("SELECT * FROM assignments").fetchall()
    }


# =========================
# START
# =========================

# Run using: uvicorn main:app --reload