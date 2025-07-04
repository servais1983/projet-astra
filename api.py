import torch
import joblib
import pandas as pd
from flask import Flask, request, jsonify

from advanced_detector import AdvancedAnomalyDetector

# --- Configuration et Chargement des Modèles ---
print("Initialisation du serveur API ASTRA HIVE...")

# 1. Charger la configuration et les chemins
CONFIG = {
    "INPUT_DIM": 3,
    "ENCODING_DIM": 16,
    "MODEL_PATH": "astra_anomaly_detector.pth",
    "SCALER_PATH": "astra_data_scaler.pkl"
}

# 2. Initialiser l'architecture du détecteur
# Note : Nous créons une instance pour pouvoir charger le state_dict
detector = AdvancedAnomalyDetector(
    input_dim=CONFIG["INPUT_DIM"], 
    encoding_dim=CONFIG["ENCODING_DIM"]
)

# 3. Charger les poids du modèle entraîné
detector.model.load_state_dict(torch.load(CONFIG["MODEL_PATH"]))
detector.model.eval() # Très important : passer le modèle en mode évaluation
print(f"Modèle chargé depuis '{CONFIG['MODEL_PATH']}'")

# 4. Charger le scaler
scaler = joblib.load(CONFIG["SCALER_PATH"])
print(f"Scaler chargé depuis '{CONFIG['SCALER_PATH']}'")

# 5. Initialiser l'application Flask
app = Flask(__name__)
print("Serveur API prêt à recevoir des requêtes.")

# --- Définition de l'Endpoint de Prédiction ---
@app.route("/predict", methods=["POST"])
def predict():
    """
    Endpoint pour prédire si un signal est une anomalie.
    Accepte des données JSON avec les clés 'frequency', 'power', 'modulation'.
    """
    # Récupérer les données JSON de la requête
    input_data = request.get_json()
    if not input_data:
        return jsonify({"error": "Données non fournies"}), 400

    try:
        # Convertir les données en DataFrame pour le scaler
        df = pd.DataFrame([input_data])
        
        # Normaliser les données avec le scaler chargé
        scaled_data = scaler.transform(df)
        tensor_data = torch.FloatTensor(scaled_data).to(detector.device)

        # Faire la prédiction
        with torch.no_grad():
            reconstructed = detector.model(tensor_data)
            # Calculer l'erreur de reconstruction
            loss = torch.mean((tensor_data - reconstructed) ** 2, dim=1)
            is_anomaly = loss > 0.001 # Utiliser un seuil prédéfini ou celui calculé
        
        result = "Anomalie Détectée" if is_anomaly.item() else "Signal Normal"
        confidence_score = loss.item()

        # Retourner une réponse JSON claire
        return jsonify({
            "prediction": result,
            "reconstruction_error": confidence_score
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    # Lancer le serveur sur le port 5000
    app.run(debug=True, port=5000) 