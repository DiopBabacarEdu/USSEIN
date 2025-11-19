# Programmation Socket TCP en Python

## Table des Matières
1. [Introduction](#introduction)
2. [Gestion des Connexions Multiples](#gestion-des-connexions-multiples)
3. [Serveur et Client Multi-Connexions](#serveur-et-client-multi-connexions)
4. [Application Client-Serveur Avancée](#application-client-serveur-avancée)
5. [Protocole de Communication](#protocole-de-communication)
6. [Dépannage](#dépannage)
7. [Exercices Pratiques](#exercices-pratiques)

---

## Introduction

Ce tutoriel vous guidera à travers les concepts avancés de la programmation socket en Python, en partant des limitations des serveurs simples jusqu'à la création d'applications client-serveur robustes et performantes.

### Prérequis
- Python 3.4+
- Connaissances de base en Python
- Compréhension des concepts réseau de base

---

## Gestion des Connexions Multiples

### 1.1 Les Limitations des Serveurs Simples

Les serveurs echo basiques ont deux problèmes majeurs :

1. **Ils ne servent qu'un seul client** puis se terminent
2. **La gestion des données partielles** : `recv()` peut ne retourner qu'une partie des données

#### Exemple du Problème

```python
# echo-client.py
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    s.sendall(b"Hello, world")
    data = s.recv(1024)  # Peut ne recevoir que b'H' !

print(f"Received {data!r}")
```

**⚠️ Point Important :** L'argument `bufsize=1024` est la quantité MAXIMALE de données à recevoir, pas la quantité garantie !

### 1.2 Gestion de `.send()` et `.recv()`

#### Comportement de `.send()`
```python
# .send() retourne le nombre d'octets envoyés
# qui peut être inférieur à la taille des données
sent = sock.send(data)

# Vous devez vérifier et renvoyer le reste si nécessaire
if sent < len(data):
    remaining = data[sent:]
    # Continuer à envoyer...
```

#### Solution : Utiliser `.sendall()`
```python
# .sendall() continue d'envoyer jusqu'à ce que 
# toutes les données soient envoyées ou qu'une erreur survienne
sock.sendall(b"Hello, world")  # Garantit l'envoi complet
```

### 1.3 Solutions pour la Concurrence

Vous avez plusieurs options pour gérer plusieurs connexions :

| Approche | Avantages | Inconvénients |
|----------|-----------|---------------|
| **Threads** | Traditionnel, bien documenté | Complexe, difficile à déboguer |
| **asyncio** | Moderne, efficace | Courbe d'apprentissage |
| **select()** | Simple, synchrone | Pas de vraie concurrence |

**Pour ce tutoriel, nous utiliserons `.select()`** car :
- ✅ Plus facile à comprendre
- ✅ Pas de problèmes de synchronisation
- ✅ Suffisant pour beaucoup d'applications I/O-bound

### 1.4 Le Module `selectors`

Python fournit le module `selectors` qui utilise l'implémentation la plus efficace selon votre OS :

```python
import selectors

# Crée un sélecteur utilisant la meilleure implémentation disponible
sel = selectors.DefaultSelector()
```

**Avantages :**
- Multiplexage I/O de haut niveau
- Implémentation efficace automatique
- API simple et intuitive

---

## Serveur et Client Multi-Connexions

### 2.1 Architecture du Serveur Multi-Connexions

#### Configuration Initiale

```python
# multiconn-server.py
import sys
import socket
import selectors
import types

sel = selectors.DefaultSelector()

# Configuration du socket d'écoute
host, port = sys.argv[1], int(sys.argv[2])
lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
lsock.bind((host, port))
lsock.listen()
print(f"Listening on {(host, port)}")

# MODE NON-BLOQUANT - Crucial !
lsock.setblocking(False)

# Enregistrement pour surveiller les événements de lecture
sel.register(lsock, selectors.EVENT_READ, data=None)
```

**🔑 Points Clés :**
- `setblocking(False)` : Le socket devient non-bloquant
- `sel.register()` : Surveille le socket pour les événements
- `data=None` : Indique qu'il s'agit du socket d'écoute

#### La Boucle d'Événements

```python
try:
    while True:
        # Bloque jusqu'à ce que des sockets soient prêts
        events = sel.select(timeout=None)
        
        for key, mask in events:
            if key.data is None:
                # Nouveau client à accepter
                accept_wrapper(key.fileobj)
            else:
                # Client existant à servir
                service_connection(key, mask)
                
except KeyboardInterrupt:
    print("Caught keyboard interrupt, exiting")
finally:
    sel.close()
```

**Explication :**
- `sel.select()` retourne une liste de tuples `(key, mask)`
- `key.fileobj` : L'objet socket
- `mask` : Les événements prêts (lecture/écriture)
- `key.data` : Données personnalisées associées au socket

### 2.2 Acceptation des Connexions

```python
def accept_wrapper(sock):
    # Accepter la connexion
    conn, addr = sock.accept()
    print(f"Accepted connection from {addr}")
    
    # Mode non-bloquant pour le client aussi !
    conn.setblocking(False)
    
    # Créer un objet pour stocker les données du client
    data = types.SimpleNamespace(
        addr=addr,
        inb=b"",   # Buffer de réception
        outb=b""   # Buffer d'envoi
    )
    
    # Surveiller lecture ET écriture
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    sel.register(conn, events, data=data)
```

**💡 Astuce :** `SimpleNamespace` permet de créer un objet simple pour stocker des attributs.

### 2.3 Service des Connexions

```python
def service_connection(key, mask):
    sock = key.fileobj
    data = key.data
    
    # Traitement de la lecture
    if mask & selectors.EVENT_READ:
        recv_data = sock.recv(1024)
        if recv_data:
            # Ajouter au buffer de sortie (echo)
            data.outb += recv_data
        else:
            # Client fermé, nettoyer
            print(f"Closing connection to {data.addr}")
            sel.unregister(sock)
            sock.close()
    
    # Traitement de l'écriture
    if mask & selectors.EVENT_WRITE:
        if data.outb:
            print(f"Echoing {data.outb!r} to {data.addr}")
            sent = sock.send(data.outb)
            # Retirer les octets envoyés du buffer
            data.outb = data.outb[sent:]
```

**⚠️ Important :**
- Toujours appeler `sel.unregister()` avant de fermer le socket
- Vérifier si des données sont reçues (sinon = connexion fermée)
- Retirer les octets envoyés du buffer d'envoi

### 2.4 Client Multi-Connexions

#### Initialisation des Connexions

```python
# multiconn-client.py
import selectors
import types

sel = selectors.DefaultSelector()
messages = [b"Message 1 from client.", b"Message 2 from client."]

def start_connections(host, port, num_conns):
    server_addr = (host, port)
    
    for i in range(num_conns):
        connid = i + 1
        print(f"Starting connection {connid} to {server_addr}")
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setblocking(False)
        
        # connect_ex() ne lève pas d'exception immédiate
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
```

**Différence Clé :** `connect_ex()` vs `connect()`
- `connect()` : Lève `BlockingIOError` en mode non-bloquant
- `connect_ex()` : Retourne un code d'erreur au lieu de lever une exception

#### Service du Client

```python
def service_connection(key, mask):
    sock = key.fileobj
    data = key.data
    
    if mask & selectors.EVENT_READ:
        recv_data = sock.recv(1024)
        if recv_data:
            print(f"Received {recv_data!r} from connection {data.connid}")
            data.recv_total += len(recv_data)
        
        # Fermer si toutes les données sont reçues
        if not recv_data or data.recv_total == data.msg_total:
            print(f"Closing connection {data.connid}")
            sel.unregister(sock)
            sock.close()
    
    if mask & selectors.EVENT_WRITE:
        # Prendre le prochain message à envoyer
        if not data.outb and data.messages:
            data.outb = data.messages.pop(0)
        
        if data.outb:
            print(f"Sending {data.outb!r} to connection {data.connid}")
            sent = sock.send(data.outb)
            data.outb = data.outb[sent:]
```

### 2.5 Exécution

**Démarrer le serveur :**
```bash
$ python multiconn-server.py 127.0.0.1 65432
Listening on ('127.0.0.1', 65432)
```

**Démarrer le client (2 connexions) :**
```bash
$ python multiconn-client.py 127.0.0.1 65432 2
Starting connection 1 to ('127.0.0.1', 65432)
Starting connection 2 to ('127.0.0.1', 65432)
Sending b'Message 1 from client.' to connection 1
Sending b'Message 2 from client.' to connection 1
...
```

---

## Application Client-Serveur Avancée

### 3.1 Architecture de l'Application

L'application avancée ajoute :
- ✅ Gestion robuste des erreurs
- ✅ Protocole applicatif personnalisé
- ✅ Support texte ET binaire
- ✅ En-têtes de message structurés

#### Structure des Fichiers

```
Serveur:
├── app-server.py      # Script principal
└── libserver.py       # Classe Message

Client:
├── app-client.py      # Script principal
└── libclient.py       # Classe Message
```

### 3.2 Gestion des Erreurs

```python
# app-server.py - Boucle d'événements avec gestion d'erreurs
try:
    while True:
        events = sel.select(timeout=None)
        for key, mask in events:
            if key.data is None:
                accept_wrapper(key.fileobj)
            else:
                message = key.data
                try:
                    message.process_events(mask)
                except Exception:
                    print(
                        f"Main: Error: Exception for {message.addr}:\n"
                        f"{traceback.format_exc()}"
                    )
                    message.close()  # Nettoyer en cas d'erreur
except KeyboardInterrupt:
    print("Caught keyboard interrupt, exiting")
finally:
    sel.close()
```

**🛡️ Protection :** Les erreurs d'un client n'affectent pas les autres connexions.

### 3.3 Comprendre les Flux de Données

#### Le Problème des Frontières de Messages

```
Données envoyées:  [Message1][Message2][Message3]
Données reçues:    [Mes][sage1][Message2Mes][sage3]
                    ↑ Les frontières ne sont pas préservées !
```

**Solution :** Définir un protocole de niveau application qui :
1. Préfixe chaque message avec sa longueur
2. Utilise des en-têtes structurés
3. Marque clairement les frontières

---

## Protocole de Communication

### 4.1 Format du Message Complet

```
┌─────────────────────────────────────────────────────────────┐
│                    MESSAGE COMPLET                          │
├─────────────────┬───────────────────────┬───────────────────┤
│  En-tête fixe   │   En-tête JSON        │    Contenu        │
│   (2 octets)    │   (longueur variable) │  (données réelles)│
└─────────────────┴───────────────────────┴───────────────────┘
     ↓                      ↓                       ↓
  Longueur de          Métadonnées             Payload
  l'en-tête JSON       du message
```

### 4.2 En-tête Fixe (2 octets)

```python
import struct

# Créer l'en-tête fixe (entier 16 bits, big-endian)
json_header_len = 100  # Exemple
fixed_header = struct.pack(">H", json_header_len)
# Résultat : b'\x00d' (2 octets)

# Lire l'en-tête fixe
header_bytes = sock.recv(2)
json_header_len = struct.unpack(">H", header_bytes)[0]
```

**Format :** `">H"`
- `>` : Big-endian (ordre réseau)
- `H` : Unsigned short (2 octets, 0-65535)

### 4.3 En-tête JSON

```python
# Structure de l'en-tête JSON
json_header = {
    "byteorder": "little",          # Ordre des octets de la machine
    "content-type": "text/json",    # Type du contenu
    "content-encoding": "utf-8",    # Encodage
    "content-length": 41            # Longueur du contenu
}

# Sérialisation
import json
json_bytes = json.dumps(json_header).encode("utf-8")
```

#### Champs Requis

| Champ | Description | Exemple |
|-------|-------------|---------|
| `byteorder` | Ordre des octets (`sys.byteorder`) | `"little"`, `"big"` |
| `content-type` | Type MIME du contenu | `"text/json"`, `"binary/custom"` |
| `content-encoding` | Encodage utilisé | `"utf-8"`, `"binary"` |
| `content-length` | Longueur en octets du contenu | `145` |

### 4.4 La Classe Message

#### Point d'Entrée

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

    def process_events(self, mask):
        """Point d'entrée appelé par select()"""
        if mask & selectors.EVENT_READ:
            self.read()
        if mask & selectors.EVENT_WRITE:
            self.write()
```

**🎯 Design Pattern :** Gestion d'état centralisée
- Toute la logique passe par `read()` et `write()`
- Les variables d'état contrôlent le flux
- Simple à déboguer et maintenir

#### Lecture des Messages

```python
def read(self):
    """Lit et traite les données reçues"""
    self._read()  # Lit les données du socket
    
    # Traiter l'en-tête fixe (2 octets)
    if self._jsonheader_len is None:
        self.process_protoheader()
    
    # Traiter l'en-tête JSON
    if self._jsonheader_len is not None:
        if self.jsonheader is None:
            self.process_jsonheader()
    
    # Traiter le contenu
    if self.jsonheader:
        if self.request is None:
            self.process_request()
```

**Ordre de Traitement :**
1. **En-tête fixe** → `self._jsonheader_len`
2. **En-tête JSON** → `self.jsonheader`
3. **Contenu** → `self.request`

#### Traitement de l'En-tête Fixe

```python
def process_protoheader(self):
    hdrlen = 2
    if len(self._recv_buffer) >= hdrlen:
        # Décoder l'en-tête fixe
        self._jsonheader_len = struct.unpack(
            ">H", 
            self._recv_buffer[:hdrlen]
        )[0]
        # Retirer du buffer
        self._recv_buffer = self._recv_buffer[hdrlen:]
```

#### Traitement de l'En-tête JSON

```python
def process_jsonheader(self):
    hdrlen = self._jsonheader_len
    if len(self._recv_buffer) >= hdrlen:
        # Décoder l'en-tête JSON
        self.jsonheader = self._json_decode(
            self._recv_buffer[:hdrlen], 
            "utf-8"
        )
        self._recv_buffer = self._recv_buffer[hdrlen:]
        
        # Vérifier les champs requis
        for reqhdr in (
            "byteorder",
            "content-length",
            "content-type",
            "content-encoding",
        ):
            if reqhdr not in self.jsonheader:
                raise ValueError(f"Missing required header '{reqhdr}'.")
```

#### Traitement du Contenu

```python
def process_request(self):
    content_len = self.jsonheader["content-length"]
    
    # Attendre d'avoir tout le contenu
    if not len(self._recv_buffer) >= content_len:
        return
    
    data = self._recv_buffer[:content_len]
    self._recv_buffer = self._recv_buffer[content_len:]
    
    # Traiter selon le type
    if self.jsonheader["content-type"] == "text/json":
        encoding = self.jsonheader["content-encoding"]
        self.request = self._json_decode(data, encoding)
        print(f"Received request {self.request!r} from {self.addr}")
    else:
        # Requête binaire
        self.request = data
        print(
            f"Received {self.jsonheader['content-type']} "
            f"request from {self.addr}"
        )
    
    # Passer en mode écriture uniquement
    self._set_selector_events_mask("w")
```

#### Écriture des Réponses

```python
def write(self):
    """Écrit les réponses sur le socket"""
    if self.request:
        if not self.response_created:
            self.create_response()
    
    self._write()

def create_response(self):
    """Crée le message de réponse"""
    if self.jsonheader["content-type"] == "text/json":
        response = self._create_response_json_content()
    else:
        response = self._create_response_binary_content()
    
    message = self._create_message(**response)
    self.response_created = True
    self._send_buffer += message

def _write(self):
    """Envoie les données du buffer d'envoi"""
    if self._send_buffer:
        print(f"Sending {self._send_buffer!r} to {self.addr}")
        try:
            sent = self.sock.send(self._send_buffer)
        except BlockingIOError:
            # Socket temporairement indisponible
            pass
        else:
            self._send_buffer = self._send_buffer[sent:]
            # Fermer quand tout est envoyé
            if sent and not self._send_buffer:
                self.close()
```

### 4.5 Script Serveur Principal

```python
# app-server.py
import sys
import socket
import selectors
import traceback
import libserver

sel = selectors.DefaultSelector()

def accept_wrapper(sock):
    conn, addr = sock.accept()
    print(f"Accepted connection from {addr}")
    conn.setblocking(False)
    
    # Créer l'objet Message pour ce client
    message = libserver.Message(sel, conn, addr)
    sel.register(conn, selectors.EVENT_READ, data=message)

# Configuration
host, port = sys.argv[1], int(sys.argv[2])
lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# SO_REUSEADDR pour éviter "Address already in use"
lsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

lsock.bind((host, port))
lsock.listen()
print(f"Listening on {(host, port)}")
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
                message = key.data
                try:
                    message.process_events(mask)
                except Exception:
                    print(
                        f"Main: Error: Exception for {message.addr}:\n"
                        f"{traceback.format_exc()}"
                    )
                    message.close()
except KeyboardInterrupt:
    print("Caught keyboard interrupt, exiting")
finally:
    sel.close()
```

**🔐 Option SO_REUSEADDR :**
- Évite l'erreur "Address already in use"
- Utile pendant le développement
- Permet de redémarrer le serveur rapidement

### 4.6 Script Client Principal

```python
# app-client.py
import sys
import socket
import selectors
import traceback
import libclient

sel = selectors.DefaultSelector()

def create_request(action, value):
    """Crée la requête selon l'action"""
    if action == "search":
        return dict(
            type="text/json",
            encoding="utf-8",
            content=dict(action=action, value=value),
        )
    else:
        return dict(
            type="binary/custom-client-binary-type",
            encoding="binary",
            content=bytes(action + value, encoding="utf-8"),
        )

def start_connection(host, port, request):
    addr = (host, port)
    print(f"Starting connection to {addr}")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setblocking(False)
    sock.connect_ex(addr)
    
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    message = libclient.Message(sel, sock, addr, request)
    sel.register(sock, events, data=message)

# Parsing des arguments
host, port = sys.argv[1], int(sys.argv[2])
action, value = sys.argv[3], sys.argv[4]
request = create_request(action, value)
start_connection(host, port, request)

# Boucle d'événements
try:
    while True:
        events = sel.select(timeout=1)
        for key, mask in events:
            message = key.data
            try:
                message.process_events(mask)
            except Exception:
                print(
                    f"Main: Error: Exception for {message.addr}:\n"
                    f"{traceback.format_exc()}"
                )
                message.close()
        # Sortir si plus de sockets surveillés
        if not sel.get_map():
            break
except KeyboardInterrupt:
    print("Caught keyboard interrupt, exiting")
finally:
    sel.close()
```

### 4.7 Exemples d'Exécution

#### Recherche JSON

**Démarrer le serveur :**
```bash
$ python app-server.py '' 65432
Listening on ('', 65432)
```

**Recherche morpheus :**
```bash
$ python app-client.py 127.0.0.1 65432 search morpheus
Starting connection to ('127.0.0.1', 65432)
Sending b'\x00d{"byteorder": "little", "content-type": "text/json", ...
Received response {'result': 'Follow the white rabbit. 🐰'} from ...
Got result: Follow the white rabbit. 🐰
Closing connection to ('127.0.0.1', 65432)
```

**Recherche avec emoji :**
```bash
$ python app-client.py 127.0.0.1 65432 search 🐶
Got result: 🐾 Playing ball! 🏐
```

#### Requête Binaire

```bash
$ python app-client.py 127.0.0.1 65432 binary 😃
Received binary/custom-server-binary-type response
Got response: b'First 10 bytes of request: binary\xf0\x9f\x98\x83'
```

---

## Dépannage

### 5.1 Outils de Diagnostic

#### 5.1.1 La Commande `ping`

```bash
# Tester la connectivité
$ ping -c 3 127.0.0.1
PING 127.0.0.1 (127.0.0.1): 56 data bytes
64 bytes from 127.0.0.1: icmp_seq=0 ttl=64 time=0.058 ms
64 bytes from 127.0.0.1: icmp_seq=1 ttl=64 time=0.165 ms
64 bytes from 127.0.0.1: icmp_seq=2 ttl=64 time=0.164 ms

--- 127.0.0.1 ping statistics ---
3 packets transmitted, 3 packets received, 0.0% packet loss
round-trip min/avg/max/stddev = 0.058/0.129/0.165/0.050 ms
```

**À vérifier :**
- Perte de paquets (packet loss)
- Latence (round-trip time)
- Temps de réponse variable

#### Messages ICMP Importants

| Type | Code | Description |
|------|------|-------------|
| 8 | 0 | Echo request (ping) |
| 0 | 0 | Echo reply (pong) |
| 3 | 0 | Réseau de destination inaccessible |
| 3 | 1 | Hôte de destination inaccessible |
| 3 | 3 | Port de destination inaccessible |
| 11 | 0 | TTL expiré en transit |

#### 5.1.2 La Commande `netstat`

```bash
# Voir l'état des connexions
$ netstat -an | grep 65432
Proto Recv-Q Send-Q  Local Address          Foreign Address        (state)
tcp4  408300      0  127.0.0.1.65432        127.0.0.1.53225        ESTABLISHED
tcp4       0 269868  127.0.0.1.53225        127.0.0.1.65432        ESTABLISHED
```

**Colonnes importantes :**
- **Recv-Q** : Octets en attente de lecture (buffer de réception)
- **Send-Q** : Octets en attente d'envoi (buffer d'envoi)
- **State** : État de la connexion TCP

**⚠️ Problème détecté :**
- `Recv-Q` élevé → Le serveur ne lit pas assez vite
- `Send-Q` élevé → Le client/serveur ne peut pas envoyer

#### 5.1.3 Wireshark / tshark

**Capture avec tshark :**
```bash
$ tshark -i lo0 'tcp port 65432'
Capturing on 'Loopback'
    1   0.000000    127.0.0.1 → 127.0.0.1    TCP 68 53942 → 65432 [SYN]
    2   0.000057    127.0.0.1 → 127.0.0.1    TCP 68 65432 → 53942 [SYN, ACK]
    3   0.000068    127.0.0.1 → 127.0.0.1    TCP 56 53942 → 65432 [ACK]
    ...
```

**Ce que vous pouvez voir :**
- ✅ Paquets envoyés/reçus
- ✅ Flags TCP (SYN, ACK, FIN, etc.)
- ✅ Taille des données
- ✅ Timing des paquets
- ✅ Retransmissions

### 5.2 Erreurs Communes et Solutions

#### Erreur : "Address already in use"

```python
# Solution : Ajouter SO_REUSEADDR
lsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
```

**Cause :** Port en état TIME_WAIT (dure 2+ minutes après fermeture)

#### Erreur : BlockingIOError

```python
# C'est NORMAL en mode non-bloquant !
try:
    data = sock.recv(4096)
except BlockingIOError:
