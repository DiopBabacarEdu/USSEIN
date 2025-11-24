# Architecture Client-Serveur Simplifiée avec Base de Données MySQL

Ce projet vise à créer une architecture client-serveur simple permettant à des applications distantes d'interagir avec une base de données MySQL via des sockets réseau, sans nécessiter l'installation locale de MySQL. 

Cette version simplifiée traite les clients de manière séquentielle, ce qui la rend plus facile à comprendre et à maintenir pour des projets de petite envergure.

## Serveur Simplifié

```python
# server.py
import socket
import mysql.connector
from mysql.connector import Error
import json

class DatabaseServer:
    def __init__(self, host='localhost', port=3306, socket_port=8888):
        self.db_config = {
            'host': host,
            'port': port,
            'user': 'root',  # À modifier
            'password': 'votre_mot_de_passe',  # À modifier
            'database': 'test_db'
        }
        self.socket_host = 'localhost'
        self.socket_port = socket_port
        self.setup_database()
        
    def setup_database(self):
        """Initialise la base de données et crée les tables si nécessaire"""
        try:
            # Connexion sans base de données spécifique pour la créer
            temp_config = self.db_config.copy()
            temp_config.pop('database', None)
            
            conn = mysql.connector.connect(**temp_config)
            cursor = conn.cursor()
            
            # Créer la base de données si elle n'existe pas
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.db_config['database']}")
            cursor.execute(f"USE {self.db_config['database']}")
            
            # Créer une table exemple
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    email VARCHAR(100) UNIQUE NOT NULL,
                    age INT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Créer une table pour les produits
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS products (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    price DECIMAL(10,2) NOT NULL,
                    stock INT DEFAULT 0,
                    category VARCHAR(50)
                )
            ''')
            
            conn.commit()
            cursor.close()
            conn.close()
            print("✓ Base de données initialisée avec succès")
            
        except Error as e:
            print(f"✗ Erreur lors de l'initialisation de la base: {e}")
    
    def execute_query(self, query, params=None):
        """Exécute une requête SQL et retourne le résultat"""
        try:
            conn = mysql.connector.connect(**self.db_config)
            cursor = conn.cursor(dictionary=True)
            
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            # Pour les SELECT, récupérer les résultats
            if query.strip().upper().startswith('SELECT'):
                result = cursor.fetchall()
            else:
                conn.commit()
                result = {"affected_rows": cursor.rowcount}
            
            cursor.close()
            conn.close()
            
            return {"success": True, "data": result}
            
        except Error as e:
            return {"success": False, "error": str(e)}
    
    def handle_client(self, client_socket, address):
        """Gère la communication avec un client"""
        print(f"\n→ Connexion établie avec {address}")
        
        try:
            # Recevoir la requête du client
            data = client_socket.recv(4096).decode('utf-8')
            
            if data:
                try:
                    request = json.loads(data)
                    query = request.get('query')
                    params = request.get('params')
                    
                    print(f"→ Requête reçue: {query[:50]}...")
                    
                    # Exécuter la requête
                    result = self.execute_query(query, params)
                    
                    # Envoyer la réponse
                    response = json.dumps(result)
                    client_socket.send(response.encode('utf-8'))
                    print(f"✓ Réponse envoyée")
                    
                except json.JSONDecodeError:
                    error_response = json.dumps({
                        "success": False, 
                        "error": "Format JSON invalide"
                    })
                    client_socket.send(error_response.encode('utf-8'))
                    
        except Exception as e:
            print(f"✗ Erreur avec le client {address}: {e}")
        finally:
            client_socket.close()
            print(f"← Connexion fermée avec {address}")
    
    def start_server(self):
        """Démarre le serveur socket"""
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        try:
            server_socket.bind((self.socket_host, self.socket_port))
            server_socket.listen(5)
            print(f"\n{'='*50}")
            print(f"Serveur démarré sur {self.socket_host}:{self.socket_port}")
            print(f"{'='*50}\n")
            print("En attente de connexions...")
            
            while True:
                # Accepter une connexion
                client_socket, address = server_socket.accept()
                
                # Traiter le client immédiatement (pas de thread)
                self.handle_client(client_socket, address)
                
        except KeyboardInterrupt:
            print("\n\nArrêt du serveur...")
        except Exception as e:
            print(f"✗ Erreur du serveur: {e}")
        finally:
            server_socket.close()
            print("Serveur arrêté")

if __name__ == "__main__":
    server = DatabaseServer()
    server.start_server()
```

