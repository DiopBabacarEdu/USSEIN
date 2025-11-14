# Programmation par sockets en Python : tutoriel complet

## Introduction

La programmation par sockets permet de connecter deux nœuds (processus) sur un réseau pour qu'ils échangent des données. En Python, les sockets sont gérés par le module `socket` de la bibliothèque standard, offrant une API simple et élégante. Ce mécanisme sert de base au modèle client-serveur : le client envoie des requêtes de service et le serveur les traite avant de renvoyer des réponses. Les sockets sont couramment utilisés dans les applications de messagerie instantanée, le streaming multimédia, la collaboration en ligne, etc.

## Exemple simple de communication client-serveur

Illustrons le principe par un mini-programme en Python où le client et le serveur échangent un simple message « Hello ». Le serveur attend une connexion, lit un message et répond, tandis que le client envoie le message et affiche la réponse.

### server.py (serveur en Python)

```python
import socket

# Configuration
HOST = '127.0.0.1'  # Adresse locale (localhost)
PORT = 8080         # Port d'écoute

def main():
    # 1. Création du socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # 2. Option pour réutiliser l'adresse immédiatement
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    # 3. Liaison (bind) du socket à l'adresse et au port
    server_socket.bind((HOST, PORT))
    print(f"Serveur démarré sur {HOST}:{PORT}")
    
    # 4. Mise en écoute (listen)
    server_socket.listen(5)  # File d'attente de 5 connexions max
    print("En attente de connexion...")
    
    try:
        # 5. Acceptation d'une connexion entrante
        client_socket, client_address = server_socket.accept()
        print(f"Client connecté : {client_address}")
        
        # 6. Réception du message du client
        data = client_socket.recv(1024)  # Buffer de 1024 octets
        message = data.decode('utf-8')
        print(f"Serveur reçu : {message}")
        
        # 7. Envoi d'une réponse au client
        response = "Hello from server"
        client_socket.send(response.encode('utf-8'))
        print("Serveur : Message envoyé")
        
        # 8. Fermeture de la connexion client
        client_socket.close()
        
    except Exception as e:
        print(f"Erreur : {e}")
    finally:
        # 9. Fermeture du socket serveur
        server_socket.close()
        print("Serveur fermé")

if __name__ == "__main__":
    main()
```

### client.py (client en Python)

```python
import socket

# Configuration
SERVER_HOST = '127.0.0.1'  # Adresse du serveur
SERVER_PORT = 8080         # Port du serveur

def main():
    # 1. Création du socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        # 2. Connexion au serveur
        client_socket.connect((SERVER_HOST, SERVER_PORT))
        print(f"Connecté au serveur {SERVER_HOST}:{SERVER_PORT}")
        
        # 3. Envoi d'un message au serveur
        message = "Hello from client"
        client_socket.send(message.encode('utf-8'))
        print("Client : Message envoyé")
        
        # 4. Réception de la réponse du serveur
        data = client_socket.recv(1024)
        response = data.decode('utf-8')
        print(f"Client reçu : {response}")
        
    except ConnectionRefusedError:
        print("Erreur : Connexion refusée. Le serveur est-il démarré ?")
    except Exception as e:
        print(f"Erreur : {e}")
    finally:
        # 5. Fermeture du socket
        client_socket.close()
        print("Client déconnecté")

if __name__ == "__main__":
    main()
```

### Exécution

Lancez le serveur dans un terminal :

```bash
python server.py
```

Puis le client dans un autre terminal :

```bash
python client.py
```

Vous obtiendrez un échange de messages. Exemple de sortie console :

**Terminal serveur :**
```
Serveur démarré sur 127.0.0.1:8080
En attente de connexion...
Client connecté : ('127.0.0.1', 54321)
Serveur reçu : Hello from client
Serveur : Message envoyé
Serveur fermé
```

**Terminal client :**
```
Connecté au serveur 127.0.0.1:8080
Client : Message envoyé
Client reçu : Hello from server
Client déconnecté
```

