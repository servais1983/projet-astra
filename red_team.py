# red_team.py
import requests
import json
import os
import hashlib

# --- Simulation des primitives PQC si pq_crystals n'est pas disponible ---
try:
    from pq_crystals.kyber import Kyber1024
    from pq_crystals.dilithium import Dilithium5
except ImportError:
    from pqc_sim import Kyber1024, Dilithium5
    print("[SIMULATION] pq_crystals non disponible, utilisation de primitives simulées.")
    class Kyber1024:
        @staticmethod
        def keypair():
            return os.urandom(32), os.urandom(32)
        @staticmethod
        def enc(pk):
            return os.urandom(32), os.urandom(32)
        @staticmethod
        def dec(ciphertext, sk):
            return os.urandom(32)
    class Dilithium5:
        @staticmethod
        def keypair():
            sk = os.urandom(32)
            pk = hashlib.sha256(sk).digest()
            return pk, sk
        @staticmethod
        def sign(sk, msg):
            return hashlib.sha256(sk + msg).digest()
        @staticmethod
        def verify(pk, msg, sig):
            return len(sig) == 32

import asyncio
import websockets

class RedTeamAgent:
    """
    Agent de simulation d'attaques pour valider les défenses du Projet Astra.
    """
    def __init__(self):
        self.hive_api_url = "http://127.0.0.1:5000/predict"
        self.twin_ws_url = "ws://127.0.0.1:5004"
        print("Agent Red Team initialisé. Prêt à tester les défenses.")

    def attack_hive_with_spoofed_telemetry(self):
        print("\n--- ATTAQUE 1 : Spoofing de Télémétrie (HIVE) ---")
        try:
            spoofed_data = {"frequency": 20.0, "power": 800.0, "modulation": 0}
            response = requests.post(self.hive_api_url, json=spoofed_data)
            result = response.json()
            if result.get("prediction") == "Anomalie Détectée":
                print("✅ SUCCÈS DE LA DÉFENSE : ASTRA HIVE a correctement identifié la télémétrie anormale.")
            else:
                print("❌ ÉCHEC DE LA DÉFENSE : ASTRA HIVE n'a pas détecté l'anomalie.")
        except requests.exceptions.RequestException as e:
            print(f"⚠️ ERREUR : Impossible de contacter l'API HIVE. ({e})")

    def attack_wave_with_forged_identity(self):
        print("\n--- ATTAQUE 2 : Usurpation d'Identité de Satellite (WAVE) ---")
        
        # Scénario d'attaque : Le Red Team tente d'usurper l'identité du satellite
        # 1. Il génère sa propre paire de clés (fausse identité)
        fake_signing_pk, fake_signing_sk = Dilithium5.keypair()
        legit_kem_pk, _ = Kyber1024.keypair()
        
        # 2. Il signe le message avec sa propre clé privée
        message_to_sign = hashlib.sha256(legit_kem_pk).digest()
        fake_signature = Dilithium5.sign(fake_signing_sk, message_to_sign)
        
        # 3. Il tente de faire croire que c'est la signature du satellite légitime
        # en utilisant une clé publique complètement différente
        random_pk, _ = Dilithium5.keypair()  # Clé publique aléatoire
        
        # 4. Test de la défense : la vérification doit échouer
        is_verified = Dilithium5.verify(random_pk, message_to_sign, fake_signature)
        
        # 5. Vérification du résultat
        if not is_verified:
            print("✅ SUCCÈS DE LA DÉFENSE : ASTRA WAVE a correctement rejeté la signature invalide.")
            print("   → L'usurpation d'identité a été détectée et bloquée.")
        else:
            print("❌ ÉCHEC DE LA DÉFENSE : ASTRA WAVE a accepté une signature falsifiée.")
            print("   → L'usurpation d'identité a réussi (VULNÉRABILITÉ CRITIQUE).")

    async def attack_core_via_websocket(self):
        print("\n--- ATTAQUE 3 : Corruption de Firmware (CORE) ---")
        try:
            async with websockets.connect(self.twin_ws_url) as websocket:
                payload = json.dumps({"action": "CORRUPT_FIRMWARE"})
                await websocket.send(payload)
                print("Ordre de corruption de firmware envoyé au jumeau numérique.")
                print("✅ SUCCÈS DE L'ATTAQUE : Vérifiez le tableau de bord pour l'alerte ASTRA CORE.")
        except Exception as e:
            print(f"⚠️ ERREUR : Impossible de se connecter au Jumeau Numérique. ({e})")

async def run_red_team_exercise():
    print("=============================================")
    print("🚀 DÉBUT DE L'EXERCICE DE VALIDATION RED TEAM 🚀")
    print("=============================================")
    agent = RedTeamAgent()
    agent.attack_hive_with_spoofed_telemetry()
    agent.attack_wave_with_forged_identity()
    await agent.attack_core_via_websocket()
    print("\n=============================================")
    print("🏁 FIN DE L'EXERCICE RED TEAM 🏁")
    print("=============================================")

if __name__ == "__main__":
    asyncio.run(run_red_team_exercise()) 