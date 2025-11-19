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
import json

def calculer(operation, a, b):
    """Effectue le calcul selon l'opération demandée"""
    try:
        a = float(a)
        b = float(b)
        
        if operation == '+':
            return a + b
        elif operation == '-':
            return a - b
        elif operation == '*':
            return a * b
        elif operation == '/':
            if b == 0:
                return "Erreur: Division par zéro"
            return a / b
        elif operation == '**':
            return a ** b
        else:
            return "Erreur: Opération non supportée"
    except ValueError:
        return "Erreur: Valeurs invalides"

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
    print("En attente de connexions...\n")
    
    try:
        while True:
            # Accepte une connexion (BLOQUANT)
            client_socket, adresse_client = serveur_socket.accept()
            print(f"Connexion établie avec {adresse_client}")
            
            try:
                while True:
                    # Réception des données (BLOQUANT)
                    donnees = client_socket.recv(1024).decode('utf-8')
                    
                    if not donnees:
                        print(f"Client {adresse_client} déconnecté")
                        break
                    
                    print(f"Reçu de {adresse_client}: {donnees}")
                    
                    # Traitement de la requête
                    try:
                        requete = json.loads(donnees)
                        operation = requete.get('operation')
                        a = requete.get('a')
                        b = requete.get('b')
                        
                        if operation == 'quit':
                            reponse = {'resultat': 'Au revoir!'}
                            client_socket.sendall(json.dumps(reponse).encode('utf-8'))
                            break
                        
                        resultat = calculer(operation, a, b)
                        reponse = {'resultat': resultat}
                        
                    except json.JSONDecodeError:
                        reponse = {'resultat': 'Erreur: Format JSON invalide'}
                    
                    # Envoi de la réponse
                    client_socket.sendall(json.dumps(reponse).encode('utf-8'))
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
import json

def envoyer_requete(client_socket, operation, a=None, b=None):
    """Envoie une requête au serveur et retourne la réponse"""
    
    # Préparation de la requête
    requete = {
        'operation': operation,
        'a': a,
        'b': b
    }
    
    # Envoi de la requête au serveur
    client_socket.sendall(json.dumps(requete).encode('utf-8'))
    
    # Réception de la réponse (BLOQUANT)
    reponse = client_socket.recv(1024).decode('utf-8')
    
    # Décodage de la réponse
    return json.loads(reponse)

def demarrer_client(host='127.0.0.1', port=65432):
    """Démarre le client de calculatrice"""
    
    # Création du socket TCP/IP
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        # Connexion au serveur (BLOQUANT)
        print(f"Connexion au serveur {host}:{port}...")
        client_socket.connect((host, port))
        print("Connecté au serveur!\n")
        
        print("=== Calculatrice Réseau ===")
        print("Opérations disponibles: +, -, *, /, **")
        print("Tapez 'quit' pour quitter\n")
        
        while True:
            # Saisie de l'opération
            operation = input("Opération (+, -, *, /, ** ou quit): ").strip()
            
            if operation == 'quit':
                reponse = envoyer_requete(client_socket, 'quit')
                print(reponse['resultat'])
                break
            
            if operation not in ['+', '-', '*', '/', '**']:
                print("Opération invalide!\n")
                continue
            
            # Saisie des opérandes
            try:
                a = input("Premier nombre: ").strip()
                b = input("Deuxième nombre: ").strip()
                
                # Envoi de la requête et réception de la réponse
                reponse = envoyer_requete(client_socket, operation, a, b)
                
                print(f"\nRésultat: {a} {operation} {b} = {reponse['resultat']}\n")
                
            except ValueError:
                print("Erreur: Veuillez entrer des nombres valides\n")
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

```
Connexion au serveur 127.0.0.1:65432...
Connecté au serveur!

=== Calculatrice Réseau ===
Opérations disponibles: +, -, *, /, **
Tapez 'quit' pour quitter

Opération (+, -, *, /, ** ou quit): +
Premier nombre: 15
Deuxième nombre: 7

Résultat: 15 + 7 = 22.0

Opération (+, -, *, /, ** ou quit): *
Premier nombre: 12
Deuxième nombre: 5

Résultat: 12 * 5 = 60.0

Opération (+, -, *, /, ** ou quit): /
Premier nombre: 100
Deuxième nombre: 0

Résultat: 100 / 0 = Erreur: Division par zéro

Opération (+, -, *, /, ** ou quit): **
Premier nombre: 2
Deuxième nombre: 10

Résultat: 2 ** 10 = 1024.0

Opération (+, -, *, /, ** ou quit): quit
Au revoir!
Connexion fermée.
```

## 🔍 Points d'apprentissage

### 1. Communication par JSON
Les données sont échangées au format JSON pour une sérialisation simple :
```json
{"operation": "+", "a": "15", "b": "7"}
```

### 2. Protocole requête/réponse
- Le client envoie une requête structurée
- Le serveur traite et répond avec le résultat
- Communication synchrone et bloquante

### 3. Gestion des erreurs
- Division par zéro
- Valeurs non numériques
- Opérations non supportées
- Déconnexions inattendues

### 4. Architecture client-serveur
- Un serveur peut gérer plusieurs clients séquentiellement
- Chaque client a sa propre session
- Fermeture propre des connexions

## 💡 Exercices d'extension

### Niveau débutant
1. Ajouter d'autres opérations (modulo %, racine carrée)
2. Créer un mode debug avec plus de logs
3. Permettre de changer le port via argument en ligne de commande

### Niveau intermédiaire
4. Implémenter un historique des calculs côté serveur
5. Ajouter une commande `history` pour voir les derniers calculs
6. Créer un système d'authentification simple (nom d'utilisateur)
7. Ajouter la possibilité de faire des calculs avec plus de 2 opérandes

### Niveau avancé
8. Utiliser le threading pour gérer plusieurs clients simultanément
9. Implémenter un timeout sur les opérations
10. Créer un protocole de commandes plus riche (HELP, STATS, etc.)
11. Ajouter la persistance de l'historique dans un fichier
12. Créer une version avec sockets non-bloquants (select/asyncio)

## 📚 Ressources

### Documentation Python
- [Module socket](https://docs.python.org/3/library/socket.html)
- [Module json](https://docs.python.org/3/library/json.html)

### Concepts réseau
- **TCP/IP** : protocole de transport fiable
- **Port** : identifiant d'application (65432 dans cet exemple)
- **localhost/127.0.0.1** : adresse de bouclage local
- **Sockets bloquants** : les appels bloquent jusqu'à complétion

## ⚠️ Limitations actuelles

1. **Séquentiel** : le serveur ne gère qu'un client à la fois
2. **Pas d'authentification** : aucune sécurité
3. **Réseau local seulement** : configuré pour localhost
4. **Pas de chiffrement** : communication en clair
5. **Gestion d'erreurs basique** : pourrait être plus robuste

## 🎓 Ce que vous avez appris

✅ Créer et configurer des sockets TCP  
✅ Établir une connexion client-serveur  
✅ Envoyer et recevoir des données via le réseau  
✅ Sérialiser/désérialiser des données en JSON  
✅ Gérer la fermeture propre des connexions  
✅ Comprendre le comportement bloquant des sockets  
✅ Implémenter un protocole de communication simple  

---

**Bon apprentissage ! 🚀**
