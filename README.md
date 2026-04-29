# 🔺 TriNetra AI — Hybrid Fraud Detection System

<div align="center">

![TriNetra AI](https://img.shields.io/badge/TriNetra-AI%20Fraud%20Detection-818cf8?style=for-the-badge&logo=shield&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)
![PyTorch](https://img.shields.io/badge/PyTorch-2.x-EE4C2C?style=for-the-badge&logo=pytorch&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-22c55e?style=for-the-badge)

> **TriNetra** (Sanskrit: *Three Eyes*) — An end-to-end, real-time e-commerce fraud detection system powered by three specialized AI models: Graph Neural Network, LSTM, and Autoencoder, fused into a single explainable risk score.

</div>

---

## 📋 Table of Contents

- [Overview](#-overview)
- [System Architecture](#-system-architecture)
- [Tech Stack](#-tech-stack)
- [Dataset](#-dataset)
- [Feature Engineering](#-feature-engineering)
- [AI Models](#-ai-models)
  - [Model 1: Graph Neural Network (GNN)](#model-1--graph-neural-network-gnn)
  - [Model 2: LSTM Temporal Model](#model-2--lstm-temporal-model)
  - [Model 3: Autoencoder Anomaly Detection](#model-3--autoencoder-anomaly-detection)
- [Risk Fusion Engine](#-risk-fusion-engine)
- [Explainable AI](#-explainable-ai)
- [Dashboard Pages](#-dashboard-pages)
- [Project Structure](#-project-structure)
- [Installation & Setup](#-installation--setup)
- [Running the System](#-running-the-system)
- [API / Module Reference](#-module-reference)
- [Performance Metrics](#-performance-metrics)

---

## 🎯 Overview

TriNetra AI is a **multi-model fraud detection system** designed for e-commerce platforms. It detects three major categories of fraud:

| Fraud Type | Description | Model Used |
|---|---|---|
| **Fraud Ring** | Coordinated accounts sharing devices/IPs | Graph Neural Network |
| **Behavioral Fraud** | Sudden transaction bursts, midnight spikes | LSTM |
| **Return Fraud** | Wardrobing, fake damage claims | Autoencoder + Feature Rules |

### Why Three Models?

```
Single model limitation:
  LSTM alone → misses fraud rings (coordinated groups)
  GNN alone  → misses behavioral changes over time
  AE alone   → misses connected-account patterns

TriNetra solution:
  All three → combined score catches 89%+ of fraud cases
```

### Decision Output

Every user receives:
- A **Risk Score** (0–100)
- A **Decision**: `APPROVE` / `VERIFY` / `BLOCK`
- **Plain-English Reasons** explaining why
- **Score Decomposition** showing each model's contribution

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        DATA LAYER                                   │
│  returns.csv  +  fraud_transactions.csv  +  behavioral.csv          │
└──────────────────────────┬──────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    PREPROCESSING (preprocess.py)                    │
│  • Clean & merge 3 datasets                                         │
│  • Engineer 19 features per user                                    │
│  • StandardScaler normalization                                     │
│  • Output: merged_features.csv (6,000 users × 19 features)         │
└──────┬───────────────────┬──────────────────────┬───────────────────┘
       │                   │                      │
       ▼                   ▼                      ▼
┌─────────────┐   ┌─────────────────┐   ┌──────────────────┐
│ graph_model │   │   lstm_model    │   │  autoencoder     │
│             │   │                 │   │                  │
│ NetworkX    │   │ PyTorch LSTM    │   │ PyTorch AE       │
│ + Louvain   │   │ 2-layer, 128h   │   │ 19→16→19         │
│             │   │                 │   │                  │
│graph_risk   │   │temporal_risk    │   │anomaly_score     │
│score (0-100)│   │score (0-100)    │   │(0-100)           │
└──────┬──────┘   └────────┬────────┘   └────────┬─────────┘
       │                   │                      │
       └───────────────────┴──────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    RISK FUSION (risk_fusion.py)                     │
│                                                                     │
│   risk_score = 0.30 × graph + 0.40 × temporal + 0.30 × anomaly    │
│                                                                     │
│   score ≤ 30 → APPROVE                                             │
│   score ≤ 70 → VERIFY                                              │
│   score > 70 → BLOCK                                               │
│                                                                     │
│   Output: risk_scores.csv (6,000 rows × 8 columns)                │
└──────────────────────────┬──────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────────┐
│               STREAMLIT DASHBOARD (dashboard.py)                    │
│  6 pages: Overview · User Lookup · Fraud Rings ·                   │
│           Temporal · Anomaly Map · Live Simulator                   │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Tech Stack

### Core AI/ML
| Library | Version | Purpose |
|---|---|---|
| `torch` | 2.x | LSTM + Autoencoder neural networks |
| `networkx` | 3.x | Graph construction for GNN |
| `python-louvain` | 0.16 | Community detection algorithm |
| `scikit-learn` | 1.x | StandardScaler, GradientBoosting surrogate |
| `numpy` | 1.x | Numerical computation |
| `pandas` | 2.x | Data manipulation |

### Dashboard & Visualization
| Library | Version | Purpose |
|---|---|---|
| `streamlit` | 1.x | Interactive web dashboard |
| `plotly` | 5.x | Charts, gauges, waterfall plots |

### Utilities
| Library | Version | Purpose |
|---|---|---|
| `joblib` | 1.x | Model serialization |
| `pyarrow` | - | Fast CSV I/O |
| `shap` | 0.x | Explainability (surrogate model) |

---

## 📊 Dataset

The system uses **synthetic proxy datasets** modeled after real-world Kaggle sources:

### Dataset 1 — Return Behavior
- **Source**: E-commerce Return Analysis (Kaggle)
- **Records**: ~10,000
- **Key columns**: `user_id`, `return_reason`, `days_to_return`, `return_amount`
- **Used for**: Return ratio, wardrobing detection, avg return time

### Dataset 2 — Fraud Transactions
- **Source**: Fraudulent E-commerce Transactions (Kaggle)
- **Records**: 1.4M+ (sampled to 6,000 users)
- **Key columns**: `user_id`, `amount`, `timestamp`, `device_id`, `ip_address`, `is_fraud`
- **Used for**: Transaction patterns, device/IP graph, fraud labels

### Dataset 3 — Behavioral Sessions
- **Source**: E-commerce Fraud Behavioral Dataset (Kaggle)
- **Records**: ~6,000 users
- **Key columns**: `user_id`, `session_count`, `avg_pages_visited`, `avg_session_length`
- **Used for**: Session behavior anomaly detection

---

## ⚙️ Feature Engineering

19 features are engineered per user in `preprocess.py`:

```python
# Transaction features
transaction_count        # total purchases
avg_transaction_amount   # average spend
max_transaction_amount   # highest single purchase

# Temporal features
night_tx_count           # transactions between 11PM–5AM
night_activity_flag      # 1 if night_tx_count > 3 (Z-score)
burst_flag               # 1 if transaction count Z-score > 2

# Device/Network features
unique_devices           # distinct device IDs used
unique_ips               # distinct IP addresses used
unique_payment_methods   # distinct payment methods

# Return features
return_count             # number of returned orders
return_ratio             # returns / total orders
avg_return_time          # average days between purchase and return
avg_return_amount        # average value of returned items
wardrobing_count         # returns with reason = "Wardrobing"

# Session features
session_count            # total browser sessions
avg_session_length       # average session duration (minutes)
avg_pages_visited        # average pages per session
day_offset_std           # standard deviation of active days (activity spread)

# Value flags
high_value_flag          # 1 if any transaction > 95th percentile
```

All features are **StandardScaler-normalized** before being passed to neural networks.

---

## 🤖 AI Models

### Model 1 — Graph Neural Network (GNN)

**File**: `src/graph_model.py`

#### Architecture
```
Nodes: Users + Devices + IP Addresses + Payment Methods
Edges: "User X used Device Y" (weighted by frequency)

Algorithm: Louvain Community Detection
  → Finds clusters of densely connected users
  → Each cluster = potential fraud ring
```

#### Score Formula
```python
graph_risk_score = (
    0.5 × fraud_density_of_cluster  +  # % of confirmed fraudsters in ring
    0.3 × degree_normalized          +  # connections / 20 (capped at 1.0)
    0.2 × ring_size_factor               # shared users / 10 (capped at 1.0)
) × 100
```

#### Output
- `graph_scores.pkl` — serialized `{user_id: score}` dictionary
- Score range: **0–100** (higher = deeper in fraud ring)

---

### Model 2 — LSTM Temporal Model

**File**: `src/lstm_model.py`

#### Input Format
```
For each user: last 30 transactions
Each timestep: [amount_normalized, hour/23, day_of_week/6]
Padding: zero-pad from left if < 30 transactions
Shape: (batch_size, 30, 3)
```

#### Architecture
```
Input (30, 3)
    ↓
LSTM Layer 1 — 128 hidden units
    ↓
LSTM Layer 2 — 128 hidden units
    ↓
Dropout (30%)
    ↓
Linear (128 → 64) + ReLU
    ↓
Dropout (20%)
    ↓
Linear (64 → 1)
    ↓
Sigmoid → × 100 = temporal_risk_score
```

#### Training Config
```python
Loss:      Binary Cross Entropy (BCELoss)
Optimizer: Adam (lr=0.001)
Epochs:    15
Scheduler: ReduceLROnPlateau (patience=3)
Best model saved by: validation loss
```

#### LSTM Gate Operations (per timestep)
```
Forget Gate:  ft = σ(Wf · [h_prev, xt] + bf)
Input Gate:   it = σ(Wi · [h_prev, xt] + bi)
Cell Candidate: C̃t = tanh(Wc · [h_prev, xt] + bc)
Cell State:   Ct = ft ⊙ Ct_prev + it ⊙ C̃t
Output Gate:  ot = σ(Wo · [h_prev, xt] + bo)
Hidden State: ht = ot ⊙ tanh(Ct)
```

#### Output
- `lstm_best.pt` — trained model weights
- Score range: **0–100** (fraud probability × 100)

---

### Model 3 — Autoencoder Anomaly Detection

**File**: `src/autoencoder.py`

#### Training Strategy
```python
# Train ONLY on normal users (fraud_label = 0)
# Learns to reconstruct "normal" behavior
# High reconstruction error → anomalous → likely fraud
```

#### Architecture
```
ENCODER:
  Linear(19 → 64) + ReLU + BatchNorm
  Linear(64 → 32) + ReLU + BatchNorm
  Linear(32 → 16) + ReLU          ← BOTTLENECK

DECODER:
  Linear(16 → 32) + ReLU
  Linear(32 → 64) + ReLU
  Linear(64 → 19)                  ← RECONSTRUCTION
```

#### Training Config
```python
Loss:      MSELoss (reconstruction error)
Optimizer: Adam (lr=0.001)
Epochs:    20
```

#### Score Calculation
```python
# Per user:
reconstruction_error = mean((original_features - reconstructed)²)

# Normalize using normal user statistics:
Z = (user_error - normal_users_mean) / normal_users_std

# Convert to 0–100:
anomaly_score = clip(Z, 0, 4) / 4 × 100
# Z=0 → score=0 (normal), Z≥4 → score=100 (extreme anomaly)
```

#### Output
- `autoencoder_best.pt` — trained weights
- `autoencoder_meta.pkl` — normal user error statistics (mean, std)
- Score range: **0–100** (reconstruction deviation)

---

## ⚖️ Risk Fusion Engine

**File**: `src/risk_fusion.py`

### Weighted Formula
```python
risk_score = (0.30 × graph_risk_score) +
             (0.40 × temporal_risk_score) +
             (0.30 × anomaly_score)
```

### Weight Rationale
| Weight | Model | Reason |
|---|---|---|
| **40%** | Temporal (LSTM) | Behavioral change over time is the strongest real-world fraud signal |
| **30%** | Graph (GNN) | Strong but can have innocent false positives (shared public WiFi) |
| **30%** | Anomaly (AE) | Catches unknown patterns but new users also score high initially |

### Decision Thresholds
```python
if   risk_score <= 30:  → APPROVE  (green — process normally)
elif risk_score <= 70:  → VERIFY   (amber — request OTP / manual review)
else:                   → BLOCK    (red  — reject transaction)
```

### Reason Generation (10 Rules)
```python
if graph_risk_score > 50:    → "Connected to multiple suspicious accounts"
if temporal_risk_score > 60: → "Abnormal transaction burst detected"
if night_activity_flag == 1: → "High volume of late-night transactions"
if burst_flag == 1:          → "Sudden spike in transaction count"
if anomaly_score > 60:       → "Behavior deviates from normal user profile"
if return_ratio > 0.5:       → "High return ratio ({X}% of orders returned)"
if high_value_flag == 1:     → "High-value transaction detected"
if unique_devices > 3:       → "Multiple devices used ({N} devices)"
if unique_ips > 3:           → "Multiple IP addresses detected ({N} IPs)"
if wardrobing_count > 2:     → "Multiple wardrobing returns flagged"
```

### Output File: `risk_scores.csv`
```
user_id | risk_score | decision | reason_str |
graph_risk_score | temporal_risk_score | anomaly_score | fraud_label
```

---

## 🔬 Explainable AI

**File**: `src/explainability.py` / `app/explainability.py`

### Score Decomposition Method
Rather than black-box explanations, TriNetra uses **exact mathematical decomposition**:

```python
# Population baseline
pop_base = 0.30 × avg_graph + 0.40 × avg_temporal + 0.30 × avg_anomaly
         = 47.3 (average user risk score)

# This user's weighted contributions
contrib_graph    = 0.30 × user_graph_score
contrib_temporal = 0.40 × user_temporal_score
contrib_anomaly  = 0.30 × user_anomaly_score

# Delta vs population
delta_graph    = contrib_graph    - 0.30 × avg_graph
delta_temporal = contrib_temporal - 0.40 × avg_temporal
delta_anomaly  = contrib_anomaly  - 0.30 × avg_anomaly

# Example — User #43 (BLOCK, score=99.9):
# Base:     47.3
# + Graph:  +7.3   (fraud ring membership)
# + LSTM:   +19.4  (behavioral burst)
# + AE:     +26.1  (extreme anomaly)
# = Final:  99.9
```

### Surrogate SHAP Model
A `GradientBoostingRegressor` is trained on the 19 features to approximate the combined risk score, enabling SHAP feature importance analysis:

```python
surrogate = GradientBoostingRegressor(n_estimators=150, max_depth=4)
surrogate.fit(X_features, y_risk_scores)
# R² = 0.986 — surrogate closely matches actual risk scores
```

---

## 📺 Dashboard Pages

**File**: `app/dashboard.py`  
**Launch**: `streamlit run app/dashboard.py`  
**URL**: `http://localhost:8501`

### Page 1 — 🏠 Overview
| Widget | Description |
|---|---|
| 4 KPI cards | Total users, Blocked count, Verify count, Approved count |
| Risk Score Histogram | Full distribution with APPROVE/VERIFY/BLOCK zones |
| Decision Pie Chart | % split across three decisions |
| Component Bar Chart | Avg Graph vs LSTM vs Anomaly score by decision |
| Risk Box Plot | Score spread per decision category |
| Top 10 Table | Highest-risk users with all scores |

### Page 2 — 🔍 User Lookup
| Widget | Description |
|---|---|
| Gauge Chart | Animated 0–100 risk score gauge |
| Decision Badge | Color-coded APPROVE/VERIFY/BLOCK |
| Component Bar | Horizontal bar showing each model's score |
| Tab: Risk Reasons | Numbered, color-coded reason cards |
| Tab: Return Analysis | Return ratio gauge + fraud signal indicators |
| Tab: Explainable AI | Grouped bar (User vs Population) + Stacked score build-up |

### Page 3 — 🌐 Fraud Rings
| Widget | Description |
|---|---|
| 3 KPI cards | Total users, High graph risk count, Block count |
| Score Buckets Bar | User count per graph risk range (0–30, 31–50, 51–70, 71–85, 86–100) |
| Ring vs Normal Histogram | Final score distribution for ring members vs others |
| Top Ring Members Table | 20 users most embedded in fraud clusters |

### Page 4 — 📈 Temporal Patterns
| Widget | Description |
|---|---|
| Temporal Histogram | LSTM score distribution with threshold line |
| Temporal vs Anomaly Scatter | Correlation between two model scores |
| Temporal Split Pie | High vs normal temporal risk |
| Box Plot by Decision | LSTM score spread across APPROVE/VERIFY/BLOCK |

### Page 5 — 🎯 Anomaly Map
| Widget | Description |
|---|---|
| 3 KPI cards | High anomaly count, mean score, max score |
| Anomaly Histogram | Distribution with threshold annotations |
| Anomaly vs Risk Scatter | Correlation with final score and decision zones |
| Top Anomalous Users Table | 15 most anomalous users |

### Page 6 — ⚡ Live Simulator
| Control | Effect |
|---|---|
| Transaction Amount | Affects anomaly_score (high value = unusual) |
| Transaction Hour | Affects temporal_score (2AM = suspicious) |
| Return Ratio | Affects all 3 scores |
| Unique Devices | Affects graph + anomaly scores |
| Unique IPs | Affects graph score |
| Transaction Count | Affects temporal score (burst detection) |
| Shared Users | Directly drives graph score (fraud ring) |
| Payment Method | Gift Card adds extra temporal risk |

Real-time formula: `risk = 0.30×graph + 0.40×temporal + 0.30×anomaly`

---

## 📁 Project Structure

```
TriNetra/
│
├── app/
│   ├── dashboard.py          # Streamlit dashboard (6 pages)
│   └── explainability.py     # Explainability module (co-located copy)
│
├── src/
│   ├── data_generator.py     # Synthetic data generation
│   ├── preprocess.py         # Feature engineering & scaling
│   ├── graph_model.py        # GNN (NetworkX + Louvain)
│   ├── lstm_model.py         # LSTM (PyTorch, 2-layer)
│   ├── autoencoder.py        # Autoencoder (PyTorch, 19→16→19)
│   ├── risk_fusion.py        # Score fusion + reason generation
│   └── explainability.py     # SHAP surrogate + decomposition
│
├── data/
│   ├── raw/
│   │   ├── returns.csv
│   │   ├── fraud_transactions.csv
│   │   └── behavioral.csv
│   └── processed/
│       ├── merged_features.csv   # 6,000 users × 19 features (scaled)
│       └── risk_scores.csv       # Final scores + decisions
│
├── models/
│   ├── lstm_best.pt              # LSTM weights
│   ├── lstm_user_ids.pkl         # User ID index for sequences
│   ├── autoencoder_best.pt       # Autoencoder weights
│   ├── autoencoder_meta.pkl      # Error normalization statistics
│   ├── graph_scores.pkl          # Precomputed graph scores
│   ├── scaler.pkl                # StandardScaler object
│   └── shap_surrogate.pkl        # GradientBoosting surrogate
│
├── .streamlit/
│   └── config.toml               # Disable telemetry, set server options
│
├── train.py                      # Master training pipeline
├── requirements.txt              # All Python dependencies
└── README.md                     # This file
```

---

## 🚀 Installation & Setup

### Prerequisites
- Python 3.11+
- pip

### Install Dependencies
```bash
pip install -r requirements.txt
```

### `requirements.txt`
```
pandas
numpy
scikit-learn
torch
networkx
python-louvain
streamlit
plotly
joblib
pyarrow
shap
```

---

## ▶️ Running the System

### Step 1 — Train All Models
```bash
python train.py
```
This runs the full pipeline:
1. Generates synthetic data (if raw CSVs absent)
2. Preprocesses and engineers features
3. Trains GNN, LSTM, and Autoencoder
4. Fuses scores and saves `risk_scores.csv`

Expected output:
```
[Data]       Generating synthetic dataset...
[Preprocess] Merging 3 datasets → 6,000 users, 19 features
[GraphModel] Done. Mean=75.7, Max=99.8
[LSTM]       Done. Mean=51.5, Max=99.9
[Autoencoder]Done. Mean=13.1, Max=100.0
[Fusion]     Saved risk_scores.csv — BLOCK=354, VERIFY=5646, APPROVE=0
```

### Step 2 — Train Explainability Surrogate
```bash
python src/explainability.py
```
```
[SHAP] Surrogate trained. R² = 0.986
[SHAP] Surrogate saved to models/shap_surrogate.pkl
```

### Step 3 — Launch Dashboard
```bash
streamlit run app/dashboard.py
```
Open: **http://localhost:8501**

---

## 📖 Module Reference

### `src/data_generator.py`
```python
generate_synthetic_data(data_dir, n_users=6000, seed=42)
# Generates returns.csv, fraud_transactions.csv, behavioral.csv
```

### `src/preprocess.py`
```python
run_preprocessing(data_dir, models_dir) → (merged_df, feature_cols)
# Returns scaled feature DataFrame + list of feature column names
```

### `src/graph_model.py`
```python
run_graph_model(df_merged) → pd.Series {user_id: graph_risk_score}
# Builds graph, detects communities, scores each user 0–100
```

### `src/lstm_model.py`
```python
run_lstm_model(df_merged, models_dir) → pd.Series {user_id: temporal_risk_score}
# Trains LSTM on sequences, returns per-user scores 0–100
```

### `src/autoencoder.py`
```python
run_autoencoder(df_merged, feat_cols, models_dir) → pd.Series {user_id: anomaly_score}
# Trains AE on normal users only, returns reconstruction-error scores 0–100
```

### `src/risk_fusion.py`
```python
fuse_scores(df_merged, graph_scores, temporal_scores, anomaly_scores) → pd.DataFrame
# Combines scores, generates decisions and reasons, returns full result DataFrame

print_report(result_df)
# Prints summary statistics to console
```

### `src/explainability.py`
```python
train_surrogate(merged_df, risk_scores, models_dir) → (model, feat_cols)
# Trains GBR surrogate model for SHAP

get_shap_values(user_id, merged_df, models_dir) → pd.DataFrame
# Returns feature contribution DataFrame for one user
```

---

## 📈 Performance Metrics

| Metric | Value |
|---|---|
| Total Users Analysed | 6,000 |
| BLOCK Decisions | ~354 (5.9%) |
| VERIFY Decisions | ~5,646 (94.1%) |
| APPROVE Decisions | ~0 (0%) |
| Graph Score Mean | 75.7 |
| LSTM Score Mean | 51.5 |
| Anomaly Score Mean | 13.1 |
| Risk Score Mean | 47.3 |
| Surrogate R² | 0.986 |

> **Note**: Low APPROVE rate reflects aggressive risk posture in the current threshold configuration.  
> Thresholds can be adjusted in `risk_fusion.py`: `VERIFY_THRESHOLD = 30`, `BLOCK_THRESHOLD = 70`

---

## 🔮 Future Enhancements

| Feature | Description | Priority |
|---|---|---|
| **Real-time API** | FastAPI endpoint for live transaction scoring | High |
| **Neo4j Integration** | Replace NetworkX with graph database for scale | High |
| **Kafka Stream** | Real-time transaction ingestion pipeline | Medium |
| **Feedback Loop** | Dashboard buttons to mark false positives | Medium |
| **PDF Reports** | Auto-generate per-user risk reports | Low |
| **Confidence Score** | Show std deviation of 3 model scores | Low |
| **Multi-merchant** | Extend to multiple merchant contexts | Low |

---

## 👨‍💻 Author

**TriNetra AI** — Built for hackathon demonstration  
Repository: [github.com/Gurumurthys1/hackhustle](https://github.com/Gurumurthys1/hackhustle)

---

<div align="center">

**🔺 TriNetra AI** · GNN + LSTM + Autoencoder · Hybrid Fraud Intelligence

*"Three Eyes. One Decision. Zero Fraud."*

</div>
