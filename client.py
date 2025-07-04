import requests
import json

API_URL = "http://127.0.0.1:5000/predict"

def test_signal(signal_data):
    """Envoie un signal à l'API et affiche la réponse."""
    try:
        response = requests.post(API_URL, json=signal_data)
        response.raise_for_status() # Lève une exception si le statut est une erreur (4xx ou 5xx)
        
        print(f"Test du signal : {signal_data}")
        print(f"  -> Réponse de l'API : {response.json()}")
        print("-" * 20)

    except requests.exceptions.RequestException as e:
        print(f"Erreur lors de la communication avec l'API : {e}")

if __name__ == "__main__":
    # Scénario 1 : Un signal parfaitement normal
    normal_signal = {
        "frequency": 12.5,
        "power": 100.0,
        "modulation": 1
    }
    test_signal(normal_signal)
    
    # Scénario 2 : Un signal clairement anormal (jamming)
    attack_signal = {
        "frequency": 18.2,
        "power": 550.8,
        "modulation": 0
    }
    test_signal(attack_signal) 