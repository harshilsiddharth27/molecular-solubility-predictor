# ⚗️ SoluPredict: Molecular Aqueous Solubility Prediction System

[![React](https://img.shields.io/badge/Frontend-React%2019%20%7C%20Vite%20%7C%20Tailwind-61DAFB?logo=react&logoColor=black)](https://react.dev/)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI%20%7C%20Python%203.10+-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![RDKit](https://img.shields.io/badge/Cheminformatics-RDKit-2D72D9?logo=python&logoColor=white)](https://www.rdkit.org/)
[![Scikit-Learn](https://img.shields.io/badge/ML-RandomForest%20%7C%20Morgan%20FP-F7931E?logo=scikit-learn&logoColor=white)](https://scikit-learn.org/)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)

An end-to-end, decoupled cheminformatics application that predicts the **aqueous solubility ($\text{Log } S$)** of chemical compounds from their **SMILES** (Simplified Molecular Input Line Entry System) string or common chemical names. Developed as a **Database Systems Lab [CSS 2212] Mini Project** at the **School of Computer Engineering, Manipal Institute of Technology, Bengaluru**.

---

## 🌟 Key Features

- **🎯 Machine Learning Solubility Prediction**:
  Trained on the benchmark **Delaney (ESOL)** dataset using 2048-bit radius-2 Morgan Chemical Fingerprints and an ensemble `RandomForestRegressor` ($R^2 \approx 0.88$, $RMSE \approx 0.61$).

- **🛡️ Uncertainty & Confidence Scoring**:
  Calculates epistemic confidence based on the **variance and standard deviation across ensemble decision tree estimators** ($\sigma_{\text{trees}}$), providing researchers with a tangible 0–100% prediction reliability gauge.

- **🔬 2D Vector Molecular Structure Rendering**:
  Interactive, crisp SVG canvas visualizer powered by `smiles-drawer` and RDKit with full support for organic molecules (Aspirin, Caffeine, Paracetamol) and inorganic salts (e.g., Sodium Chloride `[Na+].[Cl-]`).

- **📊 Dynamic Chemical Descriptor Comparison**:
  Computes key Lipinski descriptors (Molecular Weight, Heavy Atoms, Rotatable Bonds, H-Donors, H-Acceptors). Includes a **Compare** mode with trend badges indicating whether a query deviates above or below the rolling average of searched compounds.

- **📈 Historical Trend Tracking (Recharts)**:
  Visualizes chronological shifts in predicted $\text{Log } S$ values over the last 5 queries with threshold reference lines for solubility classifications (*Highly Soluble*, *Moderately Soluble*, *Poorly Soluble*, *Insoluble*).

- **💾 Laboratory CSV Export**:
  Single-click export of structured prediction reports including compound name, canonical SMILES, descriptors, confidence metrics, and timestamp for database logging and wet-lab records.

- **🗃️ Persistent Local Query History**:
  Retains the user's recent searches and session descriptors in `localStorage` for instant re-selection and analysis.

---

## 🏗️ System Architecture

```
┌────────────────────────────────────────────────────────────────────────┐
│                        Next.js / React 19 Frontend                     │
│  - Interactive SMILES & Formula Input                                  │
│  - 2D Molecular Vector Canvas (SmilesDrawer)                           │
│  - Model Confidence Gauge & Comparison Badges                          │
│  - Recharts Solubility Trendline & CSV Exporter                        │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ HTTP / REST (JSON)
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                        FastAPI Python Microservice                     │
│  - SMILES & Chemical Alias Normalization (e.g., NaCl -> [Na+].[Cl-])   │
│  - RDKit Morgan Fingerprint Vectorizer (2048-bit, radius=2)            │
│  - RandomForest Ensemble Inference Engine                              │
│  - Tree Standard Deviation Confidence Calculator                       │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                    Database & Model Storage Layer                      │
│  - Delaney Processed Dataset (1,144 Compounds)                         │
│  - Pre-trained Pipeline Artifact: solubility_model.pkl                 │
│  - Relational Schema: Compounds, Descriptors, Predictions, History     │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 🗄️ Database Schema Design (CSS 2212)

The system is designed around a relational database architecture to store compound metadata, calculated descriptors, and prediction logs:

```sql
-- 1. Core Compounds Table
CREATE TABLE compounds (
    compound_id SERIAL PRIMARY KEY,
    canonical_smiles VARCHAR(1000) UNIQUE NOT NULL,
    common_name VARCHAR(255),
    chemical_formula VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_compounds_smiles ON compounds(canonical_smiles);

-- 2. Physicochemical Descriptors
CREATE TABLE chemical_descriptors (
    descriptor_id SERIAL PRIMARY KEY,
    compound_id INT REFERENCES compounds(compound_id) ON DELETE CASCADE,
    molecular_weight NUMERIC(8, 3) NOT NULL,
    heavy_atom_count INT NOT NULL,
    rotatable_bonds INT NOT NULL,
    h_donors INT NOT NULL,
    h_acceptors INT NOT NULL
);

-- 3. Solubility Predictions & Uncertainty Log
CREATE TABLE solubility_predictions (
    prediction_id SERIAL PRIMARY KEY,
    compound_id INT REFERENCES compounds(compound_id) ON DELETE CASCADE,
    predicted_logs NUMERIC(6, 3) NOT NULL,
    classification VARCHAR(50) NOT NULL,
    confidence_score NUMERIC(5, 2) NOT NULL,
    tree_std_dev NUMERIC(6, 4) NOT NULL,
    model_version VARCHAR(50) DEFAULT 'RandomForest-Delaney-v1',
    predicted_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

---

## 🚀 Getting Started

### Prerequisites
- **Node.js**: v18.0.0 or later
- **Python**: v3.10 or later
- **Conda** or **pip** (for RDKit chemical informatics library)

---

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/solupredict.git
cd solupredict
```

### 2. Backend Setup & Model Training

1. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate   # On Windows: venv\Scripts\activate
   ```

2. **Install Python dependencies:**
   ```bash
   pip install fastapi uvicorn rdkit scikit-learn pandas numpy joblib pydantic
   ```

3. **Train the Delaney Random Forest model:**
   ```bash
   python train_model.py
   ```
   *This automatically downloads the Delaney ESOL dataset, computes Morgan fingerprints, trains the `RandomForestRegressor`, outputs $R^2$ and $MSE$ metrics, and saves `solubility_model.pkl`.*

4. **Start the FastAPI backend:**
   ```bash
   uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
   ```
   The API will be live at `http://localhost:8000`. API docs: `http://localhost:8000/docs`.

---

### 3. Frontend Setup

1. **Install Node packages:**
   ```bash
   npm install
   ```

2. **Run the Vite development server:**
   ```bash
   npm run dev
   ```
   Open `http://localhost:3000` in your browser.

---

## 📡 API Specification

### Predict Solubility

- **Endpoint**: `POST /api/predict`
- **Request Body**:
  ```json
  {
    "smiles": "CC(=O)Oc1ccccc1C(=O)O"
  }
  ```
  *(Accepts canonical SMILES strings or aliases like `"nacl"`, `"aspirin"`, `"caffeine"`, etc.)*

- **Success Response (200 OK)**:
  ```json
  {
    "smiles": "CC(=O)Oc1ccccc1C(=O)O",
    "predicted_score": -2.15,
    "classification": "Moderately Soluble",
    "confidence": {
      "score": 87.5,
      "std_dev": 0.15,
      "reliability": "High"
    },
    "descriptors": {
      "Molecular Weight": 180.16,
      "Heavy Atoms": 13,
      "Rotatable Bonds": 3,
      "H-Donors": 1,
      "H-Acceptors": 4
    },
    "svg": "<svg>...</svg>"
  }
  ```

---

## 🧪 Model Performance & Benchmarks

| Metric | Delaney ESOL Test Set |
| :--- | :--- |
| **Coefficient of Determination ($R^2$)** | **0.884** |
| **Root Mean Squared Error ($RMSE$)** | **0.612 $\text{Log } S$** |
| **Mean Absolute Error ($MAE$)** | **0.457 $\text{Log } S$** |
| **Fingerprint Feature Representation** | 2048-bit Morgan Fingerprint (Radius = 2) |
| **Ensemble Estimators** | 100 Decision Trees |

---

## 👥 Project Team & Academic Credits

**Course**: Database Systems Lab `[CSS 2212]`  
**Institution**: School of Computer Engineering, Manipal Institute of Technology, Bengaluru  
**Parent University**: Manipal Academy of Higher Education (MAHE)

### Team Members
- **Harshil Siddharth** — Reg. No. `245890048`
- **Hrudayesh** — Reg. No. `245890394`
- **Pranav Kaneti** — Reg. No. `245890248`
- **Shanmukeswar** — Reg. No. `245890158`

### Project Supervisor
- **Dr. Anil Kumar**  
  Assistant Professor, School of Computer Engineering  
  Manipal Institute of Technology, Bengaluru

---

## 📜 References
1. **Delaney, J. S. (2004)**. *ESOL: Estimating Aqueous Solubility Directly from Molecular Structure*. Journal of Chemical Information and Computer Sciences, 44(3), 1000–1005.
2. **Landrum, G. (2016)**. *RDKit: Open-Source Cheminformatics Software*. [https://www.rdkit.org](https://www.rdkit.org).
3. **Lipinski, C. A., et al. (2001)**. *Experimental and computational approaches to estimate solubility and permeability in drug discovery and development settings*. Advanced Drug Delivery Reviews, 46(1-3), 3–26.

---

## 📄 License
This project is licensed under the [Apache-2.0 License](LICENSE).
