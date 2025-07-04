# wave_hybrid_prod.py
import hashlib
import os

# --- Simulation des primitives PQC si pq_crystals n'est pas disponible ---
try:
    from pq_crystals.kyber import Kyber1024
    from pq_crystals.dilithium import Dilithium5
    PQC_AVAILABLE = True
except ImportError:
    PQC_AVAILABLE = False
    print("[SIMULATION] pq_crystals non disponible, utilisation de primitives simulées.")
    from pqc_sim import Kyber1024, Dilithium5

class AuthenticatedSatellite:
    """
    Représente le satellite, qui doit prouver son identité 
    avant d'établir un canal de communication.
    """
    def __init__(self, name="Astra-Sat-042-Prod"):
        self.name = name
        print(f"Satellite de production '{self.name}' initialisé.")
        
        # 1. Génération de la paire de clés de signature (long terme)
        print(f"[{self.name}] Génération de l'identité PQC (Dilithium)...")
        self.signing_pk, self.signing_sk = Dilithium5.keypair()
        
        # 2. Génération de la paire de clés d'encapsulation (court terme)
        self.kem_pk, self.kem_sk = Kyber1024.keypair()

    def get_signed_public_keys(self):
        print(f"[{self.name}] Signature de la clé publique Kyber avec l'identité Dilithium...")
        message_to_sign = hashlib.sha256(self.kem_pk).digest()
        signature = Dilithium5.sign(self.signing_sk, message_to_sign)
        print(f"[{self.name}] Signature générée.")
        return self.signing_pk, self.kem_pk, signature

    def decrypt_hybrid_secret(self, ciphertext):
        return Kyber1024.dec(ciphertext, self.kem_sk)

class SecureGroundStation:
    def __init__(self, name="GroundStation-EU-Prod"):
        self.name = name
        print(f"Station au sol de production '{self.name}' initialisée.")

    def establish_hybrid_channel(self, signing_pk, kem_pk, signature):
        print(f"\n[{self.name}] Réception des clés publiques et de la signature du satellite.")
        print(f"[{self.name}] Vérification de la signature avec la clé publique Dilithium...")
        message_to_verify = hashlib.sha256(kem_pk).digest()
        if not Dilithium5.verify(signing_pk, message_to_verify, signature):
            print(f"[{self.name}] ❌ ALERTE SÉCURITÉ : SIGNATURE INVALIDE ! Communication annulée.")
            return None
        print(f"[{self.name}] ✅ Identité du satellite vérifiée. La clé publique Kyber est authentique.")
        print(f"[{self.name}] Création d'un secret hybride...")
        ciphertext, pqc_secret = Kyber1024.enc(kem_pk)
        classic_secret = os.urandom(32)
        final_hybrid_secret = hashlib.sha256(pqc_secret + classic_secret).digest()
        print(f"[{self.name}] ✅ Secret hybride généré.")
        return ciphertext, final_hybrid_secret, classic_secret

def run_hybrid_production_scenario():
    print("\n--- SCÉNARIO DE PRODUCTION ASTRA WAVE : CANAL AUTHENTIFIÉ ET HYBRIDE ---")
    satellite = AuthenticatedSatellite()
    ground_station = SecureGroundStation()
    signing_pk, kem_pk, signature = satellite.get_signed_public_keys()
    result = ground_station.establish_hybrid_channel(signing_pk, kem_pk, signature)
    if result:
        ciphertext, hybrid_secret_at_ground, classic_secret = result
        pqc_secret_at_satellite = satellite.decrypt_hybrid_secret(ciphertext)
        # Le satellite doit maintenant recréer le même secret hybride
        final_hybrid_secret_sat = hashlib.sha256(pqc_secret_at_satellite + classic_secret).digest()
        print("\n--- VÉRIFICATION FINALE ---")
        print(f"Secret hybride calculé par la station au sol : {hybrid_secret_at_ground.hex()}")
        print(f"Secret hybride calculé par le satellite      : {final_hybrid_secret_sat.hex()}")
        if hybrid_secret_at_ground == final_hybrid_secret_sat:
            print("\n=============================================")
            print("✅ SUCCÈS : Canal authentifié et hybride établi.")
            print("=============================================")
        else:
            print("\n=============================================")
            print("❌ ÉCHEC : Les secrets hybrides ne correspondent pas !")
            print("=============================================")

if __name__ == "__main__":
    run_hybrid_production_scenario() 