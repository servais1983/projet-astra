from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, conlist
import torch
import joblib
import numpy as np
from advanced_detector import AdvancedAnomalyDetector, Autoencoder

# --- Configuration ---
MODEL_PATH = "astra_anomaly_detector.pth"
SCALER_PATH = "astra_data_scaler.pkl"
INPUT_DIM = 3
ENCODING_DIM = 16

# --- Chargement du modèle et du scaler ---
app = FastAPI(title="ASTRA Anomaly Detection API", description="API de détection d'anomalies pour signaux satellites", version="1.0")

try:
    scaler = joblib.load(SCALER_PATH)
except Exception as e:
    scaler = None
    print(f"Erreur lors du chargement du scaler : {e}")

try:
    model = Autoencoder(INPUT_DIM, ENCODING_DIM)
    model.load_state_dict(torch.load(MODEL_PATH, map_location=torch.device('cpu')))
    model.eval()
except Exception as e:
    model = None
    print(f"Erreur lors du chargement du modèle : {e}")

# --- Schéma d'entrée pour FastAPI ---
class SignalInput(BaseModel):
    frequency: float
    power: float
    modulation: float

class BatchInput(BaseModel):
    signals: conlist(SignalInput, min_items=1)

# --- Endpoint de santé ---
@app.get("/health")
def health():
    if model is not None and scaler is not None:
        return {"status": "ok"}
    else:
        raise HTTPException(status_code=500, detail="Modèle ou scaler non chargé")

# --- Endpoint de prédiction ---
@app.post("/predict")
def predict(batch: BatchInput):
    if model is None or scaler is None:
        raise HTTPException(status_code=500, detail="Modèle ou scaler non chargé")
    # Préparation des données
    X = np.array([[s.frequency, s.power, s.modulation] for s in batch.signals])
    X_scaled = scaler.transform(X)
    X_tensor = torch.FloatTensor(X_scaled)
    with torch.no_grad():
        reconstructed = model(X_tensor)
        losses = torch.mean((X_tensor - reconstructed) ** 2, dim=1).numpy()
    # Seuil d'anomalie : on reprend la logique du modèle (max sur les données d'entraînement)
    # Ici, on peut charger le seuil depuis un fichier ou le recalculer (à adapter si besoin)
    # Pour la démo, on utilise un seuil par défaut
    threshold = 0.004
    results = []
    for i, loss in enumerate(losses):
        verdict = "Anomalie" if loss > threshold else "Normal"
        results.append({
            "signal": batch.signals[i].dict(),
            "reconstruction_error": float(loss),
            "verdict": verdict
        })
    return {"results": results}

# --- Exemple d'utilisation (pour la doc auto) ---
@app.get("/")
def root():
    return {
        "message": "Bienvenue sur l'API de détection d'anomalies ASTRA.",
        "usage": "POST /predict avec un JSON de signaux pour obtenir un verdict.",
        "example": {
            "signals": [
                {"frequency": 12.5, "power": 100.1, "modulation": 1},
                {"frequency": 15.0, "power": 400.0, "modulation": 0}
            ]
        }
    } 