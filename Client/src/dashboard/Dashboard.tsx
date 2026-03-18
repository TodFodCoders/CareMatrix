import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import "./dashboard.css";

type TransferRequest = {
  id: string;
  hospital: string;
  patient: string;
  condition: string;
  status: "PENDING" | "ADMITTED" | "TRANSFERRED" | "DECLINED";
};

type PatientStatus = {
  id: string;
  name: string;
  match: string;
};

function Dashboard() {
  const [ribbonCycle, setRibbonCycle] = useState(0);
  const navigate = useNavigate();

  const [requests, setRequests] = useState<TransferRequest[]>([]);
  const [patients, setPatients] = useState<PatientStatus[]>([]);

  const [formData, setFormData] = useState({
    name: "",
    age: "",
    contact: "",
    bloodGroup: "O+",
    priority: "High",
    condition: "",
    department: "Emergency",
  });

  /* 🔥 STREAM: 4 REQUESTS PER SECOND */
  useEffect(() => {
    setRibbonCycle(1);

    const interval = setInterval(() => {
      const newRequests: TransferRequest[] = Array.from({ length: 4 }).map(
        () => ({
          id: Math.random().toString(36).slice(2, 7),
          hospital: "City Hospital",
          patient: "Patient " + Math.floor(Math.random() * 100),
          condition: "Critical Trauma",
          status: "PENDING",
        }),
      );

      setRequests((r) => [...newRequests, ...r]);
    }, 1000);

    return () => clearInterval(interval);
  }, []);

  const triggerRibbon = () => {
    setRibbonCycle((v) => v + 1);
  };

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>,
  ) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  /* ✅ FIXED FORM */
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    if (!formData.name || !formData.age || !formData.contact) {
      alert("Please fill all required fields");
      return;
    }

    triggerRibbon();

    // const matchOptions = [
    //   "City Hospital (3 beds)",
    //   "Green Valley (1 bed)",
    //   "Northside (5 beds)",
    // ];

    const newPatient: PatientStatus = {
      id: "P-" + Math.floor(Math.random() * 9000 + 1000),
      name: formData.name,
      match: "Not yet",
    };

    setPatients((a) => [newPatient, ...a]);

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

  /* ✅ DECISION SYSTEM */
  const handleDecision = (
    id: string,
    decision: "ADMITTED" | "TRANSFERRED" | "DECLINED",
  ) => {
    setRequests((prev) =>
      prev.map((r) => (r.id === id ? { ...r, status: decision } : r)),
    );

    setTimeout(() => {
      setRequests((prev) => prev.filter((r) => r.id !== id));
    }, 1500);
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
        {/* LEFT PANEL */}
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
            <button className="mini-action">Emergency Alert</button>
            <button
              className="mini-action"
              onClick={() => navigate("/heatmap")}
            >
              Heat Map
            </button>
          </div>
        </section>

        {/* RIGHT PANEL */}
        <section className="workspace-panel split">
          {/* FORM */}
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

          {/* NOTIFICATIONS */}
          <section className="notification-panel">
            <div className="notif-block">
              <h3>Incoming Transfers</h3>

              <div className="notif-scroll">
                {requests.map((r) => (
                  <div key={r.id} className="notif-item">
                    <div>
                      <strong>{r.patient}</strong>
                      <p>{r.hospital}</p>
                      <p>{r.condition}</p>
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
                          onClick={() => handleDecision(r.id, "TRANSFERRED")}
                        >
                          ⇄
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
                {patients.map((p) => (
                  <div key={p.id} className="notif-item">
                    <span>{p.id}</span>
                    <span>{p.name}</span>
                    <span className="status-ok">{p.match}</span>
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
