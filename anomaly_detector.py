# anomaly_detector.py
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import IsolationForest # Un bon point de départ pour la détection d'anomalies

class AnomalyDetector:
    """
    Classe pour la détection d'anomalies dans les signaux satellites.
    Utilise un modèle Isolation Forest pour commencer, comme prévu dans la phase 1.
    Ce modèle est efficace pour identifier des outliers dans les données.
    """
    def __init__(self, contamination=0.01):
        """
        Initialise le détecteur.
        :param contamination: Le pourcentage attendu d'anomalies dans les données.
                              C'est un hyperparamètre clé pour notre modèle.
        """
        self.model = IsolationForest(contamination=contamination, random_state=42)
        self.is_trained = False
        print("Détecteur d'anomalies initialisé.")

    def load_data(self, legit_path, attack_path):
        """
        Charge les données légitimes et les données d'attaque.
        Dans un cas réel, ces données proviendraient de la télémétrie ASTRA HIVE.
        """
        print(f"Chargement des données depuis {legit_path} et {attack_path}...")
        df_legit = pd.read_csv(legit_path)
        df_attack = pd.read_csv(attack_path)

        # Pour notre simulation, on assigne une étiquette : 1 pour légitime, -1 pour anomalie
        df_legit['label'] = 1
        df_attack['label'] = -1

        # On combine les deux jeux de données
        df = pd.concat([df_legit, df_attack], ignore_index=True)
        print("Données chargées et combinées.")
        return df

    def train(self, data):
        """
        Entraîne le modèle sur les données fournies.
        Le modèle apprendra à distinguer les signaux normaux des anormaux.
        """
        print("Début de l'entraînement du modèle...")
        # Pour Isolation Forest, on entraîne sur les données sans les étiquettes
        features = data.drop('label', axis=1)
        self.model.fit(features)
        self.is_trained = True
        print("Entraînement terminé avec succès.")

    def predict(self, signal_data):
        """
        Prédit si un nouveau signal est une anomalie.
        :param signal_data: Un DataFrame contenant les caractéristiques du signal à analyser.
        :return: -1 si c'est une anomalie, 1 si c'est normal.
        """
        if not self.is_trained:
            raise Exception("Le modèle doit être entraîné avant de pouvoir faire des prédictions.")
        
        print(f"Prédiction sur {len(signal_data)} nouveaux signaux...")
        prediction = self.model.predict(signal_data)
        return prediction 