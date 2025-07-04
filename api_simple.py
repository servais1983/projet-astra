# api_simple.py - Version simplifiée de l'API ASTRA HIVE
from flask import Flask, request, jsonify
import numpy as np

app = Flask(__name__)

# Simulation d'un détecteur d'anomalies simple
def detect_anomaly(data):
    """
    Détecte les anomalies basées sur des seuils simples.
    """
    frequency = data.get('frequency', 0)
    power = data.get('power', 0)
    modulation = data.get('modulation', 0)
    
    # Seuils d'anomalie (simulation)
    if frequency > 15.0 or frequency < 10.0:
        return True, "Fréquence anormale"
    if power > 500.0 or power < 50.0:
        return True, "Puissance anormale"
    if modulation not in [0, 1]:
        return True, "Modulation invalide"
    
    return False, "Signal normal"

@app.route("/predict", methods=["POST"])
def predict():
    """
    Endpoint pour prédire si un signal est une anomalie.
    """
    input_data = request.get_json()
    if not input_data:
        return jsonify({"error": "Données non fournies"}), 400

    try:
        is_anomaly, reason = detect_anomaly(input_data)
        result = "Anomalie Détectée" if is_anomaly else "Normal"
        
        return jsonify({
            "prediction": result,
            "reason": reason,
            "confidence_score": 0.95 if is_anomaly else 0.05
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/health", methods=["GET"])
def health():
    """
    Endpoint de santé pour vérifier que l'API fonctionne.
    """
    return jsonify({"status": "OK", "service": "ASTRA HIVE API"})

if __name__ == "__main__":
    print("🚀 Serveur API ASTRA HIVE (version simplifiée) démarré sur http://127.0.0.1:5000")
    app.run(debug=True, port=5000) 