# Exercice Docker : Application Java avec MySQL

## Objectif
Créer une application Java simple avec Docker qui se connecte à MySQL pour gérer une liste de livres.

## Structure du projet
```
bibliotheque/
├── docker-compose.yml
├── Dockerfile
├── src/
│   └── Main.java
├── lib/
│   └── mysql-connector-java-8.0.33.jar
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

## Fichier 2 : `src/Main.java`

Application Java simple avec 4 opérations sur la base de données.

```java
import java.sql.*;

public class Main {
    
    public static void main(String[] args) {
        
        // Informations de connexion
        String url = "jdbc:mysql://mysql-db:3306/bibliotheque";
        String utilisateur = "root";
        String motDePasse = "root123";
        
        try {
            // Attendre que MySQL soit prêt
            System.out.println("Démarrage de l'application...");
            Thread.sleep(10000);
            
            // Connexion à la base de données
            Connection conn = DriverManager.getConnection(url, utilisateur, motDePasse);
            System.out.println("Connexion réussie!\n");
            
            // 1. AFFICHER tous les livres
            System.out.println("=== 1. AFFICHER tous les livres ===");
            afficherLivres(conn);
            
            // 2. AJOUTER un nouveau livre
            System.out.println("\n=== 2. AJOUTER un livre ===");
            ajouterLivre(conn, "L'Étranger", "Albert Camus");
            
            // 3. MODIFIER la disponibilité d'un livre
            System.out.println("\n=== 3. EMPRUNTER un livre (ID=1) ===");
            emprunterLivre(conn, 1);
            
            // 4. COMPTER les livres disponibles
            System.out.println("\n=== 4. COMPTER les livres disponibles ===");
            compterDisponibles(conn);
            
            // Fermer la connexion
            conn.close();
            System.out.println("\nConnexion fermée.");
            
        } catch (Exception e) {
            System.out.println("Erreur: " + e.getMessage());
            e.printStackTrace();
        }
    }
    
    // Méthode 1: Afficher tous les livres
    public static void afficherLivres(Connection conn) throws SQLException {
        
        // Créer et exécuter la requête SQL
        Statement stmt = conn.createStatement();
        ResultSet resultat = stmt.executeQuery("SELECT * FROM livres");
        
        // Parcourir et afficher les résultats
        while (resultat.next()) {
            int id = resultat.getInt("id");
            String titre = resultat.getString("titre");
            String auteur = resultat.getString("auteur");
            boolean dispo = resultat.getBoolean("disponible");
            
            System.out.println(id + " | " + titre + " - " + auteur + 
                             " [" + (dispo ? "Disponible" : "Emprunté") + "]");
        }
    }
    
    // Méthode 2: Ajouter un livre
    public static void ajouterLivre(Connection conn, String titre, String auteur) 
        throws SQLException {
        
        // Préparer la requête avec des paramètres
        String sql = "INSERT INTO livres (titre, auteur) VALUES (?, ?)";
        PreparedStatement pstmt = conn.prepareStatement(sql);
        
        // Remplacer les ? par les valeurs
        pstmt.setString(1, titre);
        pstmt.setString(2, auteur);
        
        // Exécuter la requête
        pstmt.executeUpdate();
        System.out.println("Livre ajouté: " + titre);
    }
    
    // Méthode 3: Emprunter un livre (mettre disponible = FALSE)
    public static void emprunterLivre(Connection conn, int id) throws SQLException {
        
        // Préparer la requête UPDATE
        String sql = "UPDATE livres SET disponible = FALSE WHERE id = ?";
        PreparedStatement pstmt = conn.prepareStatement(sql);
        
        // Définir l'ID du livre
        pstmt.setInt(1, id);
        
        // Exécuter la mise à jour
        pstmt.executeUpdate();
        System.out.println("Livre ID " + id + " emprunté");
    }
    
    // Méthode 4: Compter les livres disponibles
    public static void compterDisponibles(Connection conn) throws SQLException {
        
        // Requête avec COUNT
        Statement stmt = conn.createStatement();
        ResultSet resultat = stmt.executeQuery(
            "SELECT COUNT(*) as total FROM livres WHERE disponible = TRUE"
        );
        
        // Récupérer le résultat
        if (resultat.next()) {
            int total = resultat.getInt("total");
            System.out.println("Nombre de livres disponibles: " + total);
        }
    }
}
```

## Fichier 3 : `Dockerfile`

Ce fichier décrit comment construire l'image Docker de l'application Java.

```dockerfile
# Image de base: Java 11
FROM openjdk:11-jdk-slim

# Dossier de travail dans le conteneur
WORKDIR /app

# Copier le code Java
COPY src/Main.java /app/

# Copier le connecteur MySQL
COPY lib/mysql-connector-java-8.0.33.jar /app/

# Compiler le programme Java
RUN javac Main.java

# Commande pour lancer l'application
CMD ["java", "-cp", ".:/app/mysql-connector-java-8.0.33.jar", "Main"]
```

## Fichier 4 : `docker-compose.yml`

Ce fichier configure les deux conteneurs (MySQL et Java) et leurs relations.

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

  # Service 2: Application Java
  java-app:
    build: .
    container_name: mon-app-java
    depends_on:
      - mysql-db
```

## Comment utiliser l'exercice

### Étape 1: Préparer les fichiers

1. Créer les dossiers `src/` et `lib/`
2. Télécharger `mysql-connector-java-8.0.33.jar` depuis https://dev.mysql.com/downloads/connector/j/
3. Le placer dans le dossier `lib/`
4. Créer tous les fichiers ci-dessus

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

## Questions pour comprendre

1. **Que fait `docker-compose.yml`?**
   - Il définit 2 services qui communiquent ensemble

2. **Pourquoi `mysql-db` dans l'URL de connexion?**
   - C'est le nom du service MySQL dans docker-compose
   - Docker crée un réseau pour que les conteneurs se parlent

3. **À quoi sert `PreparedStatement`?**
   - À sécuriser les requêtes SQL avec des paramètres
   - Évite les injections SQL

## Exercices à faire

### Exercice 1: Ajouter une méthode
Créez une méthode `retournerLivre(conn, id)` qui remet `disponible = TRUE`

### Exercice 2: Rechercher un livre
Créez une méthode `rechercherParAuteur(conn, auteur)` qui affiche tous les livres d'un auteur

### Exercice 3: Supprimer un livre
Créez une méthode `supprimerLivre(conn, id)` qui supprime un livre par son ID

---

**Durée**: 1-2 heures  
**Concepts Docker**: Conteneurs, docker-compose, communication entre services, volumes
