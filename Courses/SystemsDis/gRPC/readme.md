# TP : Introduction à gRPC et Applications Pratiques

## Objectifs du TP
- Comprendre les concepts fondamentaux de gRPC
- Identifier les cas d'usage appropriés pour gRPC
- Maîtriser la définition de services avec Protocol Buffers
- Implémenter des services gRPC en pratique
- Comprendre l'évolution de RPC vers gRPC

---

## 1. Introduction à gRPC

### 1.1 Qu'est-ce que gRPC ?

**gRPC** (gRPC Remote Procedure Call) est un framework open-source développé par Google pour faciliter la communication entre services distribués. Il permet à des applications de s'appeler mutuellement comme si elles étaient des fonctions locales, même si elles s'exécutent sur des machines différentes.

**Caractéristiques principales :**
- **Protocol Buffers (protobuf)** : Format de sérialisation binaire compact et performant
- **HTTP/2** : Transport moderne avec multiplexage, streaming bidirectionnel
- **Multi-langage** : Support de nombreux langages (C++, Java, Python, Go, Node.js, etc.)
- **Génération automatique de code** : À partir des fichiers `.proto`
- **Types de communication** : Unaire, streaming serveur, streaming client, streaming bidirectionnel

### 1.2 Pourquoi utiliser gRPC ?

**Avantages :**
- **Performance** : Sérialisation binaire plus rapide que JSON/XML
- **Contrat strict** : Le fichier `.proto` définit clairement l'API
- **Streaming** : Support natif du streaming bidirectionnel
- **Interopérabilité** : Communication facile entre différents langages
- **Évolutivité** : Ajout de nouveaux champs sans casser la compatibilité

**Cas d'usage recommandés :**
1. **Microservices** : Communication inter-services dans une architecture distribuée
2. **Applications temps réel** : Chat, notifications, données de capteurs
3. **Applications mobiles** : Économie de batterie et de bande passante
4. **IoT** : Communication efficace entre appareils à ressources limitées
5. **APIs internes** : Entre services backend d'une même organisation

**Quand NE PAS utiliser gRPC :**
- APIs publiques nécessitant une compatibilité navigateur directe
- Projets simples où REST/JSON suffit
- Équipes sans expertise en Protocol Buffers
- Débogage facile requis (REST est plus lisible)

### 1.3 Architecture gRPC

```
┌─────────────┐                           ┌─────────────┐
│   Client    │                           │   Serveur   │
│             │                           │             │
│  ┌────────┐ │   Request (protobuf)     │  ┌────────┐ │
│  │  Stub  │─┼──────────────────────────┼─▶│Service │ │
│  └────────┘ │                           │  └────────┘ │
│             │   Response (protobuf)     │             │
│             │◀──────────────────────────┼─────────────│
└─────────────┘        HTTP/2             └─────────────┘
```

---

## 2. De RPC à gRPC : Évolution historique

### 2.1 Qu'est-ce que rpcbind ?

**rpcbind** (anciennement portmapper) est un service utilisé dans les systèmes Unix/Linux pour faciliter les appels de procédures distantes (RPC) traditionnels, notamment avec **Sun RPC** (ONC RPC).

**Fonctionnement de rpcbind :**
- Écoute sur le port 111
- Maintient une table de correspondance : (programme, version, protocole) → port
- Les clients contactent rpcbind pour découvrir sur quel port un service RPC écoute
- Utilisé par NFS, NIS et d'autres services Unix traditionnels

**Exemple de flux avec rpcbind :**
```
1. Serveur démarre et enregistre son service auprès de rpcbind
2. Client contacte rpcbind : "Où est le service NFS ?"
3. rpcbind répond : "Il écoute sur le port 2049"
4. Client se connecte directement au port 2049 pour communiquer
```

### 2.2 Différences entre rpcbind/Sun RPC et gRPC

