# main.py (version 2)
from anomaly_detector import AnomalyDetector
import pandas as pd
import os

# On importe notre interface avec le modèle local
from model import ask_phi 

def setup_dummy_data():
    """Crée des fichiers de données factices pour que notre script puisse fonctionner."""
    # (Le code de cette fonction ne change pas)
    print("Vérification des données de simulation...")
    if not os.path.exists('data'):
        os.makedirs('data')
    legit_path = 'data/legit_signals.csv'
    attack_path = 'data/attack_signals.csv'
    if not os.path.exists(legit_path):
        print("Création de données légitimes factices...")
        legit_data = pd.DataFrame({
            'frequency': [12.5, 12.51, 12.49, 12.5, 12.52],
            'power': [100.1, 100.2, 99.9, 100.0, 100.3],
            'modulation': [1, 1, 1, 1, 1]
        })
        legit_data.to_csv(legit_path, index=False)
    if not os.path.exists(attack_path):
        print("Création de données d'attaque factices (jamming)...")
        attack_data = pd.DataFrame({
            'frequency': [12.5, 12.0, 15.0, 12.5, 11.5],
            'power': [250.0, 300.1, 50.5, 280.7, 400.0],
            'modulation': [0, 0, 1, 0, 0]
        })
        attack_data.to_csv(attack_path, index=False)
    print("Données de simulation prêtes.")
    return legit_path, attack_path

def generate_advanced_detector_code():
    """
    Utilise notre IA locale Phi-3 pour générer le code du détecteur avancé.
    C'est notre "pair programming" en action.
    """
    print("\n--- Sollicitation de l'IA locale (Phi-3) pour le code avancé ---")
    prompt = """
    Bonjour. Veuillez générer le code Python pour un fichier nommé 'advanced_detector.py'.
    Ce fichier doit contenir une classe 'AdvancedAnomalyDetector' utilisant PyTorch.
    La classe doit implémenter un modèle d'Autoencodeur pour la détection d'anomalies.
    
    Elle doit avoir les méthodes suivantes :
    - __init__(self, input_dim, encoding_dim): Initialise le modèle et l'architecture de l'autoencodeur.
    - train(self, data_loader, epochs=20): Entraîne le modèle. Accepte un DataLoader PyTorch.
    - predict(self, data_loader): Calcule l'erreur de reconstruction pour chaque entrée et retourne les anomalies basées sur un seuil.

    Le code doit être complet, fonctionnel et inclure les imports nécessaires (torch, torch.nn, etc.).
    N'ajoutez pas d'exemple d'utilisation, seulement la classe et son code.
    """
    
    generated_code = ask_phi(prompt)
    
    # On sauvegarde le code généré dans un nouveau fichier
    with open("advanced_detector.py", "w") as f:
        f.write(generated_code)
        
    print("Le fichier 'advanced_detector.py' a été généré par l'IA.")
    print("Veuillez l'inspecter avant de l'utiliser.")

def run_simulation():
    """Fonction principale pour exécuter la simulation de détection."""
    print("\n--- DÉBUT DE LA SIMULATION ASTRA HIVE (Phase 1) ---")
    setup_dummy_data()
    print("Simulation avec le modèle de base 'IsolationForest' terminée.")


if __name__ == '__main__':
    # On exécute d'abord la simulation de base
    run_simulation()
    
    # Ensuite, on génère le code pour notre modèle avancé
    generate_advanced_detector_code() 