## Composants de la programmation par sockets en Python

Le fonctionnement repose sur plusieurs concepts clés :

### Module socket

Le module `socket` de Python fournit une interface pour la programmation réseau bas niveau. Il permet de créer des sockets TCP et UDP avec une syntaxe simple et pythonique.

### Objet socket

Un objet `socket` représente une extrémité de communication réseau. C'est une paire (adresse IP : numéro de port) agissant comme point d'accès pour envoyer ou recevoir des données.

### Types de sockets

Python supporte principalement deux types de communication réseau :

- **Socket TCP (SOCK_STREAM)** : communication fiable et orientée connexion (protocole TCP)
- **Socket UDP (SOCK_DGRAM)** : communication sans connexion, plus rapide mais non garantie (protocole UDP)

### Familles d'adresses

- **AF_INET** : IPv4 (le plus courant)
- **AF_INET6** : IPv6
- **AF_UNIX** : communication locale entre processus sur la même machine

### Modèle client-serveur

Dans ce modèle d'architecture, un serveur attend les requêtes d'un ou plusieurs clients. Le client envoie une requête de service (par exemple, demander des données), et le serveur répond après traitement. Les rôles sont distincts : le serveur crée un socket d'écoute, le client initie la connexion.

## Création du serveur

Pour établir un serveur en Python, on suit ces étapes :

### 1. Création du socket

On crée un socket avec la fonction `socket.socket()` :

```python
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
```

**Paramètres :**
- `socket.AF_INET` : famille d'adresses IPv4
- `socket.SOCK_STREAM` : type TCP (connexion fiable)
- Pour UDP, utilisez `socket.SOCK_DGRAM`

### 2. Configuration optionnelle (setsockopt)

On peut définir des options sur le socket, notamment pour réutiliser immédiatement une adresse/port :

```python
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
```

**Options courantes :**
- `SO_REUSEADDR` : permet de réutiliser une adresse en état TIME_WAIT
- `SO_KEEPALIVE` : active les paquets keep-alive TCP
- `SO_RCVBUF` : définit la taille du buffer de réception
- `SO_SNDBUF` : définit la taille du buffer d'envoi

### 3. Bind (liaison)

On associe le socket à une adresse IP et un port local :

```python
server_socket.bind((HOST, PORT))
```

**Points importants :**
- `HOST` peut être `'127.0.0.1'` (localhost), `'0.0.0.0'` (toutes les interfaces), ou une IP spécifique
- `PORT` doit être un entier entre 1024 et 65535 (ports < 1024 nécessitent des privilèges root)
- Le tuple `(HOST, PORT)` est obligatoire

### 4. Listen (écoute)

On place le socket en mode écoute passive :

```python
server_socket.listen(backlog)
```

Le paramètre `backlog` définit la taille maximale de la file d'attente de connexions en attente. Une valeur typique est 5 ou 10.

### 5. Accept (acceptation)

On accepte une connexion entrante, cette opération bloque jusqu'à ce qu'un client se connecte :

```python
client_socket, client_address = server_socket.accept()
```

**Retours :**
- `client_socket` : nouveau socket pour communiquer avec ce client
- `client_address` : tuple `(ip, port)` du client

### 6. Communication (send/recv)

Une fois connecté, le serveur peut échanger des données :

**Réception de données :**
```python
data = client_socket.recv(1024)  # Reçoit jusqu'à 1024 octets
message = data.decode('utf-8')    # Décode les octets en string
```

**Envoi de données :**
```python
message = "Hello from server"
client_socket.send(message.encode('utf-8'))  # Encode la string en octets
```

**Méthodes alternatives :**
```python
# sendall() garantit l'envoi de toutes les données
client_socket.sendall(message.encode('utf-8'))

# recvfrom() pour UDP (retourne aussi l'adresse de l'expéditeur)
data, address = udp_socket.recvfrom(1024)
```

