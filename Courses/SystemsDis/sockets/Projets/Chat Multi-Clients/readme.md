# Chat Multi-Clients avec Sockets Python

## 📋 Présentation du Projet

Nous allons créer une application de chat où plusieurs clients peuvent se connecter simultanément à un serveur et échanger des messages en temps réel.

### Fonctionnalités :
- 💬 Messages diffusés à tous les clients connectés
- 👤 Système de pseudonymes
- 📢 Notifications de connexion/déconnexion
- 🔄 Gestion multi-clients avec threading

---

# 🎓 PARTIE 1 : COMPRENDRE LES CONCEPTS FONDAMENTAUX

## 1.1 Qu'est-ce qu'un Socket Bloquant ?

Un **socket bloquant** est le comportement par défaut des sockets en Python :

```python
data = conn.recv(1024)  # ⏸️ BLOQUE ici jusqu'à recevoir des données
```

**Caractéristiques :**
- L'exécution du programme **s'arrête** à cet endroit
- Le programme **attend** qu'une donnée arrive
- Le code après `recv()` ne s'exécute **QUE** quand des données arrivent

### Exemple Visuel :

```
Thread Principal du Serveur :
┌─────────────────────────────────┐
│ 1. Créer le socket              │
│ 2. bind() et listen()           │
│ 3. accept() ⏸️ BLOQUE           │ ← Attend une connexion
│    (attend un client...)        │
│ 4. accept() ⏸️ BLOQUE           │ ← Attend une autre connexion
│    (attend un autre client...)  │
└─────────────────────────────────┘
```

**Problème** : Si on traite le premier client dans le même thread, on ne peut pas accepter d'autres connexions !

**Solution** : Les THREADS ! 🎯

---

## 1.2 Pourquoi Utiliser des Threads ?

Sans threads :
```python
# ❌ MAUVAIS : Un seul client à la fois
conn, addr = s.accept()  # Client 1 se connecte
handle_client(conn)      # ⏸️ BLOQUE pendant toute la conversation
# Les autres clients doivent ATTENDRE que Client 1 ait fini !
```

Avec threads :
```python
# ✅ BON : Plusieurs clients simultanés
conn, addr = s.accept()       # Client 1 se connecte
thread = Thread(target=handle_client, args=(conn,))
thread.start()                # Lance dans un thread séparé
# Le serveur peut IMMÉDIATEMENT accepter Client 2, 3, 4...
```

### Schéma de Fonctionnement :

```
SERVEUR (Thread Principal)          THREADS CLIENTS
┌─────────────────────┐            ┌──────────────────┐
│                     │            │  Thread Client 1 │
│ while True:         │  démarre   │  handle_client() │
│   accept() ⏸️       │ ──────────→│  recv() ⏸️       │
│   create_thread()   │            │  (gère Alice)    │
│   accept() ⏸️       │            └──────────────────┘
│   create_thread()   │  démarre   ┌──────────────────┐
│   accept() ⏸️       │ ──────────→│  Thread Client 2 │
│   ...               │            │  handle_client() │
│                     │            │  recv() ⏸️       │
└─────────────────────┘            │  (gère Bob)      │
                                   └──────────────────┘
```

**Chaque client a son propre thread qui BLOQUE indépendamment !**

---

# 🎓 PARTIE 2 : CODE DU SERVEUR - EXPLICATION DÉTAILLÉE

## 2.1 Vue d'Ensemble du Serveur

Le serveur a 3 responsabilités principales :
1. **Accepter** les connexions clients (boucle infinie)
2. **Créer un thread** pour chaque nouveau client
3. **Diffuser** les messages à tous les clients connectés

---

## 🖥️ Code du Serveur (`chat_server.py`) - COMMENTÉ LIGNE PAR LIGNE

