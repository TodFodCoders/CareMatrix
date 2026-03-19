import { useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { getPrediction } from "../api";
import type { PredictionResponse } from "../api";
import "./prediction.css";

const STATUS_COLOR: Record<string, string> = {
  critical: "#8f1d1d",
  high: "#8f1d1d",
  warning: "#c47a1d",
  low: "#2e7d32",
  ok: "#2e7d32",
};

function today() {
  return new Date().toISOString().slice(0, 10);
}

function buildChartPoints(data: PredictionResponse, w: number, h: number) {
  const pad = { t: 24, r: 16, b: 40, l: 48 };
  const cw = w - pad.l - pad.r;
  const ch = h - pad.t - pad.b;

  const { low, high, predicted } = data.prediction;
  const cap = data.bed_occupancy.total_beds;
  const edMax = data.emergency_load.ed_beds;

  // simulate hourly curve across 24h using the prediction values
  const hrs = Array.from({ length: 25 }, (_, i) => {
    const t = i / 24;
    const surge = Math.sin(t * Math.PI) * 0.6 + Math.sin(t * Math.PI * 2) * 0.2;
    const val = Math.round(low + (predicted - low) * (0.4 + surge * 0.6));
    const lo = Math.round(low * (0.85 + surge * 0.1));
    const hi = Math.round(high * (0.9 + surge * 0.15));
    return {
      h: i,
      val: Math.min(val, cap),
      lo: Math.min(lo, cap),
      hi: Math.min(hi, cap),
    };
  });

  const maxY = Math.max(cap, high + 5);
  const minY = 0;
  const sy = (v: number) => pad.t + ch - ((v - minY) / (maxY - minY)) * ch;
  const sx = (i: number) => pad.l + (i / 24) * cw;

  const mainPath = hrs
    .map(
      (p, i) =>
        `${i === 0 ? "M" : "L"}${sx(i).toFixed(1)},${sy(p.val).toFixed(1)}`,
    )
    .join(" ");
  const bandTop = hrs
    .map(
      (p, i) =>
        `${i === 0 ? "M" : "L"}${sx(i).toFixed(1)},${sy(p.hi).toFixed(1)}`,
    )
    .join(" ");
  const bandBot = [...hrs]
    .reverse()
    .map(
      (p, i) =>
        `${i === 0 ? "" : "L"}${sx(24 - i).toFixed(1)},${sy(p.lo).toFixed(1)}`,
    )
    .join(" ");
  const bandPath = `${bandTop} ${bandBot} Z`;

  const capY = sy(cap);
  const edY = sy(edMax);
  const tgtY = sy(Math.round((cap * data.bed_occupancy.nhm_target_pct) / 100));

  const xTicks = [0, 4, 8, 12, 16, 20, 24];
  const yTicks = [
    0,
    Math.round(maxY * 0.25),
    Math.round(maxY * 0.5),
    Math.round(maxY * 0.75),
    maxY,
  ];

  return {
    hrs,
    sx,
    sy,
    mainPath,
    bandPath,
    capY,
    edY,
    tgtY,
    xTicks,
    yTicks,
    pad,
    maxY,
    minY,
    cw,
    ch,
  };
}

export default function PredictionPage() {
  const navigate = useNavigate();
  const [date, setDate] = useState(today());
  const [data, setData] = useState<PredictionResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const svgRef = useRef<SVGSVGElement>(null);
  const [svgSize, setSvgSize] = useState({ w: 800, h: 400 });

  useEffect(() => {
    const obs = new ResizeObserver((entries) => {
      const e = entries[0];
      if (e) setSvgSize({ w: e.contentRect.width, h: e.contentRect.height });
    });
    if (svgRef.current?.parentElement)
      obs.observe(svgRef.current.parentElement);
    return () => obs.disconnect();
  }, []);

  const fetchData = async (d: string) => {
    setLoading(true);
    setError(null);
    const res = await getPrediction(d).catch(() => null);
    if (!res) setError("Backend unreachable");
    else setData(res);
    setLoading(false);
  };

  useEffect(() => {
    fetchData(date);
  }, [date]);

  const c = data ? buildChartPoints(data, svgSize.w, svgSize.h) : null;

  const statusColor = (s: string) => STATUS_COLOR[s] ?? "#888";

  return (
    <div className="pred-shell">
      <header className="pred-header">
        <div className="pred-brand">
          <div className="pred-logo" />
          <div>
            <p className="pred-label">Hospital Management System</p>
            <h1>Surge Prediction</h1>
          </div>
        </div>
        <button className="pred-back" onClick={() => navigate("/dashboard")}>
          Back
        </button>
      </header>

      <div className="pred-body">
        {/* ── LEFT: CHART ── */}
        <div className="pred-chart-panel">
          <div className="pred-chart-title">
            <span>Patient Surge — 24h Forecast</span>
            {data && (
              <span className="pred-model-badge">
                {data.prediction.model_used} · {data.prediction.ml_blend_pct}%
                ML · {data.prediction.confidence_pct}% conf
              </span>
            )}
          </div>

          <div className="pred-chart-wrap">
            {loading && <div className="pred-loading">Loading forecast…</div>}
            {error && <div className="pred-error">{error}</div>}

            {data && c && (
              <svg ref={svgRef} width="100%" height="100%" className="pred-svg">
                <defs>
                  <linearGradient id="band-grad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="#8f1d1d" stopOpacity="0.18" />
                    <stop
                      offset="100%"
                      stopColor="#8f1d1d"
                      stopOpacity="0.03"
                    />
                  </linearGradient>
                </defs>

                {/* grid lines */}
                {c.yTicks.map((v) => (
                  <g key={v}>
                    <line
                      x1={c.pad.l}
                      y1={c.sy(v)}
                      x2={c.pad.l + c.cw}
                      y2={c.sy(v)}
                      stroke="#11111118"
                      strokeWidth="1"
                    />
                    <text
                      x={c.pad.l - 6}
                      y={c.sy(v) + 4}
                      textAnchor="end"
                      className="pred-tick"
                    >
                      {v}
                    </text>
                  </g>
                ))}

                {/* x ticks */}
                {c.xTicks.map((h) => (
                  <text
                    key={h}
                    x={c.sx(h)}
                    y={svgSize.h - c.pad.b + 16}
                    textAnchor="middle"
                    className="pred-tick"
                  >
                    {h === 0
                      ? "12am"
                      : h < 12
                        ? `${h}am`
                        : h === 12
                          ? "12pm"
                          : `${h - 12}pm`}
                  </text>
                ))}

                {/* confidence band */}
                <path d={c.bandPath} fill="url(#band-grad)" />

                {/* reference lines */}
                <line
                  x1={c.pad.l}
                  y1={c.capY}
                  x2={c.pad.l + c.cw}
                  y2={c.capY}
                  stroke="#8f1d1d"
                  strokeWidth="1.5"
                  strokeDasharray="6 3"
                  opacity="0.7"
                />
                <text
                  x={c.pad.l + c.cw - 4}
                  y={c.capY - 5}
                  textAnchor="end"
                  className="pred-refline-label"
                  fill="#8f1d1d"
                >
                  CAPACITY
                </text>

                <line
                  x1={c.pad.l}
                  y1={c.tgtY}
                  x2={c.pad.l + c.cw}
                  y2={c.tgtY}
                  stroke="#2e7d32"
                  strokeWidth="1"
                  strokeDasharray="4 4"
                  opacity="0.6"
                />
                <text
                  x={c.pad.l + c.cw - 4}
                  y={c.tgtY - 5}
                  textAnchor="end"
                  className="pred-refline-label"
                  fill="#2e7d32"
                >
                  NHM TARGET
                </text>

                <line
                  x1={c.pad.l}
                  y1={c.edY}
                  x2={c.pad.l + c.cw}
                  y2={c.edY}
                  stroke="#c47a1d"
                  strokeWidth="1"
                  strokeDasharray="4 4"
                  opacity="0.6"
                />
                <text
                  x={c.pad.l + c.cw - 4}
                  y={c.edY - 5}
                  textAnchor="end"
                  className="pred-refline-label"
                  fill="#c47a1d"
                >
                  ED BEDS
                </text>

                {/* main surge line */}
                <path
                  d={c.mainPath}
                  fill="none"
                  stroke="#111111"
                  strokeWidth="2.5"
                  strokeLinejoin="round"
                />

                {/* dots at peak + current */}
                {c.hrs.map((p, i) => {
                  if (![0, 6, 12, 18, 24].includes(i)) return null;
                  return (
                    <circle
                      key={i}
                      cx={c.sx(i)}
                      cy={c.sy(p.val)}
                      r="4"
                      fill="#111"
                      stroke="#f2f0ea"
                      strokeWidth="2"
                    />
                  );
                })}
              </svg>
            )}

            {/* legend */}
            {data && (
              <div className="pred-legend">
                <span>
                  <span
                    className="pred-legend-line"
                    style={{ background: "#111" }}
                  />{" "}
                  Predicted
                </span>
                <span>
                  <span className="pred-legend-band" /> Confidence band
                </span>
                <span>
                  <span
                    className="pred-legend-dash"
                    style={{ background: "#8f1d1d" }}
                  />{" "}
                  Capacity
                </span>
                <span>
                  <span
                    className="pred-legend-dash"
                    style={{ background: "#2e7d32" }}
                  />{" "}
                  NHM target
                </span>
              </div>
            )}
          </div>
        </div>

        {/* ── RIGHT COLUMN ── */}
        <div className="pred-right">
          {/* DATE PICKER — top */}
          <div className="pred-date-block">
            <p className="pred-label">Forecast Date</p>
            <input
              type="date"
              className="pred-date-input"
              value={date}
              onChange={(e) => setDate(e.target.value)}
            />
            {data && (
              <p className="pred-season">
                Season: <strong>{data.prediction.season_used}</strong> ·
                Facility: <strong>{data.prediction.facility}</strong>
              </p>
            )}
          </div>

          {/* ALERTS */}
          {data && data.alerts.length > 0 && (
            <div className="pred-alerts">
              {data.alerts.map((a, i) => (
                <div
                  key={i}
                  className="pred-alert"
                  style={{
                    borderColor: statusColor(a.level),
                    background: statusColor(a.level) + "18",
                  }}
                >
                  <span className="pred-alert-code">
                    {a.code.replace(/_/g, " ").toUpperCase()}
                  </span>
                  <span className="pred-alert-msg">{a.message}</span>
                </div>
              ))}
            </div>
          )}

          {/* SURGE SUMMARY — bottom right */}
          {data && (
            <div className="pred-surge">
              <div className="pred-surge-header">
                <p className="pred-label">Surge Forecast</p>
                <span className="pred-surge-date">{data.prediction.date}</span>
              </div>

              <div className="pred-surge-big">
                <span className="pred-surge-num">
                  {data.prediction.predicted}
                </span>
                <div className="pred-surge-range">
                  <span>↑ {data.prediction.high}</span>
                  <span>↓ {data.prediction.low}</span>
                </div>
              </div>

              <div className="pred-stat-grid">
                {/* Bed Occupancy */}
                <div className="pred-stat-block">
                  <p className="pred-stat-label">Beds</p>
                  <p className="pred-stat-val">
                    {data.bed_occupancy.current_occupied}
                    <span>/{data.bed_occupancy.total_beds}</span>
                  </p>
                  <div className="pred-bar">
                    <div
                      className="pred-bar-fill"
                      style={{
                        width: `${data.bed_occupancy.current_bor_pct}%`,
                        background: statusColor(data.bed_occupancy.status),
                      }}
                    />
                  </div>
                  <p className="pred-stat-sub">
                    {data.bed_occupancy.current_bor_pct}% BOR →{" "}
                    {data.bed_occupancy.projected_bor_pct}% projected
                  </p>
                </div>

                {/* ED */}
                <div className="pred-stat-block">
                  <p className="pred-stat-label">Emergency Dept</p>
                  <p className="pred-stat-val">
                    {data.emergency_load.ed_occupied_now}
                    <span>/{data.emergency_load.ed_beds}</span>
                  </p>
                  <div className="pred-bar">
                    <div
                      className="pred-bar-fill"
                      style={{
                        width: `${data.emergency_load.utilisation_pct}%`,
                        background: statusColor(data.emergency_load.status),
                      }}
                    />
                  </div>
                  <p className="pred-stat-sub">
                    {data.emergency_load.utilisation_pct}% utilisation
                  </p>
                </div>

                {/* OPD */}
                <div className="pred-stat-block">
                  <p className="pred-stat-label">OPD Load</p>
                  <p className="pred-stat-val">
                    {data.opd_load.patients_per_hour}
                    <span>/hr</span>
                  </p>
                  <p className="pred-stat-sub">
                    {data.opd_load.doctors_available} doctors ·{" "}
                    {data.opd_load.counters_available} counters
                  </p>
                  <p className="pred-stat-sub">
                    {data.opd_load.patients_per_doctor} pts/doctor
                  </p>
                </div>

                {/* Triage */}
                <div className="pred-stat-block">
                  <p className="pred-stat-label">Triage Breakdown</p>
                  <div className="pred-triage">
                    <span className="triage-imm">
                      {data.emergency_load.triage_immediate} IMM
                    </span>
                    <span className="triage-urg">
                      {data.emergency_load.triage_urgent} URG
                    </span>
                    <span className="triage-non">
                      {data.emergency_load.triage_non_urgent} NON
                    </span>
                    <span className="triage-obs">
                      {data.emergency_load.triage_observation} OBS
                    </span>
                  </div>
                </div>

                {/* Waiting Times */}
                <div className="pred-stat-block pred-stat-wide">
                  <p className="pred-stat-label">Waiting Times (min)</p>
                  <div className="pred-wait-row">
                    {[
                      ["Transport", data.waiting_times.transport],
                      ["Registration", data.waiting_times.registration],
                      ["Triage", data.waiting_times.triage],
                      ["Consultation", data.waiting_times.consultation],
                      ["Pharmacy", data.waiting_times.pharmacy],
                      ["Billing", data.waiting_times.billing],
                    ].map(([label, val]) => (
                      <div key={label as string} className="pred-wait-item">
                        <span className="pred-wait-val">{val}</span>
                        <span className="pred-wait-label">{label}</span>
                      </div>
                    ))}
                  </div>
                  <p className="pred-stat-sub">
                    Total wait: <strong>{data.waiting_times.total} min</strong>
                  </p>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
