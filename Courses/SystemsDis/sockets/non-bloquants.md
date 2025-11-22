# Socket Non-Bloquant en Python - Expemple chat multi-clients

## C'est quoi un socket bloquant vs non-bloquant ?

### Analogie de la Vie Réelle

Imaginez que vous êtes au guichet d'une banque :

#### 🔴 Mode BLOQUANT (par défaut)
```
Vous arrivez au guichet
    ↓
Vous demandez quelque chose
    ↓
VOUS ATTENDEZ... ⏳
(Vous ne pouvez RIEN faire d'autre)
    ↓
Le guichetier répond
    ↓
Vous pouvez continuer
```

**Problème :** Pendant que vous attendez, vous êtes complètement bloqué !

#### 🟢 Mode NON-BLOQUANT
```
Vous arrivez au guichet
    ↓
Vous demandez quelque chose
    ↓
"Revenez plus tard !" 💨
(Vous pouvez faire autre chose)
    ↓
Vous revenez vérifier
    ↓
"C'est prêt !" ✅
```

**Avantage :** Vous pouvez faire plein d'autres choses en attendant !

---

## 📝 Exemple Pratique avec Code

### Exemple 1 : Socket BLOQUANT (problème)

```python
import socket

# Créer un socket (mode bloquant par défaut)
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(('google.com', 80))

# ⚠️ BLOQUE ICI jusqu'à recevoir des données !
# Votre programme est FIGÉ
data = sock.recv(1024)
print(f"Reçu: {data}")

# Vous ne pouvez pas faire autre chose pendant ce temps
```

**Problème :** Si le serveur ne répond pas, votre programme attend INDÉFINIMENT ! 😱

### Exemple 2 : Socket NON-BLOQUANT (solution)

```python
import socket
import time

# Créer un socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# 🔑 ACTIVER LE MODE NON-BLOQUANT
sock.setblocking(False)

# Essayer de se connecter
try:
    sock.connect(('google.com', 80))
except BlockingIOError:
    # C'est NORMAL ! La connexion est en cours
    print("Connexion en cours...")

# Maintenant vous pouvez faire autre chose !
print("Je fais autre chose pendant la connexion...")
time.sleep(1)

# Essayer de recevoir des données
try:
    data = sock.recv(1024)
    print(f"Reçu: {data}")
except BlockingIOError:
    # Pas de données disponibles pour l'instant
    print("Pas encore de données, je continue...")
```

---

## 🎯 Exemple Complet et Pratique

### Serveur qui Peut Gérer Plusieurs Clients

```python
import socket
import selectors

# Créer un sélecteur (pour surveiller plusieurs sockets)
sel = selectors.DefaultSelector()

def accept_client(server_sock):
    """Accepter un nouveau client"""
    client_sock, addr = server_sock.accept()
    print(f"✅ Nouveau client connecté: {addr}")
    
    # Mettre le client en mode non-bloquant
    client_sock.setblocking(False)
    
    # Surveiller ce client pour les données à lire
    sel.register(client_sock, selectors.EVENT_READ, data=addr)

def handle_client(client_sock, addr):
    """Gérer un client existant"""
    try:
        data = client_sock.recv(1024)
        if data:
            print(f"📨 Reçu de {addr}: {data.decode()}")
            # Renvoyer les données (echo)
            client_sock.send(data)
        else:
            # Client déconnecté
            print(f"❌ Client {addr} déconnecté")
            sel.unregister(client_sock)
            client_sock.close()
    except BlockingIOError:
        # Pas de données disponibles, c'est OK !
        pass

# Créer le serveur
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(('127.0.0.1', 8888))
server.listen(5)
server.setblocking(False)  # Mode non-bloquant !

# Surveiller le serveur pour les nouvelles connexions
sel.register(server, selectors.EVENT_READ, data=None)

print("🚀 Serveur démarré sur 127.0.0.1:8888")

# Boucle principale
try:
    while True:
        # Attendre des événements (connexions ou données)
        events = sel.select(timeout=1)
        
        for key, mask in events:
            sock = key.fileobj
            
            if key.data is None:
                # C'est le serveur -> nouveau client
                accept_client(sock)
            else:
                # C'est un client -> traiter ses données
                handle_client(sock, key.data)
        
        # Pendant ce temps, vous pourriez faire autre chose !
        # print("Je travaille sur d'autres tâches...")
        
except KeyboardInterrupt:
    print("\n🛑 Arrêt du serveur")
finally:
    sel.close()
    server.close()
```

### Client Simple pour Tester

```python
import socket

# Créer un client
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('127.0.0.1', 8888))

# Envoyer un message
message = "Bonjour serveur !"
client.send(message.encode())
print(f"📤 Envoyé: {message}")

# Recevoir la réponse
response = client.recv(1024)
print(f"📥 Reçu: {response.decode()}")

client.close()
```

---

## 🔍 Comparaison Visuelle

### Serveur BLOQUANT (peut gérer 1 seul client)

```
Client 1 se connecte ──→ [Serveur traite Client 1] ⏳
Client 2 attend... 😴   │
Client 3 attend... 😴   │ BLOQUÉ !
                        │
Client 1 termine ──────→ ✅
Client 2 peut enfin se connecter ──→ [Serveur traite Client 2] ⏳
```

### Serveur NON-BLOQUANT (peut gérer plusieurs clients)