```python
import socket
import threading

# Configuration réseau
HOST = "127.0.0.1"  # localhost = cette machine
PORT = 65432        # Port > 1023 (non privilégié)

# ========================================
# STRUCTURE DE DONNÉES PARTAGÉE
# ========================================
# Liste globale stockant tous les clients connectés
# Chaque élément = (socket_du_client, pseudo_du_client)
clients = []

# LOCK = Verrou pour protéger l'accès concurrent à 'clients'
# Pourquoi ? Plusieurs threads modifient 'clients' en même temps !
clients_lock = threading.Lock()


# ========================================
# FONCTION 1 : BROADCAST (Diffusion)
# ========================================
def broadcast(message, sender_socket=None):
    """
    Envoie un message à TOUS les clients connectés
    sauf celui qui l'a envoyé (sender_socket)
    
    Paramètres:
        message (str): Le message à diffuser
        sender_socket: Socket de l'émetteur (None = message serveur)
    """
    # SECTION CRITIQUE : On accède à la liste 'clients'
    with clients_lock:  # 🔒 Verrouiller pendant l'accès
        # Parcourir tous les clients connectés
        for client_socket, _ in clients:
            # Ne pas renvoyer le message à celui qui l'a envoyé
            if client_socket != sender_socket:
                try:
                    # Envoyer le message encodé en bytes
                    client_socket.sendall(message.encode())
                except:
                    # Si erreur (client déconnecté), on ignore
                    pass
    # 🔓 Le verrou est automatiquement libéré ici


# ========================================
# FONCTION 2 : GESTION D'UN CLIENT
# ========================================
def handle_client(conn, addr):
    """
    Fonction exécutée dans UN THREAD SÉPARÉ pour CHAQUE client
    
    Cette fonction BLOQUE sur recv() mais c'est OK car elle
    tourne dans son propre thread !
    
    Paramètres:
        conn: Socket de connexion avec ce client
        addr: Adresse (IP, port) du client
    """
    print(f"[NOUVELLE CONNEXION] {addr} connecté")
    
    # ─────────────────────────────────────
    # ÉTAPE 1 : Récupérer le pseudo
    # ─────────────────────────────────────
    conn.sendall(b"Entrez votre pseudo: ")  # Envoyer prompt
    pseudo = conn.recv(1024).decode().strip()  # ⏸️ BLOQUE jusqu'à réception
    
    # ─────────────────────────────────────
    # ÉTAPE 2 : Ajouter à la liste des clients
    # ─────────────────────────────────────
    with clients_lock:  # 🔒 Section critique
        clients.append((conn, pseudo))  # Ajouter (socket, pseudo)
    
    # ─────────────────────────────────────
    # ÉTAPE 3 : Annoncer l'arrivée
    # ─────────────────────────────────────
    broadcast(f"[SERVEUR] {pseudo} a rejoint le chat!\n")
    print(f"[INFO] {pseudo} ({addr}) a rejoint le chat")
    
    # ─────────────────────────────────────
    # BOUCLE PRINCIPALE : Recevoir les messages
    # ─────────────────────────────────────
    try:
        while True:  # Boucle infinie pour ce client
            # ⏸️ BLOQUE ici en attendant un message de CE client
            data = conn.recv(1024)
            
            # Si data est vide = client déconnecté
            if not data:
                break
            
            message = data.decode().strip()
            
            # Commande de déconnexion
            if message.lower() == "/quit":
                break
            
            # ─────────────────────────────────────
            # Diffuser le message à tous les autres
            # ─────────────────────────────────────
            full_message = f"[{pseudo}] {message}\n"
            print(f"Message reçu: {full_message.strip()}")
            broadcast(full_message, conn)  # Ne pas renvoyer à soi-même
            
    except Exception as e:
        print(f"[ERREUR] {pseudo}: {e}")
    
    # ─────────────────────────────────────
    # NETTOYAGE : Client déconnecté
    # ─────────────────────────────────────
    finally:
        # Retirer de la liste des clients
        with clients_lock:  # 🔒 Section critique
            clients.remove((conn, pseudo))
        
        # Annoncer le départ
        broadcast(f"[SERVEUR] {pseudo} a quitté le chat.\n")
        print(f"[DECONNEXION] {pseudo} ({addr})")
        conn.close()  # Fermer la connexion


# ========================================
# FONCTION 3 : DÉMARRAGE DU SERVEUR
# ========================================
def start_server():
    """
    Boucle principale du serveur :
    - Crée le socket serveur
    - Accepte les connexions en boucle
    - Crée un thread pour chaque client
    """
    # Créer le socket serveur (IPv4, TCP)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        # Lier le socket à l'adresse et au port
        s.bind((HOST, PORT))
        
        # Passer en mode écoute (file d'attente par défaut)
        s.listen()
        print(f"[SERVEUR DEMARRÉ] Écoute sur {HOST}:{PORT}")
        print("En attente de connexions...\n")
        
        # ─────────────────────────────────────
        # BOUCLE INFINIE : Accepter les clients
        # ─────────────────────────────────────
        while True:
            # ⏸️ BLOQUE jusqu'à ce qu'un client se connecte
            conn, addr = s.accept()
            
            # Créer un nouveau thread pour ce client
            thread = threading.Thread(
                target=handle_client,  # Fonction à exécuter
                args=(conn, addr)      # Arguments à passer
            )
            thread.start()  # ▶️ Démarrer le thread
            
            # Le thread principal continue IMMÉDIATEMENT
            # à la prochaine itération pour accepter d'autres clients !
            
            print(f"[CONNEXIONS ACTIVES] {threading.active_count() - 1}")
            # -1 car on ne compte pas le thread principal


# ========================================
# POINT D'ENTRÉE
# ========================================
if __name__ == "__main__":
    start_server()
```

---

## 2.2 📊 Schéma de Fonctionnement du Serveur

