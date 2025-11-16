import socket
import json
import threading
import time
import random
from datetime import datetime, timedelta
import requests

class WeatherStation:
    def __init__(self, api_key=None, city="Dakar", port=5555):
        self.api_key = api_key
        self.city = city
        self.port = port
        self.clients = []
        self.running = False
        self.current_data = {}

    def fetch_real_weather(self):
        """Récupère les données réelles d'OpenWeatherMap"""
        if not self.api_key:
            return None

        try:
            url = f"http://api.openweathermap.org/data/2.5/weather?q={self.city}&appid={self.api_key}&units=metric&lang=fr"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print("Open Weather got response !")
                return response.json()
        except Exception as e:
            print(f"Erreur API: {e}")
        return None

    def generate_weather_data(self):
        """Génère ou récupère les données météo"""
        real_data = self.fetch_real_weather()

        if real_data:
            # Données réelles
            weather_data = {
                "timestamp": datetime.now().isoformat(),
                "temperature": real_data["main"]["temp"],
                "humidity": real_data["main"]["humidity"],
                "pressure": real_data["main"]["pressure"],
                "wind_speed": real_data["wind"]["speed"],
                "wind_direction": real_data["wind"].get("deg", 0),
                "description": real_data["weather"][0]["description"],
                "clouds": real_data["clouds"]["all"],
                "visibility": real_data.get("visibility", 10000),
                "city": self.city,
                "source": "real"
            }
        else:
            # Données simulées
            base_temp = 28
            weather_data = {
                "timestamp": datetime.now().isoformat(),
                "temperature": round(base_temp + random.uniform(-3, 3), 1),
                "humidity": random.randint(50, 90),
                "pressure": random.randint(1010, 1020),
                "wind_speed": round(random.uniform(0, 15), 1),
                "wind_direction": random.randint(0, 360),
                "description": random.choice(["Ensoleillé", "Nuageux", "Partiellement nuageux"]),
                "clouds": random.randint(0, 100),
                "visibility": random.randint(8000, 10000),
                "city": self.city,
                "source": "simulated"
            }

        # Génération d'alertes
        alerts = []
        if weather_data["temperature"] > 35:
            alerts.append({"type": "chaleur", "message": "Alerte canicule"})
        if weather_data["wind_speed"] > 50:
            alerts.append({"type": "vent", "message": "Alerte tempête"})
        if weather_data["humidity"] > 85:
            alerts.append({"type": "humidité", "message": "Forte humidité"})

        weather_data["alerts"] = alerts

        # Prévisions (simulées)
        forecast = []
        for i in range(1, 6):
            day = datetime.now() + timedelta(days=i)
            forecast.append({
                "date": day.strftime("%Y-%m-%d"),
                "temp_min": round(weather_data["temperature"] - random.uniform(2, 5), 1),
                "temp_max": round(weather_data["temperature"] + random.uniform(2, 5), 1),
                "description": random.choice(["Ensoleillé", "Nuageux", "Pluie"])
            })

        weather_data["forecast"] = forecast

        return weather_data

    def handle_client(self, client_socket, address):
        """Gère la communication avec un client"""
        print(f"Nouveau client connecté: {address}")
        self.clients.append(client_socket)

        try:
            while self.running:
                if self.current_data:
                    message = json.dumps(self.current_data) + "\n"
                    client_socket.send(message.encode('utf-8'))
                time.sleep(2)
        except Exception as e:
            print(f"Erreur client {address}: {e}")
        finally:
            self.clients.remove(client_socket)
            client_socket.close()
            print(f"Client déconnecté: {address}")

    def update_weather(self):
        """Met à jour les données météo périodiquement"""
        while self.running:
            self.current_data = self.generate_weather_data()
            print(f"Données mises à jour: {self.current_data['temperature']}°C - {self.current_data['description']}")
            time.sleep(10)

    def start(self):
        """Démarre le serveur"""
        self.running = True

        # Thread de mise à jour météo
        weather_thread = threading.Thread(target=self.update_weather)
        weather_thread.daemon = True
        weather_thread.start()

        # Serveur socket
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind(('0.0.0.0', self.port))
        server.listen(5)

        print(f"🌤️  Serveur météo démarré sur le port {self.port}")
        print(f"Ville: {self.city}")
        print(f"Mode: {'API réelle' if self.api_key else 'Simulation'}")
        print("En attente de clients...\n")

        try:
            while self.running:
                client_socket, address = server.accept()
                client_thread = threading.Thread(
                    target=self.handle_client,
                    args=(client_socket, address)
                )
                client_thread.daemon = True
                client_thread.start()
        except KeyboardInterrupt:
            print("\nArrêt du serveur...")
        finally:
            self.running = False
            server.close()

if __name__ == "__main__":
    # Configuration
    API_KEY = "VOTRE-CLE-OPENWEATHERMAP"  # Remplacer par votre clé OpenWeatherMap
    # Se rendre à l'adresse OpenWeatherMap, créer un compte et générer votre clé
    CITY = "Dakar"
    PORT = 5555

    # Démarrage du serveur
    station = WeatherStation(api_key=API_KEY, city=CITY, port=PORT)
    station.start()
