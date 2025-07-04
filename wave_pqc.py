from pq_crystals.kyber import Kyber1024 # Utilisation de Kyber-1024, le plus haut niveau de sécurité

class GroundStation:
    """Représente la station au sol qui initie la communication."""
    def __init__(self, name="GroundStation-EU-1"):
        self.name = name
        self.public_key = None
        self.private_key = None
        print(f"Station au sol '{self.name}' initialisée.")

    def generate_pqc_keys(self):
        """Génère une paire de clés post-quantiques."""
        print(f"[{self.name}] Génération de la paire de clés Kyber...")
        self.public_key, self.private_key = Kyber1024.keypair()
        print(f"[{self.name}] Clé publique générée et prête à être transmise au satellite.")

    def decrypt_secret(self, ciphertext):
        """Déchiffre le secret partagé reçu du satellite avec sa clé privée."""
        print(f"[{self.name}] Réception d'un 'ciphertext' du satellite. Tentative de déchiffrement...")
        shared_secret = Kyber1024.dec(ciphertext, self.private_key)
        print(f"[{self.name}] ✅ Déchiffrement réussi.")
        return shared_secret

class Satellite:
    """Représente le satellite en orbite."""
    def __init__(self, name="Astra-Sat-042"):
        self.name = name
        print(f"Satellite '{self.name}' initialisé.")

    def encrypt_secret_for_ground(self, public_key):
        """
        Reçoit la clé publique de la station sol, génère un secret partagé,
        et le chiffre avec cette clé.
        """
        print(f"[{self.name}] Clé publique de la station sol reçue.")
        print(f"[{self.name}] Chiffrement d'un nouveau secret partagé avec Kyber...")
        ciphertext, shared_secret = Kyber1024.enc(public_key)
        print(f"[{self.name}] ✅ Chiffrement réussi. 'Ciphertext' prêt à être envoyé.")
        return ciphertext, shared_secret

def run_secure_channel_simulation():
    """Orchestre la simulation complète de l'échange."""
    print("\n--- SIMULATION ASTRA WAVE : ÉTABLISSEMENT D'UN CANAL SÉCURISÉ PQC ---")
    
    # 1. Initialisation des entités
    ground = GroundStation()
    satellite = Satellite()
    
    # 2. La station au sol génère ses clés
    ground.generate_pqc_keys()
    
    # 3. La station envoie sa clé publique au satellite (communication non sécurisée)
    print("\n>>> Transmission de la clé publique de la Terre vers l'espace...")
    
    # 4. Le satellite reçoit la clé publique et chiffre un secret
    # C'est la partie la plus importante : le satellite crée le secret et le "verrouille"
    ciphertext_from_satellite, secret_at_satellite = satellite.encrypt_secret_for_ground(ground.public_key)

    # 5. Le satellite renvoie le "ciphertext" (qui peut être intercepté sans risque)
    print("\n<<< Transmission du 'ciphertext' de l'espace vers la Terre...")

    # 6. La station au sol déchiffre le ciphertext pour obtenir le secret
    secret_at_ground = ground.decrypt_secret(ciphertext_from_satellite)
    
    print("\n--- VÉRIFICATION FINALE DU CANAL ---")
    print(f"Secret généré par le satellite : {secret_at_satellite.hex()}")
    print(f"Secret obtenu par la station sol: {secret_at_ground.hex()}")
    
    if secret_at_satellite == secret_at_ground:
        print("\n=============================================")
        print("✅ SUCCÈS : Le canal de communication sécurisé est établi.")
        print("La station au sol et le satellite partagent maintenant le même secret.")
        print("=============================================")
    else:
        print("\n=============================================")
        print("❌ ÉCHEC : Les secrets ne correspondent pas. Le canal n'est pas sécurisé.")
        print("=============================================")


if __name__ == "__main__":
    run_secure_channel_simulation() 