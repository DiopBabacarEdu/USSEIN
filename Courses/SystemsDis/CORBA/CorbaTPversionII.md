# TP CORBA - Guide Complet (Sans IDE)
## Master MaDSI

---

## 📋 Table des matières
1. [Introduction à CORBA](#introduction)
2. [Prérequis et Installation](#prérequis)
3. [Architecture Globale](#architecture)
4. [Partie 1 : IDL Enrichi](#partie-1-idl)
5. [Partie 2 : Serveur CORBA](#partie-2-serveur)
6. [Partie 3 : Client CORBA](#partie-3-client)
7. [Exécution et Tests](#exécution)
8. [Dépannage](#dépannage)

---

## <a name="introduction"></a>📚 Introduction à CORBA

**CORBA (Common Object Request Broker Architecture)** est une norme développée par l'OMG permettant la communication entre objets distribués, indépendamment des plateformes matérielles, des langages de programmation et des systèmes d'exploitation.

### Concept clé : ORB (Object Request Broker)
L'ORB fournit le mécanisme permettant aux objets distribués de communiquer entre eux, localement ou sur réseau, écrits sous différents langages ou situés à différents endroits.

---

## <a name="prérequis"></a>⚙️ Prérequis et Installation

### Logiciels nécessaires

1. **JDK 8 ou supérieur**
   ```bash
   # Vérifier la version installée
   java -version
   javac -version
   ```

2. **Éditeur de texte** : Visual Studio Code, Notepad++, Sublime Text, etc.

3. **Terminal/Console** : CMD (Windows), Terminal (Linux/Mac)

### Installation du JDK

#### Windows
- Télécharger depuis : [https://www.oracle.com/java/technologies/downloads/](https://www.oracle.com/java/technologies/downloads/)
- Suivre l'installation standard
- Ajouter le chemin `JDK\bin` aux variables d'environnement PATH

#### Linux
```bash
sudo apt-get update
sudo apt-get install openjdk-8-jdk
```

#### macOS
```bash
brew install openjdk@8
```

---

## <a name="architecture"></a>🏗️ Architecture Globale

```
┌─────────────────────────────────────────────────────┐
│                  ORBD (ORB Daemon)                   │
│              (Port 1050 par défaut)                  │
│            • Naming Service                          │
│            • Registry centralisé                     │
└─────────────────────────────────────────────────────┘
                         ▲                    ▲
                         │                    │
                         │                    │
        ┌────────────────┴──────┐     ┌──────┴──────────┐
        │                       │     │                 │
    ┌─────────────────┐   ┌──────────────────────┐   ┌──────────────────┐
    │  SERVER CORBA   │   │  NAMING SERVICE      │   │  CLIENT CORBA    │
    │                 │   │  (Registre)          │   │                  │
    │ • ORB           │   │                      │   │ • ORB            │
    │ • POA (Adapter) │◄──┤ ABC → Référence     ├──►│ • Lookup service │
    │ • Serveurs d'obj│   │      de l'objet     │   │ • Invocation     │
    │   métier        │   │                      │   │                  │
    └─────────────────┘   └──────────────────────┘   └──────────────────┘
```

### Flux de Communication

1. **Démarrage ORBD** : Lance le service de nommage centralisé
2. **Serveur s'enregistre** : Le serveur crée un objet et le lie au Naming Service
3. **Client cherche l'objet** : Le client demande au Naming Service la référence
4. **Client invoque** : Le client appelle les méthodes via l'ORB

---

## <a name="partie-1-idl"></a>## Partie 1 : Définition IDL Enrichie

### Présentation de l'IDL (Interface Definition Language)

L'IDL est un langage de spécification indépendant des implémentations. Il définit :
- Les interfaces des objets distribués
- Les types de données échangées
- Les signatures des méthodes

### Structure des Répertoires

```
TP_CORBA/
├── src/
│   ├── Addition.idl              # Spécification CORBA
│   ├── CalculatriceServer/       # Implémentation serveur
│   │   ├── CalculatriceImpl.java
│   │   └── StartServer.java
│   └── CalculatriceClient/       # Code client
│       └── StartClient.java
├── bin/                          # Classes compilées
└── GeneratedCorba/               # Classes générées par idlj
```

### Étape 1 : Créer le fichier IDL

**Fichier : `Addition.idl`**

```idl
// ============================================
// Spécification CORBA - Calculatrice Avancée
// ============================================

/**
 * Module principal encapsulant toutes les interfaces
 * Les modules organisent les namespaces pour éviter les conflits
 */
module CalculatriceApp 
{
  /**
   * Exception personnalisée : Division par zéro
   * Levée quand on essaie de diviser par zéro
   */
  exception DivisionParZeroException
  {
    string message;  // Message d'erreur détaillé
  };

  /**
   * Exception personnalisée : Opération non supportée
   * Levée quand une opération demandée n'existe pas
   */
  exception OperationNonSupporteeException
  {
    string operation;  // Nom de l'opération
    string raison;     // Raison du refus
  };

  /**
   * Structure pour encapsuler un résultat complexe
   * Contient le résultat et des métadonnées
   */
  struct ResultatCalcul
  {
    double valeur;           // Le résultat numérique
    string operationEffectuee; // Description de l'opération
    long timestampUnix;      // Moment du calcul (timestamp)
  };

  /**
   * Énumération des opérations disponibles
   */
  enum TypeOperation
  {
    ADDITION,      // +
    SOUSTRACTION,  // -
    MULTIPLICATION, // *
    DIVISION,      // /
    MODULO,        // %
    PUISSANCE      // ^
  };

  /**
   * Interface principale : Calculatrice
   * 
   * Fournit des opérations mathématiques variées
   * sur deux nombres flottants
   */
  interface Calculatrice
  {
    /**
     * Effectue l'addition de deux nombres
     * @param a Premier opérande
     * @param b Deuxième opérande
     * @return Le résultat de a + b
     */
    double add(in double a, in double b);

    /**
     * Effectue la soustraction
     * @param a Minuende
     * @param b Soustrahende
     * @return Le résultat de a - b
     */
    double substract(in double a, in double b);

    /**
     * Effectue la multiplication
     * @param a Premier facteur
     * @param b Deuxième facteur
     * @return Le résultat de a * b
     */
    double multiply(in double a, in double b);

    /**
     * Effectue la division avec vérification
     * @param numerateur Dividende
     * @param denominateur Diviseur
     * @return Le résultat de numerateur / denominateur
     * @throws DivisionParZeroException si denominateur == 0
     */
    double divide(in double numerateur, in double denominateur) 
      raises (DivisionParZeroException);

    /**
     * Calcule le modulo (reste de la division entière)
     * @param dividende Premier nombre
     * @param diviseur Deuxième nombre
     * @return Le reste de la division
     * @throws DivisionParZeroException si diviseur == 0
     */
    long modulo(in long dividende, in long diviseur) 
      raises (DivisionParZeroException);

    /**
     * Calcule la puissance (base ^ exposant)
     * @param base La base
     * @param exposant L'exposant (doit être ≥ 0)
     * @return base ^ exposant
     */
    double power(in double base, in long exposant);

    /**
     * Opération générique avec type d'opération comme paramètre
     * Permet de tester différentes opérations dynamiquement
     * @param operation Le type d'opération à effectuer
     * @param a Premier opérande
     * @param b Deuxième opérande
     * @return Structure contenant le résultat et les métadonnées
     * @throws DivisionParZeroException si division par zéro
     * @throws OperationNonSupporteeException si opération invalide
     */
    ResultatCalcul operationGenerique(
      in TypeOperation operation,
      in double a,
      in double b
    ) raises (
      DivisionParZeroException,
      OperationNonSupporteeException
    );

    /**
     * Obtient le nombre d'opérations effectuées depuis le démarrage
     * Utile pour le monitoring
     * @return Nombre d'appels reçus
     */
    long getNombreOperations();

    /**
     * Réinitialise le compteur d'opérations
     */
    void reinitialiserCompteur();

    /**
     * Méthode de shutdown asynchrone (one-way)
     * N'attend pas de réponse du serveur
     * Arrête l'exécution du serveur proprement
     */
    oneway void shutdown();
  };

  /**
   * Interface de gestion et monitoring
   * Permet de surveiller l'état du serveur
   */
  interface GestionnaireServeur
  {
    /**
     * Obtient le timestamp du démarrage du serveur
     * @return Nombre de secondes depuis le démarrage (Unix timestamp)
     */
    long getTimestampDemarrage();

    /**
     * Obtient le statut du serveur
     * @return Message descriptif du statut
     */
    string getStatut();

    /**
     * Obtient la version de la calculatrice
     * @return Numéro de version (ex: "1.0.0")
     */
    string getVersion();
  };
};
```

### Explication détaillée des constructs IDL

| Construct | Description | Exemple |
|-----------|-------------|---------|
| **module** | Organise le namespace | `module CalculatriceApp { }` |
| **interface** | Définit un contrat CORBA | `interface Calculatrice { }` |
| **in / out / inout** | Direction des paramètres | `in double a` (entrée) |
| **raises** | Exceptions possibles | `raises (DivisionParZeroException)` |
| **struct** | Structure de données | `struct ResultatCalcul { }` |
| **enum** | Type énuméré | `enum TypeOperation { }` |
| **exception** | Exception CORBA | `exception MonException { }` |
| **oneway** | Appel asynchrone sans retour | `oneway void shutdown()` |

---

## <a name="partie-2-serveur"></a>## Partie 2 : Implémentation du Serveur

### Étape 2 : Compiler le fichier IDL

**Ouvrez un terminal** dans le répertoire `src/` et exécutez :

```bash
# Compiler le fichier IDL
idlj -fall Addition.idl

# Vérifier les fichiers générés
ls -la CalculatriceApp/
# Vous verrez : Calculatrice.java, CalculatriceHelper.java, etc.
```

**Fichiers générés automatiquement :**
- `Calculatrice.java` : Interface de base
- `CalculatriceHelper.java` : Utilitaires d'accès
- `CalculatriceHolder.java` : Support pour les paramètres out
- `CalculatricePOA.java` : Classe de base pour l'implémentation
- `TypeOperation.java` : Enum
- `ResultatCalcul.java` : Structure
- `DivisionParZeroException.java` : Exception
- `OperationNonSupporteeException.java` : Exception

### Étape 3 : Créer la classe d'implémentation du serveur

**Fichier : `CalculatriceServer/CalculatriceImpl.java`**

```java
import CalculatriceApp.*;
import org.omg.CORBA.*;
import org.omg.PortableServer.*;
import java.util.Date;

/**
 * Implémentation de l'interface Calculatrice
 * 
 * Cette classe fournit l'implémentation concrète des méthodes
 * définies dans l'interface CORBA Calculatrice.
 * Elle s'exécute sur le serveur et est invoquée par les clients via l'ORB.
 */
public class CalculatriceImpl extends CalculatricePOA 
{
    private ORB orb;                      // Référence à l'ORB
    private long compteurOperations = 0;  // Compteur d'opérations
    private long timestampDemarrage;      // Timestamp du démarrage

    /**
     * Constructeur
     * Initialise le timestamp de démarrage
     */
    public CalculatriceImpl() 
    {
        this.timestampDemarrage = System.currentTimeMillis() / 1000;
    }

    /**
     * Injecte la référence ORB
     * Nécessaire pour permettre au serveur de s'arrêter
     */
    public void setORB(ORB orb_val) 
    {
        orb = orb_val;
    }

    /**
     * Addition de deux nombres
     * @param a Premier nombre
     * @param b Deuxième nombre
     * @return a + b
     */
    @Override
    public double add(double a, double b) 
    {
        compteurOperations++;
        System.out.println("[SERVEUR] Opération ADD : " + a + " + " + b + 
                          " = " + (a + b));
        return a + b;
    }

    /**
     * Soustraction
     */
    @Override
    public double substract(double a, double b) 
    {
        compteurOperations++;
        System.out.println("[SERVEUR] Opération SUBTRACT : " + a + " - " + b + 
                          " = " + (a - b));
        return a - b;
    }

    /**
     * Multiplication
     */
    @Override
    public double multiply(double a, double b) 
    {
        compteurOperations++;
        System.out.println("[SERVEUR] Opération MULTIPLY : " + a + " * " + b + 
                          " = " + (a * b));
        return a * b;
    }

    /**
     * Division avec vérification du diviseur
     * @throws DivisionParZeroException si diviseur est 0
     */
    @Override
    public double divide(double numerateur, double denominateur) 
        throws DivisionParZeroException 
    {
        if (denominateur == 0) 
        {
            System.err.println("[SERVEUR] ERREUR : Division par zéro !");
            throw new DivisionParZeroException("Division par zéro impossible");
        }
        
        compteurOperations++;
        double resultat = numerateur / denominateur;
        System.out.println("[SERVEUR] Opération DIVIDE : " + numerateur + " / " + 
                          denominateur + " = " + resultat);
        return resultat;
    }

    /**
     * Modulo (reste de la division)
     */
    @Override
    public long modulo(long dividende, long diviseur) 
        throws DivisionParZeroException 
    {
        if (diviseur == 0) 
        {
            throw new DivisionParZeroException("Modulo par zéro impossible");
        }
        
        compteurOperations++;
        long resultat = dividende % diviseur;
        System.out.println("[SERVEUR] Opération MODULO : " + dividende + " % " + 
                          diviseur + " = " + resultat);
        return resultat;
    }

    /**
     * Puissance (base ^ exposant)
     */
    @Override
    public double power(double base, long exposant) 
    {
        compteurOperations++;
        double resultat = Math.pow(base, exposant);
        System.out.println("[SERVEUR] Opération POWER : " + base + " ^ " + 
                          exposant + " = " + resultat);
        return resultat;
    }

    /**
     * Opération générique selon le type
     * Démontre l'utilisation des énumérations et structures
     */
    @Override
    public ResultatCalcul operationGenerique(
        TypeOperation operation, 
        double a, 
        double b) 
        throws DivisionParZeroException, OperationNonSupporteeException 
    {
        ResultatCalcul resultat = new ResultatCalcul();
        resultat.timestampUnix = System.currentTimeMillis() / 1000;
        
        switch (operation.value()) 
        {
            case TypeOperation._ADDITION:
                resultat.valeur = a + b;
                resultat.operationEffectuee = "Addition(" + a + " + " + b + ")";
                break;
                
            case TypeOperation._SOUSTRACTION:
                resultat.valeur = a - b;
                resultat.operationEffectuee = "Soustraction(" + a + " - " + b + ")";
                break;
                
            case TypeOperation._MULTIPLICATION:
                resultat.valeur = a * b;
                resultat.operationEffectuee = "Multiplication(" + a + " * " + b + ")";
                break;
                
            case TypeOperation._DIVISION:
                if (b == 0) 
                {
                    throw new DivisionParZeroException("Division par zéro");
                }
                resultat.valeur = a / b;
                resultat.operationEffectuee = "Division(" + a + " / " + b + ")";
                break;
                
            case TypeOperation._PUISSANCE:
                resultat.valeur = Math.pow(a, (long)b);
                resultat.operationEffectuee = "Puissance(" + a + " ^ " + (long)b + ")";
                break;
                
            default:
                throw new OperationNonSupporteeException(
                    "Operation" + operation, 
                    "Type d'opération non reconnu"
                );
        }
        
        compteurOperations++;
        System.out.println("[SERVEUR] Opération générique : " + 
                          resultat.operationEffectuee + " = " + resultat.valeur);
        return resultat;
    }

    /**
     * Obtient le nombre d'opérations effectuées
     */
    @Override
    public long getNombreOperations() 
    {
        return compteurOperations;
    }

    /**
     * Réinitialise le compteur
     */
    @Override
    public void reinitialiserCompteur() 
    {
        compteurOperations = 0;
        System.out.println("[SERVEUR] Compteur réinitialisé");
    }

    /**
     * Arrête le serveur proprement
     */
    @Override
    public void shutdown() 
    {
        System.out.println("[SERVEUR] Demande d'arrêt reçue...");
        System.out.println("[SERVEUR] Nombre d'opérations effectuées : " + 
                          compteurOperations);
        orb.shutdown(false);
    }
}
```

### Étape 4 : Créer la classe de démarrage du serveur

**Fichier : `CalculatriceServer/StartServer.java`**

```java
import CalculatriceApp.*;
import org.omg.CosNaming.*;
import org.omg.CosNaming.NamingContextPackage.*;
import org.omg.CORBA.*;
import org.omg.PortableServer.*;
import org.omg.PortableServer.POA;

/**
 * Classe de démarrage du serveur CORBA
 * 
 * Responsabilités :
 * 1. Initialiser l'ORB
 * 2. Créer et enregistrer l'implémentation
 * 3. S'enregistrer auprès du Naming Service
 * 4. Attendre les invocations des clients
 */
public class StartServer 
{
    public static void main(String args[]) 
    {
        try 
        {
            // ===== ÉTAPE 1 : Initialisation de l'ORB =====
            System.out.println(">>> Démarrage du serveur CORBA <<<");
            System.out.println("[1/4] Initialisation de l'ORB...");
            
            ORB orb = ORB.init(args, null);

            // ===== ÉTAPE 2 : Récupération du POA (Portable Object Adapter) =====
            System.out.println("[2/4] Configuration du POA (Portable Object Adapter)...");
            
            POA rootpoa = POAHelper.narrow(
                orb.resolve_initial_references("RootPOA")
            );
            
            // Activation du gestionnaire de POA
            rootpoa.the_POAManager().activate();
            System.out.println("    ✓ POA activé");

            // ===== ÉTAPE 3 : Création de l'objet serveur =====
            System.out.println("[3/4] Création de l'implémentation Calculatrice...");
            
            // Créer une instance de l'implémentation
            CalculatriceImpl calcImpl = new CalculatriceImpl();
            
            // Fournir la référence ORB pour permettre le shutdown
            calcImpl.setORB(orb);
            
            // Convertir le servant en référence CORBA
            org.omg.CORBA.Object ref = 
                rootpoa.servant_to_reference(calcImpl);
            
            // Affiner (narrow) la référence générique en Calculatrice
            Calculatrice calcRef = CalculatriceHelper.narrow(ref);
            System.out.println("    ✓ Objet Calculatrice créé");

            // ===== ÉTAPE 4 : Enregistrement au Naming Service =====
            System.out.println("[4/4] Enregistrement au Naming Service...");
            
            // Obtenir une référence au Naming Service
            org.omg.CORBA.Object objRef = 
                orb.resolve_initial_references("NameService");
            
            // Affiner en NamingContextExt
            NamingContextExt ncRef = 
                NamingContextExtHelper.narrow(objRef);
            
            // Créer un chemin de nommage pour l'objet
            // Format : "nom_du_service"
            NameComponent path[] = ncRef.to_name("CalculatriceService");
            
            // Enregistrer l'objet sous ce nom
            ncRef.rebind(path, calcRef);
            
            System.out.println("    ✓ Service enregistré comme 'CalculatriceService'");
            System.out.println();
            System.out.println("╔════════════════════════════════════════╗");
            System.out.println("║ SERVEUR CORBA PRÊT ET EN ATTENTE      ║");
            System.out.println("║ Service : CalculatriceService          ║");
            System.out.println("║ Port ORBD : 1050                       ║");
            System.out.println("║ Appuyez sur Ctrl+C pour arrêter       ║");
            System.out.println("╚════════════════════════════════════════╝");
            System.out.println();

            // ===== ÉTAPE 5 : Attendre les invocations =====
            // Boucle infinie : le serveur attend les appels clients
            orb.run();
        } 
        catch (Exception e) 
        {
            System.err.println("╔════════════════════════════════════════╗");
            System.err.println("║ ERREUR AU DÉMARRAGE DU SERVEUR         ║");
            System.err.println("╚════════════════════════════════════════╝");
            System.err.println("Message : " + e.getMessage());
            e.printStackTrace(System.out);
        }
        
        System.out.println("[SERVEUR] Arrêt du serveur...");
    }
}
```

---

## <a name="partie-3-client"></a>## Partie 3 : Implémentation du Client

### Étape 5 : Créer la classe client

**Fichier : `CalculatriceClient/StartClient.java`**

```java
import CalculatriceApp.*;
import org.omg.CosNaming.*;
import org.omg.CosNaming.NamingContextPackage.*;
import org.omg.CORBA.*;
import java.util.Scanner;

/**
 * Classe client CORBA
 * 
 * Se connecte au serveur via l'ORB et invoque les méthodes distantes
 * Propose un menu interactif pour tester les opérations
 */
public class StartClient 
{
    private static Calculatrice calculatrice;
    private static Scanner scanner;

    public static void main(String[] args) 
    {
        try 
        {
            // ===== ÉTAPE 1 : Initialisation =====
            System.out.println(">>> Démarrage du client CORBA <<<");
            System.out.println("[1/2] Initialisation de l'ORB...");
            
            ORB orb = ORB.init(args, null);

            // ===== ÉTAPE 2 : Recherche du service =====
            System.out.println("[2/2] Recherche du service CalculatriceService...");
            
            // Obtenir une référence au Naming Service
            org.omg.CORBA.Object objRef = 
                orb.resolve_initial_references("NameService");
            
            // Affiner en NamingContextExt
            NamingContextExt ncRef = 
                NamingContextExtHelper.narrow(objRef);
            
            // Résoudre le nom "CalculatriceService"
            calculatrice = CalculatriceHelper.narrow(
                ncRef.resolve_str("CalculatriceService")
            );
            
            System.out.println("    ✓ Service trouvé !");
            System.out.println();
            
            // Initialiser le scanner pour les entrées
            scanner = new Scanner(System.in);

            // Afficher le menu principal
            afficherMenuPrincipal(orb);
        } 
        catch (org.omg.CORBA.ORBPackage.InvalidName ex) 
        {
            System.err.println("ERREUR : Service de nommage non accessible");
            System.err.println("Assurez-vous que ORBD est lancé !");
            ex.printStackTrace();
        } 
        catch (NotFound ex) 
        {
            System.err.println("ERREUR : Service 'CalculatriceService' non trouvé");
            System.err.println("Vérifiez que le serveur est bien lancé");
            ex.printStackTrace();
        } 
        catch (Exception ex) 
        {
            System.err.println("ERREUR : " + ex.getMessage());
            ex.printStackTrace();
        }
    }

    /**
     * Affiche le menu principal et gère les entrées utilisateur
     */
    private static void afficherMenuPrincipal(ORB orb) 
    {
        boolean continuer = true;
        
        while (continuer) 
        {
            System.out.println();
            System.out.println("╔════════════════════════════════════════╗");
            System.out.println("║      MENU CALCULATRICE CORBA            ║");
            System.out.println("╠════════════════════════════════════════╣");
            System.out.println("║ 1. Addition                             ║");
            System.out.println("║ 2. Soustraction                         ║");
            System.out.println("║ 3. Multiplication                       ║");
            System.out.println("║ 4. Division                             ║");
            System.out.println("║ 5. Modulo                               ║");
            System.out.println("║ 6. Puissance                            ║");
            System.out.println("║ 7. Opération générique                  ║");
            System.out.println("║ 8. Voir le nombre d'opérations          ║");
            System.out.println("║ 9. Réinitialiser le compteur            ║");
            System.out.println("║ 0. Quitter                              ║");
            System.out.println("╚════════════════════════════════════════╝");
            System.out.print("Votre choix : ");
            
            String choix = scanner.nextLine().trim();
            
            try 
            {
                switch (choix) 
                {
                    case "1":
                        testAddition();
                        break;
                    case "2":
                        testSoustraction();
                        break;
                    case "3":
                        testMultiplication();
                        break;
                    case "4":
                        testDivision();
                        break;
                    case "5":
                        testModulo();
                        break;
                    case "6":
                        testPuissance();
                        break;
                    case "7":
                        testOperationGenerique();
                        break;
                    case "8":
                        afficherNombreOperations();
                        break;
                    case "9":
                        reinitialiserCompteur();
                        break;
                    case "0":
                        System.out.println("Arrêt du serveur...");
                        calculatrice.shutdown();
                        continuer = false;
                        break;
                    default:
                        System.out.println("❌ Choix invalide");
                }
            } 
            catch (DivisionParZeroException e) 
            {
                System.err.println("❌ ERREUR : " + e.message);
            } 
            catch (OperationNonSupporteeException e) 
            {
                System.err.println("❌ ERREUR : Opération '" + e.operation + 
                                   "' non supportée (" + e.raison + ")");
            } 
            catch (Exception e) 
            {
                System.err.println("❌ ERREUR : " + e.getMessage());
            }
        }
        
        scanner.close();
        System.out.println("Client fermé");
    }

    /**
     * Test de l'addition
     */
    private static void testAddition() 
    {
        System.out.print("Entrez le premier nombre : ");
        double a = Double.parseDouble(scanner.nextLine());
        
        System.out.print("Entrez le deuxième nombre : ");
        double b = Double.parseDouble(scanner.nextLine());
        
        double resultat = calculatrice.add(a, b);
        System.out.println("📊 Résultat : " + a + " + " + b + " = " + resultat);
    }

    /**
     * Test de la soustraction
     */
    private static void testSoustraction() 
    {
        System.out.print("Entrez le premier nombre : ");
        double a = Double.parseDouble(scanner.nextLine());
        
        System.out.print("Entrez le deuxième nombre : ");
        double b = Double.parseDouble(scanner.nextLine());
        
        double resultat = calculatrice.substract(a, b);
        System.out.println("📊 Résultat : " + a + " - " + b + " = " + resultat);
    }

    /**
     * Test de la multiplication
     */
    private static void testMultiplication() 
    {
        System.out.print("Entrez le premier nombre : ");
        double a = Double.parseDouble(scanner.nextLine());
        
        System.out.print("Entrez le deuxième nombre : ");
        double b = Double.parseDouble(scanner.nextLine());
        
        double resultat = calculatrice.multiply(a, b);
        System.out.println("📊 Résultat : " + a + " * " + b + " = " + resultat);
    }

    /**
     * Test de la division avec gestion d'exception
     */
    private static void testDivision() 
        throws DivisionParZeroException 
    {
        System.out.print("Entrez le dividende : ");
        double numerateur = Double.parseDouble(scanner.nextLine());
        
        System.out.print("Entrez le diviseur : ");
        double denominateur = Double.parseDouble(scanner.nextLine());
        
        double resultat = calculatrice.divide(numerateur, denominateur);
        System.out.println("📊 Résultat : " + numerateur + " / " + 
                          denominateur + " = " + resultat);
    }

    /**
     * Test du modulo
     */
    private static void testModulo() 
        throws DivisionParZeroException 
    {
        System.out.print("Entrez le dividende (entier) : ");
        long dividende = Long.parseLong(scanner.nextLine());
        
        System.out.print("Entrez le diviseur (entier) : ");
        long diviseur = Long.parseLong(scanner.nextLine());
        
        long resultat = calculatrice.modulo(dividende, diviseur);
        System.out.println("📊 Résultat : " + dividende + " % " + 
                          diviseur + " = " + resultat);
    }

    /**
     * Test de la puissance
     */
    private static void testPuissance() 
    {
        System.out.print("Entrez la base : ");
        double base = Double.parseDouble(scanner.nextLine());
        
        System.out.print("Entrez l'exposant : ");
        long exposant = Long.parseLong(scanner.nextLine());
        
        double resultat = calculatrice.power(base, exposant);
        System.out.println("📊 Résultat : " + base + " ^ " + 
                          exposant + " = " + resultat);
    }

    /**
     * Test de l'opération générique
     */
    private static void testOperationGenerique() 
        throws DivisionParZeroException, OperationNonSupporteeException 
    {
        System.out.println("\n┌─ Types d'opérations disponibles ─┐");
        System.out.println("│ 0 : ADDITION                      │");
        System.out.println("│ 1 : SOUSTRACTION                  │");
        System.out.println("│ 2 : MULTIPLICATION                │");
        System.out.println("│ 3 : DIVISION                      │");
        System.out.println("│ 4 : MODULO                        │");
        System.out.println("│ 5 : PUISSANCE                     │");
        System.out.println("└───────────────────────────────────┘");
        
        System.out.print("Choisissez le type (0-5) : ");
        int typeInt = Integer.parseInt(scanner.nextLine());
        
        TypeOperation typeOp;
        try 
        {
            typeOp = TypeOperation.from_int(typeInt);
        } 
        catch (Exception e) 
        {
            System.err.println("Type invalide");
            return;
        }
        
        System.out.print("Entrez le premier opérande : ");
        double a = Double.parseDouble(scanner.nextLine());
        
        System.out.print("Entrez le deuxième opérande : ");
        double b = Double.parseDouble(scanner.nextLine());
        
        ResultatCalcul resultat = 
            calculatrice.operationGenerique(typeOp, a, b);
        
        System.out.println("📊 Opération : " + resultat.operationEffectuee);
        System.out.println("   Résultat : " + resultat.valeur);
        System.out.println("   Timestamp : " + resultat.timestampUnix);
    }

    /**
     * Affiche le nombre d'opérations effectuées
     */
    private static void afficherNombreOperations() 
    {
        long nombre = calculatrice.getNombreOperations();
        System.out.println("📈 Nombre d'opérations depuis le démarrage : " + nombre);
    }

    /**
     * Réinitialise le compteur d'opérations
     */
    private static void reinitialiserCompteur() 
    {
        calculatrice.reinitialiserCompteur();
        System.out.println("✓ Compteur réinitialisé");
    }
}
```

---

## <a name="exécution"></a>## Exécution et Tests

### Structure des répertoires avant exécution

```
TP_CORBA/
├── src/
│   ├── Addition.idl
│   ├── CalculatriceServer/
│   │   ├── CalculatriceImpl.java
│   │   └── StartServer.java
│   ├── CalculatriceClient/
│   │   └── StartClient.java
│   └── CalculatriceApp/
│       ├── (fichiers générés par idlj)
│
└── bin/  (à créer)
```

### Compilation

**Étape 1 : Compiler le fichier IDL**

```bash
cd TP_CORBA/src
idlj -fall Addition.idl
```

**Étape 2 : Compiler les classes Java**

```bash
# Windows
javac -d ../bin CalculatriceApp/*.java
javac -cp ../bin -d ../bin CalculatriceServer/*.java
javac -cp ../bin -d ../bin CalculatriceClient/*.java

# Linux/Mac
javac -d ../bin CalculatriceApp/*.java
javac -cp ../bin -d ../bin CalculatriceServer/*.java
javac -cp ../bin -d ../bin CalculatriceClient/*.java
```

### Exécution

**Terminal 1 : Démarrer l'ORBD (Object Request Broker Daemon)**

```bash
# Windows
start orbd -ORBInitialPort 1050

# Linux/Mac
orbd -ORBInitialPort 1050 &
```

**Terminal 2 : Démarrer le serveur**

```bash
cd TP_CORBA/bin
java -cp . CalculatriceServer.StartServer -ORBInitialPort 1050 -ORBInitialHost localhost
```

**Terminal 3 : Démarrer le client**

```bash
cd TP_CORBA/bin
java -cp . CalculatriceClient.StartClient -ORBInitialPort 1050 -ORBInitialHost localhost
```

### Exemple de test interactif

```
╔════════════════════════════════════════╗
│      MENU CALCULATRICE CORBA            │
╠════════════════════════════════════════╣
│ 1. Addition                             │
│ 2. Soustraction                         │
│ 3. Multiplication                       │
│ 4. Division                             │
│ 5. Modulo                               │
│ 6. Puissance                            │
│ 7. Opération générique                  │
│ 8. Voir le nombre d'opérations          │
│ 9. Réinitialiser le compteur            │
│ 0. Quitter                              │
╚════════════════════════════════════════╝
Votre choix : 1
Entrez le premier nombre : 42
Entrez le deuxième nombre : 8
📊 Résultat : 42.0 + 8.0 = 50.0

Votre choix : 4
Entrez le dividende : 100
Entrez le diviseur : 0
❌ ERREUR : Division par zéro impossible

Votre choix : 8
📈 Nombre d'opérations depuis le démarrage : 1

Votre choix : 0
```

---

## <a name="dépannage"></a>## Dépannage

### Problème 1 : "orbd : command not found"

**Cause** : Le chemin vers le JDK n'est pas configuré

**Solution** :
```bash
# Ajouter le chemin du JDK au PATH
# Windows : Ajouter C:\Program Files\Java\jdk1.8.0_xxx\bin aux variables d'environnement
# Linux/Mac : export PATH=$PATH:/chemin/vers/jdk/bin
```

### Problème 2 : "Cannot locate the Naming Service"

**Cause** : L'ORBD n'est pas lancé ou sur un port différent

**Solution** :
1. Vérifier que l'ORBD est en cours d'exécution
2. Vérifier que tous les services utilisent le même port (1050)
3. Redémarrer l'ORBD :
```bash
# Arrêter tout
# Puis relancer
orbd -ORBInitialPort 1050
```

### Problème 3 : "Service 'CalculatriceService' not found"

**Cause** : Le serveur n'est pas lancé ou n'a pas pu s'enregistrer

**Solution** :
1. Vérifier que le serveur est bien lancé (Terminal 2)
2. Vérifier les messages d'erreur dans le terminal du serveur
3. S'assurer que le nom du service est identique côté serveur et client

### Problème 4 : "ClassNotFoundException"

**Cause** : Les fichiers générés par idlj ne sont pas compilés

**Solution** :
```bash
# S'assurer que idlj a bien généré les fichiers
ls src/CalculatriceApp/

# Recompiler :
cd src
idlj -fall Addition.idl
cd ..
javac -d bin src/CalculatriceApp/*.java
```

### Problème 5 : Port déjà utilisé

**Cause** : Un autre processus utilise le port 1050

**Solution** :
```bash
# Utiliser un port différent (ex: 1051)
orbd -ORBInitialPort 1051
# Et mettre à jour tous les services pour utiliser ce port
java ... -ORBInitialPort 1051 -ORBInitialHost localhost
```

---

## ✅ Concepts Clés Récapitulatifs

| Concept | Description |
|---------|-------------|
| **IDL** | Langage de définition indépendant du langage |
| **ORB** | Gestionnaire de communication distribuée |
| **POA** | Adaptateur permettant d'enregistrer les objets |
| **ORBD** | Daemon contenant le service de nommage |
| **Naming Service** | Registre centralisé des services disponibles |
| **Exceptions CORBA** | Gestion des erreurs sur le réseau |
| **Structs** | Conteneurs de données structurées |
| **Enums** | Types énumérés |
| **Oneway** | Appels asynchrones sans attente de réponse |

---

## 🎓 Extensions Possibles

1. **Authentification** : Ajouter un système d'authentification client
2. **Persistance** : Sauvegarder l'historique des opérations en base de données
3. **Interface GUI** : Créer une interface graphique avec Swing ou JavaFX
4. **Load Balancing** : Déployer plusieurs serveurs derrière un équilibrage de charge
5. **Metrics** : Exposer les métriques via JMX pour monitoring
6. **Logging** : Implémenter un système de logging distribué (Log4j)
7. **Multi-langage** : Développer un client en Python ou C++ utilisant le même IDL

---

**Fin du TP CORBA Reformulé - Master MaDSI**