```
TIMELINE : Comment 3 clients se connectent

T=0s    Thread Principal                Thread Alice    Thread Bob     Thread Charlie
        │                                                                              
        ├─ start_server()                                                            
        ├─ bind() & listen()                                                         
        │                                                                            
T=1s    ├─ accept() ⏸️ BLOQUE                                                        
        │  (attend client...)                                                        
T=2s    │  ✅ Alice arrive !                                                         
        ├─ create Thread(Alice) ────────→ handle_client()                           
        │                                 ├─ recv() ⏸️ (pseudo)                     
        ├─ accept() ⏸️ BLOQUE             ├─ "Alice"                                
        │  (attend client...)             ├─ clients.append()                       
        │                                 ├─ broadcast("Alice rejoint")             
T=3s    │  ✅ Bob arrive !                ├─ while True:                            
        ├─ create Thread(Bob) ─────────────────────────→ handle_client()           
        │                                 │              ├─ recv() ⏸️ (pseudo)      
        ├─ accept() ⏸️ BLOQUE             │              ├─ "Bob"                   
        │                                 │              ├─ broadcast("Bob rejoint")
T=4s    │                                 ├─ recv() ⏸️   ├─ while True:            
        │                                 │  (message)   │  recv() ⏸️              
T=5s    │  ✅ Charlie arrive !            │              │                          
        ├─ create Thread(Charlie) ──────────────────────────────────→ handle_client()
        │                                 │              │            ├─ recv() ⏸️  
        ├─ accept() ⏸️                    │              │            │             
        │                                 │              │            │             
T=6s    │                                 ├─ "Salut!"   │            │             
        │                                 ├─ broadcast() │            │             
        │                                 ├─ recv() ⏸️   ├─ ✉️ reçoit ├─ ✉️ reçoit
        │                                 │              ├─ recv() ⏸️ ├─ recv() ⏸️ 
```

**Points Clés :**
- Le thread principal ne fait QUE accepter des connexions
- Chaque client a son propre thread qui BLOQUE indépendamment
- Les threads communiquent via la liste `clients` (protégée par lock)

---

## 2.3 🔐 Pourquoi le Lock (Verrou) est CRUCIAL

### Problème Sans Lock :

Imaginez 2 threads qui modifient `clients` EN MÊME TEMPS :

```
clients = [Alice, Bob]

Thread Charlie                    Thread David
├─ Lire clients                   ├─ Lire clients
│  [Alice, Bob]                   │  [Alice, Bob]
├─ Ajouter Charlie                ├─ Ajouter David
│  [Alice, Bob, Charlie]          │  [Alice, Bob, David]
└─ Écrire dans clients            └─ Écrire dans clients
   clients = [Alice, Bob, Charlie]   clients = [Alice, Bob, David]
                                     ❌ Charlie est PERDU !
```

### Solution Avec Lock :

```python
with clients_lock:  # 🔒 Un seul thread à la fois peut entrer ici
    clients.append((conn, pseudo))
```

```
Thread Charlie                    Thread David
├─ clients_lock.acquire() ✅      ├─ clients_lock.acquire() ⏸️ BLOQUE
├─ clients.append(Charlie)        │  (attend que Charlie finisse...)
├─ clients = [A, B, Charlie]      │
├─ clients_lock.release() 🔓      │
                                  ├─ clients_lock.acquire() ✅
                                  ├─ clients.append(David)
                                  ├─ clients = [A, B, C, David] ✅
                                  └─ clients_lock.release() 🔓
```

**`with clients_lock:` = acquire() + release() automatique !**

---

# 🎓 PARTIE 3 : CODE DU CLIENT - EXPLICATION DÉTAILLÉE

## 3.1 Vue d'Ensemble du Client

Le client a 2 responsabilités **SIMULTANÉES** :
1. **Envoyer** les messages tapés par l'utilisateur ➡️ au serveur
2. **Recevoir** et afficher les messages des autres clients

**Problème** : Comment faire les 2 en même temps avec des sockets bloquants ?

**Solution** : 2 THREADS ! 🎯

```
Thread Principal          Thread de Réception
├─ input() ⏸️             ├─ recv() ⏸️
├─ "Bonjour"              │  (attend message...)
├─ send("Bonjour")        │
├─ input() ⏸️             ├─ ✉️ Reçoit "[Bob] Salut"
│  (attend user...)       ├─ print("[Bob] Salut")
│                         ├─ recv() ⏸️
│                         │  (attend message...)
```

---

## 👨‍💻 Code du Client (`chat_client.py`) - COMMENTÉ LIGNE PAR LIGNE

