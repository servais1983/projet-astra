import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset
import numpy as np

class Autoencoder(nn.Module):
    """
    Architecture de l'Autoencodeur.
    Composé d'un encodeur et d'un décodeur.
    """
    def __init__(self, input_dim, encoding_dim):
        super(Autoencoder, self).__init__()
        self.encoder = nn.Sequential(
            nn.Linear(input_dim, 128),
            nn.ReLU(),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Linear(64, encoding_dim)
        )
        self.decoder = nn.Sequential(
            nn.Linear(encoding_dim, 64),
            nn.ReLU(),
            nn.Linear(64, 128),
            nn.ReLU(),
            nn.Linear(128, input_dim),
            nn.Sigmoid() # Sigmoid car on normalisera les données d'entrée entre 0 et 1
        )

    def forward(self, x):
        encoded = self.encoder(x)
        decoded = self.decoder(encoded)
        return decoded

class AdvancedAnomalyDetector:
    """
    Détecteur avancé utilisant un Autoencodeur PyTorch.
    Il apprend la structure des données normales et détecte les déviations.
    """
    def __init__(self, input_dim, encoding_dim=32):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = Autoencoder(input_dim, encoding_dim).to(self.device)
        self.criterion = nn.MSELoss() # On mesure l'erreur de reconstruction
        self.optimizer = torch.optim.Adam(self.model.parameters(), lr=1e-3)
        self.threshold = 0.0 # Le seuil sera déterminé après l'entraînement

    def train(self, data_loader, epochs=20):
        print(f"\nDébut de l'entraînement du détecteur avancé sur {self.device}...")
        self.model.train()
        for epoch in range(epochs):
            total_loss = 0
            for (data,) in data_loader:
                data = data.to(self.device)
                self.optimizer.zero_grad()
                reconstructed = self.model(data)
                loss = self.criterion(reconstructed, data)
                loss.backward()
                self.optimizer.step()
                total_loss += loss.item()
            print(f'Epoch {epoch+1}/{epochs}, Perte: {total_loss/len(data_loader):.6f}')
        
        # Déterminer le seuil d'anomalie
        self._set_threshold(data_loader)

    def _set_threshold(self, data_loader):
        self.model.eval()
        losses = []
        with torch.no_grad():
            for (data,) in data_loader:
                data = data.to(self.device)
                reconstructed = self.model(data)
                loss = torch.mean((data - reconstructed) ** 2, dim=1)
                losses.extend(loss.cpu().numpy())
        # Le seuil est défini comme la perte de reconstruction maximale sur les données normales
        self.threshold = max(losses)
        print(f"Seuil d'anomalie déterminé : {self.threshold:.6f}")

    def predict(self, data_loader):
        self.model.eval()
        anomalies = []
        with torch.no_grad():
            for i, (data,) in enumerate(data_loader):
                data = data.to(self.device)
                reconstructed = self.model(data)
                loss = torch.mean((data - reconstructed) ** 2, dim=1)
                
                # Compare la perte au seuil
                is_anomaly = loss > self.threshold
                for anomaly_flag in is_anomaly:
                    anomalies.append(-1 if anomaly_flag.item() else 1)
        return anomalies

    def prepare_features(self, network_data):
        """
        Transforme un dictionnaire réseau en tenseur PyTorch normalisé.
        Les clés attendues sont : packet_count, latency, bandwidth, error_rate
        """
        # Ordre des features attendu
        keys = ["packet_count", "latency", "bandwidth", "error_rate"]
        values = [float(network_data.get(k, 0.0)) for k in keys]
        arr = np.array(values, dtype=np.float32)
        # Normalisation simple (pour la démo)
        arr[0] = arr[0] / 10000.0  # packet_count
        arr[1] = arr[1] / 1000.0   # latency
        arr[2] = arr[2] / 1000.0   # bandwidth
        arr[3] = arr[3]            # error_rate (déjà entre 0 et 1)
        tensor = torch.tensor(arr).unsqueeze(0)  # batch de 1
        return tensor 