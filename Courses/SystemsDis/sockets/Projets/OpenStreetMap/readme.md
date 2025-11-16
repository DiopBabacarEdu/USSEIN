# Projet Client-Serveur TCP avec utilisation d'API OpenStreetMap

Dans ce projet, l'objectif c'est de créer un serveur répondant aux requêtes ("search" et "reverse") des clients TCP, en utilisant les API d'OpenStreetMap.

<img width="1000" height="500" alt="image" src="https://github.com/user-attachments/assets/13f27d60-67d3-4145-9992-f441c6a79adb" />

## Table des Matières
1. [Architecture du Projet](#architecture)
2. [Côté Serveur](#serveur)
3. [Côté Client](#client)
4. [Tests et Démonstration](#tests)
5. [Dépannage](#depannage)

## Architecture du Projet <a name="architecture"></a>

### Structure des fichiers
```
projet-osm/
├── server/
│   ├── server.py
│   └── requirements.txt
├── client/
│   ├── client.py
│   └── requirements.txt
└── README.md
```

### Flux de communication
```
Client → Serveur TCP → API OpenStreetMap → Serveur TCP → Client
```

## Côté Serveur <a name="serveur"></a>

### Étape 1: Configuration de base du serveur

**Objectif** : Créer un serveur TCP qui écoute sur un port spécifique.

```python
# server.py - Partie 1
import socket
import threading

class OSMServer:
    def __init__(self, host='localhost', port=8888):
        self.host = host
        self.port = port
        self.socket = None
        self.running = False
```

### Étape 2: Démarrage du serveur

**Objectif** : Initialiser le socket et accepter les connexions entrantes.

```python
# server.py - Partie 2
def start_server(self):
    """Démarre le serveur TCP"""
    try:
        # Création du socket TCP
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        # Permettre la réutilisation de l'adresse
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        # Liaison du socket à l'adresse et port
        self.socket.bind((self.host, self.port))
        
        # Mise en écoute (backlog de 5 connexions)
        self.socket.listen(5)
        self.running = True
        
        print(f"✅ Serveur démarré sur {self.host}:{self.port}")
        
        # Boucle principale d'acceptation des connexions
        while self.running:
            client_socket, client_address = self.socket.accept()
            print(f"🔗 Connexion établie avec {client_address}")
            
            # Créer un thread pour chaque client
            client_thread = threading.Thread(
                target=self.handle_client,
                args=(client_socket, client_address)
            )
            client_thread.daemon = True
            client_thread.start()
            
    except Exception as e:
        print(f"❌ Erreur serveur: {e}")
    finally:
        self.stop_server()
```

### Étape 3: Gestion des clients

**Objectif** : Gérer la communication avec chaque client dans un thread séparé.

```python
# server.py - Partie 3
def handle_client(self, client_socket, client_address):
    """Gère la communication avec un client"""
    try:
        while True:
            # Recevoir les données (max 1024 bytes)
            data = client_socket.recv(1024).decode('utf-8')
            
            if not data:
                break  # Client déconnecté
                
            print(f"📨 Données reçues: {data}")
            
            # Traiter la requête et envoyer une réponse
            response = self.process_request(data)
            client_socket.send(response.encode('utf-8'))
            
    except Exception as e:
        print(f"❌ Erreur avec le client {client_address}: {e}")
    finally:
        client_socket.close()
        print(f"🔒 Connexion fermée avec {client_address}")
```

### Étape 4: Intégration avec OpenStreetMap

**Objectif** : Interroger l'API Nominatim d'OpenStreetMap.

```python
# server.py - Partie 4
import requests
import json
from urllib.parse import quote

def search_osm(self, query):
    """Recherche d'adresse avec l'API Nominatim"""
    try:
        # Encodage de la requête pour URL
        encoded_query = quote(query)
        url = f"https://nominatim.openstreetmap.org/search?q={encoded_query}&format=json&limit=5"
        
        # Headers requis par l'API OSM
        headers = {
            'User-Agent': 'OSM-Server-Tutorial/1.0',
            'Accept': 'application/json'
        }
        
        # Requête HTTP GET
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Lève une exception pour les codes d'erreur HTTP
        
        return response.json()
        
    except requests.RequestException as e:
        print(f"❌ Erreur API OSM: {e}")
        return []
```

### Étape 5: Traitement des requêtes client

**Objectif** : Parser les requêtes JSON et router vers la bonne fonction.

```python
# server.py - Partie 5
def process_request(self, data):
    """Traite la requête du client et retourne une réponse JSON"""
    try:
        # Conversion de la chaîne JSON en dictionnaire Python
        request = json.loads(data)
        action = request.get('action')
        
        if action == 'search':
            query = request.get('query', '')
            results = self.search_osm(query)
            response = {
                'status': 'success',
                'results': results
            }
            
        elif action == 'reverse':
            lat = request.get('lat')
            lon = request.get('lon')
            results = self.reverse_geocode(lat, lon)
            response = {
                'status': 'success',
                'results': results
            }
            
        else:
            response = {
                'status': 'error',
                'message': 'Action non supportée'
            }
            
    except json.JSONDecodeError:
        response = {
            'status': 'error',
            'message': 'JSON invalide'
        }
    except Exception as e:
        response = {
            'status': 'error',
            'message': f'Erreur: {str(e)}'
        }
    
    # Conversion du dictionnaire en chaîne JSON
    return json.dumps(response)
```

### Étape 6: Code complet du serveur

```python
# server.py - Version complète
import socket
import threading
import json
import requests
from urllib.parse import quote

class OSMServer:
    def __init__(self, host='localhost', port=8888):
        self.host = host
        self.port = port
        self.socket = None
        self.running = False
        
    def start_server(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.bind((self.host, self.port))
            self.socket.listen(5)
            self.running = True
            
            print(f"✅ Serveur OSM démarré sur {self.host}:{self.port}")
            print("📡 En attente de connexions clients...")
            
            while self.running:
                client_socket, client_address = self.socket.accept()
                print(f"🔗 Connexion de {client_address}")
                
                client_thread = threading.Thread(
                    target=self.handle_client,
                    args=(client_socket, client_address)
                )
                client_thread.daemon = True
                client_thread.start()
                
        except Exception as e:
            print(f"❌ Erreur serveur: {e}")
        finally:
            self.stop_server()
    
    def handle_client(self, client_socket, client_address):
        try:
            while True:
                data = client_socket.recv(1024).decode('utf-8')
                if not data:
                    break
                    
                print(f"📨 Requête de {client_address}: {data}")
                response = self.process_request(data)
                client_socket.send(response.encode('utf-8'))
                
        except Exception as e:
            print(f"❌ Erreur client {client_address}: {e}")
        finally:
            client_socket.close()
            print(f"🔒 Déconnexion de {client_address}")
    
    def process_request(self, data):
        try:
            request = json.loads(data)
            action = request.get('action')
            
            if action == 'search':
                query = request.get('query', '')
                results = self.search_osm(query)
                return json.dumps({
                    'status': 'success',
                    'results': results
                })
                
            elif action == 'reverse':
                lat = request.get('lat')
                lon = request.get('lon')
                results = self.reverse_geocode(lat, lon)
                return json.dumps({
                    'status': 'success', 
                    'results': results
                })
                
            else:
                return json.dumps({
                    'status': 'error',
                    'message': 'Action non supportée'
                })
                
        except Exception as e:
            return json.dumps({
                'status': 'error',
                'message': str(e)
            })
    
    def search_osm(self, query):
        try:
            encoded_query = quote(query)
            url = f"https://nominatim.openstreetmap.org/search?q={encoded_query}&format=json&limit=5"
            
            headers = {
                'User-Agent': 'OSM-Server-Tutorial/1.0',
                'Accept': 'application/json'
            }
            
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            print(f"❌ Erreur recherche OSM: {e}")
            return []
    
    def reverse_geocode(self, lat, lon):
        try:
            url = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json"
            
            headers = {
                'User-Agent': 'OSM-Server-Tutorial/1.0', 
                'Accept': 'application/json'
            }
            
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            print(f"❌ Erreur géocodage inverse: {e}")
            return {}
    
    def stop_server(self):
        self.running = False
        if self.socket:
            self.socket.close()
        print("🛑 Serveur arrêté")

if __name__ == "__main__":
    server = OSMServer()
    try:
        server.start_server()
    except KeyboardInterrupt:
        print("\n🛑 Arrêt demandé")
        server.stop_server()
```

## Côté Client <a name="client"></a>

### Étape 1: Connexion au serveur

**Objectif** : Établir une connexion TCP avec le serveur.

```python
# client.py - Partie 1
import socket
import json

class OSMClient:
    def __init__(self, host='localhost', port=8888):
        self.host = host
        self.port = port
        self.socket = None
    
    def connect(self):
        """Établit la connexion avec le serveur"""
        try:
            # Création du socket client
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            
            # Connexion au serveur
            self.socket.connect((self.host, self.port))
            print(f"✅ Connecté au serveur {self.host}:{self.port}")
            return True
            
        except Exception as e:
            print(f"❌ Erreur de connexion: {e}")
            return False
```

### Étape 2: Envoi de requêtes

**Objectif** : Envoyer des requêtes JSON au serveur.

```python
# client.py - Partie 2
def send_request(self, request):
    """Envoie une requête au serveur et retourne la réponse"""
    try:
        # Conversion de la requête en JSON
        request_json = json.dumps(request)
        
        # Envoi des données
        self.socket.send(request_json.encode('utf-8'))
        
        # Réception de la réponse (buffer de 4096 bytes)
        response_data = self.socket.recv(4096).decode('utf-8')
        
        # Conversion de la réponse JSON en dictionnaire Python
        return json.loads(response_data)
        
    except Exception as e:
        print(f"❌ Erreur communication: {e}")
        return None
```

### Étape 3: Fonctions de recherche

**Objectif** : Implémenter les fonctions de recherche et géocodage inverse.

```python
# client.py - Partie 3
def search_address(self, query):
    """Recherche une adresse"""
    # Construction de la requête
    request = {
        'action': 'search',
        'query': query
    }
    
    # Envoi au serveur
    response = self.send_request(request)
    
    if response and response.get('status') == 'success':
        return response.get('results', [])
    else:
        error_msg = response.get('message', 'Erreur inconnue') if response else 'Pas de réponse'
        print(f"❌ Erreur: {error_msg}")
        return []

def reverse_geocode(self, lat, lon):
    """Géocodage inverse (coordonnées → adresse)"""
    request = {
        'action': 'reverse', 
        'lat': str(lat),
        'lon': str(lon)
    }
    
    response = self.send_request(request)
    
    if response and response.get('status') == 'success':
        return response.get('results', {})
    else:
        error_msg = response.get('message', 'Erreur inconnue') if response else 'Pas de réponse'
        print(f"❌ Erreur: {error_msg}")
        return {}
```

### Étape 4: Interface utilisateur

**Objectif** : Créer une interface en ligne de commande interactive.

```python
# client.py - Partie 4
def interactive_mode(self):
    """Mode interactif"""
    print("\n" + "="*50)
    print("🌍 Client OpenStreetMap")
    print("="*50)
    print("Commandes:")
    print("  search <adresse>  - Rechercher une adresse")
    print("  reverse <lat> <lon> - Coordonnées vers adresse") 
    print("  quit              - Quitter")
    print("-"*50)
    
    while True:
        try:
            command = input("\n🔍 Commande > ").strip()
            
            if command.lower() == 'quit':
                break
                
            elif command.startswith('search '):
                query = command[7:]  # Enlève "search "
                if query:
                    self.do_search(query)
                else:
                    print("❌ Usage: search <adresse>")
                    
            elif command.startswith('reverse '):
                parts = command[8:].split()
                if len(parts) == 2:
                    lat, lon = parts
                    self.do_reverse(lat, lon)
                else:
                    print("❌ Usage: reverse <latitude> <longitude>")
                    
            else:
                print("❌ Commande non reconnue")
                
        except KeyboardInterrupt:
            print("\n👋 Au revoir!")
            break
        except Exception as e:
            print(f"❌ Erreur: {e}")

def do_search(self, query):
    """Exécute une recherche et affiche les résultats"""
    print(f"🔎 Recherche: '{query}'")
    results = self.search_address(query)
    self.display_search_results(results)

def do_reverse(self, lat, lon):
    """Exécute un géocodage inverse"""
    print(f"📍 Géocodage inverse: {lat}, {lon}")
    result = self.reverse_geocode(lat, lon)
    self.display_reverse_results(result)
```

### Étape 5: Affichage des résultats

**Objectif** : Formater et afficher joliment les résultats.

```python
# client.py - Partie 5
def display_search_results(self, results):
    """Affiche les résultats de recherche"""
    if not results:
        print("❌ Aucun résultat trouvé")
        return
    
    print(f"\n✅ {len(results)} résultat(s) trouvé(s):")
    print("─" * 80)
    
    for i, result in enumerate(results, 1):
        print(f"{i}. {result.get('display_name', 'N/A')}")
        print(f"   📍 Coordonnées: {result.get('lat', 'N/A')}, {result.get('lon', 'N/A')}")
        print(f"   🏷️  Type: {result.get('type', 'N/A')}")
        print(f"   ⭐ Importance: {result.get('importance', 'N/A')}")
        print()

def display_reverse_results(self, result):
    """Affiche les résultats du géocodage inverse"""
    if not result:
        print("❌ Aucun résultat trouvé")
        return
    
    print(f"\n✅ Adresse trouvée:")
    print("─" * 80)
    print(f"📍 {result.get('display_name', 'N/A')}")
    print(f"🌐 Coordonnées: {result.get('lat', 'N/A')}, {result.get('lon', 'N/A')}")
    
    if 'address' in result:
        print("\n📋 Détails de l'adresse:")
        for key, value in result['address'].items():
            print(f"   {key}: {value}")
```

### Étape 6: Code complet du client

```python
# client.py - Version complète
import socket
import json
import argparse
import sys

class OSMClient:
    def __init__(self, host='localhost', port=8888):
        self.host = host
        self.port = port
        self.socket = None
    
    def connect(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            print(f"✅ Connecté au serveur {self.host}:{self.port}")
            return True
        except Exception as e:
            print(f"❌ Erreur de connexion: {e}")
            return False
    
    def send_request(self, request):
        try:
            request_json = json.dumps(request)
            self.socket.send(request_json.encode('utf-8'))
            response_data = self.socket.recv(4096).decode('utf-8')
            return json.loads(response_data)
        except Exception as e:
            print(f"❌ Erreur communication: {e}")
            return None
    
    def search_address(self, query):
        request = {'action': 'search', 'query': query}
        response = self.send_request(request)
        
        if response and response.get('status') == 'success':
            return response.get('results', [])
        else:
            error_msg = response.get('message', 'Erreur inconnue') if response else 'Pas de réponse'
            print(f"❌ Erreur: {error_msg}")
            return []
    
    def reverse_geocode(self, lat, lon):
        request = {'action': 'reverse', 'lat': str(lat), 'lon': str(lon)}
        response = self.send_request(request)
        
        if response and response.get('status') == 'success':
            return response.get('results', {})
        else:
            error_msg = response.get('message', 'Erreur inconnue') if response else 'Pas de réponse'
            print(f"❌ Erreur: {error_msg}")
            return {}
    
    def interactive_mode(self):
        print("\n" + "="*50)
        print("🌍 Client OpenStreetMap")
        print("="*50)
        print("Commandes:")
        print("  search <adresse>  - Rechercher une adresse")
        print("  reverse <lat> <lon> - Coordonnées vers adresse")
        print("  quit              - Quitter")
        print("-"*50)
        
        while True:
            try:
                command = input("\n🔍 Commande > ").strip()
                
                if command.lower() == 'quit':
                    break
                elif command.startswith('search '):
                    query = command[7:]
                    if query:
                        self.do_search(query)
                    else:
                        print("❌ Usage: search <adresse>")
                elif command.startswith('reverse '):
                    parts = command[8:].split()
                    if len(parts) == 2:
                        lat, lon = parts
                        self.do_reverse(lat, lon)
                    else:
                        print("❌ Usage: reverse <latitude> <longitude>")
                else:
                    print("❌ Commande non reconnue")
                    
            except KeyboardInterrupt:
                print("\n👋 Au revoir!")
                break
            except Exception as e:
                print(f"❌ Erreur: {e}")
    
    def do_search(self, query):
        print(f"🔎 Recherche: '{query}'")
        results = self.search_address(query)
        self.display_search_results(results)
    
    def do_reverse(self, lat, lon):
        print(f"📍 Géocodage inverse: {lat}, {lon}")
        result = self.reverse_geocode(lat, lon)
        self.display_reverse_results(result)
    
    def display_search_results(self, results):
        if not results:
            print("❌ Aucun résultat trouvé")
            return
        
        print(f"\n✅ {len(results)} résultat(s) trouvé(s):")
        print("─" * 80)
        
        for i, result in enumerate(results, 1):
            print(f"{i}. {result.get('display_name', 'N/A')}")
            print(f"   📍 Coordonnées: {result.get('lat', 'N/A')}, {result.get('lon', 'N/A')}")
            print(f"   🏷️  Type: {result.get('type', 'N/A')}")
            print(f"   ⭐ Importance: {result.get('importance', 'N/A')}")
            print()
    
    def display_reverse_results(self, result):
        if not result:
            print("❌ Aucun résultat trouvé")
            return
        
        print(f"\n✅ Adresse trouvée:")
        print("─" * 80)
        print(f"📍 {result.get('display_name', 'N/A')}")
        print(f"🌐 Coordonnées: {result.get('lat', 'N/A')}, {result.get('lon', 'N/A')}")
        
        if 'address' in result:
            print("\n📋 Détails de l'adresse:")
            for key, value in result['address'].items():
                print(f"   {key}: {value}")
    
    def close(self):
        if self.socket:
            self.socket.close()
            print("🔒 Connexion fermée")

def main():
    parser = argparse.ArgumentParser(description='Client OpenStreetMap TCP')
    parser.add_argument('--host', default='localhost', help='Adresse du serveur')
    parser.add_argument('--port', type=int, default=8888, help='Port du serveur')
    parser.add_argument('--search', help='Adresse à rechercher')
    parser.add_argument('--reverse', nargs=2, metavar=('LAT', 'LON'), 
                       help='Coordonnées pour géocodage inverse')
    
    args = parser.parse_args()
    
    client = OSMClient(args.host, args.port)
    
    if not client.connect():
        sys.exit(1)
    
    try:
        if args.search:
            client.do_search(args.search)
        elif args.reverse:
            lat, lon = args.reverse
            client.do_reverse(lat, lon)
        else:
            client.interactive_mode()
    finally:
        client.close()

if __name__ == "__main__":
    main()
```

## Tests et Démonstration <a name="tests"></a>

### Étape 1: Démarrage du serveur

```bash
cd server
pip install requests
python server.py
```

**Sortie attendue:**
```
✅ Serveur OSM démarré sur localhost:8888
📡 En attente de connexions clients...
```

### Étape 2: Test du client

```bash
cd client
python client.py
```

**Session interactive exemple:**
```
🌍 Client OpenStreetMap
==================================================
Commandes:
  search <adresse>  - Rechercher une adresse  
  reverse <lat> <lon> - Coordonnées vers adresse
  quit              - Quitter
--------------------------------------------------

🔍 Commande > search Eiffel Tower

🔎 Recherche: 'Eiffel Tower'

✅ 5 résultat(s) trouvé(s):
────────────────────────────────────────────────────────────────────────────────
1. Tour Eiffel, 5, Avenue Anatole France, Gros-Caillou, 7e, Paris, Île-de-France, France métropolitaine, 75007, France
   📍 Coordonnées: 48.85837009999999, 2.2944813
   🏷️  Type: attraction
   ⭐ Importance: 0.9

🔍 Commande > reverse 48.8584 2.2945

📍 Géocodage inverse: 48.8584, 2.2945

✅ Adresse trouvée:
────────────────────────────────────────────────────────────────────────────────
📍 Tour Eiffel, 5, Avenue Anatole France, Gros-Caillou, 7e, Paris, Île-de-France, France métropolitaine, 75007, France
🌐 Coordonnées: 48.8583701, 2.2944813

📋 Détails de l'adresse:
   tourism: Eiffel Tower
   road: Avenue Anatole France
   ...

🔍 Commande > quit
👋 Au revoir!
🔒 Connexion fermée
```

## Dépannage <a name="depannage"></a>

### Problèmes courants et solutions

1. **"Connection refused"**
   - Vérifiez que le serveur est démarré
   - Vérifiez le port et l'adresse
   - Vérifiez les pare-feux

2. **"Address already in use"**
   - Attendez que le port soit libéré
   - Changez le port dans le code
   - Utilisez `sudo netstat -tulpn | grep 8888` pour trouver le processus

3. **Erreurs API OpenStreetMap**
   - Vérifiez la connexion internet
   - Respectez les conditions d'utilisation (User-Agent)
   - Limitez la fréquence des requêtes

4. **Données tronquées**
   - Augmentez la taille du buffer (4096 au lieu de 1024)
   - Implémentez un protocole avec longueur du message

Ce tutoriel vous guide pas à pas dans la création d'un système client-serveur complet avec sockets TCP et intégration d'API externe.
