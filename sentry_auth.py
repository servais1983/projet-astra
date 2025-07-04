import pyotp
import getpass
import time

class SentryMFA:
    """
    Simule le processus d'Authentification Forte Multi-Facteurs (MFA)
    pour les commandes critiques du projet Astra.
    """
    def __init__(self, user, secret_key, hardware_key_id):
        self.user = user
        # Clé secrète pour générer les codes TOTP (doit être partagée avec l'app d'authentification)
        self.totp_secret = secret_key
        # Identifiant unique de la clé matérielle simulée
        self.expected_hardware_key = hardware_key_id
        self.expected_password = "AstraControl$2025" # Mot de passe "en dur" pour la simulation

    def _verify_password(self):
        """Vérifie le facteur connaissance (mot de passe)."""
        print("--- Facteur 1: Connaissance ---")
        password = getpass.getpass("Entrez le mot de passe de commande : ")
        if password == self.expected_password:
            print("✅ Mot de passe correct.")
            return True
        print("❌ Accès refusé : mot de passe invalide.")
        return False

    def _verify_totp(self):
        """Vérifie le facteur possession (code TOTP)."""
        print("\n--- Facteur 2: Possession (TOTP) ---")
        totp = pyotp.TOTP(self.totp_secret)
        code = input("Entrez le code à 6 chiffres de votre application d'authentification : ")
        if totp.verify(code):
            print("✅ Code TOTP valide.")
            return True
        print("❌ Accès refusé : code TOTP invalide.")
        return False

    def _verify_hardware_key(self):
        """Simule la vérification du facteur possession (clé matérielle)."""
        print("\n--- Facteur 3: Possession (Clé Matérielle) ---")
        input("Veuillez insérer votre clé de sécurité et appuyer sur Entrée...")
        # Simulation d'une lecture de l'ID de la clé
        print("Lecture de la clé matérielle...")
        time.sleep(1)
        simulated_key_id = "YUBI-A58B-9C3D" # ID de la clé simulée
        
        if simulated_key_id == self.expected_hardware_key:
            print(f"✅ Clé matérielle '{simulated_key_id}' reconnue.")
            return True
        print("❌ Accès refusé : clé matérielle non reconnue.")
        return False

    def authorize_critical_command(self):
        """
        Lance le processus complet d'autorisation.
        Les 3 facteurs doivent être validés pour réussir.
        """
        print(f"\nTentative d'autorisation pour l'utilisateur '{self.user}'...")
        if self._verify_password() and self._verify_totp() and self._verify_hardware_key():
            print("\n=============================================")
            print("🔓 AUTHORISATION ACCORDÉE. Commande critique envoyée au satellite.")
            print("=============================================")
            return True
        else:
            print("\n=============================================")
            print("🔒 AUTHORISATION REFUSÉE. Tentative de commande bloquée par ASTRA SENTRY.")
            print("=============================================")
            return False

def generate_qr_code_for_setup(secret):
    """Génère une URL que vous pouvez transformer en QR Code pour votre app (Google Auth, etc.)"""
    uri = pyotp.totp.TOTP(secret).provisioning_uri(name='control@projet-astra.space', issuer_name='ProjetAstraSentry')
    print("\n--- Pour la configuration de votre application d'authentification ---")
    print("Copiez cette URL dans un générateur de QR Code en ligne :")
    print(uri)
    print("-----------------------------------------------------------------")


if __name__ == "__main__":
    # Clé secrète qui serait normalement stockée de manière sécurisée et unique par utilisateur
    # Générée une seule fois pour la configuration
    user_secret_key = pyotp.random_base32()
    
    # Affiche l'URL de configuration (à faire une seule fois par utilisateur)
    generate_qr_code_for_setup(user_secret_key)

    # Initialise le module d'authentification pour un utilisateur spécifique
    auth_module = SentryMFA(
        user="Operator-01",
        secret_key=user_secret_key,
        hardware_key_id="YUBI-A58B-9C3D"
    )

    # Lance une simulation d'autorisation
    auth_module.authorize_critical_command() 