```python
import socket
import threading
import sys

# Configuration réseau (doit correspondre au serveur)
HOST = "127.0.0.1"
PORT = 65432


# ========================================
# FONCTION 1 : THREAD DE RÉCEPTION
# ========================================
def receive_messages(sock):
    """
    Fonction exécutée dans UN THREAD SÉPARÉ
    
    Responsabilité : Recevoir et afficher TOUS les messages
    du serveur en continu
    
    Ce thread BLOQUE sur recv() mais c'est OK car le thread
    principal continue à gérer input() !
    """
    while True:  # Boucle infinie de réception
        try:
            # ⏸️ BLOQUE jusqu'à recevoir des données du serveur
            data = sock.recv(1024)
            
            # Si data vide = serveur déconnecté
            if not data:
                print("\n[DÉCONNECTÉ] Connexion au serveur perdue.")
                break
            
            # Afficher le message reçu
            print(data.decode(), end="")
            
        except:
            # Erreur de connexion
            break
    # Quand la boucle se termine, le thread se termine


# ========================================
# FONCTION 2 : DÉMARRAGE DU CLIENT
# ========================================
def start_client():
    """
    Fonction principale du client :
    1. Se connecter au serveur
    2. Lancer le thread de réception
    3. Gérer l'envoi de messages (thread principal)
    """
    try:
        # ─────────────────────────────────────
        # ÉTAPE 1 : Connexion au serveur
        # ─────────────────────────────────────
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            # Établir la connexion
            s.connect((HOST, PORT))  # ⏸️ BLOQUE jusqu'à connexion
            print(f"[CONNECTÉ] au serveur {HOST}:{PORT}\n")
            
            # ─────────────────────────────────────
            # ÉTAPE 2 : Lancer le thread de réception
            # ─────────────────────────────────────
            thread = threading.Thread(
                target=receive_messages,  # Fonction à exécuter
                args=(s,)                 # Socket à passer
            )
            # daemon=True : Le thread se termine quand le programme principal finit
            thread.daemon = True
            thread.start()  # ▶️ Démarrer le thread
            
            # Maintenant on a 2 threads qui tournent :
            # - Thread principal (ci-dessous) : envoie des messages
            # - Thread receive_messages : reçoit des messages
            
            # ─────────────────────────────────────
            # ÉTAPE 3 : Saisie du pseudo
            # ─────────────────────────────────────
            # Recevoir le prompt du serveur
            prompt = s.recv(1024).decode()
            print(prompt, end="")
            
            # Saisir le pseudo
            pseudo = input()  # ⏸️ BLOQUE jusqu'à ce que user tape Enter
            s.sendall(pseudo.encode())  # Envoyer au serveur
            
            print("\n=== Chat démarré ===")
            print("Commandes: /quit pour quitter\n")
            
            # ─────────────────────────────────────
            # BOUCLE PRINCIPALE : Envoi de messages
            # ─────────────────────────────────────
            while True:
                # ⏸️ BLOQUE jusqu'à ce que user tape un message
                message = input()
                
                # Commande de déconnexion
                if message.lower() == "/quit":
                    s.sendall(message.encode())
                    print("[INFO] Déconnexion...")
                    break
                
                # Envoyer le message (si non vide)
                if message.strip():
                    s.sendall(message.encode())
                    
    except ConnectionRefusedError:
        print("[ERREUR] Impossible de se connecter au serveur.")
    except KeyboardInterrupt:
        print("\n[INFO] Déconnexion...")
    except Exception as e:
        print(f"[ERREUR] {e}")


# ========================================
# POINT D'ENTRÉE
# ========================================
if __name__ == "__main__":
    start_client()
```

---

## 3.2 📊 Schéma de Fonctionnement du Client

```
CLIENT : Alice

Thread Principal                         Thread de Réception
│                                        │
├─ connect() au serveur                  │
├─ Lancer Thread(receive_messages) ─────→ while True:
│                                        │   recv() ⏸️ BLOQUE
├─ recv(prompt) ⏸️                       │   (attend messages...)
├─ "Entrez votre pseudo: "               │
├─ input() ⏸️ BLOQUE                     │
├─ Alice tape "Alice"                    │
├─ sendall("Alice")                      │
│                                        ├─ ✉️ Reçoit "[SERVEUR] Bob rejoint"
│                                        ├─ print("[SERVEUR] Bob rejoint")
│                                        ├─ recv() ⏸️
├─ while True:                           │
│   input() ⏸️ BLOQUE                    │
│   (attend que user tape...)            │
│                                        │
├─ Alice tape "Salut!"                   │
├─ sendall("Salut!")                     │
│                                        ├─ ✉️ Reçoit "[Bob] Salut Alice!"
│                                        ├─ print("[Bob] Salut Alice!")
├─ input() ⏸️                            ├─ recv() ⏸️
│                                        │
├─ Alice tape "Comment ça va?"           │
├─ sendall("Comment ça va?")             │
├─ input() ⏸️                            ├─ recv() ⏸️
│                                        │
```

**Points Clés :**
- Les 2 threads BLOQUENT indépendamment
- Thread principal : BLOQUE sur `input()` (attend user)
- Thread de réception : BLOQUE sur `recv()` (attend serveur)
- Ils ne se bloquent PAS mutuellement !

---

# 🎓 PARTIE 4 : COMMUNICATION COMPLÈTE - SCÉNARIO DÉTAILLÉ

## 4.1 Scénario : Alice et Bob Chattent

### Situation Initiale
- Serveur démarré et en attente
- 2 clients vont se connecter

---

### 📅 TIMELINE COMPLÈTE