### 7. Fermeture

Une fois la communication terminée, on ferme les sockets :

```python
client_socket.close()
server_socket.close()
```

**Utilisation du context manager (recommandé) :**
```python
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
    server_socket.bind((HOST, PORT))
    server_socket.listen(5)
    # Le socket sera automatiquement fermé à la sortie du bloc with
```

## Création du client

Le client suit des étapes similaires :

### 1. Création du socket

```python
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
```

### 2. Connexion au serveur

```python
client_socket.connect((SERVER_HOST, SERVER_PORT))
```

Cette méthode établit la connexion au serveur. Si elle échoue, une exception `ConnectionRefusedError` ou `socket.timeout` est levée.

### 3. Communication (envoi/réception)

```python
# Envoi
message = "Hello from client"
client_socket.send(message.encode('utf-8'))

# Réception
data = client_socket.recv(1024)
response = data.decode('utf-8')
```

### 4. Fermeture

```python
client_socket.close()
```

## Serveur multi-clients avec threading

Le serveur basique ne peut gérer qu'un seul client à la fois. Pour gérer plusieurs clients simultanément, on utilise le module `threading` :

### server_multithread.py

```python
import socket
import threading

HOST = '127.0.0.1'
PORT = 8080

def handle_client(client_socket, client_address):
    """Fonction pour gérer chaque client dans un thread séparé"""
    print(f"Nouveau client connecté : {client_address}")
    
    try:
        while True:
            # Réception des données
            data = client_socket.recv(1024)
            if not data:
                # Connexion fermée par le client
                break
            
            message = data.decode('utf-8')
            print(f"Reçu de {client_address} : {message}")
            
            # Envoi d'une réponse
            response = f"Echo: {message}"
            client_socket.send(response.encode('utf-8'))
            
            # Si le client envoie "bye", on termine
            if message.lower() == "bye":
                break
                
    except Exception as e:
        print(f"Erreur avec le client {client_address} : {e}")
    finally:
        client_socket.close()
        print(f"Client déconnecté : {client_address}")

def main():
    # Création du socket serveur
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen(5)
    
    print(f"Serveur multi-thread démarré sur {HOST}:{PORT}")
    print("En attente de connexions...")
    
    try:
        while True:
            # Acceptation d'une nouvelle connexion
            client_socket, client_address = server_socket.accept()
            
            # Création d'un nouveau thread pour ce client
            client_thread = threading.Thread(
                target=handle_client,
                args=(client_socket, client_address)
            )
            client_thread.daemon = True  # Le thread se termine avec le programme
            client_thread.start()
            
    except KeyboardInterrupt:
        print("\nArrêt du serveur...")
    finally:
        server_socket.close()

if __name__ == "__main__":
    main()
```

### Client interactif

```python
import socket
import threading
import sys

SERVER_HOST = '127.0.0.1'
SERVER_PORT = 8080

def receive_messages(client_socket):
    """Thread pour recevoir les messages du serveur"""
    while True:
        try:
            data = client_socket.recv(1024)
            if not data:
                print("\nConnexion fermée par le serveur")
                break
            message = data.decode('utf-8')
            print(f"\nServeur : {message}")
            print("Vous : ", end='', flush=True)
        except Exception as e:
            print(f"\nErreur de réception : {e}")
            break

def main():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        client_socket.connect((SERVER_HOST, SERVER_PORT))
        print(f"Connecté au serveur {SERVER_HOST}:{SERVER_PORT}")
        print("Tapez vos messages (ou 'bye' pour quitter) :")
        
        # Démarrer le thread de réception
        receive_thread = threading.Thread(target=receive_messages, args=(client_socket,))
        receive_thread.daemon = True
        receive_thread.start()
        
        # Boucle d'envoi de messages
        while True:
            message = input("Vous : ")
            if not message:
                continue
                
            client_socket.send(message.encode('utf-8'))
            
            if message.lower() == "bye":
                break
                
    except ConnectionRefusedError:
        print("Erreur : Impossible de se connecter au serveur")
    except Exception as e:
        print(f"Erreur : {e}")
    finally:
        client_socket.close()
        print("Déconnecté")

if __name__ == "__main__":
    main()
```

