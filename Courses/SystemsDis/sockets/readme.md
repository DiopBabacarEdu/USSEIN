# Programmation des Sockets en Python

## Table des matières
1. [Introduction aux Sockets](#introduction)
2. [Concepts Fondamentaux](#concepts-fondamentaux)
3. [Les Sockets TCP en Détail](#sockets-tcp)
4. [Création d'un Echo Server et Client](#echo-server-client)
5. [Gestion de Connexions Multiples](#connexions-multiples)
6. [Application Client-Serveur Avancée](#application-avancee)
7. [Dépannage](#depannage)
8. [Exercices Pratiques](#exercices)

---

## 1. Introduction aux Sockets {#introduction}

### Qu'est-ce qu'un Socket ?

Un **socket** est un point de terminaison pour l'envoi ou la réception de données à travers un réseau. C'est l'interface entre votre application et le réseau.

**Analogie :** Pensez à un socket comme à une prise électrique :
- La prise (socket) est le point de connexion
- Le câble (réseau) transporte l'information
- Les appareils (applications) communiquent à travers cette connexion

### Historique

Les sockets ont été introduits avec ARPANET en 1971 et sont devenus une API standard avec Berkeley Software Distribution (BSD) en 1983. Aujourd'hui, ils restent la base de toute communication réseau.

### Pourquoi les Sockets ?

Les sockets permettent la **communication inter-processus (IPC)** sur le réseau. Ils sont essentiels pour :
- Applications client-serveur (web, messagerie, etc.)
- Jeux en ligne multijoueurs
- Applications de chat
- Transfert de fichiers
- APIs réseau

---

## 2. Concepts Fondamentaux {#concepts-fondamentaux}

### Types de Sockets

#### Socket TCP (SOCK_STREAM)
- **Fiable** : Les paquets perdus sont détectés et retransmis
- **Ordonné** : Les données arrivent dans l'ordre d'envoi
- **Orienté connexion** : Une connexion est établie avant la communication

```python
socket.socket(socket.AF_INET, socket.SOCK_STREAM)
```

#### Socket UDP (SOCK_DGRAM)
- **Non fiable** : Pas de garantie de livraison
- **Non ordonné** : Les données peuvent arriver dans le désordre
- **Sans connexion** : Envoi direct sans établir de connexion

### Familles d'Adresses

- **AF_INET** : IPv4 (ex: 192.168.1.1)
- **AF_INET6** : IPv6 (ex: 2001:0db8:85a3::1)
- **AF_UNIX** : Communication locale entre processus sur la même machine

### Flux de Communication TCP

```
CLIENT                          SERVER
------                          ------
socket()                        socket()
   |                            bind()
   |                            listen()
connect() ------------------>   accept()
   |                               |
send() ----------------------->  recv()
recv() <-----------------------  send()
   |                               |
close() <---------------------> close()
```

---

## 3. Les Sockets TCP en Détail {#sockets-tcp}

### API Socket Python

Les principales fonctions et méthodes :

| Fonction | Description |
|----------|-------------|
| `socket()` | Crée un nouveau socket |
| `.bind()` | Associe le socket à une adresse/port |
| `.listen()` | Met le socket en mode écoute |
| `.accept()` | Accepte une connexion entrante |
| `.connect()` | Initie une connexion au serveur |
| `.send()` | Envoie des données |
| `.recv()` | Reçoit des données |
| `.close()` | Ferme le socket |

### Pourquoi choisir TCP ?

**TCP garantit :**
1. **Fiabilité** : Détection et retransmission automatique des paquets perdus
2. **Ordre** : Les données sont lues dans l'ordre d'envoi
3. **Contrôle de flux** : Adaptation automatique au débit du réseau

**Cas d'usage idéaux pour TCP :**
- Transfert de fichiers
- Pages web (HTTP/HTTPS)
- Emails (SMTP, IMAP)
- Applications nécessitant une livraison garantie

---

## 4. Création d'un Echo Server et Client {#echo-server-client}

### Echo Server - Version Simple

```python
import socket

HOST = "127.0.0.1"  # Localhost
PORT = 65432        # Port d'écoute

# Création du socket
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))        # Liaison au port
    s.listen()                  # Mode écoute
    conn, addr = s.accept()     # Acceptation d'une connexion
    
    with conn:
        print(f"Connecté par {addr}")
        while True:
            data = conn.recv(1024)  # Réception de données
            if not data:
                break
            conn.sendall(data)      # Renvoi des données
```

**Explications détaillées :**

1. **`socket.socket(socket.AF_INET, socket.SOCK_STREAM)`**
   - Crée un socket IPv4 (AF_INET) de type TCP (SOCK_STREAM)
   - Le `with` assure la fermeture automatique

2. **`s.bind((HOST, PORT))`**
   - Associe le socket à l'adresse IP et au port
   - `127.0.0.1` = interface loopback (local seulement)
   - Ports > 1023 ne nécessitent pas de privilèges superutilisateur

3. **`s.listen()`**
   - Met le socket en mode écoute pour accepter des connexions
   - Paramètre optionnel : taille de la file d'attente

4. **`conn, addr = s.accept()`**
   - **Bloque** jusqu'à ce qu'un client se connecte
   - Retourne un nouveau socket (`conn`) pour cette connexion
   - `addr` contient l'adresse du client

5. **`conn.recv(1024)`**
   - Lit jusqu'à 1024 octets
   - Retourne `b''` (bytes vide) quand le client ferme la connexion

### Echo Client - Version Simple

```python
import socket

HOST = "127.0.0.1"
PORT = 65432

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))         # Connexion au serveur
    s.sendall(b"Hello, world")      # Envoi du message
    data = s.recv(1024)             # Réception de la réponse

print(f"Reçu : {data!r}")
```

### Exécution

**Terminal 1 (Serveur) :**
```bash
$ python echo-server.py
Connecté par ('127.0.0.1', 64623)
```

**Terminal 2 (Client) :**
```bash
$ python echo-client.py
Reçu : b'Hello, world'
```

### Inspection de l'État des Sockets

**Avec `netstat` :**
```bash
$ netstat -an | grep 65432
tcp4  0  0  127.0.0.1.65432  *.*  LISTEN
```

**Avec `lsof` (Linux/macOS) :**
```bash
$ lsof -i -n
Python  67982  user  3u  IPv4  TCP *:65432 (LISTEN)
```

---

## 5. Gestion de Connexions Multiples {#connexions-multiples}

### Problèmes du Echo Server Simple

1. **Une seule connexion** : Le serveur se termine après avoir servi un client
2. **Réception partielle** : `.recv(1024)` peut retourner moins de 1024 octets
3. **Envoi partiel** : `.send()` peut envoyer moins d'octets que demandé

### Solution : Module `selectors`

Le module `selectors` permet de surveiller plusieurs sockets simultanément sans threads ni processus.

**Avantages :**
- Utilise l'implémentation la plus efficace selon l'OS (epoll, kqueue, select)
- Plus simple que les threads pour les opérations I/O
- Pas de problèmes de concurrence

### Multi-Connection Server

```python
import sys
import socket
import selectors
import types

sel = selectors.DefaultSelector()

def accept_wrapper(sock):
    conn, addr = sock.accept()
    print(f"Connexion acceptée de {addr}")
    conn.setblocking(False)  # Mode non-bloquant
    
    # Données associées au socket
    data = types.SimpleNamespace(addr=addr, inb=b"", outb=b"")
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    sel.register(conn, events, data=data)

def service_connection(key, mask):
    sock = key.fileobj
    data = key.data
    
    if mask & selectors.EVENT_READ:
        recv_data = sock.recv(1024)
        if recv_data:
            data.outb += recv_data
        else:
            print(f"Fermeture de {data.addr}")
            sel.unregister(sock)
            sock.close()
    
    if mask & selectors.EVENT_WRITE:
        if data.outb:
            print(f"Echo vers {data.addr}: {data.outb!r}")
            sent = sock.send(data.outb)
            data.outb = data.outb[sent:]

# Configuration du serveur
host, port = sys.argv[1], int(sys.argv[2])
lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
lsock.bind((host, port))
lsock.listen()
print(f"Écoute sur {(host, port)}")
lsock.setblocking(False)
sel.register(lsock, selectors.EVENT_READ, data=None)

# Boucle d'événements
try:
    while True:
        events = sel.select(timeout=None)
        for key, mask in events:
            if key.data is None:
                accept_wrapper(key.fileobj)
            else:
                service_connection(key, mask)
except KeyboardInterrupt:
    print("Interruption clavier")
finally:
    sel.close()
```

**Points clés :**

1. **`setblocking(False)`** : Mode non-bloquant
   - Les appels ne bloquent pas l'exécution
   - Permet de gérer plusieurs connexions

2. **`sel.register()`** : Enregistre un socket à surveiller
   - `EVENT_READ` : Prêt pour la lecture
   - `EVENT_WRITE` : Prêt pour l'écriture

3. **`sel.select()`** : Attend des événements
   - Retourne une liste de tuples (key, mask)
   - `key.fileobj` = le socket
   - `key.data` = données personnalisées associées

4. **Gestion du buffer** : 
   - `data.outb[sent:]` retire les octets envoyés
   - Nécessaire car `.send()` peut envoyer partiellement

### Multi-Connection Client

```python
import sys
import socket
import selectors
import types

sel = selectors.DefaultSelector()
messages = [b"Message 1", b"Message 2"]

def start_connections(host, port, num_conns):
    server_addr = (host, port)
    for i in range(num_conns):
        connid = i + 1
        print(f"Connexion {connid} vers {server_addr}")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setblocking(False)
        sock.connect_ex(server_addr)
        
        events = selectors.EVENT_READ | selectors.EVENT_WRITE
        data = types.SimpleNamespace(
            connid=connid,
            msg_total=sum(len(m) for m in messages),
            recv_total=0,
            messages=messages.copy(),
            outb=b"",
        )
        sel.register(sock, events, data=data)

def service_connection(key, mask):
    sock = key.fileobj
    data = key.data
    
    if mask & selectors.EVENT_READ:
        recv_data = sock.recv(1024)
        if recv_data:
            print(f"Reçu de connexion {data.connid}: {recv_data!r}")
            data.recv_total += len(recv_data)
        
        if not recv_data or data.recv_total == data.msg_total:
            print(f"Fermeture connexion {data.connid}")
            sel.unregister(sock)
            sock.close()
    
    if mask & selectors.EVENT_WRITE:
        if not data.outb and data.messages:
            data.outb = data.messages.pop(0)
        if data.outb:
            print(f"Envoi vers {data.connid}: {data.outb!r}")
            sent = sock.send(data.outb)
            data.outb = data.outb[sent:]

# Utilisation
host, port = sys.argv[1], int(sys.argv[2])
num_conns = int(sys.argv[3])

start_connections(host, port, num_conns)

try:
    while True:
        events = sel.select(timeout=1)
        if events:
            for key, mask in events:
                service_connection(key, mask)
        # Vérifier s'il reste des connexions
        if not sel.get_map():
            break
except KeyboardInterrupt:
    print("Interruption")
finally:
    sel.close()
```

**Exécution :**

```bash
# Terminal 1
$ python multiconn-server.py 127.0.0.1 65432

# Terminal 2
$ python multiconn-client.py 127.0.0.1 65432 2
```

---

## 6. Application Client-Serveur Avancée {#application-avancee}

### Problématique : Les Frontières de Messages

**Problème :** TCP envoie un flux continu d'octets, sans notion de "message".

**Question :** Comment savoir où un message commence et se termine ?

**Solutions possibles :**
1. **Messages à longueur fixe** : Inefficace pour petits messages
2. **Délimiteur spécial** : Peut apparaître dans les données
3. **En-tête de longueur** : Solution standard ✅

### Architecture des Messages

```
[2 octets: longueur JSON header]
[JSON header: métadonnées]
[Contenu du message]
```

**Exemple visuel :**
```
┌────────────┬──────────────────────────┬─────────────────┐
│  \x00\x64  │  {"content-length": 41}  │  {données...}   │
└────────────┴──────────────────────────┴─────────────────┘
  Longueur      En-tête JSON (100 bytes)   Contenu (41 bytes)
```

### En-tête de Protocole

**Structure JSON :**
```json
{
  "byteorder": "little",
  "content-type": "text/json",
  "content-encoding": "utf-8",
  "content-length": 41
}
```

**Champs requis :**
- `byteorder` : Ordre des octets de la machine
- `content-type` : Type de contenu (text/json, binary/custom)
- `content-encoding` : Encodage (utf-8, binary)
- `content-length` : Taille du contenu en octets

### Classe Message - Architecture

```python
class Message:
    def __init__(self, selector, sock, addr):
        self.selector = selector
        self.sock = sock
        self.addr = addr
        self._recv_buffer = b""
        self._send_buffer = b""
        self._jsonheader_len = None
        self.jsonheader = None
        self.request = None
        self.response_created = False
```

**Méthodes principales :**
- `process_events(mask)` : Point d'entrée, appelé par le sélecteur
- `read()` : Gère la lecture et traite les données reçues
- `write()` : Gère l'écriture des réponses
- `process_protoheader()` : Traite l'en-tête de 2 octets
- `process_jsonheader()` : Traite l'en-tête JSON
- `process_request()` : Traite la requête du client

### Lecture d'un Message (Serveur)

```python
def read(self):
    self._read()  # Lit les données du socket
    
    # Étape 1 : Lire l'en-tête de longueur (2 octets)
    if self._jsonheader_len is None:
        self.process_protoheader()
    
    # Étape 2 : Lire l'en-tête JSON
    if self._jsonheader_len is not None:
        if self.jsonheader is None:
            self.process_jsonheader()
    
    # Étape 3 : Lire le contenu
    if self.jsonheader:
        if self.request is None:
            self.process_request()

def process_protoheader(self):
    hdrlen = 2
    if len(self._recv_buffer) >= hdrlen:
        self._jsonheader_len = struct.unpack(
            ">H", self._recv_buffer[:hdrlen]
        )[0]
        self._recv_buffer = self._recv_buffer[hdrlen:]

def process_jsonheader(self):
    hdrlen = self._jsonheader_len
    if len(self._recv_buffer) >= hdrlen:
        self.jsonheader = json.loads(
            self._recv_buffer[:hdrlen].decode("utf-8")
        )
        self._recv_buffer = self._recv_buffer[hdrlen:]

def process_request(self):
    content_len = self.jsonheader["content-length"]
    if len(self._recv_buffer) >= content_len:
        data = self._recv_buffer[:content_len]
        self._recv_buffer = self._recv_buffer[content_len:]
        
        if self.jsonheader["content-type"] == "text/json":
            encoding = self.jsonheader["content-encoding"]
            self.request = json.loads(data.decode(encoding))
        else:
            self.request = data
        
        # Passer en mode écriture
        self._set_selector_events_mask("w")
```

### Écriture d'un Message (Serveur)

```python
def write(self):
    if self.request:
        if not self.response_created:
            self.create_response()
    
    self._write()

def create_response(self):
    if self.jsonheader["content-type"] == "text/json":
        response = self._create_response_json_content()
    else:
        response = self._create_response_binary_content()
    
    message = self._create_message(**response)
    self.response_created = True
    self._send_buffer += message

def _create_message(self, *, content_bytes, content_type, content_encoding):
    jsonheader = {
        "byteorder": sys.byteorder,
        "content-type": content_type,
        "content-encoding": content_encoding,
        "content-length": len(content_bytes),
    }
    jsonheader_bytes = json.dumps(jsonheader).encode("utf-8")
    message_hdr = struct.pack(">H", len(jsonheader_bytes))
    message = message_hdr + jsonheader_bytes + content_bytes
    return message
```

### Application Exemple : Serveur de Recherche

**Structure de la requête (client) :**
```json
{
  "type": "text/json",
  "encoding": "utf-8",
  "content": {
    "action": "search",
    "value": "morpheus"
  }
}
```

**Structure de la réponse (serveur) :**
```json
{
  "result": "Follow the white rabbit. 🐰"
}
```

**Exécution :**

```bash
# Serveur
$ python app-server.py '' 65432
Listening on ('', 65432)
Received request {'action': 'search', 'value': 'morpheus'}
Sending response...

# Client
$ python app-client.py 127.0.0.1 65432 search morpheus
Got result: Follow the white rabbit. 🐰
```

---

## 7. Dépannage {#depannage}

### Erreurs Courantes

#### 1. Connection Refused
```python
ConnectionRefusedError: [Errno 61] Connection refused
```
**Causes :**
- Le serveur n'est pas démarré
- Mauvais port ou adresse
- Pare-feu bloquant la connexion

**Solutions :**
- Vérifier que le serveur écoute : `netstat -an | grep PORT`
- Tester avec `telnet HOST PORT`

#### 2. Address Already in Use
```python
OSError: [Errno 48] Address already in use
```
**Cause :** Le port est encore en état TIME_WAIT

**Solution :**
```python
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
```

#### 3. BlockingIOError
```python
BlockingIOError: [Errno 35] Resource temporarily unavailable
```
**Cause :** Socket non-bloquant, opération non prête

**Solution :** C'est normal ! Gérer avec try/except
```python
try:
    data = sock.recv(1024)
except BlockingIOError:
    pass  # Réessayer plus tard
```

#### 4. Broken Pipe
```python
BrokenPipeError: [Errno 32] Broken pipe
```
**Cause :** L'autre côté a fermé la connexion

**Solution :** Toujours vérifier si `recv()` retourne `b''`

### Outils de Diagnostic

#### ping - Tester la Connectivité
```bash
$ ping 127.0.0.1
PING 127.0.0.1: 56 data bytes
64 bytes from 127.0.0.1: icmp_seq=0 ttl=64 time=0.058 ms
```

#### netstat - État des Sockets
```bash
$ netstat -an | grep 65432
tcp4  0  0  127.0.0.1.65432  *.*  LISTEN
```

**Colonnes importantes :**
- `Recv-Q` : Octets en attente de lecture
- `Send-Q` : Octets en attente d'envoi
- `State` : État de la connexion (LISTEN, ESTABLISHED, etc.)

#### lsof - Fichiers Ouverts
```bash
$ lsof -i -n
Python  67982  user  3u  IPv4  TCP *:65432 (LISTEN)
```

#### tcpdump/Wireshark - Capture de Paquets
```bash
$ sudo tcpdump -i lo0 port 65432 -X
```

### Checklist de Débogage

1. ✅ Le serveur est-il démarré ?
2. ✅ Les adresses IP et ports sont-ils corrects ?
3. ✅ Le pare-feu autorise-t-il la connexion ?
4. ✅ Les données sont-elles bien encodées/décodées ?
5. ✅ Les buffers sont-ils vidés correctement ?
6. ✅ Les erreurs sont-elles bien gérées ?
7. ✅ Les sockets sont-ils fermés proprement ?

---

## 8. Exercices Pratiques {#exercices}

### Exercice 1 : Chat Simple

**Objectif :** Créer un serveur de chat où plusieurs clients peuvent envoyer des messages visibles par tous.

**Spécifications :**
- Le serveur accepte plusieurs connexions
- Chaque message reçu est diffusé à tous les clients
- Format : `[Nom d'utilisateur]: Message`

**Squelette :**
```python
# À compléter
clients = {}  # {socket: username}

def broadcast(message, sender_sock):
    """Envoie un message à tous les clients sauf l'émetteur"""
    pass

def handle_client(sock, mask):
    """Gère les messages d'un client"""
    pass
```

### Exercice 2 : Transfert de Fichiers

**Objectif :** Implémenter un client-serveur pour transférer des fichiers.

**Spécifications :**
- Le client envoie un nom de fichier
- Le serveur envoie le contenu du fichier
- Gestion des fichiers volumineux (lecture par chunks)
- Barre de progression côté client

**Protocole suggéré :**
```json
// Requête
{"action": "download", "filename": "document.pdf"}

// Réponse
{"filename": "document.pdf", "size": 1048576, "data": "..."}
```

### Exercice 3 : API RESTful Simple

**Objectif :** Créer une mini-API REST avec sockets.

**Endpoints :**
- `GET /users` : Liste des utilisateurs
- `POST /users` : Créer un utilisateur
- `GET /users/:id` : Détails d'un utilisateur

**Format de requête :**
```json
{
  "method": "GET",
  "path": "/users",
  "body": null
}
```

### Exercice 4 : Jeu Multi-joueurs

**Objectif :** Créer un jeu Pierre-Papier-Ciseaux multijoueur.

**Fonctionnalités :**
- 2 joueurs se connectent
- Chacun envoie son choix
- Le serveur détermine le gagnant
- Score persistant

**États du jeu :**
1. Attente de joueurs
2. En cours (choix)
3. Résultat
4. Nouvelle partie

### Exercice 5 : Proxy HTTP Simple

**Objectif :** Implémenter un proxy HTTP basique.

**Comportement :**
- Écoute sur le port 8888
- Reçoit des requêtes HTTP
- Transfère au serveur cible
- Retourne la réponse au client

**Bonus :** Mise en cache des réponses

---

## Concepts Avancés

### Gestion de l'Endianness

**Problème :** Différents CPU stockent les octets dans des ordres différents.

**Solution :** Utiliser l'ordre réseau (big-endian)
```python
import struct

# Empaquetage en big-endian (network byte order)
data = struct.pack(">H", 1024)  # \x04\x00

# Dépaquetage
value = struct.unpack(">H", data)[0]  # 1024
```

**Formats struct :**
- `>` : Big-endian (réseau)
- `<` : Little-endian
- `H` : Unsigned short (2 octets)
- `I` : Unsigned int (4 octets)

### Timeouts

```python
# Timeout sur recv
sock.settimeout(5.0)  # 5 secondes

try:
    data = sock.recv(1024)
except socket.timeout:
    print("Timeout !")
```

### Socket Options

```python
# Réutiliser l'adresse immédiatement
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# Désactiver l'algorithme de Nagle (réduire la latence)
sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

# Buffer de réception
sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 65536)
```

### Fermeture Propre

```python
# Fermeture en écriture (envoi FIN)
sock.shutdown(socket.SHUT_WR)

# Lecture des données restantes
while True:
    data = sock.recv(1024)
    if not data:
        break

# Fermeture complète
sock.close()
```

---

## Bonnes Pratiques

### ✅ À Faire

1. **Toujours gérer les erreurs**
```python
try:
    sock.connect((host, port))
except ConnectionRefusedError:
    print("Serveur non disponible")
except socket.timeout:
    print("Timeout de connexion")
```

2. **Utiliser le context manager**
```python
with socket.socket() as sock:
    # Le socket sera fermé automatiquement
    pass
```

3. **Vérifier les retours de recv() et send()**
```python
data = sock.recv(1024)
if not data:
    # Connexion fermée
    break

sent = sock.send(message)
message = message[sent:]  # Retirer ce qui a été envoyé
```

4. **Mode non-bloquant pour connexions multiples**
```python
sock.setblocking(False)
```

5. **Encoder/décoder explicitement**
```python
message = "Hello".encode('utf-8')
text = data.decode('utf-8')
```

### ❌ À Éviter

1. **Ne pas ignorer les exceptions**
```python
# MAUVAIS
try:
    sock.send(data)
except:
    pass  # Erreur ignorée !
```

2. **Ne pas supposer recv() retourne tout**
```python
# MAUVAIS
data = sock.recv(1024)
# Peut retourner moins que prévu !

# BON
buffer = b""
while len(buffer) < expected_length:
    data = sock.recv(expected_length - len(buffer))
    if not data:
        break
    buffer += data
```

3. **Ne pas oublier de fermer**
```python
# MAUVAIS
sock = socket.socket()
# ... utilisation ...
# Oubli de sock.close() !

# BON
with socket.socket() as sock:
    # ... utilisation ...
```

4. **Ne pas bloquer dans une boucle d'événements**
```python
# MAUVAIS dans select()
def handle(sock):
    time.sleep(5)  # Bloque tout !
    
# BON
def handle(sock):
    # Opérations non-bloquantes uniquement
    pass
```

---

## Résumé des Points Clés

### Architecture Client-Serveur

```
1. Serv
