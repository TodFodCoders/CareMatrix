from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
import uuid
import time
from pydantic import BaseModel
import PridictionModel.core as coree
# =========================
# MODELS
# =========================

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
    status: str  # accepted / rejected


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

# =========================
# APP INIT
# =========================

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
  department TEXT,
  priority TEXT,
  lat REAL,
  lng REAL,
  assigned INTEGER DEFAULT 0,
  status TEXT DEFAULT 'open'
);

CREATE TABLE IF NOT EXISTS responses (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  patient_id TEXT,
  hospital_id TEXT,
  status TEXT,
  timestamp INTEGER
);

CREATE TABLE IF NOT EXISTS assignments (
  patient_id TEXT,
  hospital_id TEXT,
  timestamp INTEGER
);
                     
CREATE TABLE IF NOT EXISTS resource_requests (
  id TEXT PRIMARY KEY,
  requester_hospital_id TEXT,
  resource_type TEXT,
  quantity INTEGER,
  status TEXT DEFAULT 'open',
  timestamp INTEGER
);

CREATE TABLE IF NOT EXISTS resource_responses (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  request_id TEXT,
  provider_hospital_id TEXT,
  status TEXT,
  timestamp INTEGER
);

CREATE TABLE IF NOT EXISTS resources (
  hospital_id TEXT,
  resource_type TEXT,
  available INTEGER,
  PRIMARY KEY (hospital_id, resource_type)
);
""")
conn.commit()

# =========================
# HOSPITAL ROUTES
# =========================

@app.post("/api/hospital/predict")
def predict_capacity(data: PridictData):
    dic = {
        'hospital123': "C:\\Project\\CareMatrix\\Server\\PridictionModel\\data\\hospital123.csv",
        'hospital321': "C:\\Project\\CareMatrix\\Server\\PridictionModel\\data\\hospital321.csv"
    }
    path = dic[data.hospital_id]
    print(path)
    coree.run_training(csv_path=path)
    result = coree.predict_one(date_str=data.date)
    return result

@app.post("/api/resource/request")
def create_resource_request(data: ResourceRequest):
    request_id = str(uuid.uuid4())

    cursor.execute("""
        INSERT INTO resource_requests
        VALUES (?, ?, ?, ?, 'open', ?)
    """, (
        request_id,
        data.hospital_id,
        data.resource_type,
        data.quantity,
        int(time.time())
    ))
    conn.commit()

    return {"request_id": request_id}

@app.get("/api/resource/open")
def get_open_resource_requests():
    cursor.execute("""
        SELECT * FROM resource_requests
        WHERE status='open'
    """)
    return cursor.fetchall()

@app.post("/api/resource/respond")
def respond_resource(data: ResourceResponse):

    cursor.execute("""
        INSERT INTO resource_responses
        (request_id, provider_hospital_id, status, timestamp)
        VALUES (?, ?, ?, ?)
    """, (
        data.request_id,
        data.hospital_id,
        data.status,
        int(time.time())
    ))

    conn.commit()
    return {"status": "recorded"}

@app.get("/api/resource/responses")
def get_resource_responses(request_id: str):

    cursor.execute("""
        SELECT r.provider_hospital_id, h.name, h.lat, h.lng
        FROM resource_responses r
        JOIN hospitals h ON r.provider_hospital_id = h.id
        WHERE r.request_id=? AND r.status='accepted'
    """, (request_id,))

    return cursor.fetchall()


@app.post("/api/resource/select")
def select_resource_provider(data: ResourceSelect):

    # validate response
    cursor.execute("""
        SELECT * FROM resource_responses
        WHERE request_id=? AND provider_hospital_id=? AND status='accepted'
    """, (data.request_id, data.hospital_id))

    if not cursor.fetchone():
        return {"status": "invalid_selection"}

    # update request
    cursor.execute("""
        UPDATE resource_requests
        SET status='fulfilled'
        WHERE id=?
    """, (data.request_id,))

    conn.commit()

    return {"status": "fulfilled"}

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
# PATIENT REQUEST (BROADCAST)
# =========================

@app.post("/api/request")
def create_request(data: PatientRequest):
    patient_id = str(uuid.uuid4())

    cursor.execute("""
        INSERT INTO patients (id, department, priority, lat, lng, assigned, status)
        VALUES (?, ?, ?, ?, ?, 0, 'open')
    """, (
        patient_id,
        data.department,
        data.priority,
        data.lat,
        data.lng
    ))
    conn.commit()

    return {"patient_id": patient_id}


# =========================
# HOSPITAL FETCH OPEN REQUESTS
# =========================

@app.get("/api/hospital/open-requests")
def open_requests(department: str = None):
    if department:
        cursor.execute("""
            SELECT * FROM patients
            WHERE status='open' AND department=?
        """, (department,))
    else:
        cursor.execute("""
            SELECT * FROM patients
            WHERE status='open'
        """)

    return cursor.fetchall()


# =========================
# HOSPITAL RESPONDS
# =========================

@app.post("/api/hospital/respond")
def hospital_respond(data: HospitalResponse):

    cursor.execute("""
        INSERT INTO responses (patient_id, hospital_id, status, timestamp)
        VALUES (?, ?, ?, ?)
    """, (
        data.patient_id,
        data.hospital_id,
        data.status,
        int(time.time())
    ))
    conn.commit()

    return {"status": "recorded"}


# =========================
# PATIENT GET RESPONSES
# =========================

@app.get("/api/patient/responses")
def get_responses(patient_id: str):

    cursor.execute("""
        SELECT r.hospital_id, h.name, h.lat, h.lng
        FROM responses r
        JOIN hospitals h ON r.hospital_id = h.id
        WHERE r.patient_id=? AND r.status='accepted'
    """, (patient_id,))

    return cursor.fetchall()


# =========================
# PATIENT SELECT FINAL HOSPITAL
# =========================

@app.post("/api/patient/select")
def select_hospital(data: PatientSelect):

    # check if hospital responded
    cursor.execute("""
        SELECT * FROM responses
        WHERE patient_id=? AND hospital_id=? AND status='accepted'
    """, (data.patient_id, data.hospital_id))

    if not cursor.fetchone():
        return {"status": "invalid_selection"}

    # get patient
    cursor.execute("SELECT * FROM patients WHERE id=?", (data.patient_id,))
    p = cursor.fetchone()

    if not p or p[5] == 1:
        return {"status": "already_assigned"}

    # check capacity
    cursor.execute("""
        SELECT * FROM capacity
        WHERE hospital_id=? AND department=?
    """, (data.hospital_id, p[1]))

    cap = cursor.fetchone()

    if not cap or cap[3] <= 0:
        return {"status": "no_capacity"}

    # assign
    cursor.execute("""
        UPDATE patients SET assigned=1, status='assigned'
        WHERE id=?
    """, (data.patient_id,))

    cursor.execute("""
        INSERT INTO assignments VALUES (?, ?, ?)
    """, (
        data.patient_id,
        data.hospital_id,
        int(time.time())
    ))

    cursor.execute("""
        UPDATE capacity
        SET available=available-1
        WHERE hospital_id=? AND department=?
    """, (data.hospital_id, p[1]))

    conn.commit()

    return {"status": "assigned"}


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
        "responses": cursor.execute("SELECT * FROM responses").fetchall(),
        "assignments": cursor.execute("SELECT * FROM assignments").fetchall()
    }