## Serveur asynchrone avec asyncio

Python 3 offre le module `asyncio` pour une programmation asynchrone moderne, plus efficace que les threads pour gérer de nombreuses connexions :

### server_async.py

```python
import asyncio

HOST = '127.0.0.1'
PORT = 8080

async def handle_client(reader, writer):
    """Coroutine pour gérer chaque client"""
    address = writer.get_extra_info('peername')
    print(f"Nouveau client connecté : {address}")
    
    try:
        while True:
            # Réception des données (asynchrone)
            data = await reader.read(1024)
            if not data:
                break
            
            message = data.decode('utf-8')
            print(f"Reçu de {address} : {message}")
            
            # Envoi d'une réponse
            response = f"Echo: {message}"
            writer.write(response.encode('utf-8'))
            await writer.drain()  # Attend que les données soient envoyées
            
            if message.lower().strip() == "bye":
                break
                
    except Exception as e:
        print(f"Erreur avec {address} : {e}")
    finally:
        writer.close()
        await writer.wait_closed()
        print(f"Client déconnecté : {address}")

async def main():
    # Création du serveur asynchrone
    server = await asyncio.start_server(
        handle_client, HOST, PORT
    )
    
    address = server.sockets[0].getsockname()
    print(f"Serveur asynchrone démarré sur {address}")
    
    async with server:
        await server.serve_forever()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nArrêt du serveur...")
```

### Client asynchrone

```python
import asyncio

SERVER_HOST = '127.0.0.1'
SERVER_PORT = 8080

async def send_messages(writer):
    """Coroutine pour envoyer des messages"""
    loop = asyncio.get_event_loop()
    while True:
        # Lecture asynchrone de l'entrée utilisateur
        message = await loop.run_in_executor(None, input, "Vous : ")
        
        writer.write(message.encode('utf-8'))
        await writer.drain()
        
        if message.lower() == "bye":
            break

async def receive_messages(reader):
    """Coroutine pour recevoir des messages"""
    while True:
        data = await reader.read(1024)
        if not data:
            print("\nConnexion fermée par le serveur")
            break
        
        message = data.decode('utf-8')
        print(f"\nServeur : {message}")

async def main():
    try:
        # Connexion au serveur
        reader, writer = await asyncio.open_connection(SERVER_HOST, SERVER_PORT)
        print(f"Connecté au serveur {SERVER_HOST}:{SERVER_PORT}")
        print("Tapez vos messages (ou 'bye' pour quitter) :")
        
        # Exécution concurrente de l'envoi et de la réception
        await asyncio.gather(
            send_messages(writer),
            receive_messages(reader)
        )
        
    except ConnectionRefusedError:
        print("Erreur : Impossible de se connecter au serveur")
    except Exception as e:
        print(f"Erreur : {e}")
    finally:
        writer.close()
        await writer.wait_closed()
        print("Déconnecté")

if __name__ == "__main__":
    asyncio.run(main())
```

## Options avancées des sockets

### Timeout

Définir un timeout pour éviter d'attendre indéfiniment :

```python
# Timeout global sur toutes les opérations
client_socket.settimeout(5.0)  # 5 secondes

# Ou timeout par défaut pour tous les nouveaux sockets
socket.setdefaulttimeout(5.0)
```

### Socket non-bloquant

Passer en mode non-bloquant (retourne immédiatement même sans données) :

```python
server_socket.setblocking(False)
```

### Récupération d'informations

```python
# Obtenir l'adresse locale du socket
local_address = client_socket.getsockname()

# Obtenir l'adresse distante
remote_address = client_socket.getpeername()

# Obtenir les options du socket
buffer_size = client_socket.getsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF)
```

