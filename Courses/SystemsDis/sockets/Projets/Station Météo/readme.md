# 📡 Guide détaillé : Station météo avec Sockets TCP

## 🎯 Objectif du projet

Ce projet implémente une **station météo client-serveur** utilisant les sockets TCP pour la communication réseau. Le serveur collecte des données météorologiques (réelles ou simulées) et les diffuse à tous les clients connectés en temps réel.

---

## 🔧 Architecture du système

```
┌─────────────────────┐         Socket TCP          ┌─────────────────────┐
│                     │    (Port 5555 par défaut)   │                     │
│   SERVEUR MÉTÉO     │◄─────────────────────────►  │   CLIENT MÉTÉO      │
│  (weather_server)   │                             │  (weather_client)   │
│                     │                             │                     │
│ - OpenWeatherMap    │                             │ - Affichage données │
│ - Simulation        │                             │ - Alertes           │
│ - Multi-threading   │                             │ - Prévisions        │
└─────────────────────┘                             └─────────────────────┘
```

---

## 📄 PARTIE 1 : LE SERVEUR (`weather_server.py`)

### 1.1 Imports et dépendances

```python
import socket          # Module pour la communication réseau
import json            # Pour sérialiser/désérialiser les données
import threading       # Pour gérer plusieurs clients simultanément
import time            # Pour les délais et temporisations
import random          # Pour générer des données simulées
from datetime import datetime, timedelta  # Gestion des dates
import requests        # Pour les requêtes HTTP à l'API OpenWeatherMap
```

**Points clés :**
- `socket` : Module Python standard pour la programmation réseau
- `threading` : Permet l'exécution parallèle de plusieurs tâches
- `requests` : Bibliothèque tierce pour les requêtes HTTP (nécessite installation)

---

### 1.2 Classe `WeatherStation`

#### 1.2.1 Constructeur (`__init__`)

```python
def __init__(self, api_key=None, city="Dakar", port=5555):
    self.api_key = api_key      # Clé API OpenWeatherMap (optionnelle)
    self.city = city            # Ville pour les données météo
    self.port = port            # Port TCP d'écoute du serveur
    self.clients = []           # Liste des sockets clients connectés
    self.running = False        # État du serveur (actif/inactif)
    self.current_data = {}      # Dernières données météo disponibles
```

**Explication :**
- `self.clients` : Stocke tous les sockets des clients connectés pour leur envoyer les données
- `self.running` : Drapeau booléen pour contrôler la boucle principale du serveur
- `self.current_data` : Cache les dernières données météo pour éviter de régénérer à chaque envoi

---

#### 1.2.2 Récupération des données réelles (`fetch_real_weather`)

```python
def fetch_real_weather(self):
    """Récupère les données réelles d'OpenWeatherMap"""
    if not self.api_key:
        return None

    try:
        # Construction de l'URL de l'API avec paramètres
        url = f"http://api.openweathermap.org/data/2.5/weather?q={self.city}&appid={self.api_key}&units=metric&lang=fr"
        
        # Requête HTTP GET avec timeout de 5 secondes
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:  # Succès HTTP
            print("Open Weather got response !")
            return response.json()  # Convertit la réponse JSON en dictionnaire Python
            
    except Exception as e:
        print(f"Erreur API: {e}")
    
    return None
```

**Points techniques :**
- **Paramètres URL** :
  - `q={city}` : Nom de la ville
  - `appid={api_key}` : Authentification API
  - `units=metric` : Unités métriques (Celsius, km/h)
  - `lang=fr` : Descriptions en français
  
- **Timeout** : Évite de bloquer le serveur si l'API ne répond pas
- **Gestion d'erreurs** : Le serveur continue même si l'API échoue

---

#### 1.2.3 Génération des données météo (`generate_weather_data`)