```
Client 1 se connecte ──→ [Serveur]
                            │ ↓ Traite rapidement
Client 2 se connecte ──→ [Serveur]
                            │ ↓ Traite rapidement
Client 3 se connecte ──→ [Serveur]
                            │ ↓ Traite rapidement
                         
Tous servis en parallèle ! 🎉
```

---

## 🎓 Les Points Clés à Retenir

### 1. Activer le mode non-bloquant

```python
sock.setblocking(False)  # C'est tout !
```

### 2. Gérer les exceptions normales

```python
try:
    data = sock.recv(1024)
except BlockingIOError:
    # C'EST NORMAL ! Pas de données disponibles maintenant
    pass  # On continue tranquillement
```

### 3. Utiliser un sélecteur pour surveiller plusieurs sockets

```python
import selectors

sel = selectors.DefaultSelector()
sel.register(sock, selectors.EVENT_READ)  # Surveiller

# Attendre qu'un socket soit prêt
events = sel.select(timeout=1)
for key, mask in events:
    # Traiter uniquement les sockets prêts
    process_socket(key.fileobj)
```

---

## 💡 Cas d'Usage Réels

### Quand utiliser BLOQUANT ?
✅ Scripts simples avec un seul client  
✅ Applications qui n'ont rien d'autre à faire  
✅ Débutants qui apprennent les sockets  

### Quand utiliser NON-BLOQUANT ?
✅ Serveurs qui gèrent plusieurs clients  
✅ Applications qui doivent rester réactives  
✅ Chat, jeux en ligne, APIs web  
✅ Quand vous ne voulez pas que votre programme "gèle"  

---

## 🚀 Mini-Projet : Chat Multi-Clients

```python
import socket
import selectors

sel = selectors.DefaultSelector()
clients = {}  # Dictionnaire des clients connectés

def broadcast(message, sender_addr):
    """Envoyer un message à tous les clients sauf l'émetteur"""
    for client_sock, addr in clients.items():
        if addr != sender_addr:
            try:
                client_sock.send(message)
            except:
                pass

def accept_client(server_sock):
    client_sock, addr = server_sock.accept()
    print(f"✅ {addr} a rejoint le chat")
    client_sock.setblocking(False)
    clients[client_sock] = addr
    sel.register(client_sock, selectors.EVENT_READ, data=addr)
    broadcast(f"{addr} a rejoint le chat\n".encode(), addr)

def handle_client(client_sock, addr):
    try:
        data = client_sock.recv(1024)
        if data:
            message = f"{addr}: {data.decode()}"
            print(message)
            broadcast(message.encode(), addr)
        else:
            # Déconnexion
            print(f"❌ {addr} a quitté le chat")
            sel.unregister(client_sock)
            client_sock.close()
            del clients[client_sock]
            broadcast(f"{addr} a quitté le chat\n".encode(), addr)
    except BlockingIOError:
        pass

# Configuration du serveur
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(('127.0.0.1', 9999))
server.listen(10)
server.setblocking(False)
sel.register(server, selectors.EVENT_READ, data=None)

print("💬 Serveur de chat démarré sur 127.0.0.1:9999")

try:
    while True:
        events = sel.select(timeout=None)
        for key, mask in events:
            if key.data is None:
                accept_client(key.fileobj)
            else:
                handle_client(key.fileobj, key.data)
except KeyboardInterrupt:
    print("\n🛑 Serveur arrêté")
finally:
    sel.close()
    server.close()
```

### Client pour le Chat

```python
import socket
import threading
import sys

def receive_messages(sock):
    """Thread pour recevoir les messages"""
    while True:
        try:
            message = sock.recv(1024).decode()
            if message:
                print(f"\n{message}", end="")
                print("Vous: ", end="", flush=True)
            else:
                break
        except:
            break

# Connexion au serveur
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('127.0.0.1', 9999))

# Démarrer le thread de réception
thread = threading.Thread(target=receive_messages, args=(client,))
thread.daemon = True
thread.start()

print("💬 Connecté au chat ! Tapez vos messages:")

# Boucle d'envoi
try:
    while True:
        message = input("Vous: ")
        if message.lower() == 'quit':
            break
        client.send(message.encode())
except KeyboardInterrupt:
    pass
finally:
    client.close()
    print("\n👋 Déconnecté du chat")
```

---

## 📊 Résumé en Tableau

| Caractéristique | Bloquant | Non-Bloquant |
|----------------|----------|--------------|
| **Mode par défaut** | ✅ Oui | ❌ Non |
| **Attend les données** | ⏳ Oui (bloque) | ⚡ Non (retourne immédiatement) |
| **Clients multiples** | ❌ Difficile | ✅ Facile |
| **Complexité** | 😊 Simple | 🤔 Moyenne |
| **Performance** | 🐌 Lente | 🚀 Rapide |
| **Cas d'usage** | Scripts simples | Serveurs, apps réactives |

---

## ✅ En Conclusion

**Socket non-bloquant = Ne pas attendre bêtement !**

C'est comme jongler avec plusieurs balles en même temps :
- Vous lancez une balle (envoi de données)
- Vous attrapez une autre (réception)
- Vous en lancez une troisième (nouveau client)
- **Sans jamais rester bloqué à regarder une seule balle !** 🤹

Voilà ! Vous savez maintenant comment fonctionne un socket non-bloquant en Python ! 🎉
