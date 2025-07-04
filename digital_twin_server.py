# digital_twin_server.py (version finale)
import asyncio
import websockets
import json
import requests
import os

# --- Simulation des primitives PQC si pq_crystals n'est pas disponible ---
try:
    from pq_crystals.dilithium import Dilithium5
    from pq_crystals.kyber import Kyber1024
except ImportError:
    from pqc_sim import Dilithium5, Kyber1024

# --- Configuration ---
HIVE_API_URL = "http://127.0.0.1:5000/predict"
CONNECTED_CLIENTS = set()

# --- Simulation de l'état du satellite ---
SATELLITE_SIGNING_PK, SATELLITE_SIGNING_SK = Dilithium5.keypair()
SATELLITE_STATE = {
    "firmware_integrity": "OK",
    "last_heartbeat_status": "UNKNOWN"
}

async def send_log(message, level='info', pillar_status=None):
    """Envoie un message de log à tous les tableaux de bord connectés."""
    log_data = {"message": message, "level": level}
    if pillar_status:
        log_data["pillar_status"] = pillar_status
    
    print(f"📝 [SEND_LOG] Préparation envoi: {message[:50]}...")
    
    if CONNECTED_CLIENTS:
        to_remove = set()
        tasks = []
        for client in CONNECTED_CLIENTS:
            try:
                task = client.send(json.dumps(log_data))
                tasks.append(task)
                print(f"📤 [SEND_LOG] Tâche créée pour client")
            except Exception as e:
                print(f"❌ [SEND_LOG] Erreur création tâche: {e}")
                to_remove.add(client)
        
        for client in to_remove:
            CONNECTED_CLIENTS.discard(client)
            print(f"🗑️ [SEND_LOG] Client supprimé de la liste")
        
        if tasks:
            try:
                print(f"🚀 [SEND_LOG] Exécution de {len(tasks)} tâches...")
                results = await asyncio.gather(*tasks, return_exceptions=True)
                for i, result in enumerate(results):
                    if isinstance(result, Exception):
                        print(f"❌ [SEND_LOG] Tâche {i} échouée: {result}")
                    else:
                        print(f"✅ [SEND_LOG] Tâche {i} réussie")
            except Exception as e:
                print(f"💥 [SEND_LOG] Erreur lors de l'exécution des tâches: {e}")
    else:
        print("⚠️ [SEND_LOG] Aucun client connecté")

async def check_hive_status():
    # ... (cette fonction ne change pas) ...
    await send_log("Interrogation d'ASTRA HIVE...", 'info', {"pillar": "hive-status", "status": "ok", "message": "Analyse..."})
    try:
        telemetry = {"frequency": 12.5, "power": 100.0, "modulation": 1}
        response = requests.post(HIVE_API_URL, json=telemetry)
        data = response.json()
        if data.get("prediction") == "Anomalie Détectée":
            await send_log("ALERTE HIVE : Comportement réseau anormal.", 'critical', {"pillar": "hive-status", "status": "alert", "message": "Anomalie!"})
            return False
        await send_log("HIVE confirme un état réseau nominal.", 'info', {"pillar": "hive-status", "status": "ok", "message": "Opérationnel"})
        return True
    except requests.exceptions.RequestException:
        await send_log("Impossible de contacter ASTRA HIVE !", 'critical', {"pillar": "hive-status", "status": "alert", "message": "Hors Ligne"})
        return False

async def establish_wave_channel():
    """Simule l'établissement d'un canal sécurisé PQC avec ASTRA WAVE."""
    await send_log("ASTRA WAVE : Initiation du canal de communication post-quantique.", 'info', 
                   {"pillar": "wave-status", "status": "ok", "message": "Négociation PQC..."})
    await asyncio.sleep(1)
    # Simulation de l'échange de clés Kyber
    pk, sk = Kyber1024.keypair()
    ciphertext, shared_secret = Kyber1024.enc(pk)
    decrypted_secret = Kyber1024.dec(ciphertext, sk)
    
    if shared_secret == decrypted_secret:
         await send_log("ASTRA WAVE : Canal sécurisé établi avec succès.", 'info',
                        {"pillar": "wave-status", "status": "ok", "message": "Canal Sécurisé"})
    else:
        await send_log("ASTRA WAVE : Échec de l'établissement du canal PQC !", 'critical',
                       {"pillar": "wave-status", "status": "alert", "message": "Échec PQC"})

