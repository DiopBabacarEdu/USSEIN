# Tutoriel : Chat Multi-Clients avec Sockets Python

## 📋 Présentation du Projet

Nous allons créer une application de chat où plusieurs clients peuvent se connecter simultanément à un serveur et échanger des messages en temps réel.

### Fonctionnalités :
- 💬 Messages diffusés à tous les clients connectés
- 👤 Système de pseudonymes
- 📢 Notifications de connexion/déconnexion
- 🔄 Gestion multi-clients avec threading

---

## 🖥️ Code du Serveur (`chat_server.py`)

```python
import socket
import threading

HOST = "127.0.0.1"
PORT = 65432

# Liste des clients connectés (socket, pseudo)
clients = []
clients_lock = threading.Lock()


def broadcast(message, sender_socket=None):
    """Envoie un message à tous les clients sauf l'émetteur"""
    with clients_lock:
        for client_socket, _ in clients:
            if client_socket != sender_socket:
                try:
                    client_socket.sendall(message.encode())
                except:
                    pass


def handle_client(conn, addr):
    """Gère la communication avec un client"""
    print(f"[NOUVELLE CONNEXION] {addr} connecté")
    
    # Demander le pseudo
    conn.sendall(b"Entrez votre pseudo: ")
    pseudo = conn.recv(1024).decode().strip()
    
    # Ajouter le client à la liste
    with clients_lock:
        clients.append((conn, pseudo))
    
    # Annoncer l'arrivée
    broadcast(f"[SERVEUR] {pseudo} a rejoint le chat!\n")
    print(f"[INFO] {pseudo} ({addr}) a rejoint le chat")
    
    try:
        while True:
            data = conn.recv(1024)
            if not data:
                break
            
            message = data.decode().strip()
            
            if message.lower() == "/quit":
                break
            
            # Diffuser le message
            full_message = f"[{pseudo}] {message}\n"
            print(f"Message reçu: {full_message.strip()}")
            broadcast(full_message, conn)
            
    except Exception as e:
        print(f"[ERREUR] {pseudo}: {e}")
    
    finally:
        # Retirer le client de la liste
        with clients_lock:
            clients.remove((conn, pseudo))
        
        broadcast(f"[SERVEUR] {pseudo} a quitté le chat.\n")
        print(f"[DECONNEXION] {pseudo} ({addr})")
        conn.close()


def start_server():
    """Démarre le serveur de chat"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print(f"[SERVEUR DEMARRÉ] Écoute sur {HOST}:{PORT}")
        print("En attente de connexions...\n")
        
        while True:
            conn, addr = s.accept()
            # Créer un thread pour chaque client
            thread = threading.Thread(target=handle_client, args=(conn, addr))
            thread.start()
            print(f"[CONNEXIONS ACTIVES] {threading.active_count() - 1}")


if __name__ == "__main__":
    start_server()
```

---

## 👨‍💻 Code du Client (`chat_client.py`)

```python
import socket
import threading
import sys

HOST = "127.0.0.1"
PORT = 65432


def receive_messages(sock):
    """Reçoit et affiche les messages du serveur"""
    while True:
        try:
            data = sock.recv(1024)
            if not data:
                print("\n[DÉCONNECTÉ] Connexion au serveur perdue.")
                break
            print(data.decode(), end="")
        except:
            break


def start_client():
    """Démarre le client de chat"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, PORT))
            print(f"[CONNECTÉ] au serveur {HOST}:{PORT}\n")
            
            # Lancer le thread de réception
            thread = threading.Thread(target=receive_messages, args=(s,))
            thread.daemon = True
            thread.start()
            
            # Saisie du pseudo
            prompt = s.recv(1024).decode()
            print(prompt, end="")
            pseudo = input()
            s.sendall(pseudo.encode())
            
            print("\n=== Chat démarré ===")
            print("Commandes: /quit pour quitter\n")
            
            # Boucle d'envoi de messages
            while True:
                message = input()
                
                if message.lower() == "/quit":
                    s.sendall(message.encode())
                    print("[INFO] Déconnexion...")
                    break
                
                if message.strip():
                    s.sendall(message.encode())
                    
    except ConnectionRefusedError:
        print("[ERREUR] Impossible de se connecter au serveur.")
    except KeyboardInterrupt:
        print("\n[INFO] Déconnexion...")
    except Exception as e:
        print(f"[ERREUR] {e}")


if __name__ == "__main__":
    start_client()
```

---

## 🚀 Instructions d'Utilisation

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
