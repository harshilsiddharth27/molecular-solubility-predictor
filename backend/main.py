from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import joblib
import numpy as np
from rdkit import Chem
from rdkit.Chem import AllChem, Descriptors, rdMolDescriptors
from rdkit.Chem.Draw import rdMolDraw2D

app = FastAPI(title="Molecular Solubility Predictor API")

# 1. Configure CORS for local Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. Load the trained model into memory at startup
try:
    model = joblib.load("solubility_model.pkl")
except FileNotFoundError:
    model = None
    print("Warning: 'solubility_model.pkl' not found. Please run train_model.py first.")

# 3. Define Pydantic BaseModel for the request
class PredictRequest(BaseModel):
    smiles: str

def get_solubility_class(score: float) -> str:
    """Helper to classify logS score."""
    if score > -2.0:
        return "Highly Soluble"
    elif score > -4.0:
        return "Moderately Soluble"
    elif score > -6.0:
        return "Poorly Soluble"
    else:
        return "Insoluble"

# Common chemical formula & name to SMILES dictionary
COMMON_ALIASES = {
    "nacl": "[Na+].[Cl-]",
    "sodium chloride": "[Na+].[Cl-]",
    "kcl": "[K+].[Cl-]",
    "potassium chloride": "[K+].[Cl-]",
    "cacl2": "[Ca+2].[Cl-].[Cl-]",
    "naoh": "[Na+].[OH-]",
    "koh": "[K+].[OH-]",
    "h2o": "O",
    "water": "O",
    "hcl": "Cl",
    "nh3": "N",
    "co2": "O=C=O",
    "nahco3": "[Na+].OC(=O)[O-]",
    "aspirin": "CC(=O)Oc1ccccc1C(=O)O",
    "caffeine": "CN1C=NC2=C1C(=O)N(C(=O)N2C)C",
    "vitamin c": "C(C(C1C(=C(C(=O)O1)O)O)O)O",
    "ethanol": "CCO",
    "methanol": "CO",
    "benzene": "c1ccccc1",
    "phenol": "c1ccccc1O",
    "toluene": "Cc1ccccc1",
    "glucose": "C(C1C(C(C(C(O1)O)O)O)O)O"
}

# 4. Create the POST /api/predict endpoint
@app.post("/api/predict")
def predict_solubility(request: PredictRequest):
    if model is None:
        raise HTTPException(status_code=500, detail="Machine learning model is not loaded on the server.")

    raw_input = request.smiles.strip()
    # Normalize common chemical formulas or names (e.g., 'NaCl' -> '[Na+].[Cl-]')
    smiles = COMMON_ALIASES.get(raw_input.lower(), raw_input)
    mol = Chem.MolFromSmiles(smiles)
    
    # Validate SMILES string
    if mol is None:
        raise HTTPException(status_code=400, detail="Invalid SMILES string provided.")
        
    # Convert valid SMILES into a Morgan Fingerprint array
    fp = AllChem.GetMorganFingerprintAsBitVect(mol, 2, nBits=2048)
    fp_array = np.array(fp).reshape(1, -1)
    
    # Predict the solubility score
    score = float(model.predict(fp_array)[0])
    classification = get_solubility_class(score)
    
    # Calculate confidence score based on ensemble tree predictions
    # Standard deviation across trees measures model uncertainty/disagreement
    tree_predictions = np.array([tree.predict(fp_array)[0] for tree in model.estimators_])
    tree_std = float(np.std(tree_predictions))
    
    # Map standard deviation to a 0-100% confidence scale
    # Tree std dev in Delaney logS typically ranges 0.1 to 1.2+
    confidence_score = max(5.0, min(99.0, round((1.0 - (tree_std / 1.2)) * 100, 1)))
    
    if confidence_score >= 75:
        reliability = "High Reliability"
    elif confidence_score >= 50:
        reliability = "Moderate Reliability"
    else:
        reliability = "Low Reliability"

    confidence = {
        "score": confidence_score,
        "std_dev": round(tree_std, 3),
        "reliability": reliability
    }

    # Generate a 2D vector SVG of the molecule
    drawer = rdMolDraw2D.MolDraw2DSVG(400, 400)
    # Configure drawing options for cleaner visuals
    opts = drawer.drawOptions()
    opts.addStereoAnnotation = True
    drawer.DrawMolecule(mol)
    drawer.FinishDrawing()
    svg_content = drawer.GetDrawingText()
    
    # Extract 5 chemical descriptors
    descriptors = {
        "Molecular Weight": round(Descriptors.MolWt(mol), 2),
        "Heavy Atoms": mol.GetNumHeavyAtoms(),
        "Rotatable Bonds": rdMolDescriptors.CalcNumRotatableBonds(mol),
        "H-Donors": rdMolDescriptors.CalcNumHBD(mol),
        "H-Acceptors": rdMolDescriptors.CalcNumHBA(mol)
    }
    
    # 5. Return structured JSON response with confidence score
    return {
        "smiles": smiles,
        "predicted_score": round(score, 3),
        "classification": classification,
        "confidence": confidence,
        "svg": svg_content,
        "descriptors": descriptors
    }
