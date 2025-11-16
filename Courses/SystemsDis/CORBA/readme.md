# Guide Complet CORBA
## Common Object Request Broker Architecture

---

## Table des matières
1. [Introduction à CORBA](#introduction)
2. [Architecture et Composants](#architecture)
3. [IDL - Interface Definition Language](#idl)
4. [Prise en main de CORBA](#prise-en-main)
5. [Applications potentielles](#applications)
6. [Exercices pratiques](#exercices)
7. [Projet avancé](#projet)

---

## 1. Introduction à CORBA {#introduction}

### Qu'est-ce que CORBA ?

CORBA (Common Object Request Broker Architecture) est une architecture standardisée de middleware créée par l'OMG (Object Management Group) en 1989. C'est un système d'appel de procédures distantes (RPC) basé sur l'orienté objet.

### Principes fondamentaux

**Middleware** : CORBA agit comme une couche intermédiaire entre la couche application et la couche transport (TCP), permettant la communication entre applications hétérogènes.

**Transparence totale** : Le client n'a pas besoin de connaître :
- L'emplacement physique de l'objet
- Le langage d'implémentation
- Le système d'exploitation
- La plateforme matérielle
- Le mécanisme de communication utilisé

### Avantages de CORBA

- **Interopérabilité** : Communication entre systèmes hétérogènes
- **Multiplateforme** : Windows, Unix, Mac, Solaris, etc.
- **Multi-langage** : Java, C++, Python, COBOL, Ada, PHP, etc.
- **Standards ouverts** : Spécifications publiques et non propriétaires
- **Indépendance** : Séparation interface/implémentation

---

## 2. Architecture et Composants {#architecture}

### Object Management Architecture (OMA)

L'OMA définit quatre niveaux de services :

```
┌─────────────────────────────────────┐
│    INTERFACES APPLICATION           │  (Non standardisées)
├─────────────────────────────────────┤
│    INTERFACES DOMAINE               │  (Télécoms, Finance, Médical)
├─────────────────────────────────────┤
│    SERVICES PRÉDÉFINIS              │  (Services utilisateurs)
├─────────────────────────────────────┤
│    SERVICES OBJETS                  │  (Naming, Trading, etc.)
├─────────────────────────────────────┤
│    OBJECT REQUEST BROKER (ORB)      │  (Cœur de CORBA)
└─────────────────────────────────────┘
```

### Composants clés de CORBA

#### 1. ORB (Object Request Broker)
- Gestionnaire de requêtes sur des objets
- Achemine les invocations entre clients et serveurs
- Garantit la transparence de localisation

#### 2. IDL (Interface Definition Language)
- Langage de description d'interfaces
- Indépendant du langage de programmation
- Définit les méthodes et attributs visibles

#### 3. POA (Portable Object Adapter)
- Gère l'activation/désactivation des objets
- Fait le mapping entre ID d'objet et implémentation

#### 4. Naming Service
- Permet de retrouver les objets par leur nom
- Annuaire distribué des objets CORBA

#### 5. IIOP (Internet Inter-ORB Protocol)
- Protocole de communication entre ORBs
- Permet l'interopérabilité sur Internet

### Architecture Client-Serveur CORBA

```
┌──────────┐                           ┌──────────┐
│  CLIENT  │                           │  SERVEUR │
│          │                           │          │
│ Référence│◄────────────────────────►│  Objet   │
│  Objet   │                           │  CORBA   │
│          │                           │          │
│  Stub    │                           │Squelette │
└────┬─────┘                           └────┬─────┘
     │                                      │
     │         ┌──────────────┐            │
     └────────►│     ORB      │◄───────────┘
               │              │
               │     IIOP     │
               └──────────────┘
```

### Références Objets

Les références objets sont essentielles pour invoquer des objets distants :

1. **Création** : Une référence est créée lors de l'instanciation d'un objet CORBA
2. **Unicité** : Chaque référence identifie un unique objet
3. **Opacité** : Le contenu est connu uniquement de l'ORB
4. **Obtention** : Via Naming Service, Factory, ou création directe

---

## 3. IDL - Interface Definition Language {#idl}

### Syntaxe de base

```idl
// Définition d'une interface
interface Account {
    // Attributs
    attribute string name;
    attribute long balance;
    readonly attribute string accountNumber;
    
    // Méthodes
    void deposit(in long amount);
    boolean withdraw(in long amount);
    string getDetails();
};
```

### Types de paramètres

- **`in`** : Paramètre en entrée (Client → Serveur)
- **`out`** : Paramètre en sortie (Serveur → Client)
- **`inout`** : Paramètre bidirectionnel (Client ↔ Serveur)

### Types de données IDL

**Types primitifs** :
- `short`, `long`, `long long`
- `float`, `double`
- `char`, `string`, `wstring`
- `boolean`
- `octet`

**Types complexes** :
- `struct` : Structures de données
- `sequence<type>` : Tableaux dynamiques
- `enum` : Énumérations
- `union` : Types union
- `any` : Type générique

### Exceptions IDL

```idl
// Exception personnalisée
exception InsufficientFunds {
    string reason;
    long shortfall;
};

interface Account {
    void withdraw(in long amount) raises (InsufficientFunds);
};
```

### Pattern Factory

Le client ne peut pas créer directement des objets distants. On utilise le pattern Factory :

```idl
interface Account {
    void deposit(in long amount);
    void destroy();
};

interface AccountFactory {
    Account createAccount(in string name, in long initialBalance);
    Account findAccount(in string accountNumber);
};
```

### Héritage IDL

```idl
// Toutes les interfaces héritent implicitement de Object
interface Factory {
    Object create();
};

// Héritage explicite
interface AdvancedFactory : Factory {
    Object createWithParams(in string type);
};
```

### IDL Mapping

Le mapping IDL traduit les définitions IDL vers un langage cible :

| IDL | C++ | Java |
|-----|-----|------|
| interface | class | interface + class |
| operation | method | method |
| long | long | int |
| string | char* | String |
| sequence | class | array/List |

---

## 4. Prise en main de CORBA {#prise-en-main}

### Étapes de développement

#### Étape 1 : Définir l'interface IDL

```idl
// HelloWorld.idl
module HelloApp {
    interface Hello {
        string sayHello();
        oneway void shutdown();
    };
};
```

#### Étape 2 : Compiler l'IDL

```bash
# Pour Java
idlj -fall HelloWorld.idl

# Pour C++
omniidl -bcxx HelloWorld.idl
```

Génère :
- **Stub** (côté client)
- **Squelette** (côté serveur)
- **Helpers** et **Holders**

#### Étape 3 : Implémenter le serveur

```java
// HelloImpl.java
import HelloApp.*;
import org.omg.CORBA.*;

class HelloImpl extends HelloPOA {
    private ORB orb;
    
    public void setORB(ORB orb_val) {
        orb = orb_val;
    }
    
    public String sayHello() {
        return "Hello World from CORBA!";
    }
    
    public void shutdown() {
        orb.shutdown(false);
    }
}
```

#### Étape 4 : Créer le serveur

```java
// HelloServer.java
import HelloApp.*;
import org.omg.CosNaming.*;
import org.omg.CORBA.*;
import org.omg.PortableServer.*;

public class HelloServer {
    public static void main(String args[]) {
        try {
            // Créer et initialiser l'ORB
            ORB orb = ORB.init(args, null);
            
            // Obtenir le POA
            POA rootpoa = POAHelper.narrow(
                orb.resolve_initial_references("RootPOA")
            );
            rootpoa.the_POAManager().activate();
            
            // Créer l'objet servant
            HelloImpl helloImpl = new HelloImpl();
            helloImpl.setORB(orb);
            
            // Obtenir la référence objet
            org.omg.CORBA.Object ref = rootpoa.servant_to_reference(helloImpl);
            Hello href = HelloHelper.narrow(ref);
            
            // Obtenir le Naming Service
            org.omg.CORBA.Object objRef = 
                orb.resolve_initial_references("NameService");
            NamingContextExt ncRef = NamingContextExtHelper.narrow(objRef);
            
            // Enregistrer l'objet dans le Naming Service
            String name = "Hello";
            NameComponent path[] = ncRef.to_name(name);
            ncRef.rebind(path, href);
            
            System.out.println("HelloServer ready and waiting...");
            
            // Attendre les invocations
            orb.run();
        } catch (Exception e) {
            System.err.println("ERROR: " + e);
            e.printStackTrace(System.out);
        }
    }
}
```

#### Étape 5 : Créer le client

```java
// HelloClient.java
import HelloApp.*;
import org.omg.CosNaming.*;
import org.omg.CORBA.*;

public class HelloClient {
    public static void main(String args[]) {
        try {
            // Créer et initialiser l'ORB
            ORB orb = ORB.init(args, null);
            
            // Obtenir le Naming Service
            org.omg.CORBA.Object objRef = 
                orb.resolve_initial_references("NameService");
            NamingContextExt ncRef = NamingContextExtHelper.narrow(objRef);
            
            // Résoudre la référence objet
            String name = "Hello";
            Hello helloRef = HelloHelper.narrow(ncRef.resolve_str(name));
            
            // Invoquer la méthode
            String result = helloRef.sayHello();
            System.out.println(result);
            
            // Fermer proprement
            helloRef.shutdown();
        } catch (Exception e) {
            System.out.println("ERROR : " + e);
            e.printStackTrace(System.out);
        }
    }
}
```

#### Étape 6 : Lancer l'application

```bash
# 1. Démarrer le Naming Service
orbd -ORBInitialPort 1050 -ORBInitialHost localhost &

# 2. Compiler
javac *.java HelloApp/*.java

# 3. Lancer le serveur
java HelloServer -ORBInitialPort 1050 -ORBInitialHost localhost &

# 4. Lancer le client
java HelloClient -ORBInitialPort 1050 -ORBInitialHost localhost
```

### Invocations : Statique vs Dynamique

#### Invocation Statique
- Utilise stub et squelette générés
- Compilation statique
- Plus rapide, moins flexible

#### Invocation Dynamique (DII/DSI)
- Pas de stub/squelette nécessaire
- Utilise `create_request`
- Plus lent mais très flexible
- Utile pour proxy, passerelles, outils génériques

```java
// Exemple DII
Request req = objectRef._request("sayHello");
req.invoke();
Any result = req.return_value();
String message = result.extract_string();
```

---

## 5. Applications potentielles {#applications}

### 1. Systèmes bancaires distribués
- Gestion de comptes multi-agences
- Transactions distribuées
- Synchronisation de données entre sites

### 2. Télécommunications
- Gestion de réseaux télécom
- Système de facturation distribué
- Routage d'appels intelligent

### 3. Systèmes médicaux
- Dossiers patients distribués
- Imagerie médicale partagée
- Système de rendez-vous inter-établissements

### 4. E-commerce
- Catalogue de produits distribué
- Gestion de stocks multi-sites
- Système de paiement sécurisé

### 5. Systèmes industriels
- Supervision d'usines
- SCADA (Supervisory Control And Data Acquisition)
- Contrôle de processus distribués

### 6. Applications d'entreprise
- ERP distribués
- Workflow inter-services
- Gestion documentaire

### 7. Simulation et calcul scientifique
- Calcul distribué haute performance
- Grilles de calcul
- Simulation multi-physiques

### 8. Internet des Objets (IoT)
- Coordination de capteurs distribués
- Systèmes domotiques
- Smart cities

---

## 6. Exercices pratiques {#exercices}

### Exercice 1 : Calculatrice distribuée

**Objectif** : Créer une calculatrice CORBA avec opérations de base

**Spécifications** :
```idl
module CalcApp {
    exception DivisionByZero {
        string reason;
    };
    
    interface Calculator {
        long add(in long a, in long b);
        long subtract(in long a, in long b);
        long multiply(in long a, in long b);
        double divide(in long a, in long b) raises (DivisionByZero);
        void clear();
        long getLastResult();
    };
    
    interface CalculatorFactory {
        Calculator createCalculator();
    };
};
```

**Tâches** :
1. Définir l'interface IDL complète
2. Compiler l'IDL pour votre langage cible
3. Implémenter le serveur avec gestion d'état
4. Créer un client avec menu interactif
5. Gérer correctement l'exception DivisionByZero
6. Tester avec plusieurs clients simultanés

**Bonus** :
- Ajouter des opérations avancées (puissance, racine carrée)
- Implémenter un historique des calculs
- Créer une interface graphique pour le client

---

### Exercice 2 : Système de gestion de bibliothèque

**Objectif** : Créer un système distribué de gestion de bibliothèque

**Spécifications** :
```idl
module LibraryApp {
    struct Book {
        string isbn;
        string title;
        string author;
        long year;
        boolean available;
    };
    
    typedef sequence<Book> BookList;
    
    exception BookNotFound {
        string isbn;
    };
    
    exception BookNotAvailable {
        string isbn;
        string dueDate;
    };
    
    interface Library {
        void addBook(in Book book);
        Book findBookByISBN(in string isbn) raises (BookNotFound);
        BookList findBooksByAuthor(in string author);
        BookList listAllBooks();
        void borrowBook(in string isbn, in string userName) 
            raises (BookNotFound, BookNotAvailable);
        void returnBook(in string isbn) raises (BookNotFound);
        long getBookCount();
    };
};
```

**Tâches** :
1. Implémenter l'interface complète
2. Gérer une collection de livres côté serveur
3. Implémenter toutes les exceptions
4. Créer un client avec menu complet
5. Assurer la persistance des données (fichier ou base)
6. Gérer la concurrence d'accès

**Bonus** :
- Ajouter un système de réservation
- Implémenter des amendes pour retard
- Créer des statistiques d'emprunt
- Système de recommandation

---

### Exercice 3 : Chat distribué

**Objectif** : Créer une application de chat multi-utilisateurs

**Spécifications** :
```idl
module ChatApp {
    struct Message {
        string sender;
        string content;
        string timestamp;
    };
    
    typedef sequence<Message> MessageHistory;
    typedef sequence<string> UserList;
    
    interface ChatClient {
        void receiveMessage(in Message msg);
        void notifyUserJoined(in string userName);
        void notifyUserLeft(in string userName);
    };
    
    interface ChatRoom {
        void join(in string userName, in ChatClient client);
        void leave(in string userName);
        void sendMessage(in string userName, in string content);
        MessageHistory getHistory(in long count);
        UserList getActiveUsers();
    };
    
    interface ChatServer {
        ChatRoom createRoom(in string roomName);
        ChatRoom joinRoom(in string roomName);
        sequence<string> listRooms();
    };
};
```

**Tâches** :
1. Implémenter le modèle de callback (ChatClient)
2. Gérer plusieurs salons de discussion
3. Implémenter la diffusion des messages
4. Créer un client avec interface console
5. Gérer la déconnexion propre des clients
6. Conserver l'historique des messages

**Bonus** :
- Messages privés entre utilisateurs
- Salons protégés par mot de passe
- Transfert de fichiers
- Interface graphique (Swing, JavaFX)
- Notification de "en train d'écrire..."

---

## 7. Projet avancé : Plateforme de trading financier distribuée {#projet}

### Vue d'ensemble

Créer une plateforme complète de trading financier permettant à plusieurs courtiers de passer des ordres sur différents marchés boursiers distribués géographiquement.

### Architecture du système

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Client    │     │   Client    │     │   Client    │
│   Trader    │     │   Trader    │     │   Trader    │
└──────┬──────┘     └──────┬──────┘     └──────┬──────┘
       │                   │                   │
       └───────────────────┼───────────────────┘
                           │
              ┌────────────┴────────────┐
              │   Trading Platform      │
              │   (Load Balancer)       │
              └────────────┬────────────┘
                           │
       ┌───────────────────┼───────────────────┐
       │                   │                   │
┌──────┴──────┐     ┌──────┴──────┐     ┌──────┴──────┐
│   Market    │     │   Market    │     │   Market    │
│    NYSE     │     │  NASDAQ     │     │  EURONEXT   │
└──────┬──────┘     └──────┬──────┘     └──────┬──────┘
       │                   │                   │
       └───────────────────┼───────────────────┘
                           │
                  ┌────────┴────────┐
                  │  Market Data    │
                  │    Service      │
                  └─────────────────┘
```

### Interfaces IDL

```idl
module TradingApp {
    // Types de base
    enum OrderType { BUY, SELL };
    enum OrderStatus { PENDING, PARTIALLY_FILLED, FILLED, CANCELLED, REJECTED };
    enum MarketType { NYSE, NASDAQ, EURONEXT, LSE };
    
    struct Stock {
        string symbol;
        string name;
        MarketType market;
        double lastPrice;
        long volume;
        double dayChange;
        double dayChangePercent;
    };
    
    struct Order {
        string orderId;
        string traderId;
        string stockSymbol;
        OrderType type;
        long quantity;
        double price;
        OrderStatus status;
        string timestamp;
        long filledQuantity;
    };
    
    struct Position {
        string stockSymbol;
        long quantity;
        double averagePrice;
        double currentValue;
        double profitLoss;
        double profitLossPercent;
    };
    
    struct AccountInfo {
        string traderId;
        double balance;
        double totalValue;
        double buyingPower;
        sequence<Position> positions;
    };
    
    typedef sequence<Stock> StockList;
    typedef sequence<Order> OrderList;
    typedef sequence<Position> PositionList;
    
    // Exceptions
    exception InsufficientFunds {
        string traderId;
        double required;
        double available;
    };
    
    exception InvalidStock {
        string symbol;
        string reason;
    };
    
    exception InvalidOrder {
        string reason;
    };
    
    exception MarketClosed {
        MarketType market;
        string openingTime;
    };
    
    exception OrderNotFound {
        string orderId;
    };
    
    // Interface pour les callbacks client
    interface TradingClient {
        void onOrderUpdate(in Order order);
        void onMarketDataUpdate(in Stock stock);
        void onAccountUpdate(in AccountInfo account);
        void onAlert(in string message);
    };
    
    // Interface du marché boursier
    interface StockMarket {
        readonly attribute MarketType marketType;
        readonly attribute boolean isOpen;
        readonly attribute string tradingHours;
        
        Stock getStockInfo(in string symbol) raises (InvalidStock);
        StockList listAllStocks();
        StockList searchStocks(in string query);
        double getCurrentPrice(in string symbol) raises (InvalidStock);
        
        Order placeOrder(in Order order) 
            raises (InvalidStock, InvalidOrder, MarketClosed, InsufficientFunds);
        void cancelOrder(in string orderId) raises (OrderNotFound);
        Order getOrderStatus(in string orderId) raises (OrderNotFound);
        OrderList getOrderHistory(in string traderId);
        
        void subscribe(in TradingClient client, in string symbol);
        void unsubscribe(in TradingClient client, in string symbol);
    };
    
    // Interface de la plateforme de trading
    interface TradingPlatform {
        // Authentification
        string login(in string username, in string password);
        void logout(in string traderId);
        
        // Gestion de compte
        AccountInfo getAccountInfo(in string traderId);
        PositionList getPositions(in string traderId);
        void deposit(in string traderId, in double amount);
        void withdraw(in string traderId, in double amount) raises (InsufficientFunds);
        
        // Accès aux marchés
        StockMarket getMarket(in MarketType market);
        sequence<MarketType> getAvailableMarkets();
        
        // Ordres multi-marchés
        Order placeSmartOrder(in string traderId, in Order order)
            raises (InvalidStock, InvalidOrder, InsufficientFunds);
        OrderList getAllOrders(in string traderId);
        
        // Données de marché agrégées
        Stock findBestPrice(in string symbol);
        StockList getTopGainers(in long count);
        StockList getTopLosers(in long count);
        StockList getMostActive(in long count);
        
        // Watchlist
        void addToWatchlist(in string traderId, in string symbol);
        void removeFromWatchlist(in string traderId, in string symbol);
        StockList getWatchlist(in string traderId);
    };
    
    // Service de données de marché en temps réel
    interface MarketDataService {
        void startStreaming(in TradingClient client);
        void stopStreaming(in TradingClient client);
        Stock getSnapshot(in string symbol) raises (InvalidStock);
        sequence<Stock> getSnapshots(in sequence<string> symbols);
    };
    
    // Interface d'analyse
    interface AnalyticsService {
        struct TechnicalIndicators {
            double sma20;  // Simple Moving Average 20
            double sma50;
            double rsi;    // Relative Strength Index
            double macd;   // MACD
            double volume;
        };
        
        struct PerformanceMetrics {
            double totalReturn;
            double dailyReturn;
            double sharpeRatio;
            double maxDrawdown;
            long totalTrades;
            long winningTrades;
        };
        
        TechnicalIndicators calculateIndicators(in string symbol);
        PerformanceMetrics getPerformanceMetrics(in string traderId);
        sequence<Stock> getRecommendations(in string traderId);
    };
    
    // Factory pour créer les composants
    interface TradingFactory {
        TradingPlatform createPlatform();
        StockMarket createMarket(in MarketType type);
        MarketDataService createMarketDataService();
        AnalyticsService createAnalyticsService();
    };
};
```

### Fonctionnalités à implémenter

#### Phase 1 : Infrastructure de base
1. **Serveur de noms centralisé**
   - Configuration du Naming Service
   - Enregistrement des services

2. **Marchés boursiers multiples**
   - Implémenter 3 marchés (NYSE, NASDAQ, EURONEXT)
   - Chaque marché comme serveur CORBA indépendant
   - Données de stocks simulées ou réelles (API externe)

3. **Gestion des ordres**
   - File d'ordres (order book)
   - Matching engine basique
   - Gestion des états d'ordres

#### Phase 2 : Plateforme de trading
1. **Authentification et gestion de comptes**
   - Login/logout sécurisé
   - Gestion de portefeuilles
   - Calcul de positions

2. **Routage intelligent des ordres**
   - Recherche du meilleur prix
   - Load balancing entre marchés
   - Gestion des échecs et retry

3. **Interface client**
   - Dashboard de trading
   - Graphiques de prix
   - Gestion de watchlist

#### Phase 3 : Temps réel et avancé
1. **Market Data Service**
   - Streaming de données en temps réel
   - Callbacks asynchrones
   - Gestion de milliers de souscriptions

2. **Analytics Service**
   - Calcul d'indicateurs techniques
   - Métriques de performance
   - Système de recommandation

3. **Fonctionnalités avancées**
   - Ordres conditionnels (stop-loss, take-profit)
   - Trading algorithmique
   - Backtesting de stratégies

#### Phase 4 : Production et scalabilité
1. **Tolérance aux pannes**
   - Réplication des serveurs
   - Failover automatique
   - Persistance des données

2. **Performance**
   - Pool de connexions
   - Cache distribué
   - Optimisation des appels CORBA

3. **Monitoring**
   - Logs distribués
   - Métriques de performance
   - Alertes système

### Spécifications techniques

#### Technologies recommandées
- **Langage** : Java ou C++
- **ORB** : Java ORB (JacORB) ou omniORB (C++)
- **Base de données** : PostgreSQL pour persistance
- **Cache** : Redis pour données temps réel
- **Frontend** : JavaFX, Swing ou web (WebSocket bridge)

#### Architecture de déploiement
```
Production:
- 3 serveurs de marché (répliqués)
- 2 serveurs de plateforme (load balanced)
- 1 serveur de market data
- 1 serveur d'analytics
- 1 base de données maître + réplica
- 1 cache Redis
```

#### Défis techniques à résoudre

1. **Concurrence**
   - Accès concurrent aux order books
   - Synchronisation des positions
   - Transactions distribuées

2. **Performance**
   - Latence < 100ms pour orders
   - Capacité : 10,000 ordres/seconde
   - Streaming temps réel pour 1,000+ clients

3. **Fiabilité**
   - Aucune perte d'ordre
   - Cohérence des données
   - Récupération après crash

4. **Sécurité**
   - Authentification forte
   - Chiffrement des communications
   - Audit trail complet

### Livrables attendus

1. **Code source complet**
   - Interfaces IDL
   - Implémentations serveurs
   - Clients (console et GUI)
   - Tests unitaires et d'intégration

2. **Documentation**
   - Architecture détaillée
   - Guide d'installation
   - Manuel utilisateur
   - Documentation API

3. **Démonstration**
   - Scénarios de test
   - Benchmarks de performance
   - Vidéo de démonstration

4. **Rapport technique**
   - Choix d'architecture
   - Problèmes rencontrés et solutions
   - Optimisations réalisées
   - Perspectives d'amélioration

### Critères d'évaluation

- **Fonctionnalité** (30%) : Toutes les features implémentées
- **Architecture** (25%) : Design CORBA propre et extensible
- **Performance** (20%) : Respect des contraintes de latence
- **Qualité du code** (15%) : Lisibilité, tests, documentation
- **Innovation** (10%) : Fonctionnalités avancées

### Extensions possibles

1. **Machine Learning**
   - Prédiction de prix
   - Détection d'anomalies
   - Recommandation personnalisée

2. **Blockchain**
   - Settlement via blockchain
   - Tokenisation d'actifs
   - Smart contracts

3. **Multi-asset**
   - Support Crypto, Forex, Commodities
   - Conversion de devises
   - Portfolio diversifié

4. **Social Trading**
   - Copie de stratégies
   - Classements de traders
   - API publique

---

## Conclusion

CORBA reste une technologie importante pour comprendre les systèmes distribués, même si elle est progressivement remplacée par des solutions plus modernes (gRPC, REST, GraphQL). Les concepts de CORBA (IDL, stub/skeleton, naming service, invocation distante) sont fondamentaux pour la compréhension et l'appropriation des protocoles nouveaux.
