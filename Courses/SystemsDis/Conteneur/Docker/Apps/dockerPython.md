# Exercice Docker : Application Python avec MySQL

## Objectif
Créer une application Python simple avec Docker qui se connecte à MySQL pour gérer une liste de livres.

## Structure du projet
```
bibliotheque-python/
├── docker-compose.yml
├── Dockerfile
├── app.py
├── requirements.txt
└── init.sql
```

## Fichier 1 : `init.sql`

Ce fichier crée la base de données et la table au démarrage.

```sql
-- Créer la base de données
CREATE DATABASE IF NOT EXISTS bibliotheque;
USE bibliotheque;

-- Créer la table livres
CREATE TABLE livres (
    id INT AUTO_INCREMENT PRIMARY KEY,
    titre VARCHAR(200) NOT NULL,
    auteur VARCHAR(100) NOT NULL,
    disponible BOOLEAN DEFAULT TRUE
);

-- Insérer quelques livres
INSERT INTO livres (titre, auteur, disponible) VALUES
('Le Petit Prince', 'Saint-Exupéry', TRUE),
('1984', 'George Orwell', TRUE),
('Les Misérables', 'Victor Hugo', FALSE);
```

## Fichier 2 : `app.py`

Application Python simple avec 4 opérations sur la base de données.

```python
import mysql.connector
import time

# Fonction 1: Afficher tous les livres
def afficher_livres(cursor):
    print("=== 1. AFFICHER tous les livres ===")
    
    # Exécuter la requête SQL
    cursor.execute("SELECT * FROM livres")
    
    # Récupérer tous les résultats
    livres = cursor.fetchall()
    
    # Parcourir et afficher les résultats
    for livre in livres:
        id_livre = livre[0]
        titre = livre[1]
        auteur = livre[2]
        disponible = livre[3]
        
        statut = "Disponible" if disponible else "Emprunté"
        print(f"{id_livre} | {titre} - {auteur} [{statut}]")


# Fonction 2: Ajouter un livre
def ajouter_livre(cursor, conn, titre, auteur):
    print("\n=== 2. AJOUTER un livre ===")
    
    # Requête SQL avec des paramètres (%s)
    sql = "INSERT INTO livres (titre, auteur) VALUES (%s, %s)"
    
    # Valeurs à insérer (tuple)
    valeurs = (titre, auteur)
    
    # Exécuter la requête
    cursor.execute(sql, valeurs)
    
    # Valider la transaction
    conn.commit()
    
    print(f"Livre ajouté: {titre}")


# Fonction 3: Emprunter un livre (mettre disponible = FALSE)
def emprunter_livre(cursor, conn, id_livre):
    print("\n=== 3. EMPRUNTER un livre ===")
    
    # Requête UPDATE avec paramètre
    sql = "UPDATE livres SET disponible = FALSE WHERE id = %s"
    
    # Exécuter avec l'ID du livre
    cursor.execute(sql, (id_livre,))
    
    # Valider la transaction
    conn.commit()
    
    print(f"Livre ID {id_livre} emprunté")


# Fonction 4: Compter les livres disponibles
def compter_disponibles(cursor):
    print("\n=== 4. COMPTER les livres disponibles ===")
    
    # Requête avec COUNT
    cursor.execute("SELECT COUNT(*) as total FROM livres WHERE disponible = TRUE")
    
    # Récupérer le résultat
    resultat = cursor.fetchone()
    total = resultat[0]
    
    print(f"Nombre de livres disponibles: {total}")


# Programme principal
def main():
    print("Démarrage de l'application...")
    
    # Attendre que MySQL soit prêt
    time.sleep(10)
    
    try:
        # Connexion à la base de données
        conn = mysql.connector.connect(
            host="mysql-db",        # Nom du service Docker
            user="root",
            password="root123",
            database="bibliotheque"
        )
        
        print("Connexion réussie!\n")
        
        # Créer un curseur pour exécuter des requêtes
        cursor = conn.cursor()
        
        # 1. AFFICHER tous les livres
        afficher_livres(cursor)
        
        # 2. AJOUTER un nouveau livre
        ajouter_livre(cursor, conn, "L'Étranger", "Albert Camus")
        
        # 3. EMPRUNTER un livre
        emprunter_livre(cursor, conn, 1)
        
        # 4. COMPTER les livres disponibles
        compter_disponibles(cursor)
        
        # Fermer le curseur et la connexion
        cursor.close()
        conn.close()
        print("\nConnexion fermée.")
        
    except mysql.connector.Error as erreur:
        print(f"Erreur: {erreur}")


# Point d'entrée du programme
if __name__ == "__main__":
    main()
```

## Fichier 3 : `requirements.txt`

Liste des bibliothèques Python nécessaires.

```txt
mysql-connector-python==8.0.33
```

## Fichier 4 : `Dockerfile`

Ce fichier décrit comment construire l'image Docker de l'application Python.

```dockerfile
# Image de base: Python 3.9
FROM python:3.9-slim

# Dossier de travail dans le conteneur
WORKDIR /app

# Copier le fichier des dépendances
COPY requirements.txt .

# Installer les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code Python
COPY app.py .

# Commande pour lancer l'application
CMD ["python", "app.py"]
```

