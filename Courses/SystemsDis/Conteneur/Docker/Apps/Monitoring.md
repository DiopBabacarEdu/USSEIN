# Monitoring en Temps Réel avec Python, MySQL et Grafana

## Flux de données
1. Une application Python simule des capteurs (température, CPU, etc.)
2. Les données des capteurs sont insérées dans MySQL toutes les 5 secondes
3. Grafana lit les données et les affiche en temps réel
4. Les dashboards se rafraîchissent automatiquement

## 📁 Structure du Projet
```
monitoring-project/
│
├── docker-compose.yml
├── .env
├── requirements.txt
│
├── python-app/
│   ├── app.py
│   ├── database.py
│   ├── sensor_simulator.py
│   └── config.py
│
├── mysql-init/
│   └── init.sql
│
├── grafana/
│   ├── provisioning/
│   │   ├── datasources/
│   │   │   └── mysql-datasource.yaml
│   │   └── dashboards/
│   │       └── dashboard.yaml
│   └── dashboards/
│       └── system_monitoring.json
│
└── README.md
```

## 1. **Fichier docker-compose.yml**

```yaml
version: '3.8'

services:
  # Service MySQL
  mysql:
    image: mysql:8.0
    container_name: monitoring_mysql
    restart: unless-stopped
    environment:
      MYSQL_ROOT_PASSWORD: ${MYSQL_ROOT_PASSWORD}
      MYSQL_DATABASE: ${MYSQL_DATABASE}
      MYSQL_USER: ${MYSQL_USER}
      MYSQL_PASSWORD: ${MYSQL_PASSWORD}
    ports:
      - "3306:3306"
    volumes:
      - mysql_data:/var/lib/mysql
      - ./mysql-init:/docker-entrypoint-initdb.d
    networks:
      - monitoring_net
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost", "-u", "root", "-p${MYSQL_ROOT_PASSWORD}"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Service Grafana
  grafana:
    image: grafana/grafana:latest
    container_name: monitoring_grafana
    restart: unless-stopped
    environment:
      GF_SECURITY_ADMIN_PASSWORD: ${GF_ADMIN_PASSWORD}
      GF_INSTALL_PLUGINS: "grafana-clock-panel"
    ports:
      - "3000:3000"
    volumes:
      - grafana_data:/var/lib/grafana
      - ./grafana/provisioning:/etc/grafana/provisioning
      - ./grafana/dashboards:/var/lib/grafana/dashboards
    networks:
      - monitoring_net
    depends_on:
      mysql:
        condition: service_healthy

  # Application Python
  python-app:
    build: ./python-app
    container_name: monitoring_python
    restart: unless-stopped
    volumes:
      - ./python-app:/app
    networks:
      - monitoring_net
    depends_on:
      mysql:
        condition: service_healthy
    environment:
      MYSQL_HOST: mysql
      MYSQL_USER: ${MYSQL_USER}
      MYSQL_PASSWORD: ${MYSQL_PASSWORD}
      MYSQL_DATABASE: ${MYSQL_DATABASE}

networks:
  monitoring_net:
    driver: bridge

volumes:
  mysql_data:
    driver: local
  grafana_data:
    driver: local
```

## 2. **Fichier .env**
```env
# MySQL Configuration
MYSQL_ROOT_PASSWORD=RootPassword123!
MYSQL_DATABASE=monitoring_db
MYSQL_USER=monitoring_user
MYSQL_PASSWORD=UserPassword123!

# Grafana Configuration
GF_ADMIN_PASSWORD=admin

# Python App Configuration
SENSOR_INTERVAL=5
MAX_RECORDS=1000
```

## 3. **requirements.txt**
```txt
mysql-connector-python==8.1.0
pandas==2.0.3
numpy==1.24.3
matplotlib==3.7.2
python-dotenv==1.0.0
schedule==1.2.0
```

