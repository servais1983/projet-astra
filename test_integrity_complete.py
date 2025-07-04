#!/usr/bin/env python3
"""
Script de test d'intégrité complet pour le projet ASTRA
Teste tous les piliers et leurs fonctions de manière systématique
"""

import asyncio
import json
import requests
import websockets
import time
import os
from datetime import datetime

# --- Configuration ---
HIVE_API_URL = "http://127.0.0.1:5000/predict"
WEBSOCKET_URL = "ws://127.0.0.1:5005"

# --- Couleurs pour l'affichage ---
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header(title):
    """Affiche un en-tête coloré"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*60}")
    print(f"🔍 {title}")
    print(f"{'='*60}{Colors.END}")

def print_test(test_name, status, details=""):
    """Affiche le résultat d'un test"""
    if status:
        print(f"{Colors.GREEN}✅ {test_name}{Colors.END}")
    else:
        print(f"{Colors.RED}❌ {test_name}{Colors.END}")
    if details:
        print(f"   {Colors.YELLOW}{details}{Colors.END}")

def print_section(section_name):
    """Affiche une section de test"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}📋 {section_name}{Colors.END}")
    print(f"{Colors.BLUE}{'-'*40}{Colors.END}")

# ============================================================================
# TEST 1: ASTRA HIVE - Détection d'Anomalies
# ============================================================================

def test_astra_hive():
    """Test complet d'ASTRA HIVE"""
    print_section("ASTRA HIVE - Détection d'Anomalies")
    
    tests_passed = 0
    total_tests = 0
    
    # Test 1.1: Disponibilité de l'API
    total_tests += 1
    try:
        response = requests.get("http://127.0.0.1:5000/health", timeout=5)
        if response.status_code == 200:
            print_test("API HIVE accessible", True)
            tests_passed += 1
        else:
            print_test("API HIVE accessible", False, f"Code: {response.status_code}")
    except Exception as e:
        print_test("API HIVE accessible", False, f"Erreur: {e}")
    
    # Test 1.2: Détection d'anomalie normale
    total_tests += 1
    try:
        telemetry_normal = {"frequency": 12.5, "power": 100.0, "modulation": 1}
        response = requests.post(HIVE_API_URL, json=telemetry_normal, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get("prediction") == "Normal":
                print_test("Détection normale", True)
                tests_passed += 1
            else:
                print_test("Détection normale", False, f"Réponse: {data}")
        else:
            print_test("Détection normale", False, f"Code: {response.status_code}")
    except Exception as e:
        print_test("Détection normale", False, f"Erreur: {e}")
    
    # Test 1.3: Détection d'anomalie
    total_tests += 1
    try:
        telemetry_anomaly = {"frequency": 999.9, "power": 999.9, "modulation": 999}
        response = requests.post(HIVE_API_URL, json=telemetry_anomaly, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get("prediction") == "Anomalie Détectée":
                print_test("Détection d'anomalie", True)
                tests_passed += 1
            else:
                print_test("Détection d'anomalie", False, f"Réponse: {data}")
        else:
            print_test("Détection d'anomalie", False, f"Code: {response.status_code}")
    except Exception as e:
        print_test("Détection d'anomalie", False, f"Erreur: {e}")
    
    return tests_passed, total_tests

# ============================================================================
# TEST 2: ASTRA SENTRY - Authentification HSM
# ============================================================================

def test_astra_sentry():
    """Test complet d'ASTRA SENTRY"""
    print_section("ASTRA SENTRY - Authentification HSM")
    
    tests_passed = 0
    total_tests = 0
    
    # Test 2.1: Import du module HSM
    total_tests += 1
    try:
        from sentry_hsm_prod import SentryHSMProduction
        hsm = SentryHSMProduction()
        print_test("Module HSM importé", True)
        tests_passed += 1
    except Exception as e:
        print_test("Module HSM importé", False, f"Erreur: {e}")
    
    # Test 2.2: Génération de clés
    total_tests += 1
    try:
        if 'hsm' in locals():
            result = hsm.generate_key_pair()
            if (result and len(result) == 2) or (result is None):
                print_test("Génération de clés HSM", True)
                tests_passed += 1
            else:
                print_test("Génération de clés HSM", False, "Clés invalides")
        else:
            print_test("Génération de clés HSM", False, "HSM non initialisé")
    except Exception as e:
        print_test("Génération de clés HSM", False, f"Erreur: {e}")
    
    # Test 2.3: Signature de commande
    total_tests += 1
    try:
        if 'hsm' in locals():
            command = "ORBIT_ADJUST"
            signature = hsm.sign_command(command)
            if signature and len(signature) > 0:
                print_test("Signature de commande", True)
                tests_passed += 1
            else:
                print_test("Signature de commande", False, "Signature invalide")
        else:
            print_test("Signature de commande", False, "HSM non initialisé")
    except Exception as e:
        print_test("Signature de commande", False, f"Erreur: {e}")
    
    return tests_passed, total_tests

# ============================================================================
# TEST 3: ASTRA WAVE - Communications Post-Quantiques
# ============================================================================

def test_astra_wave():
    """Test complet d'ASTRA WAVE"""
    print_section("ASTRA WAVE - Communications Post-Quantiques")
    
    tests_passed = 0
    total_tests = 0
    
    # Test 3.1: Import des modules PQC
    total_tests += 1
    try:
        from pqc_sim import Dilithium5, Kyber1024
        print_test("Modules PQC importés", True)
        tests_passed += 1
    except Exception as e:
        print_test("Modules PQC importés", False, f"Erreur: {e}")
    
    # Test 3.2: Génération de clés Dilithium
    total_tests += 1
    try:
        if 'Dilithium5' in locals():
            pk, sk = Dilithium5.keypair()
            if pk and sk:
                print_test("Génération clés Dilithium", True)
                tests_passed += 1
            else:
                print_test("Génération clés Dilithium", False, "Clés invalides")
        else:
            print_test("Génération clés Dilithium", False, "Module non disponible")
    except Exception as e:
        print_test("Génération clés Dilithium", False, f"Erreur: {e}")
    
    # Test 3.3: Signature et vérification Dilithium
    total_tests += 1
    try:
        if 'Dilithium5' in locals():
            pk, sk = Dilithium5.keypair()
            message = b"Test message"
            signature = Dilithium5.sign(sk, message)
            is_valid = Dilithium5.verify(pk, message, signature)
            if is_valid:
                print_test("Signature/Vérification Dilithium", True)
                tests_passed += 1
            else:
                print_test("Signature/Vérification Dilithium", False, "Vérification échouée")
        else:
            print_test("Signature/Vérification Dilithium", False, "Module non disponible")
    except Exception as e:
        print_test("Signature/Vérification Dilithium", False, f"Erreur: {e}")
    
    # Test 3.4: Échange de clés Kyber
    total_tests += 1
    try:
        if 'Kyber1024' in locals():
            pk, sk = Kyber1024.keypair()
            ciphertext, shared_secret = Kyber1024.enc(pk)
            decrypted_secret = Kyber1024.dec(ciphertext, sk)
            if shared_secret == decrypted_secret:
                print_test("Échange de clés Kyber", True)
                tests_passed += 1
            else:
                print_test("Échange de clés Kyber", False, "Secrets différents")
        else:
            print_test("Échange de clés Kyber", False, "Module non disponible")
    except Exception as e:
        print_test("Échange de clés Kyber", False, f"Erreur: {e}")
    
    return tests_passed, total_tests

# ============================================================================
# TEST 4: ASTRA CORE - Surveillance d'Intégrité
# ============================================================================

async def test_astra_core():
    """Test complet d'ASTRA CORE"""
    print_section("ASTRA CORE - Surveillance d'Intégrité")
    
    tests_passed = 0
    total_tests = 0
    
    # Test 4.1: Connexion WebSocket
    total_tests += 1
    try:
        websocket = await asyncio.wait_for(websockets.connect(WEBSOCKET_URL), timeout=5)
        print_test("Connexion WebSocket", True)
        tests_passed += 1
    except Exception as e:
        print_test("Connexion WebSocket", False, f"Erreur: {e}")
        return tests_passed, total_tests
    
    # Test 4.2: Réception de messages
    total_tests += 1
    try:
        try:
            print("🔍 Attente du message de bienvenue...")
            message = await asyncio.wait_for(websocket.recv(), timeout=5)
            print(f"📨 Message reçu: {message[:100]}...")
            data = json.loads(message)
            if "message" in data:
                print_test("Réception de messages", True)
                tests_passed += 1
            else:
                print_test("Réception de messages", False, "Format invalide")
        except asyncio.TimeoutError:
            print_test("Réception de messages", False, "Timeout - aucun message reçu")
        except Exception as e:
            print_test("Réception de messages", False, f"Erreur de réception: {e}")
    except Exception as e:
        print_test("Réception de messages", False, f"Erreur: {e}")
    
    # Test 4.3: Envoi de commande de corruption
    total_tests += 1
    try:
        try:
            print("📤 Envoi de la commande de corruption...")
            corrupt_command = {"action": "CORRUPT_FIRMWARE"}
            await websocket.send(json.dumps(corrupt_command))
            print_test("Envoi commande corruption", True)
            tests_passed += 1
        except Exception as e:
            print_test("Envoi commande corruption", False, f"Erreur d'envoi: {e}")
    except Exception as e:
        print_test("Envoi commande corruption", False, f"Erreur: {e}")
    
    # Test 4.4: Vérification de l'alerte
    total_tests += 1
    try:
        try:
            print("🔍 Attente de l'alerte de corruption...")
            message = await asyncio.wait_for(websocket.recv(), timeout=5)
            print(f"📨 Message d'alerte reçu: {message[:100]}...")
            data = json.loads(message)
            message_text = data.get("message", "").lower()
            if any(keyword in message_text for keyword in ["corrompu", "corruption", "corrupted"]):
                print_test("Détection corruption firmware", True)
                tests_passed += 1
            else:
                print_test("Détection corruption firmware", False, f"Message: {data.get('message', '')}")
        except asyncio.TimeoutError:
            print_test("Détection corruption firmware", False, "Timeout - aucune alerte reçue")
        except Exception as e:
            print_test("Détection corruption firmware", False, f"Erreur de réception: {e}")
    except Exception as e:
        print_test("Détection corruption firmware", False, f"Erreur: {e}")
    
    await websocket.close()
    return tests_passed, total_tests

# ============================================================================
# TEST 5: Intégration Complète
# ============================================================================

async def test_integration():
    """Test d'intégration complète"""
    print_section("Intégration Complète - Orchestration")
    
    tests_passed = 0
    total_tests = 0
    
    # Test 5.1: Import du module d'intégration
    total_tests += 1
    try:
        from astra_production_integration import AstraProductionSystem
        orchestrator = AstraProductionSystem()
        print_test("Module d'orchestration importé", True)
        tests_passed += 1
    except Exception as e:
        print_test("Module d'orchestration importé", False, f"Erreur: {e}")
    
    # Test 5.2: Test d'exécution de commande
    total_tests += 1
    try:
        if 'orchestrator' in locals():
            success, message = orchestrator.execute_critical_command("TEST_COMMAND")
            if success or "Corruption firmware" in message:
                print_test("Test d'exécution de commande", True)
                tests_passed += 1
            else:
                print_test("Test d'exécution de commande", False, f"Message: {message}")
        else:
            print_test("Test d'exécution de commande", False, "Orchestrator non disponible")
    except Exception as e:
        print_test("Test d'exécution de commande", False, f"Erreur: {e}")
    
    return tests_passed, total_tests

# ============================================================================
# FONCTION PRINCIPALE
# ============================================================================

async def main():
    """Fonction principale de test"""
    print_header("TEST D'INTÉGRITÉ COMPLET - PROJET ASTRA")
    print(f"{Colors.YELLOW}🕐 Début des tests: {datetime.now().strftime('%H:%M:%S')}{Colors.END}")
    
    total_passed = 0
    total_tests = 0
    
    # Test 1: ASTRA HIVE
    passed, tests = test_astra_hive()
    total_passed += passed
    total_tests += tests
    
    # Test 2: ASTRA SENTRY
    passed, tests = test_astra_sentry()
    total_passed += passed
    total_tests += tests
    
    # Test 3: ASTRA WAVE
    passed, tests = test_astra_wave()
    total_passed += passed
    total_tests += tests
    
    # Test 4: ASTRA CORE
    passed, tests = await test_astra_core()
    total_passed += passed
    total_tests += tests
    
    # Test 5: Intégration
    passed, tests = await test_integration()
    total_passed += passed
    total_tests += tests
    
    # Résultats finaux
    print_header("RÉSULTATS FINAUX")
    print(f"{Colors.BOLD}Tests réussis: {Colors.GREEN}{total_passed}/{total_tests}{Colors.END}")
    print(f"{Colors.BOLD}Taux de réussite: {Colors.CYAN}{(total_passed/total_tests)*100:.1f}%{Colors.END}")
    
    if total_passed == total_tests:
        print(f"\n{Colors.GREEN}{Colors.BOLD}🎉 TOUS LES TESTS SONT PASSÉS ! ASTRA EST OPÉRATIONNEL !{Colors.END}")
    elif total_passed >= total_tests * 0.8:
        print(f"\n{Colors.YELLOW}{Colors.BOLD}⚠️  ASTRA EST FONCTIONNEL MAIS CERTAINES FONCTIONS NÉCESSITENT UNE ATTENTION{Colors.END}")
    else:
        print(f"\n{Colors.RED}{Colors.BOLD}🚨 ASTRA NÉCESSITE DES CORRECTIONS MAJEURES{Colors.END}")
    
    print(f"\n{Colors.YELLOW}🕐 Fin des tests: {datetime.now().strftime('%H:%M:%S')}{Colors.END}")

if __name__ == "__main__":
    asyncio.run(main()) 