```
════════════════════════════════════════════════════════════════════
T=0s : SERVEUR DÉMARRE
════════════════════════════════════════════════════════════════════

SERVEUR (Thread Principal)
├─ socket.socket()
├─ bind(("127.0.0.1", 65432))
├─ listen()
├─ print("[SERVEUR DEMARRÉ]")
└─ accept() ⏸️ BLOQUE (attend un client...)

clients = []  ← Liste vide


════════════════════════════════════════════════════════════════════
T=2s : ALICE SE CONNECTE
════════════════════════════════════════════════════════════════════

CLIENT ALICE (Thread Principal)           SERVEUR
│                                         │
├─ socket.socket()                        │
├─ connect(("127.0.0.1", 65432)) ────────→ accept() ✅ Connexion acceptée!
│                                         ├─ conn, addr = ...
│                                         ├─ Thread(handle_client, Alice)
│                                         ├─ thread.start() ───→ THREAD ALICE
│                                         │                     │
│                                         │                     ├─ print("[NOUVELLE CONNEXION]")
│                                         │                     ├─ sendall("Entrez votre pseudo: ")
│                                         │                     │
├─ Lancer Thread(receive) ───→ THREAD RX  │                     │
│                            ├─ recv() ⏸️ │                     │
│                            │            │                     │
├─ recv() ⏸️                 │            │                     ├─ recv() ⏸️ (attend pseudo)
├─ ✉️ "Entrez votre pseudo:  │            │                     │
├─ print("Entrez...")        │            │                     │
├─ input() ⏸️                │            │                     │
├─ User tape "Alice"         │            │                     │
├─ sendall("Alice") ─────────────────────────────────────────→ ✉️ recv() reçoit "Alice"
│                            │            │                     ├─ pseudo = "Alice"
│                            │            │                     ├─ clients.append((conn, "Alice"))
│                            │            │                     ├─ broadcast("[SERVEUR] Alice rejoint")
│                            │            │                     ├─ print("[INFO] Alice rejoint")
│                            │            │                     │
├─ print("=== Chat démarré")│            │                     ├─ while True:
├─ while True:               │            │                     │   recv() ⏸️ BLOQUE (attend message Alice)
│   input() ⏸️ (attend user) │            │                     │
│                            │            │                     │
│                            │            └─ accept() ⏸️ (attend autre client)

clients = [(conn_alice, "Alice")]  ← Alice ajoutée !


════════════════════════════════════════════════════════════════════
T=5s : BOB SE CONNECTE
════════════════════════════════════════════════════════════════════

CLIENT BOB                                SERVEUR
│                                         │
├─ connect() ────────────────────────────→ accept() ✅
│                                         ├─ Thread(handle_client, Bob)
│                                         └─ thread.start() ───→ THREAD BOB
│                                                               │
│                                         ┌──────────────────  ├─ sendall("Entrez pseudo")
│                                         │ THREAD ALICE       ├─ recv() ⏸️
│                                         ├─ recv() ⏸️          │
│                                         │                     │
├─ Lancer Thread(receive) ─→ THREAD RX    │                     │
│                          ├─ recv() ⏸️   │                     │
├─ recv() "Entrez pseudo"  │              │                     │
├─ input() ⏸️              │              │                     │
├─ User tape "Bob"         │              │                     │
├─ sendall("Bob") ──────────────────────────────────────────→ ✉️ recv() reçoit "Bob"
│                          │              │                     ├─ pseudo = "Bob"
│                          │              │                     ├─ clients.append((conn, "Bob"))
│                          │              │                     ├─ broadcast("[SERVEUR] Bob rejoint")
│                          │              │                     │
│                          │              ├─ ✉️ Reçoit broadcast├─ for client in clients:
│                          │              ├─ "[SERVEUR] Bob..."│     if client != sender:
│                          │              ├─ print(message)    │         sendall(...)
│                          │              ├─ recv() ⏸️          │
│                          │              │                     ├─ recv() ⏸️
├─ while True:             │              │                     │
│   input() ⏸️             ├─ recv() ⏸️   │                     │
│                          │              │                     │

clients = [(conn_alice, "Alice"), (conn_bob, "Bob")]  ← Bob ajouté !


════════════════════════════════════════════════════════════════════
T=8s : ALICE ENVOIE "Salut Bob!"
════════════════════════════════════════════════════════════════════

CLIENT ALICE                              SERVEUR
├─ User tape "Salut Bob!"                 │
├─ sendall("Salut Bob!") ────────────────→ THREAD ALICE
│                                         ├─ recv() ✅ reçoit "Salut Bob!"
│                                         ├─ message = "Salut Bob!"
│                                         ├─ full_message = "[Alice] Salut Bob!\n"
│                                         ├─ broadcast(full_message, conn_alice)
│                                         │
│                                         │  Parcourt clients:
│                                         │  1. (conn_alice, "Alice") ← SKIP (sender)
│                                         │  2. (conn_bob, "Bob") ← ENVOYER ✅
│                                         │     conn_bob.sendall("[Alice] Salut Bob!")
│                                         │
│                                         ├─ recv() ⏸️ (attend prochain message Alice)
│                                         │
│                          CLIENT BOB     │ THREAD BOB
│                          THREAD RX      │ ├─ recv() ⏸️
│                          ├─ recv() ✅ ←───────────────────────────── (rien à faire ici)
│                          ├─ ✉️ "[Alice] Salut Bob!"
│                          ├─ print("[Alice] Salut Bob!")
│                          ├─ recv() ⏸️
│                          │
├─ input() ⏸️              Client Bob (Principal)
│                          ├─ input() ⏸️
│                          │


════════════════════════════════════════════════════════════════════
T=10s : BOB RÉPOND "Salut Alice!"
════════════════════════════════════════════════════════════════════

CLIENT BOB                                SERVEUR
├─ User tape "Salut Alice!"               │
├─ sendall("Salut Alice!") ──────────────→ THREAD BOB
│                                         ├─ recv() ✅ reçoit "Salut Alice!"
│                                         ├─ full_message = "[Bob] Salut Alice!\n"
│                                         ├─ broadcast(full_message, conn_bob)
│                                         │
│                                         │  Parcourt clients:
│                                         │  1. (conn_alice, "Alice") ← ENVOYER ✅
│                                         │     conn_alice.sendall("[Bob] Salut Alice!")
│                                         │  2. (conn_bob, "Bob") ← SKIP (sender)
│                                         │
│                                         ├─ recv() ⏸️
│                                         │
CLIENT ALICE                              │ THREAD ALICE
THREAD RX                                 │ ├─ recv() ⏸️
├─ recv() ✅ ←──────────────────────────────────── (rien à faire)
├─ ✉️ "[Bob] Salut Alice!"
├─ print("[Bob] Salut Alice!")
├─ recv() ⏸️
│
Client Alice (Principal)
├─ input() ⏸️


════════════════════════════════════════════════════════════════════
T=15s : ALICE TAPE /quit
════════════════════════════════════════════════════════════════════

CLIENT ALICE                              SERVEUR
├─ User tape "/quit"                      │
├─ sendall("/quit") ─────────────────────→ THREAD ALICE
├─ print("[INFO] Déconnexion")            ├─ recv() ✅ reçoit "/quit"
├─ break (sortir de while)                ├─ if message == "/quit": break
├─ Connexion fermée                       ├─ finally:
└─ Programme termine                      │   clients.remove((conn, "Alice"))
                                          │   broadcast("[SERVEUR] Alice a quitté")
                                          │   conn.close()
                                          └─ Thread ALICE termine
                                          
                                          CLIENT BOB
                                          THREAD RX
                                          ├─ recv() ✅
                                          ├─ ✉️ "[SERVEUR] Alice a quitté\n"
                                          ├─ print("[SERVEUR] Alice a quitté")
                                          └─ recv() ⏸️

clients = [(conn_bob, "Bob")]  ← Alice retirée !
```

