const BASE = "http://127.0.0.1:8000";

export async function registerHospital(name: string, lat: number, lng: number) {
  const r = await fetch(`${BASE}/api/hospital/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name, lat, lng }),
  });
  return r.json() as Promise<{ id: string }>;
}

export async function updateCapacity(
  hospital_id: string,
  department: string,
  total: number,
  available: number,
) {
  await fetch(`${BASE}/api/hospital/capacity`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ hospital_id, department, total, available }),
  });
}

export async function getOpenRequests(department?: string) {
  const url = department
    ? `${BASE}/api/hospital/open-requests?department=${encodeURIComponent(department)}`
    : `${BASE}/api/hospital/open-requests`;
  const r = await fetch(url);
  const rows: any[] = await r.json();
  return rows.map((row) => ({
    id: row[0] as string,
    department: row[1] as string,
    priority: row[2] as string,
    lat: row[3] as number,
    lng: row[4] as number,
    assigned: row[5] as number,
    status: row[6] as string,
  }));
}

export async function respondToPatient(
  patient_id: string,
  hospital_id: string,
  status: "accepted" | "rejected",
) {
  await fetch(`${BASE}/api/hospital/respond`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ patient_id, hospital_id, status }),
  });
}

export async function createPatientRequest(
  department: string,
  priority: string,
  lat: number,
  lng: number,
) {
  const r = await fetch(`${BASE}/api/request`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ department, priority, lat, lng }),
  });
  return r.json() as Promise<{ patient_id: string }>;
}

export async function getPatientResponses(patient_id: string) {
  const r = await fetch(
    `${BASE}/api/patient/responses?patient_id=${patient_id}`,
  );
  const rows: any[] = await r.json();
  return rows.map((row) => ({
    hospital_id: row[0] as string,
    name: row[1] as string,
    lat: row[2] as number,
    lng: row[3] as number,
  }));
}

export async function selectHospital(patient_id: string, hospital_id: string) {
  const r = await fetch(`${BASE}/api/patient/select`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ patient_id, hospital_id }),
  });
  return r.json() as Promise<{ status: string }>;
}

export async function getHeatmap() {
  const r = await fetch(`${BASE}/api/heatmap`);
  return r.json() as Promise<
    {
      id: string;
      name: string;
      lat: number;
      lng: number;
      total: number;
      available: number;
      demand: number;
    }[]
  >;
}

export async function createResourceRequest(
  hospital_id: string,
  resource_type: string,
  quantity: number,
) {
  const r = await fetch(`${BASE}/api/resource/request`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ hospital_id, resource_type, quantity }),
  });
  return r.json() as Promise<{ request_id: string }>;
}

export async function getOpenResourceRequests() {
  const r = await fetch(`${BASE}/api/resource/open`);
  const rows: any[] = await r.json();
  return rows.map((row) => ({
    id: row[0] as string,
    requester_hospital_id: row[1] as string,
    resource_type: row[2] as string,
    quantity: row[3] as number,
    status: row[4] as string,
    timestamp: row[5] as number,
  }));
}

export async function respondToResource(
  request_id: string,
  hospital_id: string,
  status: "accepted" | "rejected",
) {
  await fetch(`${BASE}/api/resource/respond`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ request_id, hospital_id, status }),
  });
}
