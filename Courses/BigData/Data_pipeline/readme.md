# TP Complet : Pipeline de Données E-commerce en Temps Réel
## Guide Détaillé pour Étudiants

---

## 📚 Table des Matières

1. [Introduction et Objectifs](#introduction)
2. [Architecture Globale](#architecture)
3. [Partie 1 : Préparation de l'Infrastructure](#partie-1)
4. [Partie 2 : Production d'Événements Kafka](#partie-2)
5. [Partie 3 : Traitement Spark Streaming](#partie-3)
6. [Partie 4 : Analyse avec Trino](#partie-4)
7. [Partie 5 : Monitoring et Métriques](#partie-5)
8. [Exercices Avancés](#exercices)
9. [Dépannage](#depannage)

---

## 🎯 Introduction et Objectifs {#introduction}

### Objectif Pédagogique

Ce TP vous permettra de construire un **pipeline de données complet en temps réel**, simulant le flux de données d'une plateforme e-commerce. Vous allez :

- **Générer** des événements utilisateur (vues, ajouts au panier, achats)
- **Transporter** ces données via Apache Kafka
- **Traiter** les données en streaming avec Apache Spark
- **Stocker** les données dans un Data Lake (MinIO)
- **Analyser** les données avec un moteur SQL distribué (Trino)
- **Monitorer** le pipeline en temps réel

### Prérequis

- Connaissance de base en Python
- Notions de SQL
- Docker installé sur votre machine
- 8 Go de RAM minimum disponible
- 10 Go d'espace disque libre

### Durée Estimée

- 3 à 4 heures pour le TP complet
- 1 à 2 heures supplémentaires pour les exercices avancés

---

## 🏗️ Architecture Globale {#architecture}

### Schéma du Pipeline

```
┌─────────────────┐
│  Producteur     │ → Génère des événements e-commerce
│  Python         │    (achats, vues, ajouts panier)
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│  Apache Kafka   │ → Message broker (file d'attente distribuée)
│  (Topic events) │    Garantit la livraison des messages
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│  Spark Stream   │ → Traite les événements en temps réel
│  + Spark Worker │    Enrichit, transforme, agrège
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│  MinIO (S3)     │ → Data Lake (stockage objet)
│  Format Parquet │    Stockage partitionné et optimisé
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│  Trino          │ → Moteur de requêtes SQL distribué
│  (Query Engine) │    Analyse interactive des données
└─────────────────┘
```

### Composants Utilisés

| Composant | Rôle | Port |
|-----------|------|------|
| **Zookeeper** | Coordination Kafka | 2181 |
| **Kafka** | Message broker | 9092 |
| **MinIO** | Stockage S3-compatible | 9000, 9001 |
| **Spark Master** | Coordinateur Spark | 8080, 7077 |
| **Spark Worker** | Exécuteur Spark | - |
| **Trino** | Moteur SQL | 8081 |

---

## 🚀 Partie 1 : Préparation de l'Infrastructure {#partie-1}

### 1.1 Création de la Structure du Projet

Ouvrez votre terminal et créez l'arborescence du projet :

```bash
# Créer le répertoire principal du TP
mkdir tp-data-pipeline
cd tp-data-pipeline

# Créer les sous-répertoires nécessaires
mkdir -p trino/catalog  # Configuration Trino
mkdir -p data           # Données persistantes
mkdir -p scripts        # Scripts Python
mkdir -p notebooks      # Notebooks Jupyter (optionnel)

# Vérifier la structure
tree -L 2
```

**Explication** :
- `trino/catalog` : contiendra les fichiers de configuration pour connecter Trino à MinIO
- `data` : sera monté comme volume Docker pour persister les données MinIO
- `scripts` : contiendra tous nos scripts Python (producteur, traitement, monitoring)
- `notebooks` : pour des analyses exploratoires (optionnel)

### 1.2 Fichier Docker Compose

Créez le fichier `docker-compose.yml` à la racine du projet :

```yaml
version: "3.9"

# Définition de tous les services du pipeline
services:
  
  # ===== KAFKA STACK =====
  
  # Zookeeper : nécessaire pour la coordination de Kafka
  zookeeper:
    image: confluentinc/cp-zookeeper:7.5.0
    container_name: tp-zookeeper
    environment:
      # Port sur lequel Zookeeper écoute les clients Kafka
      ZOOKEEPER_CLIENT_PORT: 2181
      # Désactive l'authentification (simplification pour le TP)
      ZOOKEEPER_TICK_TIME: 2000
    networks:
      - data-network
    # Pas de port exposé car Zookeeper est uniquement utilisé en interne

  # Kafka : message broker pour le streaming de données
  kafka:
    image: confluentinc/cp-kafka:7.5.0
    container_name: tp-kafka
    depends_on:
      - zookeeper  # Kafka a besoin que Zookeeper soit démarré
    ports:
      - "9092:9092"  # Port accessible depuis l'hôte
    environment:
      # ID unique du broker Kafka (utile en cluster)
      KAFKA_BROKER_ID: 1
      
      # Adresse de Zookeeper pour la coordination
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
      
      # Adresse que les clients utiliseront pour se connecter
      # IMPORTANT : utiliser "kafka" (nom du service) pour les connexions internes
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka:9092
      
      # Facteur de réplication (1 = pas de réplication, OK pour le TP)
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
      
      # Création automatique des topics (pratique pour le développement)
      KAFKA_AUTO_CREATE_TOPICS_ENABLE: "true"
    networks:
      - data-network
    healthcheck:
      # Vérifier que Kafka est prêt à accepter des connexions
      test: ["CMD", "kafka-broker-api-versions", "--bootstrap-server", "localhost:9092"]
      interval: 10s
      timeout: 10s
      retries: 5

  # ===== STOCKAGE =====
  
  # MinIO : stockage objet compatible S3 (Data Lake)
  minio:
    image: minio/minio:latest
    container_name: tp-minio
    # Commande pour démarrer le serveur MinIO
    command: server /data --console-address ":9001"
    ports:
      - "9000:9000"  # API S3
      - "9001:9001"  # Interface Web d'administration
    environment:
      # Identifiants d'accès (à changer en production !)
      MINIO_ROOT_USER: admin
      MINIO_ROOT_PASSWORD: admin123
    volumes:
      # Montage du répertoire local pour persister les données
      - ./data:/data
    networks:
      - data-network
    healthcheck:
      # Vérifier que MinIO répond correctement
      test: ["CMD", "curl", "-f", "http://localhost:9000/minio/health/live"]
      interval: 10s
      timeout: 10s
      retries: 3

  # ===== SPARK CLUSTER =====
  
  # Spark Master : coordonne l'exécution des jobs Spark
  spark:
    image: bitnami/spark:3.5
    container_name: tp-spark-master
    environment:
      # Mode master (coordinateur)
      - SPARK_MODE=master
      # Options JVM pour le master
      - SPARK_MASTER_OPTS=-Dspark.deploy.defaultCores=2
    ports:
      - "8080:8080"  # Interface Web Spark Master
      - "7077:7077"  # Port de coordination pour les workers
      - "4040:4040"  # Interface Web Spark UI (jobs en cours)
    volumes:
      # Montage des scripts pour les exécuter dans le conteneur
      - ./scripts:/opt/spark-scripts
      # Montage des données (optionnel)
      - ./data:/data
    networks:
      - data-network

  # Spark Worker : exécute les tâches assignées par le master
  spark-worker:
    image: bitnami/spark:3.5
    container_name: tp-spark-worker
    environment:
      # Mode worker (exécuteur)
      - SPARK_MODE=worker
      # URL du master auquel se connecter
      - SPARK_MASTER_URL=spark://spark:7077
      # Ressources allouées au worker
      - SPARK_WORKER_MEMORY=2G
      - SPARK_WORKER_CORES=2
    depends_on:
      - spark  # Le worker a besoin que le master soit démarré
    volumes:
      - ./scripts:/opt/spark-scripts
      - ./data:/data
    networks:
      - data-network
    # Possibilité de scaler les workers :
    # docker-compose up -d --scale spark-worker=3

  # ===== QUERY ENGINE =====
  
  # Trino : moteur de requêtes SQL distribué
  trino:
    image: trinodb/trino:latest
    container_name: tp-trino
    ports:
      - "8081:8080"  # Interface Web Trino
    volumes:
      # Montage de la configuration des catalogues (connexions)
      - ./trino/catalog:/etc/trino/catalog
    networks:
      - data-network
    healthcheck:
      test: ["CMD", "trino", "--execute", "SELECT 1"]
      interval: 10s
      timeout: 5s
      retries: 5

# Réseau partagé pour que tous les conteneurs puissent communiquer
networks:
  data-network:
    driver: bridge
    name: tp-data-network
```

**Points Clés à Comprendre** :

1. **Ordre de démarrage** : Docker Compose respecte les `depends_on` pour démarrer les services dans le bon ordre

2. **Réseau Docker** : Tous les conteneurs sont sur le même réseau et peuvent se parler via leur nom de service (ex: `kafka`, `minio`, `spark`)

3. **Volumes** : Les données dans `./data` persistent même après l'arrêt des conteneurs

4. **Healthchecks** : Permettent de vérifier que les services sont réellement prêts (pas juste démarrés)

### 1.3 Configuration de Trino

Créez le fichier `trino/catalog/minio.properties` :

```properties
# ===== Configuration du Catalogue Trino pour MinIO =====
# Ce fichier permet à Trino de se connecter à MinIO comme s'il s'agissait de AWS S3

# Type de connecteur : Hive (standard pour les data lakes)
connector.name=hive

# URI du Metastore Hive (optionnel pour ce TP)
# Dans un environnement de production, vous auriez un Hive Metastore dédié
# hive.metastore.uri=thrift://metastore:9083

# Configuration S3 (MinIO)
# Point de terminaison MinIO (URL interne au réseau Docker)
hive.s3.endpoint=http://minio:9000

# Utiliser le style de chemin S3 (bucket/key au lieu de bucket.endpoint/key)
# Obligatoire pour MinIO
hive.s3.path-style-access=true

# Identifiants d'accès MinIO (correspondent au docker-compose)
hive.s3.aws-access-key=admin
hive.s3.aws-secret-key=admin123

# Autoriser l'écriture dans des tables non gérées (tables externes)
hive.non-managed-table-writes-enabled=true

# Désactiver SSL (MinIO en HTTP pour le TP)
hive.s3.ssl.enabled=false

# Permettre la création de schémas sans Metastore
hive.metastore=file
hive.metastore.catalog.dir=s3://ecommerce-data/
```

**Explication** :
- Trino utilise le connecteur **Hive** pour accéder aux fichiers Parquet dans MinIO
- La configuration **s3** permet de traiter MinIO comme AWS S3
- Le **path-style-access** est crucial pour la compatibilité MinIO

### 1.4 Démarrage de l'Infrastructure

```bash
# Démarrer tous les services en arrière-plan
docker-compose up -d

# Vérifier que tous les conteneurs sont bien démarrés
docker-compose ps

# Vous devriez voir :
# NAME                STATUS              PORTS
# tp-kafka            Up                  0.0.0.0:9092->9092/tcp
# tp-minio            Up                  0.0.0.0:9000-9001->9000-9001/tcp
# tp-spark-master     Up                  0.0.0.0:7077->7077/tcp, ...
# tp-spark-worker     Up
# tp-trino            Up                  0.0.0.0:8081->8080/tcp
# tp-zookeeper        Up                  2181/tcp

# Suivre les logs en temps réel (Ctrl+C pour arrêter)
docker-compose logs -f

# Suivre les logs d'un service spécifique
docker-compose logs -f kafka
```

**Vérification des Services** :

Ouvrez votre navigateur et vérifiez que les interfaces Web sont accessibles :

- **MinIO Console** : http://localhost:9001 (admin / admin123)
- **Spark Master UI** : http://localhost:8080
- **Trino UI** : http://localhost:8081

**En cas de problème** :
```bash
# Voir les logs d'erreur
docker-compose logs kafka | grep -i error

# Redémarrer un service spécifique
docker-compose restart kafka

# Arrêter et supprimer tous les conteneurs
docker-compose down

# Redémarrer proprement
docker-compose up -d
```

---

## 📊 Partie 2 : Production d'Événements dans Kafka {#partie-2}

### 2.1 Comprendre le Producteur

Le **producteur Kafka** est un script Python qui génère des événements e-commerce simulés et les envoie à Kafka. C'est la première étape de notre pipeline.

**Concept** : Dans une vraie application e-commerce, ces événements proviendraient :
- D'une application web (clics utilisateur)
- D'une application mobile
- D'un système backend (confirmation d'achat)

Pour le TP, nous simulons ces événements de manière aléatoire mais réaliste.

### 2.2 Structure des Événements

Chaque événement contient :

```json
{
  "event_id": "evt_1704117600000_1234",      // ID unique de l'événement
  "timestamp": "2024-01-01T15:30:00",        // Horodatage ISO 8601
  "event_type": "purchase",                   // Type : view, add_to_cart, purchase, remove_from_cart
  "user_id": "user_042",                      // ID de l'utilisateur
  "product_id": "P001",                       // ID du produit
  "product_name": "Laptop Dell XPS",          // Nom du produit
  "category": "Electronics",                  // Catégorie
  "price": 1299.99,                           // Prix unitaire
  "quantity": 1,                              // Quantité
  "country": "France",                        // Pays de l'utilisateur
  "device": "mobile",                         // Type d'appareil
  "session_id": "sess_12345"                  // ID de session
}
```

### 2.3 Créer le Producteur Python

Créez le fichier `scripts/producer.py` :

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Producteur Kafka pour événements e-commerce
Génère et envoie des événements simulés à Kafka
"""

import json
import time
import random
from datetime import datetime
from kafka import KafkaProducer
from kafka.errors import KafkaError

# ===== CONFIGURATION =====

# Adresse du broker Kafka
# IMPORTANT : Utiliser "localhost" depuis l'hôte, "kafka" depuis un conteneur
KAFKA_BROKER = 'localhost:9092'

# Nom du topic Kafka où envoyer les événements
TOPIC = 'ecommerce-events'

# ===== DONNÉES DE RÉFÉRENCE =====
# Ces données simulent un catalogue produit

PRODUCTS = [
    {"id": "P001", "name": "Laptop Dell XPS", "category": "Electronics", "price": 1299.99},
    {"id": "P002", "name": "iPhone 15", "category": "Electronics", "price": 999.99},
    {"id": "P003", "name": "Nike Air Max", "category": "Fashion", "price": 129.99},
    {"id": "P004", "name": "Sony Headphones WH-1000XM5", "category": "Electronics", "price": 299.99},
    {"id": "P005", "name": "Samsung TV 55\"", "category": "Electronics", "price": 799.99},
    {"id": "P006", "name": "Adidas Jacket", "category": "Fashion", "price": 89.99},
    {"id": "P007", "name": "Data Engineering Book", "category": "Books", "price": 49.99},
    {"id": "P008", "name": "Coffee Maker Deluxe", "category": "Home", "price": 79.99},
    {"id": "P009", "name": "Gaming Mouse", "category": "Electronics", "price": 59.99},
    {"id": "P010", "name": "Yoga Mat Premium", "category": "Sports", "price": 39.99},
]

# Génération d'utilisateurs simulés
# Format : user_001, user_002, ..., user_050
USERS = [f"user_{i:03d}" for i in range(1, 51)]

# Pays des utilisateurs (distribution géographique)
COUNTRIES = ["France", "USA", "UK", "Germany", "Spain", "Italy", "Canada", "Japan"]

# Types d'événements possibles
EVENT_TYPES = ["view", "add_to_cart", "purchase", "remove_from_cart"]

# ===== FONCTIONS =====

def generate_event():
    """
    Génère un événement e-commerce aléatoire mais réaliste
    
    Returns:
        dict: Événement formaté en JSON
    """
    
    # Sélection pondérée du type d'événement
    # Distribution réaliste : beaucoup de vues, peu d'achats
    # Poids : 50% vues, 25% ajouts panier, 15% achats, 10% retraits
    event_type = random.choices(
        EVENT_TYPES, 
        weights=[50, 25, 15, 10]
    )[0]
    
    # Sélectionner un produit aléatoire
    product = random.choice(PRODUCTS)
    
    # Construire l'événement
    event = {
        # ID unique basé sur le timestamp + random
        "event_id": f"evt_{int(time.time() * 1000)}_{random.randint(1000, 9999)}",
        
        # Horodatage au format ISO 8601
        "timestamp": datetime.now().isoformat(),
        
        # Type d'événement
        "event_type": event_type,
        
        # Informations utilisateur
        "user_id": random.choice(USERS),
        
        # Informations produit
        "product_id": product["id"],
        "product_name": product["name"],
        "category": product["category"],
        "price": product["price"],
        
        # Quantité (seulement pour ajout panier et achat)
        "quantity": random.randint(1, 5) if event_type in ["add_to_cart", "purchase"] else 1,
        
        # Contexte de l'événement
        "country": random.choice(COUNTRIES),
        "device": random.choice(["mobile", "desktop", "tablet"]),
        
        # Session utilisateur (pour tracker les parcours)
        "session_id": f"sess_{random.randint(10000, 99999)}"
    }
    
    return event


def main():
    """
    Fonction principale : crée le producteur et envoie les événements
    """
    
    print("=" * 80)
    print("🚀 Démarrage du Producteur Kafka E-commerce")
    print("=" * 80)
    print(f"📍 Broker Kafka : {KAFKA_BROKER}")
    print(f"📤 Topic        : {TOPIC}")
    print("=" * 80)
    print()
    
    # Créer le producteur Kafka
    try:
        producer = KafkaProducer(
            # Liste des brokers Kafka
            bootstrap_servers=[KAFKA_BROKER],
            
            # Fonction de sérialisation : convertir dict Python -> JSON -> bytes
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            
            # Configuration de fiabilité
            # acks='all' : attendre la confirmation de tous les replicas (max fiabilité)
            acks='all',
            
            # Retry en cas d'erreur
            retries=3,
            
            # Compression des messages (optionnel, économise la bande passante)
            compression_type='gzip'
        )
        
        print("✅ Producteur Kafka créé avec succès")
        print()
        
    except KafkaError as e:
        print(f"❌ Erreur de connexion à Kafka : {e}")
        print("💡 Vérifiez que Kafka est démarré : docker-compose ps")
        return
    
    # Compteur d'événements envoyés
    event_count = 0
    
    # Statistiques
    stats = {event_type: 0 for event_type in EVENT_TYPES}
    
    print("📊 En-têtes des colonnes :")
    print(f"{'#':>6} | {'Timestamp':19} | {'Type':15} | {'User':10} | {'Product':30} | {'Country':10}")
    print("-" * 110)
    
    try:
        # Boucle infinie d'envoi d'événements
        while True:
            # Générer un événement
            event = generate_event()
            
            # Envoyer l'événement à Kafka
            # La méthode send() est asynchrone (non-bloquante)
            future = producer.send(TOPIC, value=event)
            
            # On peut récupérer les métadonnées de l'envoi
            # metadata = future.get(timeout=10)  # Bloquant, attend la confirmation
            
            # Incrémenter les compteurs
            event_count += 1
            stats[event['event_type']] += 1
            
            # Afficher l'événement envoyé (format tabulaire)
            print(f"{event_count:6d} | "
                  f"{event['timestamp']:19s} | "
                  f"{event['event_type']:15s} | "
                  f"{event['user_id']:10s} | "
                  f"{event['product_name'][:30]:30s} | "
                  f"{event['country']:10s}")
            
            # Afficher les statistiques toutes les 50 événements
            if event_count % 50 == 0:
                print()
                print(f"📈 Statistiques après {event_count} événements :")
                for event_type, count in stats.items():
                    percentage = (count / event_count) * 100
                    print(f"   {event_type:15s} : {count:5d} ({percentage:5.1f}%)")
                print("-" * 110)
            
            # Attendre entre 0.5 et 2 secondes avant le prochain événement
            # Simule un flux de données réaliste (pas trop rapide)
            time.sleep(random.uniform(0.5, 2))
    
    except KeyboardInterrupt:
        # L'utilisateur a pressé Ctrl+C
        print()
        print("=" * 80)
        print("🛑 Arrêt du producteur demandé par l'utilisateur")
        print("=" * 80)
        print()
        print(f"📊 Statistiques finales :")
        print(f"   Total événements envoyés : {event_count}")
        print()
        print(f"   Répartition par type :")
        for event_type, count in sorted(stats.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / event_count) * 100 if event_count > 0 else 0
            print(f"   - {event_type:15s} : {count:5d} ({percentage:5.1f}%)")
        print()
        
    except Exception as e:
        print(f"❌ Erreur inattendue : {e}")
        
    finally:
        # Fermer proprement le producteur
        # flush() envoie tous les messages en attente avant de fermer
        producer.flush()
        producer.close()
        print("✅ Producteur fermé proprement")


if __name__ == "__main__":
    main()
```

### 2.4 Installer les Dépendances

```bash
# Installer le client Kafka pour Python
pip install kafka-python

# Vérifier l'installation
python -c "import kafka; print(kafka.__version__)"
```

**Note** : Si vous utilisez un environnement virtuel (recommandé) :
```bash
# Créer un environnement virtuel
python -m venv venv

# Activer l'environnement
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# Installer les dépendances
pip install kafka-python
```

### 2.5 Lancer le Producteur

```bash
# Donner les permissions d'exécution (Linux/Mac)
chmod +x scripts/producer.py

# Lancer le producteur
python scripts/producer.py
```

**Vous devriez voir** :
```
================================================================================
🚀 Démarrage du Producteur Kafka E-commerce
================================================================================
📍 Broker Kafka : localhost:9092
📤 Topic        : ecommerce-events
================================================================================

✅ Producteur Kafka créé avec succès

📊 En-têtes des colonnes :
     # | Timestamp           | Type            | User       | Product                        | Country   
--------------------------------------------------------------------------------------------------------------
     1 | 2024-01-01T15:30:00 | view            | user_023   | Laptop Dell XPS                | France    
     2 | 2024-01-01T15:30:01 | add_to_cart     | user_007   | iPhone 15                      | USA       
     3 | 2024-01-01T15:30:03 | purchase        | user_042   | Nike Air Max                   | UK        
...
```

**Pour arrêter le producteur** : Appuyez sur `Ctrl+C`

### 2.6 Vérifier que les Messages Arrivent dans Kafka

Ouvrez un nouveau terminal et vérifiez :

```bash
# Lister les topics Kafka
docker exec tp-kafka kafka-topics --bootstrap-server localhost:9092 --list

# Vous devriez voir : ecommerce-events

# Consommer les messages (afficher les 10 derniers)
docker exec tp-kafka kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic ecommerce-events \
  --from-beginning \
  --max-messages 10

# Pour consommer en continu (Ctrl+C pour arrêter)
docker exec tp-kafka kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic ecommerce-events \
  --from-beginning
```

**Vous devriez voir des JSON** :
```json
{"event_id": "evt_1704117600000_1234", "timestamp": "2024-01-01T15:30:00", ...}
```

---

## ⚡ Partie 3 : Traitement des Données avec Spark Streaming {#partie-3}

### 3.1 Comprendre Spark Streaming

**Spark Streaming** traite des flux de données en quasi-temps réel. Il lit les événements depuis Kafka, les transforme, les enrichit et les écrit dans MinIO.

**Concepts Clés** :
- **Micro-batch** : Spark Streaming traite les données par petits lots (ex: toutes les 30 secondes)
- **Transformation** : Opérations sur les données (filtrage, agrégation, enrichissement)
- **Sink** : Destination des données traitées (ici : MinIO)

### 3.2 Créer le Bucket MinIO

Avant de lancer Spark, créez un bucket dans MinIO pour stocker les données.

**Option 1 : Via l'interface Web**
1. Ouvrez http://localhost:9001
2. Connectez-vous (admin / admin123)
3. Cliquez sur "Create Bucket"
4. Nom : `ecommerce-data`
5. Cliquez sur "Create"

**Option 2 : Via un Script Python**

Créez `scripts/setup_minio.py` :

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Configuration initiale de MinIO
Crée les buckets nécessaires pour le pipeline
"""

from minio import Minio
from minio.error import S3Error

# ===== CONFIGURATION =====

# Point de terminaison MinIO (depuis l'hôte)
MINIO_ENDPOINT = "localhost:9000"

# Identifiants (même que dans docker-compose.yml)
ACCESS_KEY = "admin"
SECRET_KEY = "admin123"

# Nom du bucket à créer
BUCKET_NAME = "ecommerce-data"

# ===== FONCTIONS =====

def setup_minio():
    """
    Initialise MinIO : crée le bucket s'il n'existe pas
    """
    print("=" * 80)
    print("🔧 Configuration de MinIO")
    print("=" * 80)
    print(f"📍 Endpoint : {MINIO_ENDPOINT}")
    print(f"🪣 Bucket   : {BUCKET_NAME}")
    print()
    
    try:
        # Créer le client MinIO
        client = Minio(
            MINIO_ENDPOINT,
            access_key=ACCESS_KEY,
            secret_key=SECRET_KEY,
            secure=False  # HTTP (pas HTTPS) pour le TP
        )
        
        print("✅ Client MinIO créé")
        
        # Vérifier si le bucket existe déjà
        if client.bucket_exists(BUCKET_NAME):
            print(f"ℹ️  Le bucket '{BUCKET_NAME}' existe déjà")
        else:
            # Créer le bucket
            client.make_bucket(BUCKET_NAME)
            print(f"✅ Bucket '{BUCKET_NAME}' créé avec succès")
        
        # Lister tous les buckets pour vérification
        buckets = client.list_buckets()
        print()
        print("📦 Buckets disponibles :")
        for bucket in buckets:
            print(f"   - {bucket.name} (créé le {bucket.creation_date})")
        
        print()
        print("=" * 80)
        print("✅ Configuration MinIO terminée")
        print("=" * 80)
        
    except S3Error as e:
        print(f"❌ Erreur S3 : {e}")
        print(f"💡 Vérifiez que MinIO est démarré : docker-compose ps")
        
    except Exception as e:
        print(f"❌ Erreur inattendue : {e}")


if __name__ == "__main__":
    setup_minio()
```

Installez la bibliothèque MinIO et exécutez :

```bash
# Installer le client MinIO
pip install minio

# Exécuter le script
python scripts/setup_minio.py
```

### 3.3 Créer le Job Spark Streaming

Créez `scripts/spark_streaming_job.py` :

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Job Spark Streaming pour traiter les événements e-commerce
Lit depuis Kafka, transforme les données, écrit dans MinIO
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *

# ===== CONFIGURATION =====

# Configuration MinIO (S3-compatible)
MINIO_ENDPOINT = "http://minio:9000"  # URL interne Docker
MINIO_ACCESS_KEY = "admin"
MINIO_SECRET_KEY = "admin123"
BUCKET_NAME = "ecommerce-data"

# Configuration Kafka
KAFKA_BROKER = "kafka:9092"  # URL interne Docker
KAFKA_TOPIC = "ecommerce-events"

# ===== SCHEMA DES ÉVÉNEMENTS =====
# Définit la structure des données attendues
# IMPORTANT : doit correspondre aux données du producteur

event_schema = StructType([
    # Identifiants
    StructField("event_id", StringType(), True),
    StructField("timestamp", StringType(), True),  # ISO 8601 string
    
    # Type et contexte
    StructField("event_type", StringType(), True),
    StructField("user_id", StringType(), True),
    StructField("session_id", StringType(), True),
    
    # Informations produit
    StructField("product_id", StringType(), True),
    StructField("product_name", StringType(), True),
    StructField("category", StringType(), True),
    StructField("price", DoubleType(), True),
    StructField("quantity", IntegerType(), True),
    
    # Informations contextuelles
    StructField("country", StringType(), True),
    StructField("device", StringType(), True),
])

# ===== FONCTIONS =====

def create_spark_session():
    """
    Crée et configure la session Spark avec les dépendances nécessaires
    """
    print("🔧 Création de la session Spark...")
    
    spark = SparkSession.builder \
        .appName("EcommerceStreamProcessing") \
        \
        .config("spark.hadoop.fs.s3a.endpoint", MINIO_ENDPOINT) \
        .config("spark.hadoop.fs.s3a.access.key", MINIO_ACCESS_KEY) \
        .config("spark.hadoop.fs.s3a.secret.key", MINIO_SECRET_KEY) \
        .config("spark.hadoop.fs.s3a.path.style.access", "true") \
        .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") \
        \
        .config("spark.sql.streaming.checkpointLocation", "/tmp/checkpoint") \
        \
        .config("spark.sql.shuffle.partitions", "4") \
        \
        .config("spark.streaming.stopGracefullyOnShutdown", "true") \
        .getOrCreate()
    
    # Réduire la verbosité des logs
    spark.sparkContext.setLogLevel("WARN")
    
    print("✅ Session Spark créée avec succès")
    print(f"   Spark Version : {spark.version}")
    print(f"   App Name      : {spark.sparkContext.appName}")
    print()
    
    return spark


def read_kafka_stream(spark):
    """
    Lit le flux d'événements depuis Kafka
    """
    print("📖 Lecture du stream Kafka...")
    print(f"   Broker : {KAFKA_BROKER}")
    print(f"   Topic  : {KAFKA_TOPIC}")
    print()
    
    # Créer un DataFrame de streaming depuis Kafka
    kafka_df = spark.readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", KAFKA_BROKER) \
        .option("subscribe", KAFKA_TOPIC) \
        .option("startingOffsets", "latest") \
        .option("failOnDataLoss", "false") \
        .load()
    
    # Structure du DataFrame Kafka :
    # - key: bytes (clé du message, nullable)
    # - value: bytes (valeur du message, notre JSON)
    # - topic: string (nom du topic)
    # - partition: int (partition Kafka)
    # - offset: long (offset du message)
    # - timestamp: timestamp (timestamp du message)
    # - timestampType: int (type de timestamp)
    
    return kafka_df


def parse_events(kafka_df):
    """
    Parse les événements JSON depuis Kafka
    """
    print("🔄 Parsing des événements JSON...")
    
    # Convertir la colonne 'value' (bytes) en string, puis parser le JSON
    events_df = kafka_df.select(
        # from_json : convertit une string JSON en structure
        from_json(
            col("value").cast("string"),  # Convertir bytes -> string
            event_schema                   # Appliquer le schéma défini
        ).alias("data")
    ).select("data.*")  # Extraire tous les champs de la structure
    
    print("✅ Événements parsés")
    print()
    
    return events_df


def enrich_events(events_df):
    """
    Enrichit les événements avec des colonnes calculées
    """
    print("✨ Enrichissement des événements...")
    
    enriched_df = events_df \
        .withColumn("date", to_date(col("timestamp"))) \
        .withColumn("hour", hour(col("timestamp"))) \
        .withColumn("minute", minute(col("timestamp"))) \
        .withColumn("day_of_week", dayofweek(col("timestamp"))) \
        .withColumn("total_amount", col("price") * col("quantity")) \
        .withColumn("processing_time", current_timestamp())
    
    print("✅ Enrichissement terminé")
    print("   Colonnes ajoutées :")
    print("   - date           : Date de l'événement")
    print("   - hour           : Heure de l'événement")
    print("   - minute         : Minute de l'événement")
    print("   - day_of_week    : Jour de la semaine (1=dimanche, 7=samedi)")
    print("   - total_amount   : Montant total (prix * quantité)")
    print("   - processing_time: Timestamp du traitement")
    print()
    
    return enriched_df


def write_to_minio(enriched_df):
    """
    Écrit les données enrichies dans MinIO (format Parquet)
    """
    print("💾 Configuration de l'écriture vers MinIO...")
    print(f"   Destination : s3a://{BUCKET_NAME}/events/")
    print("   Format      : Parquet")
    print("   Partitions  : date, event_type")
    print("   Trigger     : 30 secondes")
    print()
    
    # Créer la requête de streaming
    query = enriched_df.writeStream \
        .format("parquet") \
        .option("path", f"s3a://{BUCKET_NAME}/events/") \
        .option("checkpointLocation", "/tmp/checkpoint/events") \
        .partitionBy("date", "event_type") \
        .outputMode("append") \
        .trigger(processingTime="30 seconds") \
        .start()
    
    print("✅ Écriture configurée et démarrée")
    print()
    
    return query


def print_streaming_stats(query):
    """
    Affiche les statistiques de streaming en continu
    """
    print("=" * 80)
    print("📊 Job Spark Streaming en cours d'exécution")
    print("=" * 80)
    print()
    print("ℹ️  Le job traite les événements toutes les 30 secondes")
    print("ℹ️  Les données sont écrites dans MinIO au format Parquet")
    print("ℹ️  Partitionnement : par date et type d'événement")
    print()
    print("📈 Pour voir les statistiques en temps réel :")
    print("   - Interface Spark UI : http://localhost:4040")
    print("   - Vérifier MinIO     : http://localhost:9001")
    print()
    print("🛑 Pour arrêter le job : Appuyez sur Ctrl+C")
    print("=" * 80)
    print()
    
    # Afficher les progrès
    import time
    batch_count = 0
    
    try:
        while query.isActive:
            time.sleep(30)  # Attendre 30 secondes
            batch_count += 1
            
            # Récupérer les statistiques de la dernière batch
            status = query.status
            progress = query.lastProgress
            
            if progress:
                print(f"📦 Batch #{batch_count} traité")
                print(f"   Timestamp    : {progress.get('timestamp', 'N/A')}")
                print(f"   Lignes traitées: {progress.get('numInputRows', 0)}")
                print(f"   Durée batch  : {progress.get('batchDuration', 'N/A')} ms")
                print("-" * 80)
    
    except KeyboardInterrupt:
        print()
        print("🛑 Arrêt du job demandé...")


def main():
    """
    Fonction principale du job Spark Streaming
    """
    print()
    print("=" * 80)
    print("🚀 DÉMARRAGE DU JOB SPARK STREAMING E-COMMERCE")
    print("=" * 80)
    print()
    
    # Étape 1 : Créer la session Spark
    spark = create_spark_session()
    
    # Étape 2 : Lire le stream Kafka
    kafka_df = read_kafka_stream(spark)
    
    # Étape 3 : Parser les événements JSON
    events_df = parse_events(kafka_df)
    
    # Étape 4 : Enrichir les événements
    enriched_df = enrich_events(events_df)
    
    # Étape 5 : Écrire dans MinIO
    query = write_to_minio(enriched_df)
    
    # Étape 6 : Afficher les statistiques
    print_streaming_stats(query)
    
    # Attendre la fin (ou Ctrl+C)
    try:
        query.awaitTermination()
    except KeyboardInterrupt:
        print()
        print("🛑 Arrêt du job...")
        query.stop()
        spark.stop()
        print("✅ Job arrêté proprement")


if __name__ == "__main__":
    main()
```

### 3.4 Lancer le Job Spark

Le job Spark nécessite des dépendances supplémentaires (connecteurs Kafka et S3). Il doit être lancé depuis le conteneur Spark avec `spark-submit`.

**Étape par étape** :

```bash
# 1. Entrer dans le conteneur Spark Master
docker exec -it tp-spark-master bash

# Vous êtes maintenant dans le conteneur
# Le prompt change : spark@abc123:/opt/bitnami/spark$

# 2. Installer PySpark et dépendances (si nécessaire)
pip install pyspark

# 3. Lancer le job avec spark-submit
spark-submit \
  --master spark://spark:7077 \
  --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0,org.apache.hadoop:hadoop-aws:3.3.4,com.amazonaws:aws-java-sdk-bundle:1.12.367 \
  --conf spark.executor.memory=1g \
  --conf spark.driver.memory=1g \
  /opt/spark-scripts/spark_streaming_job.py
```

**Explication des Paramètres** :

- `--master spark://spark:7077` : URL du Spark Master
- `--packages` : Télécharge automatiquement les dépendances JAR :
  - `spark-sql-kafka` : Connecteur Kafka
  - `hadoop-aws` : Connecteur S3/MinIO
  - `aws-java-sdk-bundle` : SDK AWS (pour MinIO)
- `--conf spark.executor.memory=1g` : Mémoire allouée aux executors
- `/opt/spark-scripts/spark_streaming_job.py` : Chemin du script dans le conteneur

**Vous devriez voir** :
```
================================================================================
🚀 DÉMARRAGE DU JOB SPARK STREAMING E-COMMERCE
================================================================================

🔧 Création de la session Spark...
✅ Session Spark créée avec succès
   Spark Version : 3.5.0
   App Name      : EcommerceStreamProcessing

📖 Lecture du stream Kafka...
   Broker : kafka:9092
   Topic  : ecommerce-events

🔄 Parsing des événements JSON...
✅ Événements parsés

✨ Enrichissement des événements...
✅ Enrichissement terminé
...
```

### 3.5 Vérifier les Données dans MinIO

Pendant que le job tourne, vérifiez que les données arrivent dans MinIO :

**Via l'interface Web** :
1. Ouvrez http://localhost:9001
2. Connectez-vous
3. Cliquez sur le bucket `ecommerce-data`
4. Naviguez dans le dossier `events/`
5. Vous devriez voir des sous-dossiers par date et type d'événement

**Structure attendue** :
```
ecommerce-data/
└── events/
    ├── date=2024-01-01/
    │   ├── event_type=view/
    │   │   └── part-00000-xxx.snappy.parquet
    │   ├── event_type=purchase/
    │   │   └── part-00000-xxx.snappy.parquet
    │   └── event_type=add_to_cart/
    │       └── part-00000-xxx.snappy.parquet
    └── date=2024-01-02/
        └── ...
```

**Via la CLI** :
```bash
# Lister les fichiers (depuis l'hôte)
docker exec tp-spark-master ls -lh /data/ecommerce-data/events/
```

---

## 🔍 Partie 4 : Analyse avec Trino {#partie-4}

### 4.1 Comprendre Trino

**Trino** (anciennement Presto) est un moteur de requêtes SQL distribué qui peut interroger des données stockées dans divers systèmes (S3, HDFS, bases de données, etc.).

**Avantages** :
- Requêtes SQL standard sur des fichiers Parquet
- Performance élevée (moteur distribué)
- Pas besoin de charger les données en mémoire
- Fédération de requêtes (plusieurs sources)

### 4.2 Se Connecter à Trino

```bash
# Entrer dans le conteneur Trino et lancer le CLI
docker exec -it tp-trino trino

# Vous devriez voir le prompt Trino :
# trino>
```

**Commandes Utiles** :
```sql
-- Lister les catalogues disponibles
SHOW CATALOGS;

-- Lister les schémas d'un catalogue
SHOW SCHEMAS FROM minio;

-- Lister les tables d'un schéma
SHOW TABLES FROM minio.ecommerce;

-- Quitter Trino
quit;
```

### 4.3 Créer le Schéma et la Table

Dans le CLI Trino, exécutez :

```sql
-- ===== CRÉATION DU SCHÉMA =====
-- Un schéma est un espace de noms pour regrouper des tables

CREATE SCHEMA IF NOT EXISTS minio.ecommerce
WITH (location = 's3a://ecommerce-data/');

-- Vérifier que le schéma est créé
SHOW SCHEMAS FROM minio;

-- ===== CRÉATION DE LA TABLE EXTERNE =====
-- Une table "externe" pointe vers des données existantes dans S3/MinIO
-- Elle ne copie pas les données, elle définit juste la structure

CREATE TABLE IF NOT EXISTS minio.ecommerce.events (
    -- Identifiants
    event_id VARCHAR,
    timestamp VARCHAR,  -- Stocké comme string, mais peut être converti en TIMESTAMP
    event_type VARCHAR,
    user_id VARCHAR,
    session_id VARCHAR,
    
    -- Informations produit
    product_id VARCHAR,
    product_name VARCHAR,
    category VARCHAR,
    price DOUBLE,
    quantity INTEGER,
    
    -- Informations contextuelles
    country VARCHAR,
    device VARCHAR,
    
    -- Colonnes ajoutées par Spark (enrichissement)
    date DATE,
    hour INTEGER,
    minute INTEGER,
    day_of_week INTEGER,
    total_amount DOUBLE,
    processing_time TIMESTAMP
)
WITH (
    -- Emplacement des données dans MinIO
    external_location = 's3a://ecommerce-data/events/',
    
    -- Format des fichiers (Parquet est un format colonne optimisé)
    format = 'PARQUET',
    
    -- Colonnes de partitionnement (doivent correspondre à Spark)
    partitioned_by = ARRAY['date', 'event_type']
);

-- ===== VÉRIFICATION =====

-- Afficher la structure de la table
DESCRIBE minio.ecommerce.events;

-- Compter le nombre d'événements
SELECT COUNT(*) as total_events
FROM minio.ecommerce.events;

-- Afficher les 10 premiers événements
SELECT *
FROM minio.ecommerce.events
LIMIT 10;
```

**Notes Importantes** :

1. **external_location** : Doit pointer vers le dossier racine où Spark écrit les données

2. **partitioned_by** : Doit correspondre exactement aux colonnes de partitionnement de Spark (ordre important !)

3. **Format Parquet** : Format colonne optimisé pour l'analyse
   - Compression efficace
   - Lecture rapide des colonnes spécifiques
   - Prédicat pushdown (filtres appliqués au niveau fichier)

### 4.4 Requêtes d'Analyse

Maintenant que la table est créée, explorons les données !

#### **Requête 1 : Vue d'ensemble des événements**

```sql
-- Compter les événements par type
SELECT 
    event_type,
    COUNT(*) as count,
    ROUND(AVG(total_amount), 2) as avg_amount,
    ROUND(SUM(total_amount), 2) as total_revenue
FROM minio.ecommerce.events
GROUP BY event_type
ORDER BY count DESC;
```

**Résultat attendu** :
```
event_type      | count | avg_amount | total_revenue
----------------+-------+------------+--------------
view            |  5023 |     650.12 |    3264752.76
add_to_cart     |  2508 |     689.45 |    1729060.60
purchase        |  1505 |     712.89 |    1072899.45
remove_from_cart|  1004 |     598.23 |     600624.92
```

#### **Requête 2 : Top produits les plus consultés**

```sql
-- Top 10 des produits avec le plus de vues
SELECT 
    product_name,
    category,
    COUNT(*) as views,
    ROUND(AVG(price), 2) as avg_price
FROM minio.ecommerce.events
WHERE event_type = 'view'
GROUP BY product_name, category
ORDER BY views DESC
LIMIT 10;
```

#### **Requête 3 : Analyse par pays**

```sql
-- Revenus et achats par pays
SELECT 
    country,
    COUNT(CASE WHEN event_type = 'purchase' THEN 1 END) as purchases,
    ROUND(SUM(CASE WHEN event_type = 'purchase' THEN total_amount ELSE 0 END), 2) as revenue,
    ROUND(AVG(CASE WHEN event_type = 'purchase' THEN total_amount END), 2) as avg_basket
FROM minio.ecommerce.events
GROUP BY country
ORDER BY revenue DESC;
```

**Interprétation** :
- `purchases` : nombre d'achats par pays
- `revenue` : chiffre d'affaires total par pays
- `avg_basket` : panier moyen par pays

#### **Requête 4 : Taux de conversion**

```sql
-- Calculer le taux de conversion (vues → achats) par catégorie
WITH stats AS (
    SELECT 
        category,
        COUNT(CASE WHEN event_type = 'view' THEN 1 END) as views,
        COUNT(CASE WHEN event_type = 'purchase' THEN 1 END) as purchases
    FROM minio.ecommerce.events
    GROUP BY category
)
SELECT 
    category,
    views,
    purchases,
    ROUND(100.0 * purchases / NULLIF(views, 0), 2) as conversion_rate_pct
FROM stats
WHERE views > 0
ORDER BY conversion_rate_pct DESC;
```

**Métrique Business** : Un taux de conversion de 3-5% est typique pour l'e-commerce.

#### **Requête 5 : Analyse temporelle**

```sql
-- Activité par heure de la journée
SELECT 
    hour,
    COUNT(*) as total_events,
    COUNT(CASE WHEN event_type = 'view' THEN 1 END) as views,
    COUNT(CASE WHEN event_type = 'purchase' THEN 1 END) as purchases,
    ROUND(SUM(CASE WHEN event_type = 'purchase' THEN total_amount ELSE 0 END), 2) as revenue
FROM minio.ecommerce.events
GROUP BY hour
ORDER BY hour;
```

**Analyse** : Identifie les heures de pointe pour optimiser les campagnes marketing.

#### **Requête 6 : Analyse par appareil**

```sql
-- Performance par type d'appareil
SELECT 
    device,
    COUNT(*) as total_events,
    COUNT(CASE WHEN event_type = 'purchase' THEN 1 END) as purchases,
    ROUND(AVG(CASE WHEN event_type = 'purchase' THEN total_amount END), 2) as avg_basket,
    ROUND(100.0 * COUNT(CASE WHEN event_type = 'purchase' THEN 1 END) / 
          NULLIF(COUNT(*), 0), 2) as conversion_rate_pct
FROM minio.ecommerce.events
GROUP BY device
ORDER BY conversion_rate_pct DESC;
```

#### **Requête 7 : Funnel d'achat**

```sql
-- Analyser le parcours utilisateur (funnel)
WITH user_funnel AS (
    SELECT 
        user_id,
        MAX(CASE WHEN event_type = 'view' THEN 1 ELSE 0 END) as has_viewed,
        MAX(CASE WHEN event_type = 'add_to_cart' THEN 1 ELSE 0 END) as has_added_to_cart,
        MAX(CASE WHEN event_type = 'purchase' THEN 1 ELSE 0 END) as has_purchased
    FROM minio.ecommerce.events
    GROUP BY user_id
)
SELECT 
    COUNT(*) as total_users,
    SUM(has_viewed) as users_viewed,
    SUM(has_added_to_cart) as users_added_to_cart,
    SUM(has_purchased) as users_purchased,
    ROUND(100.0 * SUM(has_added_to_cart) / NULLIF(SUM(has_viewed), 0), 2) as view_to_cart_pct,
    ROUND(100.0 * SUM(has_purchased) / NULLIF(SUM(has_added_to_cart), 0), 2) as cart_to_purchase_pct
FROM user_funnel;
```

**Visualisation du Funnel** :
```
Vus un produit (100%)
    ↓ 25%
Ajouté au panier (25%)
    ↓ 60%
Acheté (15%)
```

#### **Requête 8 : Cohort Analysis (Analyse de cohorte)**

```sql
-- Analyser les utilisateurs par jour d'inscription (première activité)
WITH user_first_activity AS (
    SELECT 
        user_id,
        MIN(date) as first_activity_date
    FROM minio.ecommerce.events
    GROUP BY user_id
),
cohort_analysis AS (
    SELECT 
        ufa.first_activity_date as cohort_date,
        e.date as activity_date,
        COUNT(DISTINCT e.user_id) as active_users,
        COUNT(CASE WHEN e.event_type = 'purchase' THEN 1 END) as purchases
    FROM minio.ecommerce.events e
    JOIN user_first_activity ufa ON e.user_id = ufa.user_id
    GROUP BY ufa.first_activity_date, e.date
)
SELECT 
    cohort_date,
    activity_date,
    active_users,
    purchases,
    DATE_DIFF('day', cohort_date, activity_date) as days_since_first_activity
FROM cohort_analysis
ORDER BY cohort_date, activity_date;
```

### 4.5 Optimisations et Bonnes Pratiques

#### **Utiliser les Partitions**

Les requêtes qui filtrent sur `date` ou `event_type` sont beaucoup plus rapides :

```sql
-- RAPIDE : Utilise les partitions
SELECT COUNT(*)
FROM minio.ecommerce.events
WHERE date = DATE '2024-01-01'
  AND event_type = 'purchase';

-- LENT : Scan complet
SELECT COUNT(*)
FROM minio.ecommerce.events
WHERE hour = 15;
```

#### **Projections de Colonnes**

Sélectionnez uniquement les colonnes nécessaires :

```sql
-- RAPIDE : Parquet lit uniquement price et quantity
SELECT price, quantity
FROM minio.ecommerce.events;

-- LENT : Lit toutes les colonnes
SELECT *
FROM minio.ecommerce.events;
```

#### **Agrégations Pré-calculées**

Créez des vues matérialisées pour les requêtes fréquentes :

```sql
-- Créer une vue pour les métriques quotidiennes
CREATE VIEW minio.ecommerce.daily_metrics AS
SELECT 
    date,
    country,
    event_type,
    COUNT(*) as event_count,
    SUM(total_amount) as total_revenue,
    COUNT(DISTINCT user_id) as unique_users
FROM minio.ecommerce.events
GROUP BY date, country, event_type;

-- Utiliser la vue
SELECT * FROM minio.ecommerce.daily_metrics
WHERE date = DATE '2024-01-01';
```

---

## 📈 Partie 5 : Monitoring et Métriques {#partie-5}

### 5.1 Script de Monitoring en Temps Réel

Créez `scripts/metrics.py` pour monitorer le pipeline :

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Monitoring en temps réel du pipeline e-commerce
Affiche les métriques agrégées depuis Kafka
"""

import json
from collections import defaultdict, Counter
from datetime import datetime
from kafka import KafkaConsumer

# ===== CONFIGURATION =====

KAFKA_BROKER = 'localhost:9092'
TOPIC = 'ecommerce-events'

# ===== CLASSE DE MONITORING =====

class StreamMonitor:
    """
    Classe pour agréger et afficher les métriques en temps réel
    """
    
    def __init__(self):
        """Initialiser les compteurs"""
        # Compteurs globaux
        self.total_events = 0
        self.event_types = Counter()
        self.categories = Counter()
        self.countries = Counter()
        self.devices = Counter()
        
        # Métriques financières
        self.total_revenue = 0.0
        self.revenue_by_category = defaultdict(float)
        self.revenue_by_country = defaultdict(float)
        
        # Métriques utilisateurs
        self.unique_users = set()
        self.unique_sessions = set()
        
        # Timestamp de début
        self.start_time = datetime.now()
    
    def process_event(self, event):
        """
        Traiter un événement et mettre à jour les métriques
        """
        # Compteurs globaux
        self.total_events += 1
        self.event_types[event['event_type']] += 1
        self.categories[event['category']] += 1
        self.countries[event['country']] += 1
        self.devices[event['device']] += 1
        
        # Utilisateurs et sessions uniques
        self.unique_users.add(event['user_id'])
        self.unique_sessions.add(event['session_id'])
        
        # Métriques financières (seulement pour les achats)
        if event['event_type'] == 'purchase':
            amount = event['price'] * event['quantity']
            self.total_revenue += amount
            self.revenue_by_category[event['category']] += amount
            self.revenue_by_country[event['country']] += amount
    
    def print_dashboard(self):
        """
        Afficher le dashboard de métriques
        """
        # Calculer la durée
        duration = (datetime.now() - self.start_time).total_seconds()
        events_per_sec = self.total_events / duration if duration > 0 else 0
        
        # Clear screen (optionnel)
        print("\033[2J\033[H")  # ANSI escape codes
        
        print("=" * 100)
        print(" " * 35 + "📊 DASHBOARD TEMPS RÉEL E-COMMERCE")
        print("=" * 100)
        print()
        
        # ===== MÉTRIQUES GLOBALES =====
        print("🌍 MÉTRIQUES GLOBALES")
        print("-" * 100)
        print(f"  Total Événements    : {self.total_events:,}")
        print(f"  Utilisateurs Uniques: {len(self.unique_users):,}")
        print(f"  Sessions Uniques    : {len(self.unique_sessions):,}")
        print(f"  Durée Monitoring    : {duration:.0f}s")
        print(f"  Débit               : {events_per_sec:.2f} événements/sec")
        print()
        
        # ===== RÉPARTITION PAR TYPE =====
        print("📊 RÉPARTITION PAR TYPE D'ÉVÉNEMENT")
        print("-" * 100)
        for event_type, count in self.event_types.most_common():
            pct = (count / self.total_events) * 100
            bar = "█" * int(pct / 2)  # Barre de progression
            print(f"  {event_type:20s} : {count:6,} ({pct:5.1f}%) {bar}")
        print()
        
        # ===== MÉTRIQUES FINANCIÈRES =====
        print("💰 MÉTRIQUES FINANCIÈRES")
        print("-" * 100)
        purchases = self.event_types.get('purchase', 0)
        avg_basket = self.total_revenue / purchases if purchases > 0 else 0
        
        print(f"  Revenu Total        : ${self.total_revenue:,.2f}")
        print(f"  Nombre d'Achats     : {purchases:,}")
        print(f"  Panier Moyen        : ${avg_basket:,.2f}")
        print()
        
        # Top 5 catégories par revenu
        print("  Top 5 Catégories par Revenu :")
        for category, revenue in sorted(self.revenue_by_category.items(), 
                                       key=lambda x: x[1], reverse=True)[:5]:
            print(f"    - {category:20s} : ${revenue:,.2f}")
        print()
        
        # ===== RÉPARTITION GÉOGRAPHIQUE =====
        print("🌍 RÉPARTITION GÉOGRAPHIQUE")
        print("-" * 100)
        for country, count in self.countries.most_common(5):
            pct = (count / self.total_events) * 100
            revenue = self.revenue_by_country.get(country, 0)
            print(f"  {country:15s} : {count:6,} événements ({pct:5.1f}%) | Revenue: ${revenue:,.2f}")
        print()
        
        # ===== RÉPARTITION PAR APPAREIL =====
        print("📱 RÉPARTITION PAR APPAREIL")
        print("-" * 100)
        for device, count in self.devices.most_common():
            pct = (count / self.total_events) * 100
            print(f"  {device:15s} : {count:6,} ({pct:5.1f}%)")
        print()
        
        print("=" * 100)
        print(f"  Dernière mise à jour : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("  Appuyez sur Ctrl+C pour arrêter le monitoring")
        print("=" * 100)


# ===== FONCTION PRINCIPALE =====

def monitor_stream():
    """
    Consommer les événements Kafka et afficher les métriques
    """
    print("🚀 Démarrage du monitoring...")
    print(f"📍 Broker: {KAFKA_BROKER}")
    print(f"📤 Topic : {TOPIC}")
    print()
    print("⏳ Connexion à Kafka...")
    
    try:
        # Créer le consumer Kafka
        consumer = KafkaConsumer(
            TOPIC,
            bootstrap_servers=[KAFKA_BROKER],
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            auto_offset_reset='latest',  # Lire seulement les nouveaux messages
            group_id='metrics-monitor',
            enable_auto_commit=True
        )
        
        print("✅ Connecté à Kafka")
        print("📊 Début du monitoring (mise à jour toutes les 10 événements)")
        print()
        
        # Créer le moniteur
        monitor = StreamMonitor()
        
        # Consommer les messages
        for message in consumer:
            event = message.value
            
            # Traiter l'événement
            monitor.process_event(event)
            
            # Afficher le dashboard toutes les 10 événements
            if monitor.total_events % 10 == 0:
                monitor.print_dashboard()
    
    except KeyboardInterrupt:
        print()
        print("=" * 100)
        print("🛑 Arrêt du monitoring")
        print("=" * 100)
        
        # Afficher les statistiques finales
        if monitor.total_events > 0:
            monitor.print_dashboard()
        
        consumer.close()
        print("✅ Consumer fermé proprement")
    
    except Exception as e:
        print(f"❌ Erreur : {e}")


if __name__ == "__main__":
    monitor_stream()
```

### 5.2 Lancer le Monitoring

```bash
# Lancer le monitoring dans un nouveau terminal
python scripts/metrics.py
```

Le dashboard se met à jour automatiquement toutes les 10 événements.

### 5.3 Interfaces Web de Monitoring

En plus du script Python, utilisez les interfaces web des composants :

#### **Spark UI** (http://localhost:4040)
- Voir les jobs Spark en cours
- Statistiques des batches de streaming
- Utilisation des ressources

#### **Spark Master UI** (http://localhost:8080)
- État du cluster Spark
- Workers connectés
- Applications en cours

#### **MinIO Console** (http://localhost:9001)
- Taille du bucket
- Nombre de fichiers
- Trafic réseau

#### **Trino UI** (http://localhost:8081)
- Requêtes en cours
- Historique des requêtes
- Performance des requêtes

---

## 🎯 Exercices Avancés {#exercices}

### Exercice 1 : Détection d'Anomalies

**Objectif** : Détecter les achats suspects (montant très élevé ou quantité anormale).

**Tâches** :
1. Modifier `spark_streaming_job.py` pour ajouter une colonne `is_anomaly`
2. Marquer comme anomalie si `total_amount > 5000` ou `quantity > 10`
3. Créer un topic Kafka séparé `anomaly-alerts`
4. Envoyer les anomalies vers ce topic

**Indice** :
```python
# Ajouter une colonne is_anomaly
from pyspark.sql.functions import when

enriched_df = enriched_df.withColumn(
    "is_anomaly",
    when((col("total_amount") > 5000) | (col("quantity") > 10), True).otherwise(False)
)

# Filtrer les anomalies
anomalies_df = enriched_df.filter(col("is_anomaly") == True)

# Écrire dans un topic Kafka
anomalies_df.selectExpr("to_json(struct(*)) AS value") \
    .writeStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", KAFKA_BROKER) \
    .option("topic", "anomaly-alerts") \
    .option("checkpointLocation", "/tmp/checkpoint/anomalies") \
    .start()
```

### Exercice 2 : Agrégations en Fenêtre Glissante

**Objectif** : Calculer des métriques en temps réel sur une fenêtre de temps.

**Tâches** :
1. Calculer le nombre d'événements par catégorie sur les 5 dernières minutes
2. Calculer le revenu total sur les 10 dernières minutes
3. Afficher les résultats en console

**Indice** :
```python
from pyspark.sql.functions import window

# Agrégation par fenêtre de 5 minutes
windowed_df = enriched_df \
    .withWatermark("timestamp", "10 minutes") \
    .groupBy(
        window(col("timestamp"), "5 minutes", "1 minute"),
        col("category")
    ) \
    .agg(
        count("*").alias("event_count"),
        sum("total_amount").alias("revenue")
    )

# Écrire en console
windowed_df.writeStream \
    .format("console") \
    .outputMode("update") \
    .trigger(processingTime="1 minute") \
    .start()
```

### Exercice 3 : Enrichissement avec Table de Référence

**Objectif** : Enrichir les événements avec des informations utilisateur.

**Tâches** :
1. Créer une table `users` avec des infos supplémentaires (âge, segment)
2. Joindre cette table avec les événements en streaming
3. Analyser les achats par segment d'utilisateurs

**Étapes** :

```python
# 1. Créer un DataFrame statique d'utilisateurs
users_data = [
    ("user_001", "Premium", 35, "Paris"),
    ("user_002", "Standard", 28, "Lyon"),
    # ... autres utilisateurs
]

users_df = spark.createDataFrame(users_data, ["user_id", "segment", "age", "city"])

# 2. Joindre avec le stream
enriched_df = events_df.join(users_df, "user_id", "left")

# 3. Analyser par segment (via Trino)
-- SELECT 
--     u.segment,
--     COUNT(*) as purchases,
--     SUM(e.total_amount) as revenue
-- FROM minio.ecommerce.events e
-- LEFT JOIN minio.ecommerce.users u ON e.user_id = u.user_id
-- WHERE e.event_type = 'purchase'
-- GROUP BY u.segment;
```

### Exercice 4 : Système d'Alerting

**Objectif** : Envoyer une alerte si un produit dépasse 100 vues en 10 minutes.

**Tâches** :
1. Compter les vues par produit sur une fenêtre de 10 minutes
2. Filtrer les produits avec > 100 vues
3. Envoyer une notification (console, Kafka, ou email)

**Solution Partielle** :
```python
# Agrégation par fenêtre et produit
product_views = events_df \
    .filter(col("event_type") == "view") \
    .withWatermark("timestamp", "15 minutes") \
    .groupBy(
        window(col("timestamp"), "10 minutes"),
        col("product_id"),
        col("product_name")
    ) \
    .agg(count("*").alias("view_count"))

# Filtrer les produits populaires
hot_products = product_views.filter(col("view_count") > 100)

# Afficher les alertes
hot_products.writeStream \
    .format("console") \
    .outputMode("update") \
    .start()
```

### Exercice 5 : Dashboard Temps Réel avec Streamlit

**Objectif** : Créer un dashboard web interactif pour visualiser les métriques.

**Outils** : Streamlit, Plotly

**Tâches** :
1. Installer Streamlit : `pip install streamlit plotly`
2. Créer `scripts/dashboard.py`
3. Se connecter à Trino et récupérer les données
4. Créer des graphiques interactifs

**Exemple de Code** :
```python
import streamlit as st
import plotly.express as px
from trino import dbapi

# Configuration
st.set_page_config(page_title="E-commerce Dashboard", layout="wide")

# Connexion à Trino
conn = dbapi.connect(
    host='localhost',
    port=8081,
    user='admin',
    catalog='minio',
    schema='ecommerce'
)

# Titre
st.title("📊 Dashboard E-commerce Temps Réel")

# Métriques principales
col1, col2, col3 = st.columns(3)

with col1:
    # Nombre total d'événements
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM events")
    total = cursor.fetchone()[0]
    st.metric("Total Événements", f"{total:,}")

with col2:
    # Revenu total
    cursor.execute("SELECT SUM(total_amount) FROM events WHERE event_type = 'purchase'")
    revenue = cursor.fetchone()[0] or 0
    st.metric("Revenu Total", f"${revenue:,.2f}")

with col3:
    # Utilisateurs uniques
    cursor.execute("SELECT COUNT(DISTINCT user_id) FROM events")
    users = cursor.fetchone()[0]
    st.metric("Utilisateurs Uniques", f"{users:,}")

# Graphique : Événements par type
st.subheader("📈 Répartition des Événements")
cursor.execute("""
    SELECT event_type, COUNT(*) as count
    FROM events
    GROUP BY event_type
    ORDER BY count DESC
""")
data = cursor.fetchall()
df = pd.DataFrame(data, columns=['Event Type', 'Count'])
fig = px.bar(df, x='Event Type', y='Count')
st.plotly_chart(fig, use_container_width=True)

# Graphique : Revenu par pays
st.subheader("🌍 Revenu par Pays")
cursor.execute("""
    SELECT country, SUM(total_amount) as revenue
    FROM events
    WHERE event_type = 'purchase'
    GROUP BY country
    ORDER BY revenue DESC
""")
data = cursor.fetchall()
df = pd.DataFrame(data, columns=['Country', 'Revenue'])
fig = px.pie(df, values='Revenue', names='Country')
st.plotly_chart(fig, use_container_width=True)

# Bouton de rafraîchissement
if st.button("🔄 Rafraîchir"):
    st.experimental_rerun()
```

Lancer le dashboard :
```bash
streamlit run scripts/dashboard.py
```

---

## 🔧 Dépannage {#depannage}

### Problème 1 : Kafka ne démarre pas

**Symptômes** :
```
ERROR Shutdown broker because all log dirs have failed (kafka.log.LogManager)
```

**Solution** :
```bash
# Arrêter les conteneurs
docker-compose down

# Supprimer les volumes (⚠️ efface les données !)
docker-compose down -v

# Redémarrer
docker-compose up -d
```

### Problème 2 : Spark ne trouve pas les packages

**Symptômes** :
```
java.lang.ClassNotFoundException: org.apache.spark.sql.kafka010
```

**Solution** :
Vérifier que les packages sont bien spécifiés dans `spark-submit` :
```bash
spark-submit \
  --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0,org.apache.hadoop:hadoop-aws:3.3.4,com.amazonaws:aws-java-sdk-bundle:1.12.367 \
  ...
```

### Problème 3 : Trino ne voit pas les données

**Symptômes** :
```sql
SELECT COUNT(*) FROM minio.ecommerce.events;
-- Retourne 0 alors que des données existent
```

**Solution** :
1. Vérifier que les données sont bien dans MinIO :
```bash
docker exec tp-spark-master ls -lah /data/ecommerce-data/events/
```

2. Recréer la table en forçant la détection des partitions :
```sql
DROP TABLE IF EXISTS minio.ecommerce.events;
-- Puis recréer la table
```

3. Forcer le rafraîchissement des métadonnées :
```sql
CALL system.sync_partition_metadata('minio', 'ecommerce', 'events', 'FULL');
```

### Problème 4 : MinIO refuse les connexions

**Symptômes** :
```
Py4JJavaError: An error occurred while calling o123.save.
: com.amazonaws.SdkClientException: Unable to execute HTTP request
```

**Solution** :
Vérifier la configuration S3 dans Spark :
```python
.config("spark.hadoop.fs.s3a.endpoint", "http://minio:9000")  # Nom du service Docker
.config("spark.hadoop.fs.s3a.path.style.access", "true")      # Obligatoire pour MinIO
```

### Problème 5 : Mémoire insuffisante

**Symptômes** :
```
java.lang.OutOfMemoryError: Java heap space
```

**Solution** :
Augmenter la mémoire allouée à Spark :
```bash
spark-submit \
  --conf spark.executor.memory=2g \
  --conf spark.driver.memory=2g \
  ...
```

Ou dans le `docker-compose.yml` :
```yaml
spark-worker:
  environment:
    - SPARK_WORKER_MEMORY=4G
```

### Problème 6 : Le producteur Python bloque

**Symptômes** :
Le producteur se bloque sans afficher d'erreur.

**Solution** :
1. Vérifier que Kafka est accessible :
```bash
nc -zv localhost 9092
```

2. Augmenter le timeout :
```python
producer = KafkaProducer(
    ...
    request_timeout_ms=30000,  # 30 secondes
    api_version_auto_timeout_ms=10000
)
```

---

## 📝 Checklist de Validation

Avant de considérer le TP terminé, vérifiez :

- [ ] Tous les conteneurs Docker sont démarrés (`docker-compose ps`)
- [ ] Le producteur Python envoie des événements sans erreur
- [ ] Kafka contient des messages (vérifier avec `kafka-console-consumer`)
- [ ] Le job Spark tourne et affiche des statistiques
- [ ] MinIO contient des fichiers Parquet (vérifier via l'interface web)
- [ ] Trino peut lire les données (`SELECT COUNT(*) FROM ...`)
- [ ] Au moins 5 requêtes d'analyse ont été exécutées avec succès
- [ ] Le monitoring en temps réel fonctionne

---

## 🎓 Conclusion et Apprentissages

### Ce que vous avez appris :

1. **Architecture Distribuée** : Conception d'un pipeline de données avec plusieurs composants communiquant entre eux

2. **Streaming de Données** : Traitement en temps réel avec Kafka et Spark Streaming

3. **Data Lake** : Stockage optimisé avec MinIO et format Parquet

4. **Analyse SQL Distribuée** : Requêtes sur des données massives avec Trino

5. **Partitionnement** : Optimisation des performances via le partitionnement

6. **Monitoring** : Suivi en temps réel d'un pipeline de données

### Compétences Acquises :

- ✅ Kafka : Producteur, consumer, topics
- ✅ Spark Streaming : Lecture, transformation, écriture
- ✅ MinIO : Stockage objet S3-compatible
- ✅ Trino : Requêtes SQL sur data lake
- ✅ Docker Compose : Orchestration de services
- ✅ Python : Manipulation de données, APIs Kafka et MinIO
- ✅ SQL Analytique : Agrégations, fenêtres, CTEs

### Pour Aller Plus Loin :

1. **Orchestration** : Ajouter Apache Airflow pour orchestrer le pipeline
2. **Qualité des Données** : Implémenter Great Expectations pour valider les données
3. **BI Tools** : Connecter Superset ou Metabase à Trino
4. **Machine Learning** : Entraîner un modèle de recommandation sur les données
5. **Production** : Déployer sur Kubernetes avec Helm charts

---

## 📚 Ressources Complémentaires

### Documentation Officielle :
- [Kafka Documentation](https://kafka.apache.org/documentation/)
- [Spark Streaming Guide](https://spark.apache.org/docs/latest/structured-streaming-programming-guide.html)
- [MinIO Documentation](https://min.io/docs/minio/linux/index.html)
- [Trino Documentation](https://trino.io/docs/current/)

### Tutoriels Recommandés :
- [Kafka Streams Tutorial](https://kafka.apache.org/documentation/streams/)
- [Spark By Examples](https://sparkbyexamples.com/)
- [Data Engineering Zoomcamp](https://github.com/DataTalksClub/data-engineering-zoomcamp)

### Livres :
- "Designing Data-Intensive Applications" par Martin Kleppmann
- "Spark: The Definitive Guide" par Bill Chambers et Matei Zaharia
- "Kafka: The Definitive Guide" par Neha Narkhede

---

## 🧹 Nettoyage Final

Lorsque vous avez terminé le TP :

```bash
# Arrêter tous les conteneurs
docker-compose down

# Supprimer les volumes (⚠️ efface toutes les données)
docker-compose down -v

# Supprimer les images Docker (optionnel, libère de l'espace)
docker rmi $(docker images -q)

# Nettoyer les fichiers temporaires
rm -rf data/ scripts/__pycache__/
```

---

**Bon courage pour votre TP ! 🚀**

*N'hésitez pas à poser des questions si vous rencontrez des difficultés.*