---

## 4.2 🔍 Analyse Détaillée : Que se Passe-t-il dans `broadcast()` ?

Quand Alice envoie "Salut Bob!", voici ce qui se passe EXACTEMENT :

```python
# Dans THREAD ALICE du serveur :
full_message = "[Alice] Salut Bob!\n"
broadcast(full_message, conn_alice)  # conn_alice = socket d'Alice

# ────────────────────────────────────────────────────
# Fonction broadcast() est appelée :
# ────────────────────────────────────────────────────

def broadcast(message, sender_socket=None):
    # message = "[Alice] Salut Bob!\n"
    # sender_socket = conn_alice
    
    with clients_lock:  # 🔒 Acquérir le verrou
        # clients = [(conn_alice, "Alice"), (conn_bob, "Bob")]
        
        for client_socket, _ in clients:
            # ITÉRATION 1 :
            # client_socket = conn_alice
            # sender_socket = conn_alice
            if client_socket != sender_socket:  # False !
                # On ne rentre PAS ici (Alice ne reçoit pas son propre message)
                pass
            
            # ITÉRATION 2 :
            # client_socket = conn_bob
            # sender_socket = conn_alice
            if client_socket != sender_socket:  # True !
                try:
                    # On envoie à Bob ! ✅
                    conn_bob.sendall("[Alice] Salut Bob!\n".encode())
                except:
                    pass
    # 🔓 Libérer le verrou
```

**Résultat** : Seul Bob reçoit le message !

---

# 🎓 PARTIE 5 : CONCEPTS AVANCÉS ET PIÈGES

## 5.1 Pourquoi `thread.daemon = True` pour le Client ?

```python
thread = threading.Thread(target=receive_messages, args=(s,))
thread.daemon = True  # ← Pourquoi ?
thread.start()
```

**Sans daemon :**
```
Programme Principal         Thread de Réception
├─ while True:              ├─ while True:
│   input()                 │   recv() ⏸️
│   ...                     │
├─ break (user tape /quit)  │   recv() ⏸️ ← TOUJOURS EN ATTENTE !
└─ Programme veut finir     │
   ❌ BLOQUÉ car thread      │ ← Thread empêche la fin du programme
   non-daemon tourne encore  │
```

**Avec daemon :**
```
Programme Principal         Thread de Réception (daemon)
├─ while True:              ├─ while True:
│   input()                 │   recv() ⏸️
│   ...                     │
├─ break                    │   recv() ⏸️
└─ Programme termine ✅     │
                            └─ Thread DAEMON s'arrête automatiquement ✅
```

