import os
import hashlib

# Registre temporaire pour la correspondance pk/sk (simulation)
DILITHIUM_SK_REGISTRY = {}

# Compteur pour s'assurer que chaque clé publique est unique
KEY_COUNTER = 0

class Kyber1024:
    @staticmethod
    def keypair():
        sk = os.urandom(32)
        pk = hashlib.sha256(sk).digest()
        return pk, sk
    @staticmethod
    def enc(pk):
        # Générer un secret partagé basé sur la clé publique
        shared_secret = hashlib.sha256(pk).digest()
        ciphertext = os.urandom(32)  # Simulation du chiffrement
        return ciphertext, shared_secret
    @staticmethod
    def dec(ciphertext, sk):
        # Récupérer le secret partagé basé sur la clé privée
        pk = hashlib.sha256(sk).digest()
        shared_secret = hashlib.sha256(pk).digest()
        return shared_secret

class Dilithium5:
    @staticmethod
    def keypair():
        global KEY_COUNTER
        sk = os.urandom(32)
        # Ajouter un compteur pour garantir l'unicité
        pk = hashlib.sha256(sk + str(KEY_COUNTER).encode()).digest()
        KEY_COUNTER += 1
        DILITHIUM_SK_REGISTRY[pk] = sk
        return pk, sk
    @staticmethod
    def sign(sk, msg):
        return hashlib.sha256(sk + msg).digest()
    @staticmethod
    def verify(pk, msg, sig):
        """
        Vérifie une signature avec une logique stricte.
        La clé publique doit correspondre à la clé privée utilisée pour signer.
        """
        # Vérifier que la clé publique existe dans le registre
        sk = DILITHIUM_SK_REGISTRY.get(pk)
        if sk is None:
            return False
        
        # Calculer la signature attendue avec la clé privée correspondante
        expected_sig = hashlib.sha256(sk + msg).digest()
        
        # Vérifier que les signatures correspondent exactement
        return sig == expected_sig 