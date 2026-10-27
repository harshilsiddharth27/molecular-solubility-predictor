import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import joblib
from rdkit import Chem
from rdkit.Chem import AllChem

def main():
    print("Downloading Delaney ESOL dataset...")
    # Raw CSV URL for the Delaney ESOL dataset
    url = "https://raw.githubusercontent.com/deepchem/deepchem/master/datasets/delaney-processed.csv"
    df = pd.read_csv(url)

    print("Converting SMILES to Morgan Fingerprints...")
    def smiles_to_fp(smiles):
        mol = Chem.MolFromSmiles(smiles)
        # Fallback to zero vector if SMILES is invalid
        if mol is None:
            return np.zeros((2048,))
        # Generate 2048-bit Morgan fingerprint (radius = 2)
        fp = AllChem.GetMorganFingerprintAsBitVect(mol, 2, nBits=2048)
        return np.array(fp)

    # Apply transformation to the 'smiles' column
    X = np.array([smiles_to_fp(s) for s in df['smiles']])
    # Target variable: measured log solubility in mols per litre
    y = df['measured log solubility in mols per litre'].values

    print("Splitting dataset and training RandomForestRegressor...")
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Train the RandomForest model
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    print("Evaluating model...")
    y_pred = model.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)

    print(f"Mean Squared Error: {mse:.4f}")
    print(f"R-squared: {r2:.4f}")

    print("Exporting model to solubility_model.pkl...")
    joblib.dump(model, 'solubility_model.pkl')
    print("Pipeline complete!")

if __name__ == "__main__":
    main()
