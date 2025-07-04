import torch
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import classification_report
from torch.utils.data import DataLoader, TensorDataset
import os
import joblib # Pour sauvegarder notre scaler

from advanced_detector import AdvancedAnomalyDetector

# --- Configuration du Modèle (Hyperparamètres) ---
CONFIG = {
    "INPUT_DIM": 3, # Fréquence, puissance, modulation
    "ENCODING_DIM": 16, # Dimension de la représentation compressée
    "EPOCHS": 100, # Augmentation pour un meilleur entraînement
    "BATCH_SIZE": 2,
    "MODEL_PATH": "astra_anomaly_detector.pth", # Chemin pour sauvegarder le modèle
    "SCALER_PATH": "astra_data_scaler.pkl" # Chemin pour sauvegarder le scaler
}

def setup_dummy_data():
    """Crée des fichiers de données factices pour que notre script puisse fonctionner."""
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

def run_production_cycle():
    """
    Simule un cycle de production complet : entraînement, validation et sauvegarde.
    """
    print("\n--- DÉBUT DU CYCLE DE PRODUCTION ASTRA HIVE ---")

    # 1. Préparation des données
    legit_path, attack_path = setup_dummy_data()
    df_legit = pd.read_csv(legit_path)
    df_attack = pd.read_csv(attack_path)

    # 2. Normalisation et sauvegarde du scaler
    scaler = MinMaxScaler()
    df_legit_scaled = scaler.fit_transform(df_legit)
    joblib.dump(scaler, CONFIG["SCALER_PATH"])
    print(f"Scaler de normalisation sauvegardé dans {CONFIG['SCALER_PATH']}")

    # 3. Création des DataLoaders
    train_dataset = TensorDataset(torch.FloatTensor(df_legit_scaled))
    train_loader = DataLoader(train_dataset, batch_size=CONFIG["BATCH_SIZE"], shuffle=True)

    # 4. Entraînement du modèle
    detector = AdvancedAnomalyDetector(
        input_dim=CONFIG["INPUT_DIM"], 
        encoding_dim=CONFIG["ENCODING_DIM"]
    )
    detector.train(train_loader, epochs=CONFIG["EPOCHS"])

    # 5. Sauvegarde du modèle entraîné
    torch.save(detector.model.state_dict(), CONFIG["MODEL_PATH"])
    print(f"Modèle entraîné sauvegardé dans {CONFIG['MODEL_PATH']}")

    # 6. Évaluation rigoureuse des performances
    print("\n--- Évaluation des Performances du Modèle Final ---")
    # On prépare un jeu de test complet
    df_test = pd.concat([df_legit, df_attack], ignore_index=True)
    true_labels = [1] * len(df_legit) + [-1] * len(df_attack) # Les vraies étiquettes
    df_test_scaled = scaler.transform(df_test)
    test_dataset = TensorDataset(torch.FloatTensor(df_test_scaled))
    test_loader = DataLoader(test_dataset, batch_size=1)
    
    predicted_labels = detector.predict(test_loader)

    # Affichage du rapport de classification
    print(classification_report(true_labels, predicted_labels, target_names=['Anomalie', 'Signal Normal']))
    print("--------------------------------------------------")
    print("✅ Le module de détection d'anomalies est maintenant prêt pour la production.")


if __name__ == '__main__':
    run_production_cycle() 