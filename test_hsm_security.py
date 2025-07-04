# test_hsm_security.py
import os
import json
from sentry_hsm_prod import SentryHSMProduction

def test_hsm_security():
    """Teste la robustesse de notre implémentation HSM contre différents vecteurs d'attaque."""
    print("\n=== TESTS DE SÉCURITÉ HSM ASTRA SENTRY ===")
    
    hsm_service = SentryHSMProduction()
    
    # Test 1 : Tentative de signature avec une clé inexistante
    print("\n🔒 Test 1 : Tentative de signature avec clé inexistante")
    fake_signature = hsm_service.sign_command("CMD:TEST", "FAKE-KEY")
    if fake_signature is None:
        print("✅ SÉCURITÉ : Rejet correct d'une clé inexistante")
    else:
        print("❌ VULNÉRABILITÉ : Signature acceptée avec une clé inexistante")
    
    # Test 2 : Tentative de vérification avec une signature modifiée
    print("\n🔒 Test 2 : Tentative de vérification avec signature corrompue")
    command = "CMD:SET_ORBIT;SAT:ASTRA-042;PARAMS:400km,90deg"
    valid_signature = hsm_service.sign_command(command)
    
    if valid_signature:
        # Modification de la signature
        corrupted_signature = bytearray(valid_signature)
        if len(corrupted_signature) > 0:
            corrupted_signature[0] ^= 1  # Modification d'un bit
        
        is_valid = hsm_service.verify_command(command, bytes(corrupted_signature))
        if not is_valid:
            print("✅ SÉCURITÉ : Détection correcte d'une signature corrompue")
        else:
            print("❌ VULNÉRABILITÉ : Signature corrompue acceptée")
    
    # Test 3 : Tentative de vérification avec une commande modifiée
    print("\n🔒 Test 3 : Tentative de vérification avec commande modifiée")
    original_command = "CMD:SET_ORBIT;SAT:ASTRA-042;PARAMS:400km,90deg"
    modified_command = "CMD:SET_ORBIT;SAT:ASTRA-042;PARAMS:800km,90deg"  # Altitude modifiée
    
    if valid_signature:
        is_valid = hsm_service.verify_command(modified_command, valid_signature)
        if not is_valid:
            print("✅ SÉCURITÉ : Détection correcte d'une commande modifiée")
        else:
            print("❌ VULNÉRABILITÉ : Commande modifiée acceptée")
    
    # Test 4 : Tentative d'accès direct aux clés privées
    print("\n🔒 Test 4 : Tentative d'accès direct aux clés privées")
    try:
        with open("astra_hsm_simulation.json", 'r') as f:
            hsm_data = json.load(f)
            private_key = hsm_data["keys"]["Operator-01-Key"]["private_key"]
            print("⚠️  ATTENTION : Les clés sont stockées en clair dans le fichier JSON")
            print("   En production, utiliser un vrai HSM avec chiffrement matériel")
    except Exception as e:
        print(f"❌ ERREUR : Impossible d'accéder aux données HSM : {e}")
    
    # Test 5 : Validation de l'intégrité cryptographique
    print("\n🔒 Test 5 : Validation de l'intégrité cryptographique")
    test_command = "CMD:EMERGENCY_SHUTDOWN;SAT:ASTRA-042"
    signature = hsm_service.sign_command(test_command)
    
    if signature:
        is_valid = hsm_service.verify_command(test_command, signature)
        if is_valid:
            print("✅ SÉCURITÉ : Intégrité cryptographique validée")
        else:
            print("❌ VULNÉRABILITÉ : Échec de la validation cryptographique")
    
    print("\n=== RÉSUMÉ DES TESTS DE SÉCURITÉ ===")
    print("✅ HSM simulé opérationnel pour les tests de développement")
    print("⚠️  Pour la production : utiliser un vrai HSM (Thales, Utimaco, etc.)")
    print("⚠️  Implémenter le chiffrement des clés stockées")
    print("⚠️  Ajouter des contrôles d'accès physiques et logiques")

if __name__ == "__main__":
    test_hsm_security() 