```python
def generate_weather_data(self):
    """Génère ou récupère les données météo"""
    real_data = self.fetch_real_weather()

    if real_data:
        # DONNÉES RÉELLES depuis l'API
        weather_data = {
            "timestamp": datetime.now().isoformat(),  # Horodatage ISO 8601
            "temperature": real_data["main"]["temp"],
            "humidity": real_data["main"]["humidity"],
            "pressure": real_data["main"]["pressure"],
            "wind_speed": real_data["wind"]["speed"],
            "wind_direction": real_data["wind"].get("deg", 0),  # .get() évite KeyError
            "description": real_data["weather"][0]["description"],
            "clouds": real_data["clouds"]["all"],
            "visibility": real_data.get("visibility", 10000),
            "city": self.city,
            "source": "real"  # Indicateur de source
        }
    else:
        # DONNÉES SIMULÉES (mode fallback)
        base_temp = 28
        weather_data = {
            "timestamp": datetime.now().isoformat(),
            "temperature": round(base_temp + random.uniform(-3, 3), 1),  # ±3°C
            "humidity": random.randint(50, 90),      # 50-90%
            "pressure": random.randint(1010, 1020),  # 1010-1020 hPa
            "wind_speed": round(random.uniform(0, 15), 1),
            "wind_direction": random.randint(0, 360),  # Degrés boussole
            "description": random.choice(["Ensoleillé", "Nuageux", "Partiellement nuageux"]),
            "clouds": random.randint(0, 100),
            "visibility": random.randint(8000, 10000),
            "city": self.city,
            "source": "simulated"
        }
```