## 4. **mysql-init/init.sql**
```sql
-- Création de la base de données (déjà créée par Docker)
USE monitoring_db;

-- Table pour les données de capteurs
CREATE TABLE IF NOT EXISTS sensor_data (
    id INT AUTO_INCREMENT PRIMARY KEY,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    sensor_id VARCHAR(50) NOT NULL,
    temperature FLOAT,
    humidity FLOAT,
    pressure FLOAT,
    cpu_usage FLOAT,
    memory_usage FLOAT,
    status ENUM('normal', 'warning', 'critical') DEFAULT 'normal'
);

-- Table pour les logs d'événements
CREATE TABLE IF NOT EXISTS system_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    log_level ENUM('INFO', 'WARNING', 'ERROR', 'CRITICAL'),
    source VARCHAR(100),
    message TEXT,
    sensor_id VARCHAR(50)
);

-- Table pour les statistiques horaires
CREATE TABLE IF NOT EXISTS hourly_stats (
    id INT AUTO_INCREMENT PRIMARY KEY,
    hour_start DATETIME,
    sensor_id VARCHAR(50),
    avg_temperature FLOAT,
    avg_humidity FLOAT,
    max_cpu_usage FLOAT,
    min_cpu_usage FLOAT,
    record_count INT
);

-- Création d'index pour améliorer les performances
CREATE INDEX idx_timestamp ON sensor_data(timestamp);
CREATE INDEX idx_sensor_id ON sensor_data(sensor_id);
CREATE INDEX idx_status ON sensor_data(status);

-- Insertion de données de test
INSERT INTO sensor_data (sensor_id, temperature, humidity, pressure, cpu_usage, memory_usage, status)
VALUES 
    ('sensor_1', 22.5, 45.0, 1013.25, 45.5, 67.8, 'normal'),
    ('sensor_2', 24.8, 50.2, 1012.80, 60.3, 72.1, 'warning'),
    ('sensor_3', 21.2, 48.5, 1014.10, 30.7, 55.4, 'normal');

-- Création d'une vue pour les données récentes
CREATE VIEW recent_sensor_data AS
SELECT * FROM sensor_data 
WHERE timestamp > NOW() - INTERVAL 1 HOUR
ORDER BY timestamp DESC;

-- Procédure stockée pour nettoyer les anciennes données
DELIMITER $$
CREATE PROCEDURE cleanup_old_data(IN days_to_keep INT)
BEGIN
    DELETE FROM sensor_data 
    WHERE timestamp < NOW() - INTERVAL days_to_keep DAY;
    
    DELETE FROM system_logs 
    WHERE timestamp < NOW() - INTERVAL days_to_keep DAY;
    
    INSERT INTO system_logs (log_level, source, message)
    VALUES ('INFO', 'Database', CONCAT('Cleanup completed. Kept ', days_to_keep, ' days of data.'));
END$$
DELIMITER ;

-- Création d'un utilisateur avec privilèges limités (pour Grafana)
GRANT SELECT ON monitoring_db.* TO '${MYSQL_USER}'@'%';
GRANT SELECT, INSERT, UPDATE ON monitoring_db.sensor_data TO '${MYSQL_USER}'@'%';
GRANT SELECT ON monitoring_db.recent_sensor_data TO '${MYSQL_USER}'@'%';

FLUSH PRIVILEGES;
```

## 5. **Grafana Configuration**

### `grafana/provisioning/datasources/mysql-datasource.yaml`
```yaml
apiVersion: 1

datasources:
  - name: MySQL
    type: mysql
    access: proxy
    url: mysql:3306
    database: monitoring_db
    user: monitoring_user
    secureJsonData:
      password: "UserPassword123!"
    jsonData:
      maxOpenConns: 10
      maxIdleConns: 5
      connMaxLifetime: 14400
      cacheMode: "strict"
    editable: true
```

### `grafana/provisioning/dashboards/dashboard.yaml`
```yaml
apiVersion: 1

providers:
  - name: 'default'
    orgId: 1
    folder: ''
    type: file
    disableDeletion: false
    editable: true
    options:
      path: /var/lib/grafana/dashboards
```

