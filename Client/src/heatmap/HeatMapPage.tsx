import { MapContainer, TileLayer, CircleMarker } from "react-leaflet";
import "./heatmap.css";
import { useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { getHeatmap } from "../api";

type Hospital = {
  id: string;
  name: string;
  lat: number;
  lng: number;
  demand: number;
  total: number;
  available: number;
};

function demandColor(demand: number) {
  if (demand >= 75) return "#8f1d1d";
  if (demand >= 45) return "#c4d8df";
  return "#2e7d32";
}

export default function HeatMapPage() {
  const mapRef = useRef(null);
  const navigate = useNavigate();
  const [selected, setSelected] = useState<Hospital | null>(null);
  const [hospitals, setHospitals] = useState<Hospital[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const load = async () => {
      const data = await getHeatmap().catch(() => []);
      setHospitals(
        data.map((h) => ({
          id: h.id,
          name: h.name,
          lat: h.lat,
          lng: h.lng,
          demand: h.demand,
          total: h.total,
          available: h.available,
        })),
      );
      setLoading(false);
    };

    load();
    const iv = setInterval(load, 10000);
    return () => clearInterval(iv);
  }, []);

  return (
    <div className="heatmap-shell">
      <header className="heatmap-header">
        <h2>Nearby Hospitals — Demand Heatmap</h2>
        <button className="back-button" onClick={() => navigate("/dashboard")}>
          Back
        </button>
      </header>

      <div className="heatmap-body">
        <div className="map-container">
          {loading ? (
            <div className="heatmap-loading">Loading hospital data…</div>
          ) : (
            <MapContainer
              ref={mapRef}
              center={[28.6, 77.1]}
              zoom={10}
              className="heatmap-map"
            >
              <TileLayer
                attribution="&copy; OpenStreetMap contributors"
                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
              />
              {hospitals.map((h) => (
                <CircleMarker
                  key={h.id}
                  center={[h.lat, h.lng]}
                  radius={8 + Math.round(h.demand / 15)}
                  pathOptions={{
                    color: selected?.id === h.id ? "#111111" : "#111111",
                    fillColor: demandColor(h.demand),
                    fillOpacity: 1,
                    weight: selected?.id === h.id ? 4 : 2,
                  }}
                  eventHandlers={{ click: () => setSelected(h) }}
                />
              ))}
            </MapContainer>
          )}
        </div>

        <div className="info-panel">
          {hospitals.length === 0 && !loading ? (
            <div className="info-placeholder">
              <p>No hospitals registered yet</p>
            </div>
          ) : selected ? (
            <div className="info-card">
              <h3>{selected.name}</h3>
              <p>
                <strong>Demand:</strong> {selected.demand}%
              </p>
              <p>
                <strong>Total Capacity:</strong> {selected.total}
              </p>
              <p>
                <strong>Available:</strong> {selected.available}
              </p>
              <p className="vacant">
                <strong>Occupied:</strong> {selected.total - selected.available}
              </p>
              <div
                className="demand-bar"
                style={
                  { "--demand": `${selected.demand}%` } as React.CSSProperties
                }
              />
            </div>
          ) : (
            <div className="info-placeholder">
              <p>Select a hospital to view details</p>
              <div className="legend">
                <span
                  className="legend-dot"
                  style={{ background: "#2e7d32" }}
                />{" "}
                Low
                <span
                  className="legend-dot"
                  style={{ background: "#c4d8df" }}
                />{" "}
                Medium
                <span
                  className="legend-dot"
                  style={{ background: "#8f1d1d" }}
                />{" "}
                High
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
