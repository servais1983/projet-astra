# main_advanced.py
import torch
from torch.utils.data import DataLoader, TensorDataset
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
import os

from advanced_detector import AdvancedAnomalyDetector

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

def run_advanced_simulation():
    """
    Orchestre l'entraînement et le test du détecteur avancé.
    """
    print("\n--- DÉBUT DE LA SIMULATION ASTRA HIVE (Phase 2 : Modèle Avancé) ---")
    
    # 1. Charger les données
    legit_path, attack_path = setup_dummy_data()
    df_legit = pd.read_csv(legit_path)
    df_attack = pd.read_csv(attack_path)
    
    # 2. Normaliser les données (essentiel pour les autoencodeurs)
    scaler = MinMaxScaler()
    df_legit_scaled = scaler.fit_transform(df_legit)
    # On utilise le même scaler pour les données d'attaque pour être cohérent
    df_attack_scaled = scaler.transform(df_attack)
    
    # 3. Préparer les DataLoader PyTorch
    # Le DataLoader d'entraînement ne contient QUE des données légitimes
    train_dataset = TensorDataset(torch.FloatTensor(df_legit_scaled))
    train_loader = DataLoader(train_dataset, batch_size=2, shuffle=True)
    
    # Le DataLoader de test contient un mélange
    test_data = pd.concat([df_legit, df_attack], ignore_index=True)
    test_data_scaled = scaler.transform(test_data)
    test_dataset = TensorDataset(torch.FloatTensor(test_data_scaled))
    test_loader = DataLoader(test_dataset, batch_size=1)
    
    # 4. Initialiser et entraîner le détecteur
    input_dim = df_legit.shape[1]
    detector = AdvancedAnomalyDetector(input_dim=input_dim)
    detector.train(train_loader, epochs=50) # On augmente les époques pour une meilleure convergence
    
    # 5. Prédire sur l'ensemble de test
    predictions = detector.predict(test_loader)
    
    print("\n--- RÉSULTATS DE LA PRÉDICTION (Modèle Avancé) ---")
    for i, p in enumerate(predictions):
        original_signal = test_data.iloc[i].to_dict()
        result = "Anomalie Détectée" if p == -1 else "Signal Normal"
        print(f"Signal #{i+1} {original_signal}: {result}")
    print("-------------------------------------------------")


if __name__ == '__main__':
    run_advanced_simulation() 