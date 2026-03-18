import { useEffect, useState } from "react";

function Login() {
  const [ribbonCycle, setRibbonCycle] = useState(0);

  useEffect(() => {
    setRibbonCycle(1);
  }, []);

  const triggerRibbon = () => {
    setRibbonCycle((value) => value + 1);
  };

  return (
    <main
      className={`dashboard-shell ${ribbonCycle > 0 ? "animate-ribbon" : ""}`}
      data-ribbon-cycle={ribbonCycle % 2}
    >
      <header className="dashboard-topbar">
        <div className="brand-block">
          <div className="brand-logo" aria-hidden="true" />
          <p className="dashboard-label">Hospital Management System</p>
          <h1>CareMatrix General Hospital</h1>
        </div>

        <div className="account-menu">
          <div className="account-avatar" aria-hidden="true">
            DR
          </div>
          <button
            type="button"
            className="signout-button"
            onClick={triggerRibbon}
          >
            Sign Out
          </button>
        </div>
      </header>

      <section className="dashboard-grid">
        <section className="welcome-panel">
          <div className="hero-cross" aria-hidden="true" />
          <div className="panel-logo" aria-hidden="true" />
          <p className="dashboard-label">Emergency Access</p>
          <h2>Welcome</h2>
          <p className="welcome-copy">Rapid intake controls.</p>
          <div className="quick-links">
            <button
              type="button"
              className="mini-action"
              onClick={triggerRibbon}
            >
              Register Patient
            </button>
            <button
              type="button"
              className="mini-action"
              onClick={triggerRibbon}
            >
              Predictions
            </button>
            <button
              type="button"
              className="mini-action"
              onClick={triggerRibbon}
            >
              Emergency Alert
            </button>
          </div>
        </section>

        <section className="workspace-panel">
          <section className="form-panel">
            <div className="section-heading">
              <div className="panel-logo" aria-hidden="true" />
              <div>
                <p className="dashboard-label">Quick Register</p>
                <h3>New Patient</h3>
              </div>
            </div>

            <form className="quick-form">
              <label>
                Patient Name
                <input type="text" placeholder="Full name" />
              </label>

              <div className="form-grid">
                <label>
                  Age
                  <input type="text" placeholder="Years" />
                </label>
                <label>
                  Contact
                  <input type="text" placeholder="+91 98765 43210" />
                </label>
              </div>

              <div className="form-grid">
                <label>
                  Blood Group
                  <select defaultValue="O+">
                    <option>O+</option>
                    <option>O-</option>
                    <option>A+</option>
                    <option>A-</option>
                    <option>B+</option>
                    <option>B-</option>
                    <option>AB+</option>
                    <option>AB-</option>
                  </select>
                </label>
                <label>
                  Priority
                  <select defaultValue="High">
                    <option>Critical</option>
                    <option>High</option>
                    <option>Moderate</option>
                    <option>Low</option>
                  </select>
                </label>
              </div>

              <label>
                Condition
                <input type="text" placeholder="Primary complaint" />
              </label>

              <label>
                Department
                <select defaultValue="Emergency">
                  <option>Emergency</option>
                  <option>ICU</option>
                  <option>Surgery</option>
                  <option>Radiology</option>
                  <option>Cardiology</option>
                </select>
              </label>

              <button
                type="button"
                className="action-card"
                onClick={triggerRibbon}
              >
                Register Patient
              </button>
            </form>
          </section>
        </section>
      </section>
    </main>
  );
}

export default Login;
