# Patient Influx & Capacity Prediction System
## CLI Trainer — Offline, CPU/GPU, Persistent Memory

---

## Quick start (3 commands)

```bash
pip install -r requirements.txt
python train.py --csv your_data.csv
python train.py --forecast --days 30
```

---

## Installation

### 1. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 2. GPU acceleration (optional)

**NVIDIA CUDA GPU:**
```bash
pip install xgboost[cuda] lightgbm
# scikit-learn RandomForest uses all CPU cores automatically
# XGBoost and LightGBM will use GPU when available
```

**Apple Silicon (M1/M2/M3):**
```bash
# scikit-learn uses Apple Accelerate framework automatically
# No extra install needed — just run as normal
```

**AMD GPU (Linux):**
```bash
pip install lightgbm  # supports OpenCL
```

**CPU only (default):**
```bash
# All models use all available CPU cores automatically (-1 = all cores)
python train.py --csv data.csv --jobs 4   # limit to 4 cores
```

---

## Commands

### Train on a new CSV
```bash
python train.py --csv data/patients.csv
```

### Train and merge with all previous data (incremental memory)
```bash
python train.py --csv data/june.csv --retrain
```
Every time you use `--retrain`, the system merges the new CSV with all previous
training sessions. The model gets better with each new batch of data.

### Predict a specific date
```bash
python train.py --predict --date 2025-08-15
python train.py --predict --date 2025-08-15 --facility "General Medicine"
python train.py --predict --date 2025-08-15 --season peak
```

### Generate a multi-day forecast
```bash
python train.py --forecast --days 30
python train.py --forecast --days 14 --facility "Dental"
python train.py --forecast --days 30 --start 2025-09-01
```
Forecast is also saved as a CSV in `exports/`.

### Export model for the HTML dashboard
```bash
python train.py --export-dashboard
```
This creates a `.json` file in `exports/`. Open the HTML dashboard,
click **"Load saved model"**, and select this file to use your
Python-trained model in the browser — no internet needed.

### Check training memory status
```bash
python train.py --status
```

### Clear all training memory (start fresh)
```bash
python train.py --clear-memory
```

---

## CSV format

Minimum required columns:
| Column | Description |
|--------|-------------|
| `date` | Any date format: `2024-01-15`, `15/01/2024`, `Jan 15 2024` |
| `patients` | Integer patient count (also: `count`, `visits`, `arrivals`) |

Optional columns (auto-detected by name):
| Column | Description |
|--------|-------------|
| `specialty` / `facility` / `dept` | Department or specialty name |
| `hour` | Hour of day (0–23) — enables intraday analysis |
| `temperature` | Ambient temperature °C |
| `aqi` | Air quality index |
| `rainfall` | Daily precipitation mm |
| `holiday` | 1 = holiday, 0 = normal |
| `revisit` | Revisit patient count |
| `doctors` | Number of doctors on duty |
| `counters` | Registration counters open |

---

## How memory works

Each training session saves:
- A processed copy of your CSV to `data/session_NNNN.csv`
- An entry in `models/memory.json` with session metadata
- The trained model bundle to `models/ensemble.pkl`

When you run `--retrain`, all previous session CSVs are loaded and merged
with the new data before training. The model therefore learns from the
entire history, not just the latest file.

**Memory files:**
```
models/
  ensemble.pkl      ← trained sklearn models (joblib)
  scaler.pkl        ← feature scaler
  stats.json        ← learned patterns, multipliers, results
  memory.json       ← session index and cross-session metadata
data/
  session_0001.csv  ← first training session data
  session_0002.csv  ← second session, etc.
exports/
  forecast_*.csv    ← exported forecasts
  dashboard_model_*.json  ← files for HTML dashboard
logs/
  train_*.log       ← training logs
```

---

## Model selection logic

The system trains **5 algorithms** on every run:

| Model | Best for (per paper: Gupta & Sharma 2025) |
|-------|-------------------------------------------|
| **GBM** (Gradient Boosting) | General Medicine, ENT |
| **RF** (Random Forest) | Dental, Orthopaedic |
| **KNN** (K-Nearest Neighbours) | Comparison baseline |
| **Ridge** (Regularised Linear) | Comparison baseline |
| **DT** (Decision Tree) | Comparison baseline |

For each specialty in your data:
- **≥ 20 rows** → cross-validates all 5 models, picks the data-winner
- **5–19 rows** → uses paper prior or global best
- **< 5 rows** → generalised fallback from global model
- **Unknown specialty** → generalised data-selected or global best

---

## Climate profiles

Choose the profile that matches your facility's region:

```bash
python train.py --csv data.csv --climate semi_arid    # default (India, N. Africa)
python train.py --csv data.csv --climate tropical      # SE Asia, coastal India
python train.py --csv data.csv --climate temperate     # Europe, N. America
python train.py --csv data.csv --climate cold          # Alpine, N. Europe
python train.py --csv data.csv --climate equatorial    # Central Africa, Singapore
```

Climate only sets the initial seasonal prior. Your actual data overrides it
once enough months are covered.

---

## Feature importance (paper-backed)

The model uses 17 features, weighted by importance from the research:

1. **Lagged arrivals** (yesterday's count) — top predictor for all specialties
2. **Day of month** — billing/admin cycles drive mid-month dips
3. **Hour of day** — intraday peak detection
4. **Morning shift flag** — key for ENT & Orthopaedic
5. **Revisit rate** — key for Dental & General Medicine
6. Day of week, Month, Seasonal prior, Temperature, AQI, Rainfall,
   Holiday, Doctor load, Weekend flag, Peak month, Early month, Lagged ratio

---

## Performance expectations

| Dataset size | Expected accuracy |
|-------------|-------------------|
| 30–100 rows | 75–82% (pattern-heavy) |
| 100–500 rows | 82–88% |
| 500–2000 rows | 88–93% |
| 2000+ rows | 92–96% |

Adding more training sessions via `--retrain` continuously improves accuracy.
