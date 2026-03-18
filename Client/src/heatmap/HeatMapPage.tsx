import { MapContainer, TileLayer, CircleMarker } from "react-leaflet";
import "./heatmap.css";
import { useRef, useState } from "react";
import { useNavigate } from "react-router-dom";

type Hospital = {
  id: string;
  name: string;
  lat: number;
  lng: number;
  demand: number;
  cases: number;
  patients: number;
};

const hospitals: Hospital[] = [
  {
    id: "h1",
    name: "Central City Hospital",
    lat: 28.7041,
    lng: 77.1025,
    demand: 80,
    cases: 120,
    patients: 45,
  },
  {
    id: "h2",
    name: "Green Valley Clinic",
    lat: 28.5355,
    lng: 77.391,
    demand: 45,
    cases: 60,
    patients: 18,
  },
  {
    id: "h3",
    name: "Lakeside Medical",
    lat: 28.4595,
    lng: 77.0266,
    demand: 20,
    cases: 15,
    patients: 4,
  },
  {
    id: "h4",
    name: "Northside General",
    lat: 28.4089,
    lng: 77.3178,
    demand: 65,
    cases: 90,
    patients: 30,
  },
];

const palette = ["#8f1d1d", "#c4d8df", "#111111", "#dde4e8"];

function getColor(id: string) {
  let hash = 0;
  for (let i = 0; i < id.length; i++) {
    hash = id.charCodeAt(i) + ((hash << 5) - hash);
  }
  return palette[Math.abs(hash) % palette.length];
}

export default function HeatMapPage() {
  const mapRef = useRef(null);
  const navigate = useNavigate();
  const [selected, setSelected] = useState<Hospital | null>(null);

  return (
    <div className="heatmap-shell">
      <header className="heatmap-header">
        <h2>Nearby Hospitals — Demand Heatmap</h2>
        <button className="back-button" onClick={() => navigate("/dashboard")}>
          Back
        </button>
      </header>

      <div className="heatmap-body">
        {/* MAP */}
        <div className="map-container">
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

            {hospitals.map((h) => {
              const color = getColor(h.id);

              return (
                <CircleMarker
                  key={h.id}
                  center={[h.lat, h.lng]}
                  radius={8 + Math.round(h.demand / 15)}
                  pathOptions={{
                    color: selected?.id === h.id ? "#8f1d1d" : "#111111",
                    fillColor: color,
                    fillOpacity: 1,
                    weight: selected?.id === h.id ? 3 : 2,
                  }}
                  eventHandlers={{
                    click: () => setSelected(h),
                  }}
                />
              );
            })}
          </MapContainer>
        </div>

        {/* INFO PANEL */}
        <div className="info-panel">
          {selected ? (
            <div className="info-card">
              <h3>{selected.name}</h3>

              <p>
                <strong>Demand:</strong> {selected.demand}%
              </p>
              <p>
                <strong>Total Capacity:</strong> {selected.cases}
              </p>
              <p>
                <strong>Occupied:</strong> {selected.patients}
              </p>

              <p className="vacant">
                <strong>Vacant Beds:</strong>{" "}
                {selected.cases - selected.patients}
              </p>
            </div>
          ) : (
            <div className="info-placeholder">
              <p>Select a hospital to view details</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
