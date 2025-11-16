# Architecture Client-Serveur avec Base de Données MySQL

Ce projet vise à créer une architecture client-serveur permettant à des applications distantes d'interagir avec une base de données MySQL via des sockets réseau, sans nécessiter l'installation locale de MySQL. 

L'objectif principal est de centraliser et sécuriser l'accès aux données tout en offrant une interface simple et standardisée pour exécuter des requêtes SQL. 

Cette solution permet de découpler le client de l'infrastructure base de données, facilitant le déploiement, la maintenance et la scalabilité des applications, tout en maintenant une communication efficace et sécurisée entre les différents composants du système.

## Architecture du Serveur

```python
# server.py
import socket
import threading
import mysql.connector
from mysql.connector import Error
import json
import hashlib

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
            print("Base de données initialisée avec succès")
            
        except Error as e:
            print(f"Erreur lors de l'initialisation de la base: {e}")
    
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
        print(f"Connexion établie avec {address}")
        
        try:
            while True:
                # Recevoir la requête du client
                data = client_socket.recv(1024).decode('utf-8')
                if not data:
                    break
                
                try:
                    request = json.loads(data)
                    query_type = request.get('type')
                    query = request.get('query')
                    params = request.get('params')
                    
                    print(f"Requête reçue: {query}")
                    
                    # Exécuter la requête
                    result = self.execute_query(query, params)
                    
                    # Envoyer la réponse
                    response = json.dumps(result)
                    client_socket.send(response.encode('utf-8'))
                    
                except json.JSONDecodeError:
                    error_response = json.dumps({
                        "success": False, 
                        "error": "Format JSON invalide"
                    })
                    client_socket.send(error_response.encode('utf-8'))
                    
        except Exception as e:
            print(f"Erreur avec le client {address}: {e}")
        finally:
            client_socket.close()
            print(f"Connexion fermée avec {address}")
    
    def start_server(self):
        """Démarre le serveur socket"""
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        try:
            server_socket.bind((self.socket_host, self.socket_port))
            server_socket.listen(5)
            print(f"Serveur démarré sur {self.socket_host}:{self.socket_port}")
            
            while True:
                client_socket, address = server_socket.accept()
                
                # Créer un thread pour chaque client
                client_thread = threading.Thread(
                    target=self.handle_client,
                    args=(client_socket, address)
                )
                client_thread.daemon = True
                client_thread.start()
                
        except Exception as e:
            print(f"Erreur du serveur: {e}")
        finally:
            server_socket.close()

if __name__ == "__main__":
    server = DatabaseServer()
    server.start_server()
```

## Client Python

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
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((self.host, self.port))
            
            # Préparer la requête
            request = {
                "type": "sql_query",
                "query": query,
                "params": params
            }
            
            # Envoyer la requête
            client_socket.send(json.dumps(request).encode('utf-8'))
            
            # Recevoir la réponse
            response = client_socket.recv(4096).decode('utf-8')
            client_socket.close()
            
            return json.loads(response)
            
        except Exception as e:
            return {"success": False, "error": str(e)}

def main():
    client = DatabaseClient()
    
    while True:
        print("\n=== Client Base de Données ===")
        print("1. Insérer un utilisateur")
        print("2. Lister les utilisateurs")
        print("3. Insérer un produit")
        print("4. Lister les produits")
        print("5. Requête personnalisée")
        print("6. Quitter")
        
        choice = input("Choisissez une option: ")
        
        if choice == '1':
            name = input("Nom: ")
            email = input("Email: ")
            age = input("Age: ")
            
            query = "INSERT INTO users (name, email, age) VALUES (%s, %s, %s)"
            params = (name, email, int(age) if age else None)
            
            result = client.send_query(query, params)
            print("Résultat:", result)
            
        elif choice == '2':
            query = "SELECT * FROM users ORDER BY created_at DESC"
            result = client.send_query(query)
            
            if result["success"]:
                users = result["data"]
                print(f"\n{len(users)} utilisateur(s) trouvé(s):")
                for user in users:
                    print(f"ID: {user['id']}, Nom: {user['name']}, Email: {user['email']}, Age: {user['age']}")
            else:
                print("Erreur:", result["error"])
                
        elif choice == '3':
            name = input("Nom du produit: ")
            price = input("Prix: ")
            stock = input("Stock: ")
            category = input("Catégorie: ")
            
            query = "INSERT INTO products (name, price, stock, category) VALUES (%s, %s, %s, %s)"
            params = (name, float(price), int(stock), category)
            
            result = client.send_query(query, params)
            print("Résultat:", result)
            
        elif choice == '4':
            query = "SELECT * FROM products ORDER BY id DESC"
            result = client.send_query(query)
            
            if result["success"]:
                products = result["data"]
                print(f"\n{len(products)} produit(s) trouvé(s):")
                for product in products:
                    print(f"ID: {product['id']}, Nom: {product['name']}, Prix: {product['price']}€, Stock: {product['stock']}")
            else:
                print("Erreur:", result["error"])
                
        elif choice == '5':
            query = input("Entrez votre requête SQL: ")
            result = client.send_query(query)
            print("Résultat:", result)
            
        elif choice == '6':
            print("Au revoir!")
            break
            
        else:
            print("Option invalide!")

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
INSERT IGNORE INTO users (name, email, age) VALUES 
('Alice Dupont', 'alice@email.com', 30),
('Bob Martin', 'bob@email.com', 25),
('Charlie Brown', 'charlie@email.com', 35);

INSERT IGNORE INTO products (name, price, stock, category) VALUES 
('Laptop', 999.99, 10, 'Electronics'),
('Smartphone', 699.99, 25, 'Electronics'),
('Livre Python', 29.99, 100, 'Books');
```

## Configuration et Dépendances

```txt
# requirements.txt
mysql-connector-python==8.0.33
```

## Instructions d'Installation

1. **Installer MySQL** sur votre serveur
2. **Configurer MySQL** :
```bash
sudo mysql_secure_installation
```

3. **Installer les dépendances Python** :
```bash
pip install mysql-connector-python
```

4. **Modifier les paramètres de connexion** dans `server.py` :
```python
self.db_config = {
    'host': 'localhost',
    'port': 3306,
    'user': 'votre_utilisateur',
    'password': 'votre_mot_de_passe',
    'database': 'test_db'
}
```

5. **Démarrer le serveur** :
```bash
python server.py
```

6. **Démarrer le client** (dans un autre terminal) :
```bash
python client.py
```

## Fonctionnalités

- ✅ Communication client-serveur via sockets
- ✅ Gestion des connexions simultanées avec threading
- ✅ Exécution sécurisée des requêtes SQL
- ✅ Support des paramètres (prévention injection SQL)
- ✅ Format JSON pour l'échange de données
- ✅ Interface client interactive
- ✅ Gestion des erreurs

## Sécurité (Améliorations Possibles)

- Authentification des clients
- Chiffrement SSL/TLS
- Validation des requêtes SQL
- Logs détaillés
- Limitation des requêtes par client

Cette architecture vous permet d'exécuter des requêtes SQL à distance de manière sécurisée et efficace !
