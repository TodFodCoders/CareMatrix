import { useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import "./dashboard.css";
import {
  createPatientRequest,
  getOpenRequests,
  getPatientResponses,
  respondToPatient,
  selectHospital,
} from "../api";
import { useHospital } from "../HospitalContext";

type TransferRequest = {
  id: string;
  department: string;
  priority: string;
  status: "PENDING" | "ADMITTED" | "DECLINED";
};

type PatientStatus = {
  patientId: string;
  name: string;
  matches: { hospital_id: string; name: string }[];
  selected: string | null;
};

function Dashboard() {
  const [ribbonCycle, setRibbonCycle] = useState(0);
  const navigate = useNavigate();
  const { hospitalId } = useHospital();

  const [requests, setRequests] = useState<TransferRequest[]>([]);
  const [patients, setPatients] = useState<PatientStatus[]>([]);
  const seenIds = useRef<Set<string>>(new Set());
  const patientsRef = useRef<PatientStatus[]>([]);
  patientsRef.current = patients;

  const [formData, setFormData] = useState({
    name: "",
    age: "",
    contact: "",
    bloodGroup: "O+",
    priority: "High",
    condition: "",
    department: "Emergency",
  });

  const triggerRibbon = () => setRibbonCycle((v) => v + 1);

  useEffect(() => {
    setRibbonCycle(1);

    const poll = async () => {
      const open = await getOpenRequests().catch(() => []);
      const fresh = open.filter((r) => !seenIds.current.has(r.id));
      if (fresh.length === 0) return;

      fresh.forEach((r) => seenIds.current.add(r.id));
      setRequests((prev) =>
        [
          ...fresh.map((r) => ({
            id: r.id,
            department: r.department,
            priority: r.priority,
            status: "PENDING" as const,
          })),
          ...prev,
        ].slice(0, 50),
      );
    };

    poll();
    const iv = setInterval(poll, 3000);
    return () => clearInterval(iv);
  }, []);

  useEffect(() => {
    const poll = async () => {
      const current = patientsRef.current;
      for (const p of current) {
        if (p.selected) continue;
        const responses = await getPatientResponses(p.patientId).catch(
          () => [],
        );
        if (responses.length === 0) continue;
        setPatients((prev) =>
          prev.map((x) =>
            x.patientId === p.patientId ? { ...x, matches: responses } : x,
          ),
        );
      }
    };

    const iv = setInterval(poll, 4000);
    return () => clearInterval(iv);
  }, []);

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>,
  ) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.name || !formData.age || !formData.contact) {
      alert("Please fill all required fields");
      return;
    }

    triggerRibbon();

    const res = await createPatientRequest(
      formData.department,
      formData.priority,
      28.6,
      77.1,
    ).catch(() => null);

    if (!res) {
      alert("Backend unreachable — patient not registered");
      return;
    }

    setPatients((prev) => [
      {
        patientId: res.patient_id,
        name: formData.name,
        matches: [],
        selected: null,
      },
      ...prev,
    ]);

    setFormData({
      name: "",
      age: "",
      contact: "",
      bloodGroup: "O+",
      priority: "High",
      condition: "",
      department: "Emergency",
    });
  };

  const handleDecision = async (
    id: string,
    decision: "ADMITTED" | "DECLINED",
  ) => {
    if (!hospitalId) return;
    const apiStatus = decision === "ADMITTED" ? "accepted" : "rejected";
    await respondToPatient(id, hospitalId, apiStatus).catch(() => {});

    setRequests((prev) =>
      prev.map((r) => (r.id === id ? { ...r, status: decision } : r)),
    );

    // keep id in seenIds so it never re-appears after polling — do NOT delete it
    setTimeout(() => {
      setRequests((prev) => prev.filter((r) => r.id !== id));
    }, 1500);
  };

  const handleSelectHospital = async (patientId: string, hId: string) => {
    const res = await selectHospital(patientId, hId).catch(() => null);
    if (res?.status === "assigned") {
      setPatients((prev) =>
        prev.map((p) =>
          p.patientId === patientId ? { ...p, selected: hId } : p,
        ),
      );
    }
  };

  return (
    <main
      className={`dashboard-shell ${ribbonCycle > 0 ? "animate-ribbon" : ""}`}
      data-ribbon-cycle={ribbonCycle % 2}
    >
      <header className="dashboard-topbar">
        <div className="brand-block">
          <div className="brand-logo" />
          <p className="dashboard-label">Hospital Management System</p>
          <h1>CareMatrix General Hospital</h1>
        </div>

        <div className="account-menu">
          <div className="account-avatar">DR</div>
          <button className="signout-button" onClick={() => navigate("/login")}>
            Sign Out
          </button>
        </div>
      </header>

      <section className="dashboard-grid">
        <section className="welcome-panel">
          <div className="hero-cross" />
          <div className="panel-logo" />
          <p className="dashboard-label">Emergency Access</p>
          <h2>Welcome</h2>
          <p className="welcome-copy">Rapid intake controls.</p>

          <div className="quick-links">
            <button className="mini-action">Register Patient</button>
            <button
              className="mini-action"
              onClick={() => navigate("/inventory")}
            >
              Inventory Management
            </button>
            <button
              className="mini-action"
              onClick={() => navigate("/predictions")}
            >
              Predictions
            </button>
            <button
              className="mini-action"
              onClick={() => navigate("/heatmap")}
            >
              Heat Map
            </button>
          </div>
        </section>

        <section className="workspace-panel split">
          <section className="form-panel">
            <div className="section-heading">
              <div className="panel-logo" />
              <div>
                <p className="dashboard-label">Quick Register</p>
                <h3>New Patient</h3>
              </div>
            </div>

            <form className="quick-form" onSubmit={handleSubmit}>
              <label>
                Patient Name
                <input
                  name="name"
                  value={formData.name}
                  onChange={handleChange}
                />
              </label>

              <div className="form-grid">
                <input
                  name="age"
                  value={formData.age}
                  onChange={handleChange}
                  placeholder="Age"
                />
                <input
                  name="contact"
                  value={formData.contact}
                  onChange={handleChange}
                  placeholder="Contact"
                />
              </div>

              <div className="form-grid">
                <select
                  name="bloodGroup"
                  value={formData.bloodGroup}
                  onChange={handleChange}
                >
                  <option>O+</option>
                  <option>O-</option>
                  <option>A+</option>
                  <option>B+</option>
                </select>
                <select
                  name="priority"
                  value={formData.priority}
                  onChange={handleChange}
                >
                  <option>Critical</option>
                  <option>High</option>
                  <option>Moderate</option>
                  <option>Low</option>
                </select>
              </div>

              <label>
                Condition
                <input
                  name="condition"
                  value={formData.condition}
                  onChange={handleChange}
                />
              </label>

              <select
                name="department"
                value={formData.department}
                onChange={handleChange}
              >
                <option>Emergency</option>
                <option>ICU</option>
                <option>Surgery</option>
                <option>Radiology</option>
              </select>

              <button className="action-card">Register Patient</button>
            </form>
          </section>

          <section className="notification-panel">
            <div className="notif-block">
              <h3>Incoming Transfers</h3>
              <div className="notif-scroll">
                {requests.length === 0 && (
                  <p className="notif-empty">No open requests</p>
                )}
                {requests.map((r) => (
                  <div key={r.id} className="notif-item">
                    <div>
                      <strong>{r.department}</strong>
                      <p className="notif-sub">Priority: {r.priority}</p>
                      <p className={`status-${r.status.toLowerCase()}`}>
                        {r.status}
                      </p>
                    </div>
                    {r.status === "PENDING" && (
                      <div className="notif-actions">
                        <button
                          onClick={() => handleDecision(r.id, "ADMITTED")}
                        >
                          ✓
                        </button>
                        <button
                          onClick={() => handleDecision(r.id, "DECLINED")}
                        >
                          ✕
                        </button>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>

            <div className="notif-block">
              <h3>Patient Status</h3>
              <div className="notif-scroll">
                {patients.length === 0 && (
                  <p className="notif-empty">No patients registered yet</p>
                )}
                {patients.map((p) => (
                  <div key={p.patientId} className="notif-item">
                    <div>
                      <strong>{p.name}</strong>
                      <p className="notif-sub">{p.patientId.slice(0, 8)}…</p>
                    </div>
                    {p.selected ? (
                      <span className="status-admitted">ASSIGNED</span>
                    ) : p.matches.length === 0 ? (
                      <span className="status-pending">Awaiting…</span>
                    ) : (
                      <div className="match-list">
                        {p.matches.map((m) => (
                          <button
                            key={m.hospital_id}
                            className="match-btn"
                            onClick={() =>
                              handleSelectHospital(p.patientId, m.hospital_id)
                            }
                          >
                            ✓ {m.name}
                          </button>
                        ))}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          </section>
        </section>
      </section>
    </main>
  );
}

export default Dashboard;