| Aspect | Sun RPC + rpcbind | gRPC |
|--------|-------------------|------|
| **Époque** | Années 1980 | 2015+ |
| **Format** | XDR (External Data Representation) | Protocol Buffers |
| **Transport** | TCP/UDP | HTTP/2 |
| **Découverte** | rpcbind (portmapper) | Service discovery externe (Consul, etc.) |
| **Streaming** | Non supporté | Natif (4 modes) |
| **Langages** | Principalement C | Multi-langage moderne |
| **Définition** | Fichiers `.x` (RPC Language) | Fichiers `.proto` |
| **Sécurité** | Limitée (AUTH_SYS, AUTH_DES) | TLS intégré, authentification moderne |
| **Usage moderne** | Systèmes legacy Unix | Microservices cloud-native |

### 2.3 Lien conceptuel

gRPC est une **évolution moderne** des concepts RPC traditionnels :
- **Même objectif** : Appeler des fonctions distantes comme des fonctions locales
- **Meilleure performance** : Protocol Buffers vs XDR
- **Transport moderne** : HTTP/2 vs TCP brut
- **Meilleure intégration** : Cloud-native, conteneurs, Kubernetes
- **Pas de portmapper** : gRPC utilise des ports fixes ou service discovery externe

**En résumé :** Si rpcbind/Sun RPC était la solution des années 80-90 pour Unix, gRPC est la solution moderne pour les architectures distribuées cloud-native.

---

## 3. Protocol Buffers : Le langage de gRPC

### 3.1 Structure d'un fichier .proto

```protobuf
syntax = "proto3";

package monservice;

// Définition d'un message (structure de données)
message Utilisateur {
  int32 id = 1;
  string nom = 2;
  string email = 3;
  bool actif = 4;
}

// Définition d'un service avec ses méthodes RPC
service GestionUtilisateurs {
  // RPC unaire : une requête, une réponse
  rpc ObtenirUtilisateur(RequeteUtilisateur) returns (Utilisateur);
  
  // RPC streaming serveur : une requête, plusieurs réponses
  rpc ListerUtilisateurs(RequeteVide) returns (stream Utilisateur);
  
  // RPC streaming client : plusieurs requêtes, une réponse
  rpc AjouterUtilisateurs(stream Utilisateur) returns (ReponseAjout);
  
  // RPC streaming bidirectionnel
  rpc DiscuterAvecUtilisateurs(stream Message) returns (stream Message);
}

message RequeteUtilisateur {
  int32 id = 1;
}

message RequeteVide {}

message ReponseAjout {
  int32 nombre_ajoutes = 1;
}

message Message {
  string contenu = 1;
  int64 timestamp = 2;
}
```

### 3.2 Types de RPC dans gRPC

1. **Unaire** : Requête → Réponse (comme une fonction classique)
2. **Streaming serveur** : Requête → Stream de réponses
3. **Streaming client** : Stream de requêtes → Réponse
4. **Streaming bidirectionnel** : Stream de requêtes ↔ Stream de réponses

---

## 4. Installation et Configuration

### 4.1 Installation des outils (Python)

```bash
# Installer gRPC et les outils
pip install grpcio grpcio-tools

# Vérifier l'installation
python -m grpc_tools.protoc --version
```

### 4.2 Génération du code depuis .proto

```bash
# Générer les fichiers Python à partir du .proto
python -m grpc_tools.protoc \
  -I. \
  --python_out=. \
  --grpc_python_out=. \
  mon_service.proto
```

Cela génère :
- `mon_service_pb2.py` : Classes des messages
- `mon_service_pb2_grpc.py` : Classes des services (stub client et servicer serveur)

---

## Exercice 1 : Calculatrice gRPC Simple

### Objectif
Créer un service gRPC de calculatrice avec opérations de base (addition, soustraction, multiplication, division).

### Étapes

1. **Créer le fichier `calculatrice.proto`**

```protobuf
syntax = "proto3";

package calculatrice;

service Calculatrice {
  rpc Addition(OperationRequest) returns (OperationResponse);
  rpc Soustraction(OperationRequest) returns (OperationResponse);
  rpc Multiplication(OperationRequest) returns (OperationResponse);
  rpc Division(OperationRequest) returns (OperationResponse);
}

message OperationRequest {
  double a = 1;
  double b = 2;
}

message OperationResponse {
  double resultat = 1;
  string message = 2;
}
```

2. **Générer le code**

