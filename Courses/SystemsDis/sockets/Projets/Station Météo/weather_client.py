import socket
import json
import sys

class WeatherClient:
    def __init__(self, host='localhost', port=5555):
        self.host = host
        self.port = port
        self.socket = None

    def connect(self):
        """Se connecte au serveur météo"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            print(f"✅ Connecté au serveur {self.host}:{self.port}\n")
            return True
        except Exception as e:
            print(f"❌ Erreur de connexion: {e}")
            return False

    def receive_data(self):
        """Reçoit et affiche les données météo"""
        buffer = ""
        try:
            while True:
                chunk = self.socket.recv(4096).decode('utf-8')
                if not chunk:
                    break

                buffer += chunk
                while '\n' in buffer:
                    line, buffer = buffer.split('\n', 1)
                    if line.strip():
                        data = json.loads(line)
                        self.display_weather(data)
        except KeyboardInterrupt:
            print("\n\nDéconnexion...")
        except Exception as e:
            print(f"Erreur: {e}")
        finally:
            self.disconnect()

    def display_weather(self, data):
        """Affiche les données météo de manière formatée"""
        print("\n" + "="*60)
        print(f"📍 {data['city']} - {data['timestamp']}")
        print(f"Source: {data['source']}")
        print("="*60)
        print(f"🌡️  Température: {data['temperature']}°C")
        print(f"💧 Humidité: {data['humidity']}%")
        print(f"📊 Pression: {data['pressure']} hPa")
        print(f"💨 Vent: {data['wind_speed']} km/h ({data['wind_direction']}°)")
        print(f"☁️  Nébulosité: {data['clouds']}%")
        print(f"👁️  Visibilité: {data['visibility']}m")
        print(f"📝 Description: {data['description']}")

        # Alertes
        if data.get('alerts'):
            print("\n⚠️  ALERTES:")
            for alert in data['alerts']:
                print(f"   - {alert['type'].upper()}: {alert['message']}")

        # Prévisions
        if data.get('forecast'):
            print("\n📅 Prévisions 5 jours:")
            for day in data['forecast']:
                print(f"   {day['date']}: {day['temp_min']}°C - {day['temp_max']}°C | {day['description']}")

        print("="*60)

    def disconnect(self):
        """Ferme la connexion"""
        if self.socket:
            self.socket.close()
            print("Déconnecté du serveur")

if __name__ == "__main__":
    # Configuration
    HOST = sys.argv[1] if len(sys.argv) > 1 else 'localhost'
    PORT = int(sys.argv[2]) if len(sys.argv) > 2 else 5555

    # Connexion et réception
    client = WeatherClient(host=HOST, port=PORT)
    if client.connect():
        client.receive_data()
