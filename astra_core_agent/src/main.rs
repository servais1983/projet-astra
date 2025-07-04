use std::fs;
use std::path::Path;
use std::time::Duration;
use std::thread;
use sha2::{Sha256, Digest};

// --- Configuration du Micro-Agent ---
const FIRMWARE_PATH: &str = "satellite_firmware.bin";
const CHECK_INTERVAL_SECONDS: u64 = 5;

/// Calcule le hash SHA-256 d'un fichier.
/// Retourne le hash sous forme de chaîne hexadécimale.
fn calculate_checksum(file_path: &Path) -> Result<String, std::io::Error> {
    let data = fs::read(file_path)?;
    let mut hasher = Sha256::new();
    hasher.update(data);
    let hash = hasher.finalize();
    Ok(format!("{:x}", hash))
}

/// Simule la création ou la mise à jour d'un fichier de firmware.
fn create_simulated_firmware(content: &str) {
    fs::write(FIRMWARE_PATH, content).expect("Impossible d'écrire le fichier firmware.");
    println!("[SIMULATION] Le fichier '{}' a été créé/modifié.", FIRMWARE_PATH);
}

/// Le coeur du micro-agent de surveillance ASTRA CORE.
fn run_integrity_monitor(trusted_checksum: &str) {
    println!("\n--- ASTRA CORE : Moniteur d'intégrité activé ---");
    println!("Checksum de confiance : {}", trusted_checksum);

    loop {
        thread::sleep(Duration::from_secs(CHECK_INTERVAL_SECONDS));
        
        print!("[AGENT] Vérification de l'intégrité du firmware... ");
        
        match calculate_checksum(Path::new(FIRMWARE_PATH)) {
            Ok(current_checksum) => {
                if current_checksum == trusted_checksum {
                    println!("✅ OK");
                } else {
                    println!("❌ ALERTE CRITIQUE !");
                    println!("   -> Hash attendu : {}", trusted_checksum);
                    println!("   -> Hash actuel   : {}", current_checksum);
                    println!("   -> CORRUPTION DE FIRMWARE DÉTECTÉE !");
                    println!("   -> Activation du 'Mode Sanctuaire Autonome'...");
                    // Ici, le vrai agent activerait le mode sanctuaire
                    break; // Arrête la simulation
                }
            },
            Err(e) => {
                println!("❌ ERREUR SYSTÈME : Impossible de lire le firmware ! ({})", e);
                break;
            }
        }
    }
}

fn main() {
    println!("--- DÉMARRAGE DU SYSTÈME EMBARQUÉ ASTRA CORE ---");

    // 1. Création d'un firmware initial sain
    create_simulated_firmware("Données du firmware satellite v1.0 - Stables");

    // 2. Calcul et stockage du checksum de confiance au démarrage
    let trusted_checksum = calculate_checksum(Path::new(FIRMWARE_PATH))
        .expect("Impossible de calculer le checksum initial.");

    // 3. Lancement du moniteur dans un thread séparé
    let monitor_thread = thread::spawn(move || {
        run_integrity_monitor(&trusted_checksum);
    });

    // 4. Simulation d'une attaque qui modifie le firmware après 12 secondes
    println!("\n[SIMULATION] Le satellite fonctionne normalement...");
    thread::sleep(Duration::from_secs(12));
    println!("\n[SIMULATION] Une attaque de type 'zero-day' est en cours...");
    create_simulated_firmware("Données corrompues par un attaquant !");

    // Attendre la fin du thread du moniteur
    monitor_thread.join().unwrap();
}