```bash
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. calculatrice.proto
```

3. **Implémenter le serveur (`serveur_calculatrice.py`)**

```python
import grpc
from concurrent import futures
import calculatrice_pb2
import calculatrice_pb2_grpc

class CalculatriceServicer(calculatrice_pb2_grpc.CalculatriceServicer):
    def Addition(self, request, context):
        resultat = request.a + request.b
        return calculatrice_pb2.OperationResponse(
            resultat=resultat,
            message=f"{request.a} + {request.b} = {resultat}"
        )
    
    def Soustraction(self, request, context):
        resultat = request.a - request.b
        return calculatrice_pb2.OperationResponse(
            resultat=resultat,
            message=f"{request.a} - {request.b} = {resultat}"
        )
    
    def Multiplication(self, request, context):
        resultat = request.a * request.b
        return calculatrice_pb2.OperationResponse(
            resultat=resultat,
            message=f"{request.a} * {request.b} = {resultat}"
        )
    
    def Division(self, request, context):
        if request.b == 0:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details("Division par zéro impossible")
            return calculatrice_pb2.OperationResponse()
        
        resultat = request.a / request.b
        return calculatrice_pb2.OperationResponse(
            resultat=resultat,
            message=f"{request.a} / {request.b} = {resultat}"
        )

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    calculatrice_pb2_grpc.add_CalculatriceServicer_to_server(
        CalculatriceServicer(), server
    )
    server.add_insecure_port('[::]:50051')
    print("Serveur démarré sur le port 50051")
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
```

4. **Implémenter le client (`client_calculatrice.py`)**

```python
import grpc
import calculatrice_pb2
import calculatrice_pb2_grpc

def run():
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = calculatrice_pb2_grpc.CalculatriceStub(channel)
        
        # Test addition
        response = stub.Addition(calculatrice_pb2.OperationRequest(a=10, b=5))
        print(response.message)
        
        # Test division
        response = stub.Division(calculatrice_pb2.OperationRequest(a=20, b=4))
        print(response.message)
        
        # Test division par zéro
        try:
            response = stub.Division(calculatrice_pb2.OperationRequest(a=10, b=0))
        except grpc.RpcError as e:
            print(f"Erreur: {e.details()}")

if __name__ == '__main__':
    run()
```

### Questions
1. Que se passe-t-il si vous envoyez des nombres négatifs ?
2. Comment pourriez-vous ajouter une opération "puissance" ?
3. Quelle est la différence entre lever une exception Python et utiliser `context.set_code()` ?

---

## Exercice 2 : Service de Streaming - Générateur de Nombres

### Objectif
Créer un service qui génère une séquence de nombres (streaming serveur) et un service qui calcule la somme d'une séquence (streaming client).

### Fichier `nombres.proto`

```protobuf
syntax = "proto3";

package nombres;

service GenerateurNombres {
  // Streaming serveur : génère N nombres
  rpc GenererSequence(RequeteSequence) returns (stream Nombre);
  
  // Streaming client : calcule la somme
  rpc CalculerSomme(stream Nombre) returns (ReponseSomme);
}

message RequeteSequence {
  int32 debut = 1;
  int32 fin = 2;
  int32 pas = 3;
}

message Nombre {
  int32 valeur = 1;
}

message ReponseSomme {
  int32 somme = 1;
  int32 nombre_elements = 2;
}
```

### Implémentation serveur

```python
import grpc
from concurrent import futures
import time
import nombres_pb2
import nombres_pb2_grpc

class GenerateurNombresServicer(nombres_pb2_grpc.GenerateurNombresServicer):
    def GenererSequence(self, request, context):
        """Génère une séquence de nombres avec streaming"""
        for i in range(request.debut, request.fin + 1, request.pas):
            yield nombres_pb2.Nombre(valeur=i)
            time.sleep(0.5)  # Simule un traitement
    
    def CalculerSomme(self, request_iterator, context):
        """Reçoit un stream de nombres et retourne leur somme"""
        somme = 0
        count = 0
        for nombre in request_iterator:
            somme += nombre.valeur
            count += 1
        return nombres_pb2.ReponseSomme(somme=somme, nombre_elements=count)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    nombres_pb2_grpc.add_GenerateurNombresServicer_to_server(
        GenerateurNombresServicer(), server
    )
    server.add_insecure_port('[::]:50052')
    print("Serveur démarré sur le port 50052")
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
```