## Client Python Simplifié

```python
# client.py
import socket
import json

class DatabaseClient:
    def __init__(self, host='localhost', port=8888):
        self.host = host
        self.port = port
    
    def send_query(self, query, params=None):
        """Envoie une requête SQL au serveur"""
        try:
            # Créer la connexion
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((self.host, self.port))
            
            # Préparer la requête
            request = {
                "query": query,
                "params": params
            }
            
            # Envoyer la requête
            client_socket.send(json.dumps(request).encode('utf-8'))
            
            # Recevoir la réponse
            response = client_socket.recv(4096).decode('utf-8')
            client_socket.close()
            
            return json.loads(response)
            
        except ConnectionRefusedError:
            return {"success": False, "error": "Impossible de se connecter au serveur"}
        except Exception as e:
            return {"success": False, "error": str(e)}

def afficher_menu():
    """Affiche le menu principal"""
    print("\n" + "="*40)
    print("    CLIENT BASE DE DONNÉES")
    print("="*40)
    print("1. Ajouter un utilisateur")
    print("2. Voir tous les utilisateurs")
    print("3. Ajouter un produit")
    print("4. Voir tous les produits")
    print("5. Requête personnalisée")
    print("6. Quitter")
    print("="*40)

def main():
    client = DatabaseClient()
    
    print("\nConnexion au serveur de base de données...")
    
    while True:
        afficher_menu()
        choice = input("\nVotre choix: ")
        
        if choice == '1':
            print("\n--- Ajouter un utilisateur ---")
            name = input("Nom: ")
            email = input("Email: ")
            age = input("Age: ")
            
            query = "INSERT INTO users (name, email, age) VALUES (%s, %s, %s)"
            params = (name, email, int(age) if age else None)
            
            result = client.send_query(query, params)
            
            if result["success"]:
                print("✓ Utilisateur ajouté avec succès!")
            else:
                print(f"✗ Erreur: {result['error']}")
            
        elif choice == '2':
            print("\n--- Liste des utilisateurs ---")
            query = "SELECT * FROM users ORDER BY created_at DESC"
            result = client.send_query(query)
            
            if result["success"]:
                users = result["data"]
                if users:
                    print(f"\n{len(users)} utilisateur(s) trouvé(s):\n")
                    for user in users:
                        print(f"  ID: {user['id']}")
                        print(f"  Nom: {user['name']}")
                        print(f"  Email: {user['email']}")
                        print(f"  Age: {user['age']}")
                        print(f"  Créé le: {user['created_at']}")
                        print("-" * 40)
                else:
                    print("Aucun utilisateur trouvé")
            else:
                print(f"✗ Erreur: {result['error']}")
                
        elif choice == '3':
            print("\n--- Ajouter un produit ---")
            name = input("Nom du produit: ")
            price = input("Prix: ")
            stock = input("Stock: ")
            category = input("Catégorie: ")
            
            query = "INSERT INTO products (name, price, stock, category) VALUES (%s, %s, %s, %s)"
            params = (name, float(price), int(stock), category)
            
            result = client.send_query(query, params)
            
            if result["success"]:
                print("✓ Produit ajouté avec succès!")
            else:
                print(f"✗ Erreur: {result['error']}")
            
        elif choice == '4':
            print("\n--- Liste des produits ---")
            query = "SELECT * FROM products ORDER BY id DESC"
            result = client.send_query(query)
            
            if result["success"]:
                products = result["data"]
                if products:
                    print(f"\n{len(products)} produit(s) trouvé(s):\n")
                    for product in products:
                        print(f"  ID: {product['id']}")
                        print(f"  Nom: {product['name']}")
                        print(f"  Prix: {product['price']}€")
                        print(f"  Stock: {product['stock']}")
                        print(f"  Catégorie: {product['category']}")
                        print("-" * 40)
                else:
                    print("Aucun produit trouvé")
            else:
                print(f"✗ Erreur: {result['error']}")
                
        elif choice == '5':
            print("\n--- Requête personnalisée ---")
            query = input("Entrez votre requête SQL: ")
            result = client.send_query(query)
            
            if result["success"]:
                print("\n✓ Résultat:")
                print(json.dumps(result["data"], indent=2, default=str))
            else:
                print(f"✗ Erreur: {result['error']}")
            
        elif choice == '6':
            print("\nAu revoir!")
            break
            
        else:
            print("\n✗ Option invalide!")

if __name__ == "__main__":
    main()
```

