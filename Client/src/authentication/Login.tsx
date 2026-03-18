import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

function Login() {
  const [ribbonCycle, setRibbonCycle] = useState(0);
  const navigate = useNavigate();

  useEffect(() => {
    setRibbonCycle(1);
  }, []);

  const triggerRibbon = () => {
    setRibbonCycle((v) => v + 1);
  };

  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault();
    triggerRibbon();

    // fake login → navigate to dashboard/heatmap
    setTimeout(() => {
      navigate("/dashboard");
    }, 200);
  };

  return (
    <main
      className={`dashboard-shell ${ribbonCycle > 0 ? "animate-ribbon" : ""}`}
      data-ribbon-cycle={ribbonCycle % 2}
    >
      {/* TOP BAR */}
      <header className="dashboard-topbar">
        <div className="brand-block">
          <div className="brand-logo" />
          <p className="dashboard-label">Hospital Management System</p>
          <h1>CareMatrix</h1>
        </div>
      </header>

      {/* MAIN LOGIN GRID */}
      <section className="dashboard-grid">
        {/* LEFT PANEL (INFO / HERO) */}
        <section className="welcome-panel">
          <div className="hero-cross" />
          <div className="panel-logo" />

          <p className="dashboard-label">Secure Access</p>
          <h2>Clinical Control Interface</h2>

          <p className="welcome-copy">
            Authorized personnel only. Monitor patient flow, manage admissions,
            and respond to critical demand in real-time.
          </p>

          <div className="quick-links">
            <div className="mini-action">24/7 Monitoring</div>
            <div className="mini-action">Emergency Ready</div>
            <div className="mini-action">Live Demand Map</div>
          </div>
        </section>

        {/* RIGHT PANEL (LOGIN FORM) */}
        <section className="workspace-panel">
          <section className="form-panel">
            <div className="section-heading">
              <div className="panel-logo" />
              <div>
                <p className="dashboard-label">Authentication</p>
                <h3>Sign In</h3>
              </div>
            </div>

            <form className="quick-form" onSubmit={handleLogin}>
              <label>
                Staff ID
                <input type="text" placeholder="Enter ID" required />
              </label>

              <label>
                Password
                <input type="password" placeholder="••••••••" required />
              </label>

              <button type="submit" className="action-card">
                Enter System
              </button>
            </form>
          </section>
        </section>
      </section>
    </main>
  );
}

export default Login;