### Implémentation client

```python
import grpc
import nombres_pb2
import nombres_pb2_grpc

def test_streaming_serveur():
    """Teste le streaming serveur"""
    with grpc.insecure_channel('localhost:50052') as channel:
        stub = nombres_pb2_grpc.GenerateurNombresStub(channel)
        
        print("=== Streaming Serveur ===")
        requete = nombres_pb2.RequeteSequence(debut=1, fin=10, pas=2)
        
        for nombre in stub.GenererSequence(requete):
            print(f"Reçu: {nombre.valeur}")

def test_streaming_client():
    """Teste le streaming client"""
    with grpc.insecure_channel('localhost:50052') as channel:
        stub = nombres_pb2_grpc.GenerateurNombresStub(channel)
        
        print("\n=== Streaming Client ===")
        
        def generer_nombres():
            for i in [1, 2, 3, 4, 5, 10, 20]:
                print(f"Envoi: {i}")
                yield nombres_pb2.Nombre(valeur=i)
        
        response = stub.CalculerSomme(generer_nombres())
        print(f"Somme: {response.somme}, Éléments: {response.nombre_elements}")

if __name__ == '__main__':
    test_streaming_serveur()
    test_streaming_client()
```

### Questions
1. Pourquoi utiliser `yield` dans le streaming serveur ?
2. Comment gérer un client qui se déconnecte pendant le streaming ?
3. Quel est l'avantage du streaming par rapport à envoyer tout en une fois ?

---

## Exercice 3 : Chat Bidirectionnel

### Objectif
Créer un service de chat temps réel avec streaming bidirectionnel où plusieurs clients peuvent échanger des messages.

### Fichier `chat.proto`

```protobuf
syntax = "proto3";

package chat;

service ChatService {
  rpc Discuter(stream MessageChat) returns (stream MessageChat);
}

message MessageChat {
  string pseudo = 1;
  string contenu = 2;
  int64 timestamp = 3;
}
```

### Implémentation serveur

```python
import grpc
from concurrent import futures
import time
import threading
import chat_pb2
import chat_pb2_grpc

class ChatServicer(chat_pb2_grpc.ChatServiceServicer):
    def __init__(self):
        self.clients = []
        self.lock = threading.Lock()
    
    def Discuter(self, request_iterator, context):
        """Gère le streaming bidirectionnel pour le chat"""
        # File d'attente pour ce client
        queue = []
        
        # Ajouter le client à la liste
        with self.lock:
            self.clients.append(queue)
        
        def cleanup():
            with self.lock:
                self.clients.remove(queue)
        
        context.add_callback(cleanup)
        
        # Thread pour recevoir les messages du client
        def recevoir_messages():
            try:
                for message in request_iterator:
                    # Broadcast à tous les clients
                    with self.lock:
                        for client_queue in self.clients:
                            client_queue.append(message)
            except:
                pass
        
        thread = threading.Thread(target=recevoir_messages)
        thread.daemon = True
        thread.start()
        
        # Envoyer les messages à ce client
        try:
            while context.is_active():
                while queue:
                    message = queue.pop(0)
                    yield message
                time.sleep(0.1)
        except:
            pass

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    chat_pb2_grpc.add_ChatServiceServicer_to_server(ChatServicer(), server)
    server.add_insecure_port('[::]:50053')
    print("Serveur de chat démarré sur le port 50053")
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
```

### Implémentation client