## Script d'Initialisation de la Base de Données

```sql
-- init_database.sql
-- Créer la base de données
CREATE DATABASE IF NOT EXISTS test_db;
USE test_db;

-- Créer l'utilisateur pour l'application (optionnel)
CREATE USER IF NOT EXISTS 'app_user'@'localhost' IDENTIFIED BY 'app_password';
GRANT ALL PRIVILEGES ON test_db.* TO 'app_user'@'localhost';
FLUSH PRIVILEGES;

-- Données d'exemple
INSERT INTO users (name, email, age) VALUES 
('Alice Dupont', 'alice@email.com', 30),
('Bob Martin', 'bob@email.com', 25),
('Charlie Brown', 'charlie@email.com', 35);

INSERT INTO products (name, price, stock, category) VALUES 
('Laptop', 999.99, 10, 'Electronics'),
('Smartphone', 699.99, 25, 'Electronics'),
('Livre Python', 29.99, 100, 'Books');
```

## Configuration

```txt
# requirements.txt
mysql-connector-python==8.0.33
```

## Installation et Utilisation

### 1. Installer MySQL
```bash
# Sur Ubuntu/Debian
sudo apt update
sudo apt install mysql-server

# Sur macOS
brew install mysql
```

### 2. Installer les dépendances Python
```bash
pip install mysql-connector-python
```

### 3. Configurer la base de données
```bash
# Se connecter à MySQL
sudo mysql -u root -p

# Exécuter le script d'initialisation
source init_database.sql
```

### 4. Configurer le serveur
Modifiez les paramètres dans `server.py`:
```python
self.db_config = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',  # Votre utilisateur MySQL
    'password': 'votre_mot_de_passe',  # Votre mot de passe
    'database': 'test_db'
}
```

### 5. Démarrer le serveur
```bash
python server.py
```

### 6. Lancer le client (dans un autre terminal)
```bash
python client.py
```

## Avantages de cette Version Simplifiée

✅ **Code plus simple** : Pas de gestion de threads, plus facile à comprendre

✅ **Moins de bugs potentiels** : Moins de complexité = moins de risques

✅ **Débogage facile** : Les erreurs sont plus simples à tracer

✅ **Parfait pour l'apprentissage** : Idéal pour comprendre les bases

✅ **Utilisation des ressources** : Moins gourmand en mémoire

## Limitations

⚠️ **Un client à la fois** : Le serveur traite les connexions séquentiellement

⚠️ **Performance** : Non adapté pour de multiples clients simultanés

⚠️ **Temps d'attente** : Les clients doivent attendre leur tour

## Fonctionnalités

- Communication client-serveur via sockets
- Exécution sécurisée des requêtes SQL
- Support des paramètres (protection contre l'injection SQL)
- Format JSON pour l'échange de données
- Interface client interactive et conviviale
- Gestion des erreurs claire
- Initialisation automatique de la base de données

## Améliorations Possibles

Pour passer à une version plus avancée, vous pourriez ajouter :

- Authentification avec nom d'utilisateur et mot de passe
- Chiffrement SSL/TLS pour sécuriser les communications
- Fichier de logs pour tracer les opérations
- Validation avancée des requêtes SQL
- Limitation du nombre de requêtes par client

Cette architecture simplifiée est parfaite pour débuter et comprendre les principes de communication client-serveur avec base de données!