**Règle** : Un thread daemon ne peut pas empêcher le programme de se terminer.

---

## 5.2 Race Condition et Importance du Lock

### Scénario Problématique Sans Lock :

```python
# ❌ CODE DANGEREUX SANS LOCK
clients = [Alice, Bob]

# Thread Charlie                    Thread David
def handle_client(conn, pseudo):   def handle_client(conn, pseudo):
    # Pas de lock !                 # Pas de lock !
    clients.append((conn, pseudo))  clients.append((conn, pseudo))
```

**Ce qui se passe au niveau CPU :**

```
T=0   Thread Charlie lit clients        → [Alice, Bob]
T=1   Thread David lit clients          → [Alice, Bob]
T=2   Thread Charlie calcule nouvelle   → [Alice, Bob, Charlie]
T=3   Thread David calcule nouvelle     → [Alice, Bob, David]
T=4   Thread Charlie écrit clients      → clients = [Alice, Bob, Charlie]
T=5   Thread David écrit clients        → clients = [Alice, Bob, David]
      ❌ Charlie est ÉCRASÉ !
```

### Avec Lock :

```python
# ✅ CODE SÛR AVEC LOCK
with clients_lock:  # 🔒
    clients.append((conn, pseudo))
```

```
T=0   Thread Charlie acquiert lock 🔒   ✅ Autorisé
T=1   Thread David tente lock 🔒         ⏸️ BLOQUE (attend)
T=2   Thread Charlie lit clients        → [Alice, Bob]
T=3   Thread Charlie append              → [Alice, Bob, Charlie]
T=4   Thread Charlie écrit clients      → clients = [Alice, Bob, Charlie]
T=5   Thread Charlie libère lock 🔓     
T=6   Thread David acquiert lock 🔒     ✅ Autorisé
T=7   Thread David lit clients          → [Alice, Bob, Charlie]
T=8   Thread David append                → [Alice, Bob, Charlie, David]
T=9   Thread David écrit clients        → clients = [A, B, C, D] ✅
```

---

## 5.3 Pourquoi recv(1024) ?

```python
data = conn.recv(1024)  # ← Que signifie 1024 ?
```

**1024** = Taille maximum du buffer de réception (en bytes)

### Si le message est plus grand que 1024 bytes ?

```python
# Client envoie : "A" * 3000 (3000 caractères 'A')
s.sendall(("A" * 3000).encode())

# Serveur reçoit :
data1 = conn.recv(1024)  # Reçoit les 1024 premiers bytes
# Il reste encore 1976 bytes dans le buffer TCP !

data2 = conn.recv(1024)  # Reçoit les 1024 suivants
data3 = conn.recv(1024)  # Reçoit les 952 derniers

# Pour tout recevoir :
full_data = b""
while len(full_data) < expected_size:
    chunk = conn.recv(1024)
    full_data += chunk
```

**Dans notre chat** : Les messages sont généralement courts (<1024), donc OK !

---

## 5.4 Que se Passe-t-il si un Client Plante ?

```python
# Alice plante brutalement (Ctrl+C, crash, perte réseau...)

SERVEUR - THREAD ALICE
├─ recv() ⏸️ (attend message Alice)
│
├─ ❌ Connexion perdue !
│
├─ recv() retourne b"" (bytes vide)
│
├─ if not data:  # True !
│     break
│
└─ finally:
      clients.remove((conn, "Alice"))  # ✅ Nettoyage
      broadcast("Alice a quitté")
      conn.close()
```

**Gestion robuste** : Le `finally` garantit le nettoyage !

---

# 🎓 PARTIE 6 : GESTION MULTI-CLIENTS AVEC THREADS - SYNTHÈSE

## 6.1 Architecture Complète

```
┌─────────────────────────────────────────────────────────────┐
│                         SERVEUR                             │
│                                                             │
│  Thread Principal          Ressources Partagées            │
│  ┌──────────────┐         ┌──────────────────┐            │
│  │ while True:  │         │ clients = []     │            │
│  │   accept() ⏸️ │ ◄─────► │ clients_lock 🔒  │            │
│  │   create     │         └──────────────────┘            │
│  │   thread     │                   ▲                      │
│  └──────┬───────┘                   │                      │
│         │                           │                      │
│         ├───────────────────────────┼──────────────┐       │
│         │                           │              │       │
│         ▼                           │              ▼       │
│  ┌──────────────┐            ┌──────────────┐  ┌─────────┐│
│  │ Thread       │            │ Thread       │  │ Thread  ││
│  │ Alice        │            │ Bob          │  │ Charlie ││
│  │              │            │              │  │         ││
│  │ recv() ⏸️    │            │ recv() ⏸️    │  │ recv()⏸️││
│  │ broadcast()  │────────────│ broadcast()  │──│ recv()⏸️││
│  └──────────────┘     ▲      └──────────────┘  └─────────┘│
│                       │                                     │
└───────────────────────┼─────────────────────────────────────┘
                        │
          sendall() à tous les autres clients
                        │
        ┌───────────────┴────────────────┐
        │                                │
        ▼                                ▼
   ┌─────────┐                      ┌─────────┐
   │ CLIENT  │                      │ CLIENT  │
   │ Alice   │                      │ Bob     │
   │         │                      │         │
   │ Thread  │  Thread Principal    │ Thread  │  Thread Principal
   │ RX      │                      │ RX      │
   │ recv()⏸️│  input() ⏸️          │ recv()⏸️│  input() ⏸️
   └─────────┘                      └─────────┘
```