## Fichier 5 : `docker-compose.yml`

Ce fichier configure les deux conteneurs (MySQL et Python) et leurs relations.

```yaml
version: '3.8'

services:
  # Service 1: Base de données MySQL
  mysql-db:
    image: mysql:8.0
    container_name: ma-base-mysql
    environment:
      MYSQL_ROOT_PASSWORD: root123
      MYSQL_DATABASE: bibliotheque
    volumes:
      # Initialiser la base avec init.sql
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql
    ports:
      - "3307:3306"

  # Service 2: Application Python
  python-app:
    build: .
    container_name: mon-app-python
    depends_on:
      - mysql-db
```

## Comment utiliser l'exercice

### Étape 1: Créer les fichiers

Créez tous les fichiers ci-dessus dans le dossier `bibliotheque-python/`

### Étape 2: Lancer l'application

```bash
# Construire et démarrer les conteneurs
docker-compose up --build

# Pour arrêter
docker-compose down
```

### Étape 3: Observer les résultats

L'application va:
1. Afficher les 3 livres initiaux
2. Ajouter "L'Étranger"
3. Marquer "Le Petit Prince" comme emprunté
4. Compter les livres disponibles

## Comparaison Java vs Python

### Java (PreparedStatement)
```java
String sql = "INSERT INTO livres (titre, auteur) VALUES (?, ?)";
PreparedStatement pstmt = conn.prepareStatement(sql);
pstmt.setString(1, titre);
pstmt.setString(2, auteur);
pstmt.executeUpdate();
```

### Python (paramètres avec %s)
```python
sql = "INSERT INTO livres (titre, auteur) VALUES (%s, %s)"
valeurs = (titre, auteur)
cursor.execute(sql, valeurs)
conn.commit()
```

## Points importants Python

### 1. Le curseur (cursor)
```python
cursor = conn.cursor()  # Créer un curseur
cursor.execute(sql)     # Exécuter une requête
cursor.fetchall()       # Récupérer tous les résultats
cursor.fetchone()       # Récupérer un seul résultat
cursor.close()          # Fermer le curseur
```

### 2. Les paramètres sécurisés
```python
# ✅ Correct: Utiliser %s et un tuple
sql = "SELECT * FROM livres WHERE auteur = %s"
cursor.execute(sql, (auteur,))  # Notez la virgule pour un tuple d'un élément

# ❌ Incorrect: Concaténation (vulnérable aux injections SQL)
sql = f"SELECT * FROM livres WHERE auteur = '{auteur}'"
```

### 3. Commit pour les modifications
```python
# Pour INSERT, UPDATE, DELETE, il faut faire commit()
cursor.execute("INSERT INTO livres (titre) VALUES (%s)", (titre,))
conn.commit()  # ← Important ! Sinon les changements ne sont pas sauvegardés

# Pour SELECT, pas besoin de commit()
cursor.execute("SELECT * FROM livres")
```

### 4. Récupérer les résultats
```python
# fetchall() → Liste de tous les résultats
cursor.execute("SELECT * FROM livres")
livres = cursor.fetchall()  # [(1, 'Titre1', 'Auteur1', True), (2, 'Titre2', ...)]

# fetchone() → Un seul résultat
cursor.execute("SELECT COUNT(*) FROM livres")
resultat = cursor.fetchone()  # (3,)
total = resultat[0]           # 3
```

## Exercices à faire

### Exercice 1: Retourner un livre
Créez une fonction `retourner_livre(cursor, conn, id_livre)` qui remet `disponible = TRUE`

```python
def retourner_livre(cursor, conn, id_livre):
    # Votre code ici
    pass
```

### Exercice 2: Rechercher par auteur
Créez une fonction `rechercher_par_auteur(cursor, auteur)` qui affiche tous les livres d'un auteur

```python
def rechercher_par_auteur(cursor, auteur):
    # Votre code ici
    pass
```

### Exercice 3: Supprimer un livre
Créez une fonction `supprimer_livre(cursor, conn, id_livre)` qui supprime un livre

```python
def supprimer_livre(cursor, conn, id_livre):
    # Votre code ici
    pass
```

## Astuces Python + MySQL

### Afficher les noms des colonnes
```python
cursor.execute("SELECT * FROM livres")
colonnes = [desc[0] for desc in cursor.description]
print(colonnes)  # ['id', 'titre', 'auteur', 'disponible']
```

### Utiliser un dictionnaire pour les résultats
```python
cursor = conn.cursor(dictionary=True)
cursor.execute("SELECT * FROM livres")
livres = cursor.fetchall()
# [{'id': 1, 'titre': 'Titre', 'auteur': 'Auteur', 'disponible': True}, ...]
```

### Gestion des erreurs
```python
try:
    cursor.execute(sql, valeurs)
    conn.commit()
except mysql.connector.Error as erreur:
    print(f"Erreur SQL: {erreur}")
    conn.rollback()  # Annuler les changements en cas d'erreur
```

---

**Durée**: 1-2 heures  
**Concepts**: Python, MySQL, Docker, curseurs, requêtes paramétrées, commit/rollback
