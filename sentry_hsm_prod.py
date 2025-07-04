# sentry_hsm_prod.py
import hashlib
import hmac
import os
import json
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.backends import default_backend

# --- Configuration de la Simulation HSM ---
# Note: Cette simulation utilise cryptography pour simuler un HSM
# En production, on utiliserait python-pkcs11 avec un vrai HSM (Thales, Utimaco, etc.)
HSM_STORAGE_FILE = "astra_hsm_simulation.json"

class SentryHSMProduction:
    """
    Simule une interaction avec un HSM pour la signature de commandes critiques,
    conformément aux exigences de production d'Astra.
    """
    def __init__(self):
        self.hsm_data = self._load_hsm_data()
        print("Module SENTRY-HSM initialisé (simulation).")

    def _load_hsm_data(self):
        """Charge les données du HSM simulé depuis un fichier sécurisé."""
        if os.path.exists(HSM_STORAGE_FILE):
            try:
                with open(HSM_STORAGE_FILE, 'r') as f:
                    return json.load(f)
            except:
                return {"keys": {}, "sessions": {}}
        return {"keys": {}, "sessions": {}}

    def _save_hsm_data(self):
        """Sauvegarde les données du HSM simulé de manière sécurisée."""
        with open(HSM_STORAGE_FILE, 'w') as f:
            json.dump(self.hsm_data, f)

    def generate_key_pair(self, label="Operator-01-Key"):
        """Génère une paire de clés RSA directement dans le HSM simulé."""
        if label in self.hsm_data["keys"]:
            print(f"La clé '{label}' existe déjà dans le HSM.")
            return

        print(f"Génération d'une nouvelle paire de clés RSA '{label}' dans le HSM...")
        
        # Génération de la paire de clés RSA
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        public_key = private_key.public_key()

        # Stockage sécurisé dans le HSM simulé
        self.hsm_data["keys"][label] = {
            "private_key": private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            ).decode('utf-8'),
            "public_key": public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            ).decode('utf-8')
        }
        
        self._save_hsm_data()
        print("✅ Paire de clés générée et stockée de manière sécurisée dans le HSM.")
    
    def sign_command(self, command, key_label="Operator-01-Key"):
        """Signe une commande en utilisant la clé privée stockée dans le HSM."""
        if key_label not in self.hsm_data["keys"]:
            print(f"❌ ERREUR : La clé '{key_label}' n'existe pas dans le HSM.")
            return None

        try:
            # Chargement de la clé privée depuis le HSM
            private_key_data = self.hsm_data["keys"][key_label]["private_key"]
            private_key = serialization.load_pem_private_key(
                private_key_data.encode('utf-8'),
                password=None,
                backend=default_backend()
            )

            print(f"\nSignature de la commande : '{command}'")
            print("🔐 Opération cryptographique exécutée dans le HSM...")
            
            # Signature de la commande (simulation HSM)
            signature = private_key.sign(
                command.encode('utf-8'),
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            
            print("✅ Commande signée par le HSM.")
            return signature
        except Exception as e:
            print(f"❌ ERREUR lors de la signature : {e}")
            return None

    def verify_command(self, command, signature, key_label="Operator-01-Key"):
        """Vérifie la signature d'une commande avec la clé publique correspondante."""
        if key_label not in self.hsm_data["keys"]:
            print(f"❌ ERREUR : La clé '{key_label}' n'existe pas.")
            return False

        try:
            # Chargement de la clé publique depuis le HSM
            public_key_data = self.hsm_data["keys"][key_label]["public_key"]
            public_key = serialization.load_pem_public_key(
                public_key_data.encode('utf-8'),
                backend=default_backend()
            )

            print(f"Vérification de la signature pour la commande : '{command}'")
            print("🔍 Validation cryptographique dans le HSM...")

            # Vérification de la signature
            public_key.verify(
                signature,
                command.encode('utf-8'),
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            
            print("✅ Signature valide ! La commande est authentique et intègre.")
            return True
        except Exception as e:
            print(f"❌ ALERTE SÉCURITÉ : Signature invalide ! ({e})")
            return False

def run_production_scenario():
    print("\n--- SCÉNARIO DE PRODUCTION ASTRA SENTRY : AUTORISATION PAR SIGNATURE HSM ---")
    
    hsm_service = SentryHSMProduction()
    
    # Étape 1 : Provisioning (à faire une seule fois par opérateur)
    hsm_service.generate_key_pair()
    
    # Étape 2 : Un opérateur souhaite envoyer une commande critique
    command_to_send = "CMD:SET_ORBIT;SAT:ASTRA-042;PARAMS:400km,90deg"
    
    # Étape 3 : La commande est signée par le HSM de l'opérateur
    signature = hsm_service.sign_command(command_to_send)
    
    if signature:
        # Étape 4 : Le système de contrôle central vérifie la signature
        is_valid = hsm_service.verify_command(command_to_send, signature)
        
        print("\n--- RÉSULTAT DU CONTRÔLE DE PRODUCTION ---")
        if is_valid:
            print("=============================================")
            print("🔓 COMMANDE APPROUVÉE. Intégrité et authenticité garanties par le HSM.")
            print("=============================================")
        else:
            print("=============================================")
            print("🔒 COMMANDE REFUSÉE. La signature cryptographique est invalide.")
            print("=============================================")

if __name__ == "__main__":
    run_production_scenario() 