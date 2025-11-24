# Exercice : Calculatrice Client-Serveur avec Sockets Bloquants en Python

## 📋 Objectif

Créer une application client-serveur de calculatrice utilisant des sockets TCP bloquants en Python. Le serveur effectue les calculs demandés par les clients et renvoie les résultats.

## 🎯 Concepts clés

### Sockets bloquants
- **`accept()`** : bloque jusqu'à ce qu'un client se connecte
- **`recv()`** : bloque jusqu'à recevoir des données
- **`connect()`** : bloque jusqu'à établir la connexion
- **`sendall()`** : bloque jusqu'à ce que toutes les données soient envoyées

## 📁 Fichier 1 : serveur.py

```python
import socket

def addition(a, b):
    """Additionne deux nombres"""
    return a + b

def soustraction(a, b):
    """Soustrait b de a"""
    return a - b

def multiplication(a, b):
    """Multiplie deux nombres"""
    return a * b

def division(a, b):
    """Divise a par b"""
    if b == 0:
        return "ERREUR:Division par zéro"
    return a / b

def puissance(a, b):
    """Calcule a puissance b"""
    return a ** b

def modulo(a, b):
    """Calcule le reste de la division de a par b"""
    if b == 0:
        return "ERREUR:Division par zéro"
    return a % b

def racine_carree(a, b=None):
    """Calcule la racine carrée de a"""
    if a < 0:
        return "ERREUR:Racine carrée d'un nombre négatif"
    return a ** 0.5

def calculer(operation, a, b):
    """Effectue le calcul selon l'opération demandée"""
    try:
        a = float(a)
        b = float(b) if b else 0
        
        operations = {
            'ADD': addition,
            'SUB': soustraction,
            'MUL': multiplication,
            'DIV': division,
            'POW': puissance,
            'MOD': modulo,
            'SQRT': racine_carree
        }
        
        if operation in operations:
            resultat = operations[operation](a, b)
            if isinstance(resultat, str) and resultat.startswith("ERREUR"):
                return resultat
            return f"RESULTAT:{resultat}"
        else:
            return "ERREUR:Opération non supportée"
    except ValueError:
        return "ERREUR:Valeurs invalides"
    except Exception as e:
        return f"ERREUR:{str(e)}"

def demarrer_serveur(host='127.0.0.1', port=65432):
    """Démarre le serveur de calculatrice"""
    
    # Création du socket TCP/IP
    serveur_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # Permet de réutiliser l'adresse immédiatement
    serveur_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    # Liaison du socket à l'adresse et au port
    serveur_socket.bind((host, port))
    
    # Écoute des connexions entrantes (max 5 en attente)
    serveur_socket.listen(5)
    
    print(f"Serveur de calculatrice démarré sur {host}:{port}")
    print("Protocole: OPERATION|NOMBRE1|NOMBRE2")
    print("Opérations disponibles: ADD, SUB, MUL, DIV, POW, MOD, SQRT")
    print("En attente de connexions...\n")
    
    try:
        while True:
            # Accepte une connexion (BLOQUANT)
            client_socket, adresse_client = serveur_socket.accept()
            print(f"Connexion établie avec {adresse_client}")
            
            try:
                while True:
                    # Réception des données (BLOQUANT)
                    donnees = client_socket.recv(1024).decode('utf-8').strip()
                    
                    if not donnees:
                        print(f"Client {adresse_client} déconnecté")
                        break
                    
                    print(f"Reçu de {adresse_client}: {donnees}")
                    
                    # Traitement de la requête
                    if donnees == 'QUIT':
                        reponse = "Au revoir!"
                        client_socket.sendall(reponse.encode('utf-8'))
                        break
                    
                    # Format attendu: OPERATION|a|b
                    parties = donnees.split('|')
                    
                    if len(parties) < 2:
                        reponse = "ERREUR:Format invalide. Utilisez OPERATION|a|b"
                    else:
                        operation = parties[0].upper()
                        a = parties[1]
                        b = parties[2] if len(parties) > 2 else None
                        
                        reponse = calculer(operation, a, b)
                    
                    # Envoi de la réponse
                    client_socket.sendall(reponse.encode('utf-8'))
                    print(f"Réponse envoyée: {reponse}\n")
                    
            except Exception as e:
                print(f"Erreur avec le client {adresse_client}: {e}")
            finally:
                client_socket.close()
                print(f"Connexion fermée avec {adresse_client}\n")
                
    except KeyboardInterrupt:
        print("\nArrêt du serveur...")
    finally:
        serveur_socket.close()
        print("Serveur fermé.")

if __name__ == "__main__":
    demarrer_serveur()
```