```python
import grpc
import chat_pb2
import chat_pb2_grpc
import threading
import time
import sys

def run(pseudo):
    with grpc.insecure_channel('localhost:50053') as channel:
        stub = chat_pb2_grpc.ChatServiceStub(channel)
        
        def generer_messages():
            while True:
                texte = input()
                if texte.lower() == 'quit':
                    break
                yield chat_pb2.MessageChat(
                    pseudo=pseudo,
                    contenu=texte,
                    timestamp=int(time.time())
                )
        
        def recevoir_messages(responses):
            try:
                for message in responses:
                    if message.pseudo != pseudo:
                        print(f"\n[{message.pseudo}]: {message.contenu}")
                        print(f"{pseudo}> ", end='', flush=True)
            except:
                pass
        
        responses = stub.Discuter(generer_messages())
        
        thread = threading.Thread(target=recevoir_messages, args=(responses,))
        thread.daemon = True
        thread.start()
        
        print(f"Connecté en tant que {pseudo}. Tapez 'quit' pour quitter.")
        print(f"{pseudo}> ", end='', flush=True)
        
        thread.join()

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python client_chat.py <pseudo>")
        sys.exit(1)
    run(sys.argv[1])
```

### Questions
1. Comment gérez-vous la synchronisation entre threads ?
2. Que se passe-t-il si un client envoie 1000 messages par seconde ?
3. Comment ajouteriez-vous des salons de discussion séparés ?

---

## Exercice 4 : Système de Gestion de Tâches avec Métadonnées

### Objectif
Créer un service de gestion de tâches avec authentification via métadonnées gRPC.

### Fichier `taches.proto`

```protobuf
syntax = "proto3";

package taches;

service GestionTaches {
  rpc CreerTache(Tache) returns (ReponseCreation);
  rpc ObtenirTaches(RequeteUtilisateur) returns (ListeTaches);
  rpc MarquerComplete(RequeteMiseAJour) returns (Tache);
  rpc SupprimerTache(RequeteSuppression) returns (ReponseOperation);
}

message Tache {
  string id = 1;
  string titre = 2;
  string description = 3;
  bool complete = 4;
  int64 date_creation = 5;
  string utilisateur_id = 6;
}

message RequeteUtilisateur {
  string utilisateur_id = 1;
}

message ReponseCreation {
  bool succes = 1;
  string message = 2;
  Tache tache = 3;
}

message ListeTaches {
  repeated Tache taches = 1;
}

message RequeteMiseAJour {
  string id = 1;
}

message RequeteSuppression {
  string id = 1;
}

message ReponseOperation {
  bool succes = 1;
  string message = 2;
}
```

### Implémentation avec authentification

```python
import grpc
from concurrent import futures
import uuid
import time
import taches_pb2
import taches_pb2_grpc

# Base de données simulée
taches_db = {}

def verifier_authentification(context):
    """Vérifie le token d'authentification dans les métadonnées"""
    metadata = dict(context.invocation_metadata())
    token = metadata.get('authorization', '')
    
    if token != 'Bearer secret-token-123':
        context.abort(grpc.StatusCode.UNAUTHENTICATED, 'Token invalide')
    
    return metadata.get('user-id', 'anonymous')

class GestionTachesServicer(taches_pb2_grpc.GestionTachesServicer):
    def CreerTache(self, request, context):
        user_id = verifier_authentification(context)
        
        tache_id = str(uuid.uuid4())
        tache = taches_pb2.Tache(
            id=tache_id,
            titre=request.titre,
            description=request.description,
            complete=False,
            date_creation=int(time.time()),
            utilisateur_id=user_id
        )
        
        taches_db[tache_id] = tache
        
        return taches_pb2.ReponseCreation(
            succes=True,
            message="Tâche créée avec succès",
            tache=tache
        )
    
    def ObtenirTaches(self, request, context):
        user_id = verifier_authentification(context)
        
        taches_utilisateur = [
            tache for tache in taches_db.values()
            if tache.utilisateur_id == user_id
        ]
        
        return taches_pb2.ListeTaches(taches=taches_utilisateur)
    
    def MarquerComplete(self, request, context):
        user_id = verifier_authentification(context)
        
        if request.id not in taches_db:
            context.abort(grpc.StatusCode.NOT_FOUND, 'Tâche non trouvée')
        
        tache = taches_db[request.id]
        
        if tache.utilisateur_id != user_id:
            context.abort(grpc.StatusCode.PERMISSION_DENIED, 'Accès refusé')
        
        tache.complete = True
        return tache
    
    def SupprimerTache(self, request, context):
        user_id = verifier_authentification(context)
        
        if request.id not in taches_db:
            context.abort(grpc.StatusCode.NOT_FOUND, 'Tâche non trouvée')
        
        tache = taches_db[request.id]
        
        if tache.utilisateur_id != user_id:
            context.abort(grpc.StatusCode.PERMISSION_DENIED, 'Accès refusé')
        
        del taches_db[request.id]
        
        return taches_pb2.ReponseOperation(
            succes=True,
            message="Tâche supprimée"
        )

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    taches_pb2_grpc.add_GestionTachesServicer_to_server(
        GestionTachesServicer(), server
    )
    server.add_insecure_port('[::]:50054')
    print("Serveur de gestion de tâches démarré sur le port 50054")
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
```