**Logique de décision :**
1. Tente d'abord les données réelles
2. Si échec (pas d'API key ou erreur réseau) → génère des données aléatoires
3. Le champ `"source"` permet au client de savoir l'origine des données

**Génération des alertes :**
```python
    # Génération d'alertes basées sur des seuils
    alerts = []
    if weather_data["temperature"] > 35:
        alerts.append({"type": "chaleur", "message": "Alerte canicule"})
    if weather_data["wind_speed"] > 50:
        alerts.append({"type": "vent", "message": "Alerte tempête"})
    if weather_data["humidity"] > 85:
        alerts.append({"type": "humidité", "message": "Forte humidité"})
    
    weather_data["alerts"] = alerts
```

**Prévisions sur 5 jours :**
```python
    # Prévisions (simulées)
    forecast = []
    for i in range(1, 6):  # Jours 1 à 5
        day = datetime.now() + timedelta(days=i)  # Date future
        forecast.append({
            "date": day.strftime("%Y-%m-%d"),  # Format : 2024-01-15
            "temp_min": round(weather_data["temperature"] - random.uniform(2, 5), 1),
            "temp_max": round(weather_data["temperature"] + random.uniform(2, 5), 1),
            "description": random.choice(["Ensoleillé", "Nuageux", "Pluie"])
        })
    
    weather_data["forecast"] = forecast
    return weather_data
```

---

#### 1.2.4 Gestion des clients (`handle_client`)

```python
def handle_client(self, client_socket, address):
    """Gère la communication avec un client"""
    print(f"Nouveau client connecté: {address}")
    self.clients.append(client_socket)  # Ajoute à la liste des clients actifs

    try:
        while self.running:  # Boucle tant que le serveur est actif
            if self.current_data:  # Si des données sont disponibles
                # Sérialisation JSON + caractère de fin de ligne
                message = json.dumps(self.current_data) + "\n"
                
                # Envoi via le socket (encodage UTF-8)
                client_socket.send(message.encode('utf-8'))
            
            time.sleep(2)  # Pause de 2 secondes entre chaque envoi
            
    except Exception as e:
        print(f"Erreur client {address}: {e}")
    finally:
        # Nettoyage : retrait de la liste et fermeture du socket
        self.clients.remove(client_socket)
        client_socket.close()
        print(f"Client déconnecté: {address}")
```

**Détails techniques :**
- **Threading** : Chaque client est géré dans un thread séparé
- **Encodage** : Les données JSON sont encodées en UTF-8 pour la transmission
- **Délimiteur `\n`** : Permet au client de séparer les messages dans le flux TCP
- **Gestion d'erreurs** : Le bloc `finally` garantit le nettoyage même en cas d'erreur

---

#### 1.2.5 Mise à jour périodique (`update_weather`)

```python
def update_weather(self):
    """Met à jour les données météo périodiquement"""
    while self.running:
        # Génère de nouvelles données
        self.current_data = self.generate_weather_data()
        
        print(f"Données mises à jour: {self.current_data['temperature']}°C - {self.current_data['description']}")
        
        time.sleep(10)  # Mise à jour toutes les 10 secondes
```

**Pourquoi un thread séparé ?**
- Permet de mettre à jour les données indépendamment des clients
- Évite de bloquer l'acceptation de nouvelles connexions
- Tous les clients reçoivent les mêmes données synchronisées

---

#### 1.2.6 Démarrage du serveur (`start`)

```python
def start(self):
    """Démarre le serveur"""
    self.running = True

    # Thread de mise à jour météo
    weather_thread = threading.Thread(target=self.update_weather)
    weather_thread.daemon = True  # Thread daemon : s'arrête avec le programme principal
    weather_thread.start()

    # Création du socket serveur
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # SO_REUSEADDR : permet de réutiliser le port immédiatement après fermeture
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    # Liaison à toutes les interfaces réseau (0.0.0.0) sur le port spécifié
    server.bind(('0.0.0.0', self.port))
    
    # File d'attente de 5 connexions maximum
    server.listen(5)

    print(f"🌤️  Serveur météo démarré sur le port {self.port}")
    print(f"Ville: {self.city}")
    print(f"Mode: {'API réelle' if self.api_key else 'Simulation'}")
    print("En attente de clients...\n")

    try:
        while self.running:
            # Bloque jusqu'à ce qu'un client se connecte
            client_socket, address = server.accept()
            
            # Crée un thread pour gérer ce client
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
```

**Concepts de socket TCP :**
- **`socket.AF_INET`** : Famille d'adresses IPv4
- **`socket.SOCK_STREAM`** : Type de socket TCP (orienté connexion)
- **`bind()`** : Associe le socket à une adresse et un port
- **`listen()`** : Met le socket en mode écoute
- **`accept()`** : Bloque jusqu'à réception d'une connexion entrante

**Thread daemon :**
- Un thread daemon se termine automatiquement quand le programme principal se termine
- Évite que les threads ne bloquent la fermeture du programme

---

### 1.3 Point d'entrée principal

```python
if __name__ == "__main__":
    # Configuration
    API_KEY = "f0061bc0f917b53ac33cef91c9a8b27b"  # Clé OpenWeatherMap
    CITY = "Dakar"
    PORT = 5555

    # Démarrage du serveur
    station = WeatherStation(api_key=API_KEY, city=CITY, port=PORT)
    station.start()
```

**Note de sécurité :** En production, la clé API ne devrait JAMAIS être dans le code source. Utilisez des variables d'environnement ou fichiers de configuration.

---

## 📄 PARTIE 2 : LE CLIENT (`weather_client.py`)

### 2.1 Imports

```python
import socket   # Communication réseau
import json     # Parsing des données JSON
import sys      # Accès aux arguments de ligne de commande
```

---

### 2.2 Classe `WeatherClient`

#### 2.2.1 Constructeur

```python
def __init__(self, host='localhost', port=5555):
    self.host = host    # Adresse IP ou nom d'hôte du serveur
    self.port = port    # Port TCP du serveur
    self.socket = None  # Socket client (initialisé lors de la connexion)
```

---

#### 2.2.2 Connexion au serveur (`connect`)

```python
def connect(self):
    """Se connecte au serveur météo"""
    try:
        # Création d'un socket TCP client
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        # Connexion au serveur (triple handshake TCP)
        self.socket.connect((self.host, self.port))
        
        print(f"✅ Connecté au serveur {self.host}:{self.port}\n")
        return True
        
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")
        return False
```

**Processus de connexion TCP :**
1. Le client envoie un SYN au serveur
2. Le serveur répond avec SYN-ACK
3. Le client répond avec ACK
4. La connexion est établie

**Erreurs possibles :**
- `ConnectionRefusedError` : Serveur non démarré ou port incorrect
- `socket.gaierror` : Nom d'hôte invalide
- `TimeoutError` : Serveur injoignable

---

#### 2.2.3 Réception des données (`receive_data`)

```python
def receive_data(self):
    """Reçoit et affiche les données météo"""
    buffer = ""  # Tampon pour les données partielles
    
    try:
        while True:
            # Reçoit jusqu'à 4096 octets
            chunk = self.socket.recv(4096).decode('utf-8')
            
            if not chunk:  # Connexion fermée par le serveur
                break
            
            buffer += chunk  # Ajoute au tampon
            
            # Traite tous les messages complets (délimités par \n)
            while '\n' in buffer:
                line, buffer = buffer.split('\n', 1)  # Sépare au premier \n
                
                if line.strip():  # Ignore les lignes vides
                    data = json.loads(line)  # Parse le JSON
                    self.display_weather(data)  # Affiche les données
                    
    except KeyboardInterrupt:
        print("\n\nDéconnexion...")
    except Exception as e:
        print(f"Erreur: {e}")
    finally:
        self.disconnect()
```

**Concepts importants :**

1. **Buffering** : TCP est un protocole de flux, les données peuvent arriver en plusieurs fragments
   - Le buffer accumule les données jusqu'à avoir un message complet
   - Le `\n` sert de délimiteur entre messages

2. **`recv(4096)`** : 
   - Reçoit jusqu'à 4096 octets (taille standard)
   - Peut retourner moins de données que demandé
   - Retourne une chaîne vide si la connexion est fermée

3. **Parsing JSON** :
   - `json.loads()` convertit une chaîne JSON en dictionnaire Python
   - Peut lever une exception si le JSON est malformé

---

#### 2.2.4 Affichage des données (`display_weather`)

```python
def display_weather(self, data):
    """Affiche les données météo de manière formatée"""
    print("\n" + "="*60)
    print(f"📍 {data['city']} - {data['timestamp']}")
    print(f"Source: {data['source']}")
    print("="*60)
    
    # Données principales
    print(f"🌡️  Température: {data['temperature']}°C")
    print(f"💧 Humidité: {data['humidity']}%")
    print(f"📊 Pression: {data['pressure']} hPa")
    print(f"💨 Vent: {data['wind_speed']} km/h ({data['wind_direction']}°)")
    print(f"☁️  Nébulosité: {data['clouds']}%")
    print(f"👁️  Visibilité: {data['visibility']}m")
    print(f"📝 Description: {data['description']}")
    
    # Alertes (si présentes)
    if data.get('alerts'):
        print("\n⚠️  ALERTES:")
        for alert in data['alerts']:
            print(f"   - {alert['type'].upper()}: {alert['message']}")
    
    # Prévisions (si présentes)
    if data.get('forecast'):
        print("\n📅 Prévisions 5 jours:")
        for day in data['forecast']:
            print(f"   {day['date']}: {day['temp_min']}°C - {day['temp_max']}°C | {day['description']}")
    
    print("="*60)
```

**Techniques de présentation :**
- Emojis pour une meilleure lisibilité
- Formatage avec f-strings Python
- `.get()` pour éviter les erreurs si certains champs sont absents

---

#### 2.2.5 Déconnexion (`disconnect`)

```python
def disconnect(self):
    """Ferme la connexion"""
    if self.socket:
        self.socket.close()  # Ferme le socket proprement
        print("Déconnecté du serveur")
```

**Importance de la fermeture :**
- Libère les ressources système (descripteurs de fichiers)
- Envoie un FIN au serveur pour terminer la connexion TCP proprement
- Évite les fuites de ressources

---

### 2.3 Point d'entrée

```python
if __name__ == "__main__":
    # Lecture des arguments de ligne de commande
    HOST = sys.argv[1] if len(sys.argv) > 1 else 'localhost'
    PORT = int(sys.argv[2]) if len(sys.argv) > 2 else 5555
    
    # Connexion et réception
    client = WeatherClient(host=HOST, port=PORT)
    if client.connect():
        client.receive_data()
```

**Utilisation :**
```bash
# Connexion locale
python weather_client.py

# Connexion à un serveur distant
python weather_client.py 192.168.1.10 5555
```

---

## 🔍 Concepts réseau approfondis

### Protocole TCP vs UDP

| Aspect | TCP (utilisé ici) | UDP |
|--------|-------------------|-----|
| **Connexion** | Orienté connexion | Sans connexion |
| **Fiabilité** | Garantit la livraison | Pas de garantie |
| **Ordre** | Données dans l'ordre | Ordre non garanti |
| **Overhead** | Plus lourd | Léger |
| **Cas d'usage** | Applications nécessitant fiabilité | Streaming, jeux en temps réel |

**Pourquoi TCP pour ce projet ?**
- Les données météo doivent arriver de manière fiable
- L'ordre des messages est important
- La latence supplémentaire est acceptable

---

### Sérialisation JSON

**Pourquoi JSON ?**
- Format texte lisible par l'humain
- Supporté nativement par Python
- Portable entre langages et plateformes
- Facilité de debug

**Alternative :** Protocole binaire (protobuf, msgpack) pour performance

---

### Multi-threading

**Architecture du serveur :**
```
Thread principal (Main)
├── Thread mise à jour météo (daemon)
├── Thread client 1 (daemon)
├── Thread client 2 (daemon)
└── Thread client N (daemon)
```

**Avantages :**
- Chaque client est traité indépendamment
- Le serveur peut accepter de nouvelles connexions pendant les envois
- Les mises à jour météo ne bloquent pas les communications

**Limites :**
- GIL (Global Interpreter Lock) de Python limite la vraie parallélisation
- Pour des milliers de clients, considérer asyncio ou multiprocessing

---

## 🚀 Améliorations possibles

### 1. Sécurité
- **Authentification** : Ajouter un système login/mot de passe
- **Chiffrement** : Utiliser SSL/TLS (socket.ssl)
- **Protection API key** : Variables d'environnement

### 2. Protocole
- **Messages bidirectionnels** : Le client peut envoyer des commandes
- **Compression** : Réduire la taille des données avec gzip
- **Format binaire** : Plus efficace que JSON

### 3. Robustesse
- **Reconnexion automatique** : Le client se reconnecte en cas de déconnexion
- **Heartbeat** : Vérification périodique de la connexion
- **Logs** : Système de logging pour debug et monitoring

### 4. Fonctionnalités
- **Historique** : Stocker les données dans une base de données
- **Graphiques** : Visualisation avec matplotlib
- **WebSocket** : Interface web en temps réel

---

## 📋 Questions de compréhension

### Questions de base

1. **Quelle est la différence entre `socket.bind()` et `socket.connect()` ?**

2. **Pourquoi utilise-t-on `\n` comme délimiteur de message ?**

3. **Que se passe-t-il si on oublie d'appeler `socket.close()` ?**

4. **Expliquez le rôle du paramètre `daemon=True` dans les threads.**

5. **Que retourne `socket.recv(4096)` si moins de 4096 octets sont disponibles ?**

### Questions intermédiaires

6. **Pourquoi le serveur utilise-t-il `0.0.0.0` et pas `127.0.0.1` dans `bind()` ?**

7. **Comment le client sait-il qu'un message JSON est complet dans le flux TCP ?**

8. **Que se passe-t-il si deux clients se connectent simultanément ? Expliquez le rôle de `listen(5)`.**

9. **Pourquoi sérialise-t-on les données en JSON plutôt que d'envoyer directement un dictionnaire Python ?**

10. **Que se passerait-il si on supprimait le `time.sleep(2)` dans `handle_client()` ?**

### Questions avancées

11. **Implémentez un mécanisme de heartbeat : le client envoie un "ping" toutes les 30 secondes, et le serveur répond "pong". Si pas de ping pendant 1 minute, le serveur déconnecte le client.**

12. **Modifiez le protocole pour que le client puisse demander les données d'une ville spécifique en envoyant un message au serveur.**

13. **Le code actuel utilise des threads. Réécrivez le serveur avec `asyncio` pour gérer les connexions de manière asynchrone.**

14. **Ajoutez une authentification : le client doit envoyer un token valide dans les 5 premières secondes, sinon il est déconnecté.**

15. **Implémentez un mécanisme de "subscription" : le client peut s'abonner à certains types d'alertes uniquement (chaleur, vent, humidité).**

### Questions de réflexion

16. **Quels sont les risques de sécurité de ce système ? Comment un attaquant pourrait-il exploiter le serveur ?**

17. **Comment adapter ce système pour supporter 10 000 clients simultanés ?**

18. **Proposez une architecture pour synchroniser plusieurs serveurs météo entre eux (réplication des données).**

19. **Comment implémenter une file d'attente de messages si un client est temporairement déconnecté ?**

20. **Comparez cette architecture avec une approche pub/sub (MQTT, Redis Pub/Sub). Quels sont les avantages et inconvénients ?**

---

## 🔬 Exercices pratiques

### Exercice 1 : Gestion d'erreurs
Améliorez la gestion d'erreurs du client pour qu'il affiche des messages détaillés selon le type d'erreur (timeout, connexion refusée, format JSON invalide, etc.).

### Exercice 2 : Protocole de commandes
Implémentez un protocole où le client peut envoyer des commandes :
- `GET_CURRENT` : Données actuelles
- `GET_FORECAST` : Prévisions uniquement
- `SET_CITY Paris` : Changer de ville

### Exercice 3 : Compression
Ajoutez la compression gzip des données JSON avant envoi et décompression côté client.

### Exercice 4 : Interface graphique
Créez une interface graphique avec Tkinter pour afficher les données météo en temps réel.

### Exercice 5 : Base de données
Ajoutez une base de données SQLite pour stocker l'historique des données météo et permettre aux clients de requêter l'historique.

---

## 📚 Ressources complémentaires

### Documentation officielle
- [Socket Programming HOWTO](https://docs.python.org/3/howto/sockets.html)
- [Threading in Python](https://docs.python.org/3/library/threading.html)
- [JSON en Python](https://docs.python.org/3/library/json.html)

### Concepts réseau
- TCP/IP Protocol Suite
- OSI Model (7 layers)
- Port numbers and IANA assignments

### Livres recommandés
- "Computer Networking: A Top-Down Approach" - Kurose & Ross
- "Python Network Programming Cookbook" - Pradeeban Kathiravelu

---

## ✅ Checklist de maîtrise

Après avoir étudié ce projet, vous devriez être capable de :

- [ ] Expliquer le fonctionnement d'un socket TCP
- [ ] Créer un serveur multi-clients
- [ ] Gérer la sérialisation/désérialisation des données
- [ ] Utiliser le threading pour la parallélisation
- [ ] Implémenter un protocole de communication simple
- [ ] Gérer les erreurs réseau courantes
- [ ] Comprendre les différences entre TCP et UDP
- [ ] Déboguer des problèmes de connexion réseau

---

**Bon apprentissage ! 🎓**