## 📁 Fichier 2 : client.py

```python
import socket

def envoyer_requete(client_socket, message):
    """Envoie une requête au serveur et retourne la réponse"""
    
    # Envoi de la requête au serveur
    client_socket.sendall(message.encode('utf-8'))
    
    # Réception de la réponse (BLOQUANT)
    reponse = client_socket.recv(1024).decode('utf-8')
    
    return reponse

def afficher_menu():
    """Affiche le menu des opérations disponibles"""
    print("\n=== Calculatrice Réseau ===")
    print("Opérations disponibles:")
    print("  ADD  - Addition")
    print("  SUB  - Soustraction")
    print("  MUL  - Multiplication")
    print("  DIV  - Division")
    print("  POW  - Puissance")
    print("  MOD  - Modulo")
    print("  SQRT - Racine carrée (un seul nombre)")
    print("  QUIT - Quitter")
    print("\nFormat: OPERATION|nombre1|nombre2")
    print("Exemple: ADD|5|3 ou SQRT|16\n")

def demarrer_client(host='127.0.0.1', port=65432):
    """Démarre le client de calculatrice"""
    
    # Création du socket TCP/IP
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        # Connexion au serveur (BLOQUANT)
        print(f"Connexion au serveur {host}:{port}...")
        client_socket.connect((host, port))
        print("Connecté au serveur!")
        
        afficher_menu()
        
        while True:
            # Saisie de l'opération
            operation = input("Opération (ADD, SUB, MUL, DIV, POW, MOD, SQRT, QUIT): ").strip().upper()
            
            if operation == 'QUIT':
                reponse = envoyer_requete(client_socket, 'QUIT')
                print(reponse)
                break
            
            operations_valides = ['ADD', 'SUB', 'MUL', 'DIV', 'POW', 'MOD', 'SQRT']
            if operation not in operations_valides:
                print("Opération invalide!\n")
                continue
            
            # Saisie des opérandes
            try:
                a = input("Premier nombre: ").strip()
                
                # SQRT ne nécessite qu'un seul nombre
                if operation == 'SQRT':
                    message = f"{operation}|{a}|0"
                else:
                    b = input("Deuxième nombre: ").strip()
                    message = f"{operation}|{a}|{b}"
                
                # Envoi de la requête et réception de la réponse
                reponse = envoyer_requete(client_socket, message)
                
                # Affichage de la réponse
                if reponse.startswith("RESULTAT:"):
                    resultat = reponse.split(":", 1)[1]
                    if operation == 'SQRT':
                        print(f"\nRésultat: √{a} = {resultat}\n")
                    else:
                        symboles = {
                            'ADD': '+', 'SUB': '-', 'MUL': '*', 
                            'DIV': '/', 'POW': '**', 'MOD': '%'
                        }
                        symbole = symboles.get(operation, operation)
                        print(f"\nRésultat: {a} {symbole} {b} = {resultat}\n")
                elif reponse.startswith("ERREUR:"):
                    erreur = reponse.split(":", 1)[1]
                    print(f"\nErreur: {erreur}\n")
                else:
                    print(f"\nRéponse: {reponse}\n")
                
            except Exception as e:
                print(f"Erreur: {e}\n")
                
    except ConnectionRefusedError:
        print("Erreur: Impossible de se connecter au serveur.")
        print("Assurez-vous que le serveur est démarré.")
    except Exception as e:
        print(f"Erreur: {e}")
    finally:
        client_socket.close()
        print("Connexion fermée.")

if __name__ == "__main__":
    demarrer_client()
```

## 🚀 Utilisation

### 1. Démarrer le serveur
```bash
python serveur.py
```

Sortie attendue :
```
Serveur de calculatrice démarré sur 127.0.0.1:65432
En attente de connexions...
```

### 2. Démarrer un ou plusieurs clients
Dans un autre terminal :
```bash
python client.py
```

### 3. Exemple d'interaction


**Bon apprentissage ! 🚀**