### Client avec métadonnées

```python
import grpc
import taches_pb2
import taches_pb2_grpc

def run():
    with grpc.insecure_channel('localhost:50054') as channel:
        stub = taches_pb2_grpc.GestionTachesStub(channel)
        
        # Métadonnées d'authentification
        metadata = [
            ('authorization', 'Bearer secret-token-123'),
            ('user-id', 'user-001')
        ]
        
        # Créer une tâche
        tache = taches_pb2.Tache(
            titre="Apprendre gRPC",
            description="Compléter tous les exercices du TP"
        )
        
        response = stub.CreerTache(tache, metadata=metadata)
        print(f"Tâche créée: {response.tache.id}")
        
        # Récupérer les tâches
        liste = stub.ObtenirTaches(
            taches_pb2.RequeteUtilisateur(utilisateur_id='user-001'),
            metadata=metadata
        )
        
        print(f"\nNombre de tâches: {len(liste.taches)}")
        for t in liste.taches:
            print(f"- {t.titre} ({'✓' if t.complete else '✗'})")
        
        # Marquer comme complete
        if liste.taches:
            tache_id = liste.taches[0].id
            tache_maj = stub.MarquerComplete(
                taches_pb2.RequeteMiseAJour(id=tache_id),
                metadata=metadata
            )
            print(f"\nTâche '{tache_maj.titre}' marquée comme complète")

if __name__ == '__main__':
    run()
```

### Questions
1. Comment implémenteriez-vous un système de tokens JWT réel ?
2. Que se passe-t-il si deux clients modifient la même tâche simultanément ?
3. Comment ajouteriez-vous du TLS pour sécuriser les communications ?

---

## Projet Final : Plateforme de Monitoring IoT

### Description
Créez une plateforme complète de monitoring pour capteurs IoT utilisant tous les concepts gRPC appris.

### Fonctionnalités requises

1. **Enregistrement des capteurs** (RPC unaire)
   - Les capteurs s'enregistrent avec un ID, type, et localisation

2. **Envoi de données** (Streaming client)
   - Les capteurs envoient continuellement des mesures (température, humidité, etc.)

3. **Monitoring en temps réel** (Streaming serveur)
   - Les clients peuvent s'abonner aux données d'un capteur spécifique

4. **Alertes bidirectionnelles** (Streaming bidirectionnel)
   - Le serveur envoie des alertes quand des seuils sont dépassés
   - Les clients peuvent modifier les seuils dynamiquement

5. **Statistiques** (RPC unaire)
   - Obtenir min/max/moyenne sur une période

### Spécifications techniques

**Fichier `iot.proto`** (à compléter)

```protobuf
syntax = "proto3";

package iot;

service PlatformeIoT {
  // À COMPLÉTER : définir les 5 méthodes RPC nécessaires
  // ...
}

message Capteur {
  string id = 1;
  string type = 2;  // temperature, humidite, pression
  string localisation = 3;
  int64 date_enregistrement = 4;
}

message Mesure {
  string capteur_id = 1;
  double valeur = 2;
  int64 timestamp = 3;
  string unite = 4;
}

// À COMPLÉTER : définir les autres messages nécessaires
// ...
```

### Architecture suggérée

```
┌──────────────┐         ┌──────────────────┐         ┌─────────────┐
│  Capteur 1   │────────▶│                  │◀────────│  Client 1   │
│  (Streaming) │         │   Serveur gRPC   │         │ (Monitoring
