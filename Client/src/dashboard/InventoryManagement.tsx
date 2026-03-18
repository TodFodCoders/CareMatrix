import { useNavigate } from "react-router-dom";
import { useState } from "react";

type Item = {
  id: string;
  name: string;
  quantity: number;
  price: number;
  icon: string;
};

const inventory: Item[] = [
  { id: "i1", name: "Oxygen Cylinders", quantity: 3, price: 5000, icon: "🫧" },
  { id: "i2", name: "Ventilators", quantity: 12, price: 15000, icon: "🫁" },
  { id: "i4", name: "Blood Units", quantity: 25, price: 1200, icon: "🩸" },
  { id: "i5", name: "Syringes", quantity: 150, price: 10, icon: "💉" },
  { id: "i6", name: "Saline Bottles", quantity: 8, price: 200, icon: "🧴" },
  { id: "i7", name: "Defibrillators", quantity: 2, price: 7000, icon: "⚡" },
  { id: "i8", name: "Wheelchairs", quantity: 18, price: 8000, icon: "♿" },
  { id: "i10", name: "Gloves", quantity: 300, price: 5, icon: "🧤" },
];

export default function InventoryManagement() {
  const navigate = useNavigate();

  const [predictions, setPredictions] = useState<Record<string, number>>({});
  const [status, setStatus] = useState<Record<string, string>>({});
  const [bill, setBill] = useState<any[]>([]);
  const [total, setTotal] = useState(0);

  const formatINR = (num: number) =>
    new Intl.NumberFormat("en-IN", {
      style: "currency",
      currency: "INR",
      maximumFractionDigits: 0,
    }).format(num);

  const generatePrediction = () => {
    let predMap: Record<string, number> = {};
    let statusMap: Record<string, string> = {};
    let newBill: any[] = [];
    let sum = 0;

    inventory.forEach((item) => {
      const predicted = Math.floor(Math.random() * 150 + 20);

      predMap[item.id] = predicted;

      if (item.quantity >= predicted) {
        statusMap[item.id] = "SATISFIED";
      } else {
        statusMap[item.id] = "REQUIRED";

        const deficit = predicted - item.quantity;
        const cost = deficit * item.price;

        sum += cost;

        newBill.push({
          ...item,
          predicted,
          deficit,
          cost,
        });
      }
    });

    setPredictions(predMap);
    setStatus(statusMap);
    setBill(newBill);
    setTotal(sum);
  };

  return (
    <main className="dashboard-shell inventory-shell">
      <header className="dashboard-topbar">
        <div className="brand-block">
          <div className="brand-logo" />
          <p className="dashboard-label">Hospital Management System</p>
          <h1>Inventory Management</h1>
        </div>

        <div className="account-menu">
          <div className="account-avatar">H</div>
          <button
            className="signout-button"
            onClick={() => navigate("/dashboard")}
          >
            Back
          </button>
        </div>
      </header>

      <section className="inventory-layout">
        {/* TABLE */}
        <div className="inventory-table">
          <div className="table-header">
            <span>Item</span>
            <span>Available</span>
            <span>Predicted</span>
            <span>Status</span>
          </div>

          {inventory.map((item) => {
            const state = status[item.id];
            const isRequired = state === "REQUIRED";
            const isOk = state === "SATISFIED";

            return (
              <div
                key={item.id}
                className={`table-row ${
                  isRequired ? "row-required" : isOk ? "row-ok" : ""
                }`}
              >
                <span className="item-name">
                  <span className="icon">{item.icon}</span>
                  {item.name}
                </span>

                <span className="number">{item.quantity}</span>

                <span className="number">{predictions[item.id] ?? "-"}</span>

                <span
                  className={`status ${
                    isRequired ? "status-bad" : isOk ? "status-ok" : ""
                  }`}
                >
                  {state ?? "-"}
                </span>
              </div>
            );
          })}
        </div>

        {/* SIDE PANEL */}
        <div className="inventory-side">
          <button className="action-card" onClick={generatePrediction}>
            Predict Resources
          </button>

          <div className="bill-panel">
            {bill.length > 0 ? (
              <>
                <h3>Restock Bill</h3>

                {bill.map((b) => (
                  <div key={b.id} className="bill-row">
                    <span>{b.name}</span>

                    <span className="number bill-calc">
                      {b.deficit} × {formatINR(b.price)}
                    </span>

                    <span className="number bill-amount">
                      {formatINR(b.cost)}
                    </span>
                  </div>
                ))}

                <div className="bill-total">
                  <span>Total</span>
                  <span className="number">{formatINR(total)}</span>
                </div>

                <button className="order-button">Order Now</button>
              </>
            ) : (
              <p className="placeholder">No prediction yet</p>
            )}
          </div>
        </div>
      </section>
    </main>
  );
}
