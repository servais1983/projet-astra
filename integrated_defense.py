import requests
import json
from sentry_auth import SentryMFA, generate_qr_code_for_setup
import pyotp

class IntegratedDefenseController:
    """
    Orchestre la collaboration entre ASTRA SENTRY et ASTRA HIVE
    pour une prise de décision de sécurité contextuelle.
    """
    def __init__(self, user, secret_key, hardware_key_id):
        self.sentry_module = SentryMFA(user, secret_key, hardware_key_id)
        self.hive_api_url = "http://127.0.0.1:5000/predict"

    def _check_network_status_with_hive(self):
        """
        Interroge l'API ASTRA HIVE pour vérifier l'état du réseau.
        C'est notre corrélation multi-domaines.
        """
        print("\n--- Facteur 4: Corrélation de l'Intelligence (HIVE) ---")
        try:
            # Simulation d'une télémétrie réseau suspecte
            suspicious_network_telemetry = {
                "frequency": 19.0, "power": 600.0, "modulation": 0
            }
            response = requests.post(self.hive_api_url, json=suspicious_network_telemetry)
            response.raise_for_status()
            
            data = response.json()
            print(f"Analyse HIVE reçue: {data}")
            
            if data.get("prediction") == "Anomalie Détectée":
                print("🚨 ALERTE HIVE : Comportement réseau anormal détecté sur la constellation.")
                return False
            
            print("✅ HIVE confirme un état réseau nominal.")
            return True
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Impossible de contacter ASTRA HIVE : {e}")
            # Principe de précaution : en cas de doute, on refuse la commande
            return False

    def attempt_critical_command(self):
        """
        Tente une commande critique en validant d'abord l'opérateur,
        puis en vérifiant le contexte de sécurité avec HIVE.
        """
        print("\n>>> INITIATION D'UNE COMMANDE CRITIQUE <<<")
        # 1. Authentification forte de l'opérateur
        is_operator_authorized = self.sentry_module.authorize_critical_command()
        
        if not is_operator_authorized:
            print(">>> ECHEC DE LA COMMANDE : Opérateur non authentifié.")
            return

        # 2. Vérification du contexte de sécurité avec HIVE
        is_network_safe = self._check_network_status_with_hive()
        
        if not is_network_safe:
            print("\n=============================================")
            print("🔒 COMMANDE REFUSÉE PAR POLITIQUE DE SÉCURITÉ INTÉGRÉE.")
            print("Raison: L'opérateur est valide, mais HIVE signale une menace potentielle.")
            print("=============================================")
            return

        print("\n=============================================")
        print("✅ COMMANDE APPROUVÉE ET ENVOYÉE.")
        print("Opérateur et contexte réseau validés.")
        print("=============================================")


if __name__ == "__main__":
    # La configuration reste la même que pour sentry_auth
    user_secret_key = pyotp.random_base32()
    generate_qr_code_for_setup(user_secret_key)

    # Initialisation du contrôleur de défense intégré
    controller = IntegratedDefenseController(
        user="Operator-01",
        secret_key=user_secret_key,
        hardware_key_id="YUBI-A58B-9C3D"
    )

    # Lancement du scénario
    controller.attempt_critical_command() 