### `grafana/dashboards/system_monitoring.json`
```json
{
  "dashboard": {
    "title": "Monitoring Système en Temps Réel",
    "description": "Tableau de bord pour visualiser les données des capteurs",
    "tags": ["monitoring", "sensors", "real-time"],
    "timezone": "browser",
    "panels": [
      {
        "title": "Température en Temps Réel",
        "type": "timeseries",
        "targets": [
          {
            "rawSql": "SELECT timestamp, sensor_id, temperature FROM sensor_data WHERE timestamp > NOW() - INTERVAL 1 HOUR ORDER BY timestamp",
            "format": "table",
            "datasource": "MySQL"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "unit": "celsius",
            "color": {"mode": "palette-classic"}
          }
        },
        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 0}
      },
      {
        "title": "Utilisation CPU",
        "type": "timeseries",
        "targets": [
          {
            "rawSql": "SELECT timestamp, sensor_id, cpu_usage FROM sensor_data WHERE timestamp > NOW() - INTERVAL 1 HOUR",
            "format": "table",
            "datasource": "MySQL"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "unit": "percent",
            "min": 0,
            "max": 100
          }
        },
        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 0}
      },
      {
        "title": "Statut des Capteurs",
        "type": "stat",
        "targets": [
          {
            "rawSql": "SELECT status, COUNT(*) as count FROM sensor_data WHERE timestamp > NOW() - INTERVAL 5 MINUTE GROUP BY status",
            "format": "table",
            "datasource": "MySQL"
          }
        ],
        "options": {
          "colorMode": "value",
          "graphMode": "none",
          "justifyMode": "auto"
        },
        "gridPos": {"h": 4, "w": 8, "x": 0, "y": 8}
      },
      {
        "title": "Table des Dernières Mesures",
        "type": "table",
        "targets": [
          {
            "rawSql": "SELECT timestamp, sensor_id, temperature, humidity, cpu_usage, memory_usage, status FROM sensor_data ORDER BY timestamp DESC LIMIT 20",
            "format": "table",
            "datasource": "MySQL"
          }
        ],
        "gridPos": {"h": 10, "w": 24, "x": 0, "y": 12}
      }
    ],
    "refresh": "5s"
  }
}
```

## 6. **Application Python**

### `python-app/Dockerfile`
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "app.py"]
```

### `python-app/config.py`
```python
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Configuration MySQL
    MYSQL_HOST = os.getenv('MYSQL_HOST', 'mysql')
    MYSQL_USER = os.getenv('MYSQL_USER', 'monitoring_user')
    MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', 'UserPassword123!')
    MYSQL_DATABASE = os.getenv('MYSQL_DATABASE', 'monitoring_db')
    
    # Configuration application
    SENSOR_INTERVAL = int(os.getenv('SENSOR_INTERVAL', 5))
    MAX_RECORDS = int(os.getenv('MAX_RECORDS', 1000))
    
    # Liste des capteurs
    SENSORS = ['sensor_1', 'sensor_2', 'sensor_3', 'sensor_4', 'sensor_5']
    
    # Plages de valeurs réalistes
    TEMP_RANGE = (18.0, 35.0)  # °C
    HUMIDITY_RANGE = (30.0, 80.0)  # %
    PRESSURE_RANGE = (1000.0, 1030.0)  # hPa
    CPU_RANGE = (10.0, 90.0)  # %
    MEMORY_RANGE = (40.0, 95.0)  # %
```

### `python-app/database.py`
```python
import mysql.connector
import logging
from datetime import datetime
from config import Config