### Configuration TCP avancée

```python
# Désactiver l'algorithme de Nagle (envoie immédiatement)
client_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

# Activer keep-alive
client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)

# Configurer keep-alive (Linux uniquement)
client_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, 60)
client_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, 10)
client_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPCNT, 5)
```

## Gestion des données

### Envoi de données complètes

La méthode `send()` peut ne pas envoyer toutes les données en une fois. Utilisez `sendall()` :

```python
# send() peut envoyer partiellement
bytes_sent = client_socket.send(data)

# sendall() garantit l'envoi complet
client_socket.sendall(data)
```

### Réception de données complètes

La méthode `recv()` peut retourner moins de données que demandé. Pour recevoir exactement N octets :

```python
def recv_all(sock, n):
    """Recevoir exactement n octets"""
    data = bytearray()
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            raise ConnectionError("Connexion fermée prématurément")
        data.extend(packet)
    return bytes(data)

# Utilisation
data = recv_all(client_socket, 1024)
```

### Protocole avec longueur

Pour éviter la troncature, envoyez d'abord la longueur du message :

```python
import struct

def send_message(sock, message):
    """Envoie un message avec sa longueur"""
    data = message.encode('utf-8')
    length = len(data)
    # Envoie la longueur sur 4 octets (entier non signé)
    sock.sendall(struct.pack('!I', length))
    # Envoie les données
    sock.sendall(data)

def recv_message(sock):
    """Reçoit un message avec sa longueur"""
    # Reçoit la longueur (4 octets)
    length_data = recv_all(sock, 4)
    length = struct.unpack('!I', length_data)[0]
    # Reçoit les données
    data = recv_all(sock, length)
    return data.decode('utf-8')
```

## Communication UDP

Pour une communication sans connexion (UDP) :

### Serveur UDP

```python
import socket

HOST = '127.0.0.1'
PORT = 8080

def main():
    # Création d'un socket UDP
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.bind((HOST, PORT))
    
    print(f"Serveur UDP démarré sur {HOST}:{PORT}")
    
    try:
        while True:
            # Réception de données (avec l'adresse de l'expéditeur)
            data, client_address = udp_socket.recvfrom(1024)
            message = data.decode('utf-8')
            print(f"Reçu de {client_address} : {message}")
            
            # Envoi d'une réponse à cet expéditeur
            response = f"Echo: {message}"
            udp_socket.sendto(response.encode('utf-8'), client_address)
            
    except KeyboardInterrupt:
        print("\nArrêt du serveur UDP")
    finally:
        udp_socket.close()

if __name__ == "__main__":
    main()
```

### Client UDP

```python
import socket

SERVER_HOST = '127.0.0.1'
SERVER_PORT = 8080

def main():
    # Création d'un socket UDP
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    try:
        # Envoi de données (pas de connexion préalable)
        message = "Hello from UDP client"
        udp_socket.sendto(message.encode('utf-8'), (SERVER_HOST, SERVER_PORT))
        print("Message UDP envoyé")
        
        # Réception de la réponse
        data, server_address = udp_socket.recvfrom(1024)
        response = data.decode('utf-8')
        print(f"Réponse reçue de {server_address} : {response}")
        
    finally:
        udp_socket.close()

if __name__ == "__main__":
    main()
```

## Problèmes courants et solutions

### Erreur "Address already in use"

**Cause :** Le port est encore utilisé par un processus précédent.

**Solution :**
```python
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
```

### ConnectionRefusedError

**Cause :** Le serveur n'est pas démarré ou écoute sur un port différent.

**Solution :** Vérifiez que le serveur est lancé et que client et serveur utilisent le même port.

### Timeout exception

**Cause :** Aucune donnée reçue dans le délai imparti.

**Solution :**
```python
try:
    client_socket.settimeout(10)  # 10 secondes
    data = client_socket.recv(1024)
except socket.timeout:
    print("Timeout - aucune donnée reçue")
```