async def check_core_integrity():
    """Vérifie périodiquement l'intégrité du firmware simulé."""
    while True:
        await asyncio.sleep(10) # Vérifie toutes les 10 secondes
        if SATELLITE_STATE["firmware_integrity"] == "CORRUPTED":
            await send_log("ASTRA CORE : ALERTE CRITIQUE ! CORRUPTION DE FIRMWARE DÉTECTÉE !", 'critical',
                           {"pillar": "core-status", "status": "alert", "message": "INTÉGRITÉ COMPROMISE"})
        else:
             await send_log("ASTRA CORE : Vérification d'intégrité OK.", 'info',
                           {"pillar": "core-status", "status": "ok", "message": "Opérationnel"})

async def cryptographic_heartbeat_protocol():
    """
    Simule le protocole de heartbeat cryptographique continu avec ASTRA CORE.
    """
    while True:
        await asyncio.sleep(7)
        await send_log("ASTRA CORE : Envoi du défi 'heartbeat' au satellite...", 'info')
        challenge = os.urandom(32)
        signature = Dilithium5.sign(SATELLITE_SIGNING_SK, challenge)
        if Dilithium5.verify(SATELLITE_SIGNING_PK, challenge, signature):
            SATELLITE_STATE["last_heartbeat_status"] = "OK"
            await send_log("ASTRA CORE : Réponse 'heartbeat' valide. Le satellite est vivant et authentique.", 'info',
                           {"pillar": "core-status", "status": "ok", "message": "Heartbeat OK"})
        else:
            SATELLITE_STATE["last_heartbeat_status"] = "FAILED"
            await send_log("ASTRA CORE : ALERTE ! Le heartbeat cryptographique a échoué !", 'critical',
                           {"pillar": "core-status", "status": "alert", "message": "Heartbeat Échoué!"})

async def handle_command_attempt():
    await send_log("Tentative de commande critique reçue.", 'warning')
    if not await check_hive_status():
        await send_log("COMMANDE REFUSÉE : Contexte de sécurité anormal.", 'critical')
        return

    await asyncio.sleep(1)
    await send_log("SENTRY : Opérateur authentifié avec succès (MFA OK).", 'info',
                   {"pillar": "sentry-status", "status": "ok", "message": "Opérationnel"})
    
    await establish_wave_channel() # Intégration de WAVE
    
    await asyncio.sleep(1)
    await send_log("COMMANDE APPROUVÉE ET ENVOYÉE via le canal sécurisé WAVE.", 'info')

async def handler(websocket, path=None):
    print(f"🔗 Nouvelle connexion WebSocket établie (path: {path})")
    CONNECTED_CLIENTS.add(websocket)
    try:
        print("📤 Envoi du message de bienvenue...")
        await send_log("Client connecté. Synchronisation de l'état des piliers.", 'info')
        print("✅ Message de bienvenue envoyé avec succès")
        
        async for message in websocket:
            try:
                print(f"📨 Message reçu: {message[:100]}...")
                data = json.loads(message)
                if data.get("action") == "ATTEMPT_COMMAND":
                    print("🚀 Exécution de la commande...")
                    await handle_command_attempt()
                elif data.get("action") == "CORRUPT_FIRMWARE":
                    print("⚠️ Simulation de corruption firmware...")
                    SATELLITE_STATE["firmware_integrity"] = "CORRUPTED"
                    await send_log("ATTAQUE SIMULÉE : Le firmware du satellite a été corrompu !", 'critical')
                else:
                    print(f"❓ Action non reconnue: {data.get('action')}")
            except json.JSONDecodeError as e:
                print(f"❌ Erreur JSON: {e}")
                await send_log(f"Erreur de format JSON : {e}", 'error')
            except Exception as e:
                print(f"❌ Erreur lors du traitement du message : {e}")
                await send_log(f"Erreur lors du traitement du message : {e}", 'error')
    except websockets.exceptions.ConnectionClosed as e:
        print(f"🔌 Connexion fermée normalement: {e}")
    except Exception as e:
        print(f"💥 Erreur WebSocket critique : {e}")
        await send_log(f"Erreur WebSocket : {e}", 'error')
    finally:
        print("🧹 Nettoyage de la connexion...")
        CONNECTED_CLIENTS.discard(websocket)
        print(f"📊 Clients connectés restants: {len(CONNECTED_CLIENTS)}")

async def main():
    print("Serveur du Jumeau Numérique (v3 - Heartbeat) démarré sur ws://127.0.0.1:5005")
    asyncio.create_task(cryptographic_heartbeat_protocol())
    async with websockets.serve(handler, "127.0.0.1", 5005):
        await asyncio.Future()

if __name__ == "__main__":
    # Assurez-vous que l'API HIVE (api.py) est lancée avant ce serveur.
    asyncio.run(main()) 