class DatabaseManager:
    def __init__(self):
        self.config = Config()
        self.connection = None
        self.connect()
        
    def connect(self):
        """Établir la connexion à MySQL"""
        try:
            self.connection = mysql.connector.connect(
                host=self.config.MYSQL_HOST,
                user=self.config.MYSQL_USER,
                password=self.config.MYSQL_PASSWORD,
                database=self.config.MYSQL_DATABASE,
                connection_timeout=30
            )
            logging.info("✅ Connexion à MySQL établie")
        except mysql.connector.Error as err:
            logging.error(f"❌ Erreur de connexion MySQL: {err}")
            raise
    
    def insert_sensor_data(self, sensor_id, temperature, humidity, pressure, cpu_usage, memory_usage):
        """Insérer des données de capteur"""
        try:
            # Déterminer le statut basé sur les seuils
            status = 'normal'
            if cpu_usage > 80 or temperature > 30:
                status = 'warning'
            if cpu_usage > 90 or temperature > 35:
                status = 'critical'
            
            cursor = self.connection.cursor()
            query = """
            INSERT INTO sensor_data 
            (sensor_id, temperature, humidity, pressure, cpu_usage, memory_usage, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            
            values = (sensor_id, temperature, humidity, pressure, cpu_usage, memory_usage, status)
            cursor.execute(query, values)
            self.connection.commit()
            
            # Loguer l'événement si statut critique
            if status in ['warning', 'critical']:
                self.log_event(
                    'WARNING' if status == 'warning' else 'ERROR',
                    'Sensor',
                    f"Capteur {sensor_id} en statut {status}",
                    sensor_id
                )
            
            cursor.close()
            return cursor.lastrowid
            
        except mysql.connector.Error as err:
            logging.error(f"❌ Erreur d'insertion: {err}")
            self.connect()  # Tentative de reconnexion
            return None
    
    def log_event(self, log_level, source, message, sensor_id=None):
        """Loguer un événement dans la base de données"""
        try:
            cursor = self.connection.cursor()
            query = """
            INSERT INTO system_logs 
            (log_level, source, message, sensor_id)
            VALUES (%s, %s, %s, %s)
            """
            
            cursor.execute(query, (log_level, source, message, sensor_id))
            self.connection.commit()
            cursor.close()
            
        except mysql.connector.Error as err:
            logging.error(f"❌ Erreur de log: {err}")
    
    def get_recent_data(self, limit=100):
        """Récupérer les données récentes"""
        try:
            cursor = self.connection.cursor(dictionary=True)
            query = """
            SELECT * FROM sensor_data 
            ORDER BY timestamp DESC 
            LIMIT %s
            """
            
            cursor.execute(query, (limit,))
            results = cursor.fetchall()
            cursor.close()
            return results
            
        except mysql.connector.Error as err:
            logging.error(f"❌ Erreur de récupération: {err}")
            return []
    
    def cleanup_old_data(self, days_to_keep=7):
        """Nettoyer les anciennes données"""
        try:
            cursor = self.connection.cursor()
            cursor.callproc('cleanup_old_data', [days_to_keep])
            self.connection.commit()
            cursor.close()
            logging.info(f"✅ Données vieilles de {days_to_keep} jours nettoyées")
            
        except mysql.connector.Error as err:
            logging.error(f"❌ Erreur de nettoyage: {err}")
    
    def close(self):
        """Fermer la connexion"""
        if self.connection:
            self.connection.close()
            logging.info("🔌 Connexion MySQL fermée")
```

### `python-app/sensor_simulator.py`
```python
import random
import time
from datetime import datetime
from config import Config

class SensorSimulator:
    def __init__(self, sensor_id):
        self.sensor_id = sensor_id
        self.config = Config()
        
        # État initial basé sur l'ID du capteur
        self.base_temp = random.uniform(*self.config.TEMP_RANGE)
        self.base_humidity = random.uniform(*self.config.HUMIDITY_RANGE)
        self.base_cpu = random.uniform(20.0, 60.0)
        
    def generate_measurement(self):
        """Générer une mesure simulée"""
        # Ajouter des variations réalistes
        temp_variation = random.uniform(-2.0, 2.0)
        humidity_variation = random.uniform(-5.0, 5.0)
        cpu_variation = random.uniform(-15.0, 15.0)
        
        # Simuler des pics occasionnels
        if random.random() < 0.05:  # 5% de chance d'un pic
            cpu_variation += random.uniform(20.0, 40.0)
        
        if random.random() < 0.02:  # 2% de chance d'une anomalie
            temp_variation += random.uniform(5.0, 10.0)
        
        # Calculer les valeurs finales
        temperature = max(self.config.TEMP_RANGE[0], 
                         min(self.config.TEMP_RANGE[1], 
                             self.base_temp + temp_variation))
        
        humidity = max(self.config.HUMIDITY_RANGE[0], 
                      min(self.config.HUMIDITY_RANGE[1], 
                          self.base_humidity + humidity_variation))
        
        cpu_usage = max(self.config.CPU_RANGE[0], 
                       min(self.config.CPU_RANGE[1], 
                           self.base_cpu + cpu_variation))
        
        # Autres métriques
        pressure = random.uniform(*self.config.PRESSURE_RANGE)
        memory_usage = random.uniform(*self.config.MEMORY_RANGE)
        
        return {
            'sensor_id': self.sensor_id,
            'temperature': round(temperature, 2),
            'humidity': round(humidity, 2),
            'pressure': round(pressure, 2),
            'cpu_usage': round(cpu_usage, 2),
            'memory_usage': round(memory_usage, 2),
            'timestamp': datetime.now()
        }
    
    def simulate_day_pattern(self):
        """Simuler un pattern journalier"""
        hour = datetime.now().hour
        
        # Plus chaud en journée
        day_temp_adjustment = 0
        if 8 <= hour < 18:  # Journée
            day_temp_adjustment = random.uniform(2.0, 6.0)
        elif 0 <= hour < 6:  # Nuit
            day_temp_adjustment = random.uniform(-3.0, -1.0)
        
        # Plus d'activité CPU en journée
        cpu_adjustment = 0
        if 9 <= hour < 17:  # Heures de bureau
            cpu_adjustment = random.uniform(10.0, 30.0)
        
        measurement = self.generate_measurement()
        measurement['temperature'] += day_temp_adjustment
        measurement['cpu_usage'] += cpu_adjustment
        
        # Limiter les valeurs
        measurement['temperature'] = max(self.config.TEMP_RANGE[0],
                                       min(self.config.TEMP_RANGE[1],
                                           measurement['temperature']))
        measurement['cpu_usage'] = max(self.config.CPU_RANGE[0],
                                     min(self.config.CPU_RANGE[1],
                                         measurement['cpu_usage']))
        
        return measurement
```

### `python-app/app.py`
```python
import time
import logging
import signal
import sys
from threading import Thread
from datetime import datetime, timedelta
from database import DatabaseManager
from sensor_simulator import SensorSimulator
from config import Config

class MonitoringApplication:
    def __init__(self):
        self.config = Config()
        self.db = DatabaseManager()
        self.running = True
        
        # Initialiser les simulateurs de capteurs
        self.sensors = {sensor_id: SensorSimulator(sensor_id) 
                       for sensor_id in self.config.SENSORS}
        
        # Configurer le logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler('monitoring.log')
            ]
        )
        
        # Gestion des signaux pour un arrêt propre
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def signal_handler(self, sig, frame):
        """Gérer les signaux d'arrêt"""
        logging.info("🛑 Signal d'arrêt reçu, arrêt en cours...")
        self.running = False
    
    def collect_sensor_data(self):
        """Collecter les données de tous les capteurs"""
        logging.info("📡 Collecte des données des capteurs...")
        
        for sensor_id, simulator in self.sensors.items():
            try:
                # Générer des mesures avec pattern journalier
                measurement = simulator.simulate_day_pattern()
                
                # Insérer dans la base de données
                record_id = self.db.insert_sensor_data(
                    sensor_id=measurement['sensor_id'],
                    temperature=measurement['temperature'],
                    humidity=measurement['humidity'],
                    pressure=measurement['pressure'],
                    cpu_usage=measurement['cpu_usage'],
                    memory_usage=measurement['memory_usage']
                )
                
                if record_id:
                    logging.info(f"✅ Données insérées pour {sensor_id}: "
                                f"Temp={measurement['temperature']}°C, "
                                f"CPU={measurement['cpu_usage']}%")
                
            except Exception as e:
                logging.error(f"❌ Erreur avec le capteur {sensor_id}: {e}")
    
    def cleanup_task(self):
        """Tâche de nettoyage périodique"""
        while self.running:
            time.sleep(3600)  # Toutes les heures
            if self.running:
                self.db.cleanup_old_data(days_to_keep=7)
    
    def stats_task(self):
        """Tâche de calcul de statistiques"""
        while self.running:
            time.sleep(300)  # Toutes les 5 minutes
            if self.running:
                self.calculate_hourly_stats()
    
    def calculate_hourly_stats(self):
        """Calculer les statistiques horaires"""
        try:
            cursor = self.db.connection.cursor()
            
            # Calculer l'heure de début (heure précédente)
            hour_start = datetime.now().replace(minute=0, second=0, microsecond=0)
            hour_start -= timedelta(hours=1)
            
            # Calculer les stats pour chaque capteur
            for sensor_id in self.config.SENSORS:
                query = """
                SELECT 
                    AVG(temperature) as avg_temp,
                    AVG(humidity) as avg_humidity,
                    MAX(cpu_usage) as max_cpu,
                    MIN(cpu_usage) as min_cpu,
                    COUNT(*) as record_count
                FROM sensor_data 
                WHERE sensor_id = %s 
                AND timestamp >= %s 
                AND timestamp < %s
                """
                
                hour_end = hour_start + timedelta(hours=1)
                cursor.execute(query, (sensor_id, hour_start, hour_end))
                result = cursor.fetchone()
                
                if result and result[0]:  # Si on a des données
                    insert_query = """
                    INSERT INTO hourly_stats 
                    (hour_start, sensor_id, avg_temperature, avg_humidity, 
                     max_cpu_usage, min_cpu_usage, record_count)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """
                    
                    cursor.execute(insert_query, (
                        hour_start, sensor_id, 
                        float(result[0]), float(result[1]),
                        float(result[2]), float(result[3]),
                        int(result[4])
                    ))
            
            self.db.connection.commit()
            cursor.close()
            logging.info("📊 Statistiques horaires calculées")
            
        except Exception as e:
            logging.error(f"❌ Erreur calcul stats: {e}")
    
    def display_live_stats(self):
        """Afficher les statistiques en temps réel dans le terminal"""
        while self.running:
            time.sleep(10)  # Toutes les 10 secondes
            if self.running:
                try:
                    recent_data = self.db.get_recent_data(limit=5)
                    
                    if recent_data:
                        print("\n" + "="*60)
                        print("📊 DERNIÈRES MESURES (Temps Réel)")
                        print("="*60)
                        
                        for data in recent_data:
                            status_icon = "🟢" if data['status'] == 'normal' else \
                                         "🟡" if data['status'] == 'warning' else "🔴"
                            
                            print(f"{status_icon} {data['sensor_id']} - "
                                  f"Temp: {data['temperature']}°C | "
                                  f"Hum: {data['humidity']}% | "
                                  f"CPU: {data['cpu_usage']}% | "
                                  f"À: {data['timestamp'].strftime('%H:%M:%S')}")
                        
                        print("="*60)
                    
                except Exception as e:
                    logging.error(f"❌ Erreur d'affichage: {e}")
    
    def run(self):
        """Lancer l'application principale"""
        logging.info("🚀 Démarrage de l'application de monitoring...")
        logging.info(f"⏰ Intervalle de collecte: {self.config.SENSOR_INTERVAL}s")
        logging.info(f"🎯 Capteurs actifs: {', '.join(self.config.SENSORS)}")
        
        # Démarrer les tâches en arrière-plan
        cleanup_thread = Thread(target=self.cleanup_task, daemon=True)
        stats_thread = Thread(target=self.stats_task, daemon=True)
        display_thread = Thread(target=self.display_live_stats, daemon=True)
        
        cleanup_thread.start()
        stats_thread.start()
        display_thread.start()
        
        # Loguer un événement de démarrage
        self.db.log_event('INFO', 'Application', 'Application démarrée')
        
        # Boucle principale
        cycle_count = 0
        while self.running:
            try:
                # Collecter les données
                self.collect_sensor_data()
                
                cycle_count += 1
                if cycle_count % 12 == 0:  # Toutes les minutes (12 * 5s)
                    logging.info(f"♻️ Cycle {cycle_count} terminé")
                
                # Attendre l'intervalle configuré
                time.sleep(self.config.SENSOR_INTERVAL)
                
            except KeyboardInterrupt:
                self.running = False
            except Exception as e:
                logging.error(f"❌ Erreur dans la boucle principale: {e}")
                time.sleep(5)  # Attendre avant de réessayer
        
        # Arrêt propre
        self.shutdown()
    
    def shutdown(self):
        """Arrêt propre de l'application"""
        logging.info("🛑 Arrêt de l'application...")
        self.db.log_event('INFO', 'Application', 'Application arrêtée')
        self.db.close()
        logging.info("👋 Application arrêtée avec succès")