---

## 6.2 Points Clés à Retenir

### ✅ Côté Serveur :

1. **Thread Principal** :
   - Boucle `while True` + `accept()`
   - Ne fait QUE accepter les connexions
   - Crée un thread par client

2. **Thread par Client** :
   - Fonction `handle_client()`
   - Bloque sur `recv()` pour SON client
   - Utilise `broadcast()` pour diffuser
   - Se termine quand le client se déconnecte

3. **Synchronisation** :
   - `clients_lock` protège la liste `clients`
   - TOUJOURS utiliser `with clients_lock:` pour modifier `clients`

### ✅ Côté Client :

1. **Thread Principal** :
   - Bloque sur `input()` (attend utilisateur)
   - Envoie les messages avec `sendall()`

2. **Thread de Réception** :
   - Bloque sur `recv()` (attend serveur)
   - Affiche les messages reçus
   - Daemon pour ne pas bloquer la fin du programme

---

## 6.3 Tableau Récapitulatif des Blocages

| Où | Quoi | Bloque sur | Jusqu'à quand | Impact |
|----|------|------------|---------------|--------|
| Serveur - Thread Principal | `accept()` | Nouvelle connexion | Client se connecte | ✅ Normal, c'est son rôle |
| Serveur - Thread Client | `recv()` | Message du client | Client envoie | ✅ OK, thread séparé |
| Client - Thread Principal | `input()` | Saisie utilisateur | User tape Enter | ✅ OK, on attend user |
| Client - Thread Réception | `recv()` | Message du serveur | Serveur envoie | ✅ OK, thread séparé |

**La clé** : Les blocages sont dans des threads SÉPARÉS, donc ne se gênent pas !

---

### 1. Démarrer le Serveur

```bash
python chat_server.py
```

Vous verrez :
```
[SERVEUR DEMARRÉ] Écoute sur 127.0.0.1:65432
En attente de connexions...
```

### 2. Lancer Plusieurs Clients

Ouvrez plusieurs terminaux et lancez :

```bash
python chat_client.py
```

### 3. Utilisation

1. Entrez votre pseudo quand demandé
2. Tapez vos messages et appuyez sur Entrée
3. Les messages sont diffusés à tous les autres clients
4. Tapez `/quit` pour vous déconnecter

---

## 📊 Exemple de Session

**Terminal Serveur :**
```
[SERVEUR DEMARRÉ] Écoute sur 127.0.0.1:65432
[NOUVELLE CONNEXION] ('127.0.0.1', 52341) connecté
[INFO] Alice (('127.0.0.1', 52341)) a rejoint le chat
[NOUVELLE CONNEXION] ('127.0.0.1', 52342) connecté
[INFO] Bob (('127.0.0.1', 52342)) a rejoint le chat
Message reçu: [Alice] Salut tout le monde!
Message reçu: [Bob] Bonjour Alice!
```

**Terminal Client 1 (Alice) :**
```
Entrez votre pseudo: Alice

=== Chat démarré ===
[SERVEUR] Bob a rejoint le chat!
Salut tout le monde!
[Bob] Bonjour Alice!
```

**Terminal Client 2 (Bob) :**
```
Entrez votre pseudo: Bob

=== Chat démarré ===
[Alice] Salut tout le monde!
Bonjour Alice!
```

---

## 🔧 Points Techniques Importants

### Threading
- **Serveur** : Un thread par client pour gérer plusieurs connexions simultanées
- **Client** : Un thread pour recevoir les messages pendant que le thread principal gère l'envoi

### Synchronisation
```python
clients_lock = threading.Lock()
```
Protège la liste des clients contre les accès concurrents

### Gestion des Erreurs
- Détection de déconnexion avec `if not data:`
- Blocs `try/except` pour gérer les erreurs réseau
- Nettoyage propre dans `finally`

---

## 🎯 Améliorations Possibles

1. **Messages privés** : `/msg pseudo message`
2. **Liste des connectés** : `/list`
3. **Historique des messages** : Sauvegarder dans un fichier
4. **Interface graphique** : Utiliser Tkinter ou PyQt
5. **Chiffrement** : SSL/TLS pour sécuriser les communications
6. **Rooms/Salons** : Créer différents canaux de discussion

---

## ⚠️ Notes de Sécurité

Ce code est à but éducatif. Pour une application en production :
- Utilisez SSL/TLS
- Validez et sanitisez toutes les entrées
- Implémentez une authentification
- Limitez la taille des messages
- Gérez les timeouts de connexion
