# 🔺 TriNetra AI — Real-Time Fraud Detection System

> Hybrid fraud intelligence combining **Graph Neural Networks**, **LSTM**, and **Autoencoder** to detect return fraud, transaction fraud, and behavioral anomalies in real time.

---

## 🏗️ Architecture

```
Raw Data  →  Preprocessing  →  Feature Engineering  →  Merged Dataset
                                                              │
                          ┌───────────────────────────────────┤
                          ▼               ▼                   ▼
                    Graph Model       LSTM Model         Autoencoder
                  (Fraud Rings)    (Temporal Behavior) (Anomaly Detection)
                  graph_score      temporal_score       anomaly_score
                          └───────────────────────────────────┘
                                          │
                                  Risk Fusion Engine
                              0.3×Graph + 0.4×LSTM + 0.3×AE
                                          │
                              APPROVE / VERIFY / BLOCK
```

---

## 📦 Setup

```bash
pip install -r requirements.txt
```

## 🚀 Run

**Step 1: Train all models**
```bash
python train.py
```

**Step 2: Launch dashboard**
```bash
streamlit run app/dashboard.py
```

---

## 📊 Datasets

Place real Kaggle CSVs in `data/raw/` (optional — synthetic data is auto-generated):

| File | Source |
|---|---|
| `returns.csv` | [Return Behavior Dataset](https://www.kaggle.com/datasets/sayalikhot21/synthetic-dataset-for-e-commerce-return-analysis) |
| `fraud_transactions.csv` | [Fraudulent E-Commerce Transactions](https://www.kaggle.com/datasets/shriyashjagtap/fraudulent-e-commerce-transactions) |
| `behavioral.csv` | [E-Commerce Fraud Detection Dataset](https://www.kaggle.com/datasets/umuttuygurr/e-commerce-fraud-detection-dataset) |

---

## 🎯 Decision Engine

| Risk Score | Decision |
|---|---|
| 0 – 30 | ✅ APPROVE |
| 31 – 70 | ⚠️ VERIFY |
| 71 – 100 | 🚫 BLOCK |

---

## 🧠 Model Details

| Model | Purpose | Output |
|---|---|---|
| **GNN (NetworkX + Louvain)** | Fraud ring detection via shared device/IP/payment | `graph_risk_score` |
| **LSTM (PyTorch, 2-layer)** | Temporal burst, night activity, return spikes | `temporal_risk_score` |
| **Autoencoder (PyTorch)** | Deviation from normal user behavior profile | `anomaly_score` |

---

## 📁 Project Structure

```
TriNetra/
├── data/
│   ├── raw/                    ← Input CSVs
│   └── processed/              ← Merged features + risk scores
├── models/                     ← Saved model weights
├── src/
│   ├── data_generator.py       ← Synthetic data generation
│   ├── preprocess.py           ← Feature engineering pipeline
│   ├── graph_model.py          ← GNN fraud ring detection
│   ├── lstm_model.py           ← LSTM temporal model
│   ├── autoencoder.py          ← Anomaly detection
│   └── risk_fusion.py          ← Score fusion + decisions
├── app/
│   └── dashboard.py            ← Streamlit dashboard
├── train.py                    ← Main training entrypoint
└── requirements.txt
```