### BrokenPipeError / ConnectionResetError

**Cause :** L'autre extrémité a fermé la connexion brutalement.

**Solution :** Vérifiez que `recv()` retourne des données avant d'appeler `send()` :
```python
data = client_socket.recv(1024)
if not data:
    print("Connexion fermée")
    break
```

### Données incomplètes ou tronquées

**Cause :** TCP est un protocole de flux, les messages peuvent être fragmentés.

**Solution :** Utilisez un protocole de délimitation (newline, longueur préfixée, JSON, etc.)

## Exemple complet : Chat multi-utilisateurs

### chat_server.py

```python
import socket
import threading

HOST = '127.0.0.1'
PORT = 8080

# Liste des clients connectés
clients = []
clients_lock = threading.Lock()

def broadcast(message, sender_socket=None):
    """Envoie un message à tous les clients sauf l'expéditeur"""
    with clients_lock:
        for client in clients:
            if client != sender_socket:
                try:
                    client.send(message.encode('utf-8'))
                except:
                    # Supprime le client si l'envoi échoue
                    clients.remove(client)

def handle_client(client_socket, client_address):
    """Gère chaque client"""
    print(f"Nouveau client : {client_address}")
    
    # Ajoute le client à la liste
    with clients_lock:
        clients.append(client_socket)
    
    # Notification aux autres clients
    broadcast(f"[SYSTÈME] Un utilisateur a rejoint le chat ({len(clients)} connecté(s))")
    
    try:
        while True:
            data = client_socket.recv(1024)
            if not data:
                break
            
            message = data.decode('utf-8')
            print(f"{client_address} : {message}")
            
            # Diffusion du message aux autres clients
            formatted_message = f"[{client_address[0]}:{client_address[1]}] {message}"
            broadcast(formatted_message, client_socket)
            
    except Exception as e:
        print(f"Erreur avec {client_address} : {e}")
    finally:
        # Retire le client de la liste
        with clients_lock:
            if client_socket in clients:
                clients.remove(client_socket)
        
        client_socket.close()
        print(f"Client déconnecté : {client_address}")
        broadcast(f"[SYSTÈME] Un utilisateur a quitté le chat ({len(clients)} connecté(s))")

def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen(5)
    
    print(f"Serveur de chat démarré sur {HOST}:{PORT}")
    print("En attente de connexions...")
    
    try:
        while True:
            client_socket, client_address = server_socket.accept()
            thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
            thread.daemon = True
            thread.start()
    except KeyboardInterrupt:
        print("\nArrêt du serveur...")
    finally:
        server_socket.close()

if __name__ == "__main__":
    main()
```

### chat_client.py

```python
import socket
import threading
import sys

SERVER_HOST = '127.0.0.1'
SERVER_PORT = 8080

def receive_messages(client_socket):
    """Thread pour recevoir les messages"""
    while True:
        try:
            data = client_socket.recv(1024)
            if not data:
                print("\n[SYSTÈME] Connexion fermée par le serveur")
                break
            
            message = data.decode('utf-8')
            print(f"\n{message}")
            print(">> ", end='', flush=True)
            
        except Exception as e:
            print(f"\n[ERREUR] {e}")
            break

def main():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        client_socket.connect((SERVER_HOST, SERVER_PORT))
        print(f"Connecté au serveur de chat {SERVER_HOST}:{SERVER_PORT}")
        print("Tapez vos messages et appuyez sur Entrée")
        print("Tapez 'quit' pour quitter\n")
        
        # Thread de réception
        receive_thread = threading.Thread(target=receive_messages, args=(client_socket,))
        receive_thread.daemon = True
        receive_thread.start()
        
        # Boucle d'envoi
        while True:
            message = input(">> ")
            
            if message.lower() == 'quit':
                break
            
            if message.strip():
                client_socket.send(message.encode('utf-8'))