if __name__ == "__main__":
    app = MonitoringApplication()
    app.run()
```



## Test et vérification

### 1. Lancer les services 
# Démarrer tous les services
docker-compose up -d

# Vérifier l'état
docker-compose ps

# Voir les logs
docker-compose logs -f
```

## Accès aux Services

| Service | URL | Identifiants |
|---------|-----|--------------|
| Grafana | http://localhost:3000 | admin / admin |
| MySQL | localhost:3306 | monitoring_user / UserPassword123! |



## Application Python

### Structure:
- `app.py` : Application principale
- `database.py` : Gestion de la base de données
- `sensor_simulator.py` : Simulation de capteurs
- `config.py` : Configuration

### Fonctionnalités:
- Simulation réaliste de 5 capteurs
- Pattern journalier (jour/nuit)
- Anomalies aléatoires
- Logs dans la base de données
- Nettoyage automatique des anciennes données

## Base de données MySQL

### Tables principales:
1. `sensor_data` : Données des capteurs
2. `system_logs` : Logs d'événements
3. `hourly_stats` : Statistiques horaires

### Vues et procédures:
- `recent_sensor_data` : Vue des dernières données
- `cleanup_old_data` : Nettoyage automatique

## Visualisation Grafana

### Dashboards inclus:
1. **Monitoring en Temps Réel**
   - Graphiques de température et CPU
   - Table des dernières mesures
   - Statut des capteurs

### Configuration:
- Datasource MySQL pré-configuré
- Dashboard avec rafraîchissement automatique (5s)
- Variables pour filtrer par capteur

## Tests et Exploration

### Tester la base de données:
```bash
# Se connecter à MySQL
docker exec -it monitoring_mysql mysql -u monitoring_user -p monitoring_db

# Requêtes utiles
SELECT COUNT(*) FROM sensor_data;
SELECT * FROM sensor_data ORDER BY timestamp DESC LIMIT 5;
SELECT status, COUNT(*) FROM sensor_data GROUP BY status;
```

### Tester l'API Grafana:
```bash
# Vérifier la santé
curl http://localhost:3000/api/health
```

### Générer plus de données:
```bash
# Modifier l'intervalle dans .env
SENSOR_INTERVAL=2  # Toutes les 2 secondes
docker-compose restart python-app
```

### Exercices suggérés:
1. Ajouter un nouveau type de capteur
2. Créer un nouveau dashboard Grafana
3. Implémenter des alertes Grafana
4. Exporter les données vers un fichier CSV
5. Ajouter une API REST pour interroger les données
