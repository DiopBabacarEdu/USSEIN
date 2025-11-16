# Guide Complet : REST et HTTP

## Table des matières
1. [Introduction à REST](#introduction-à-rest)
2. [Les Méthodes HTTP/REST](#les-méthodes-httprest)
3. [Codes de Statut HTTP](#codes-de-statut-http)
4. [Formats de Données](#formats-de-données)
5. [Outils pour Pratiquer REST](#outils-pour-pratiquer-rest)
6. [REST et Sockets (Couche Transport)](#rest-et-sockets-couche-transport)
7. [Architecture Client-Serveur Avancée](#architecture-client-serveur-avancée)

---

## Introduction à REST

**REST (Representational State Transfer)** est un style d'architecture pour les systèmes distribués basé sur HTTP. Il repose sur cinq principes fondamentaux :

- **Sans état (Stateless)** : Chaque requête contient toutes les informations nécessaires
- **Client-Serveur** : Séparation des préoccupations
- **Cacheable** : Les réponses peuvent être mises en cache
- **Interface uniforme** : Utilisation standardisée des méthodes HTTP
- **Système en couches** : Architecture modulaire

---

## Les Méthodes HTTP/REST

### 1. GET - Lecture de Ressources

**Objectif** : Récupérer des données sans les modifier

**Caractéristiques** :
- Idempotente (appels multiples = même résultat)
- Cacheable
- Paramètres dans l'URL
- Pas de corps de requête

**Exemples** :
```http
GET /api/users
GET /api/users/123
GET /api/users?age=25&city=Paris
GET /api/products?category=electronics&limit=10
```

**Réponse typique** :
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "id": 123,
  "nom": "Dupont",
  "email": "dupont@example.com"
}
```

---

### 2. POST - Création de Ressources

**Objectif** : Créer une nouvelle ressource

**Caractéristiques** :
- Non idempotente (crée une nouvelle ressource à chaque appel)
- Données dans le corps de la requête
- Retourne souvent l'URL de la ressource créée

**Exemple** :
```http
POST /api/users
Content-Type: application/json

{
  "nom": "Martin",
  "email": "martin@example.com",
  "age": 30
}
```

**Réponse typique** :
```http
HTTP/1.1 201 Created
Location: /api/users/124
Content-Type: application/json

{
  "id": 124,
  "nom": "Martin",
  "email": "martin@example.com",
  "age": 30,
  "created_at": "2025-11-16T10:30:00Z"
}
```

---

### 3. PUT - Mise à Jour Complète

**Objectif** : Remplacer entièrement une ressource existante

**Caractéristiques** :
- Idempotente
- Remplace toutes les propriétés de la ressource
- Nécessite l'envoi de toutes les données

**Exemple** :
```http
PUT /api/users/124
Content-Type: application/json

{
  "nom": "Martin",
  "email": "martin.nouveau@example.com",
  "age": 31,
  "ville": "Lyon"
}
```

**Réponse typique** :
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "id": 124,
  "nom": "Martin",
  "email": "martin.nouveau@example.com",
  "age": 31,
  "ville": "Lyon",
  "updated_at": "2025-11-16T11:00:00Z"
}
```

---

### 4. PATCH - Mise à Jour Partielle

**Objectif** : Modifier partiellement une ressource

**Caractéristiques** :
- Peut être idempotente (selon l'implémentation)
- Envoie uniquement les champs à modifier
- Plus efficace que PUT pour des modifications mineures

**Exemple** :
```http
PATCH /api/users/124
Content-Type: application/json

{
  "email": "martin.updated@example.com"
}
```

**Réponse typique** :
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "id": 124,
  "nom": "Martin",
  "email": "martin.updated@example.com",
  "age": 31,
  "ville": "Lyon"
}
```

---

### 5. DELETE - Suppression de Ressources

**Objectif** : Supprimer une ressource

**Caractéristiques** :
- Idempotente
- Peut retourner un corps vide ou la ressource supprimée

**Exemple** :
```http
DELETE /api/users/124
```

**Réponses typiques** :
```http
HTTP/1.1 204 No Content
```

ou

```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "message": "Utilisateur supprimé avec succès",
  "id": 124
}
```

---

### 6. HEAD - Métadonnées

**Objectif** : Récupérer uniquement les en-têtes HTTP (comme GET mais sans corps)

**Utilisation** :
- Vérifier l'existence d'une ressource
- Obtenir la taille d'un fichier
- Vérifier la date de modification

**Exemple** :
```http
HEAD /api/users/123
```

**Réponse** :
```http
HTTP/1.1 200 OK
Content-Type: application/json
Content-Length: 256
Last-Modified: Wed, 15 Nov 2025 10:00:00 GMT
```

---

### 7. OPTIONS - Capacités du Serveur

**Objectif** : Connaître les méthodes HTTP supportées pour une ressource

**Utilisation** :
- CORS (Cross-Origin Resource Sharing)
- Découverte d'API

**Exemple** :
```http
OPTIONS /api/users/123
```

**Réponse** :
```http
HTTP/1.1 200 OK
Allow: GET, POST, PUT, PATCH, DELETE, HEAD, OPTIONS
Access-Control-Allow-Methods: GET, POST, PUT, DELETE
Access-Control-Allow-Origin: *
```

---

## Codes de Statut HTTP

### 2xx - Succès
- **200 OK** : Requête réussie
- **201 Created** : Ressource créée
- **202 Accepted** : Requête acceptée (traitement asynchrone)
- **204 No Content** : Succès sans contenu de réponse

### 3xx - Redirection
- **301 Moved Permanently** : Déplacement permanent
- **302 Found** : Redirection temporaire
- **304 Not Modified** : Ressource non modifiée (cache)

### 4xx - Erreurs Client
- **400 Bad Request** : Requête mal formée
- **401 Unauthorized** : Authentification requise
- **403 Forbidden** : Accès interdit
- **404 Not Found** : Ressource introuvable
- **405 Method Not Allowed** : Méthode HTTP non autorisée
- **409 Conflict** : Conflit (ex: doublon)
- **422 Unprocessable Entity** : Validation échouée
- **429 Too Many Requests** : Limite de taux dépassée

### 5xx - Erreurs Serveur
- **500 Internal Server Error** : Erreur serveur générique
- **502 Bad Gateway** : Erreur de passerelle
- **503 Service Unavailable** : Service temporairement indisponible
- **504 Gateway Timeout** : Timeout de passerelle

---

## Formats de Données

### JSON (JavaScript Object Notation)
Le format le plus utilisé avec REST :

```json
{
  "id": 1,
  "nom": "Produit A",
  "prix": 29.99,
  "categories": ["électronique", "accessoires"],
  "disponible": true,
  "metadata": {
    "poids": "150g",
    "couleur": "noir"
  }
}
```

### XML
Format structuré, plus verbeux :

```xml
<?xml version="1.0" encoding="UTF-8"?>
<produit>
  <id>1</id>
  <nom>Produit A</nom>
  <prix>29.99</prix>
  <categories>
    <categorie>électronique</categorie>
    <categorie>accessoires</categorie>
  </categories>
  <disponible>true</disponible>
</produit>
```

### CSV (Comma-Separated Values)
Pour les exports de données tabulaires :

```csv
id,nom,prix,disponible
1,Produit A,29.99,true
2,Produit B,49.99,false
```

---

## Outils pour Pratiquer REST

### 1. **Postman** / **Insomnia**
Clients GUI pour tester les APIs

**Fonctionnalités** :
- Créer et sauvegarder des collections de requêtes
- Gérer les environnements (dev, prod)
- Tests automatisés
- Génération de code
- Collaboration en équipe

**Exemple d'utilisation Postman** :
```
1. Créer une nouvelle requête
2. Sélectionner GET/POST/PUT/DELETE
3. Entrer l'URL : http://localhost:3000/api/users
4. Ajouter des headers (Authorization, Content-Type)
5. Ajouter un corps JSON (pour POST/PUT)
6. Cliquer sur "Send"
```

---

### 2. **cURL** (Command Line)
Outil en ligne de commande très puissant

**Exemples** :

```bash
# GET simple
curl http://localhost:3000/api/users

# GET avec headers
curl -H "Authorization: Bearer TOKEN123" \
     http://localhost:3000/api/users

# POST avec JSON
curl -X POST http://localhost:3000/api/users \
     -H "Content-Type: application/json" \
     -d '{"nom":"Dupont","email":"dupont@mail.com"}'

# PUT
curl -X PUT http://localhost:3000/api/users/123 \
     -H "Content-Type: application/json" \
     -d '{"nom":"Dupont Modifié"}'

# DELETE
curl -X DELETE http://localhost:3000/api/users/123

# Afficher les headers de réponse
curl -i http://localhost:3000/api/users

# Suivre les redirections
curl -L http://localhost:3000/api/redirect

# Sauvegarder la réponse dans un fichier
curl -o response.json http://localhost:3000/api/users
```

---

### 3. **HTTPie**
Alternative moderne à cURL, plus lisible

```bash
# GET
http GET localhost:3000/api/users

# POST
http POST localhost:3000/api/users nom=Dupont email=dupont@mail.com

# PUT avec headers
http PUT localhost:3000/api/users/123 \
     Authorization:"Bearer TOKEN" \
     nom="Nouveau Nom"

# DELETE
http DELETE localhost:3000/api/users/123
```

---

### 4. **Navigateur Web (DevTools)**
Les navigateurs modernes incluent des outils de développement

**Console JavaScript** :
```javascript
// GET avec Fetch API
fetch('http://localhost:3000/api/users')
  .then(response => response.json())
  .then(data => console.log(data));

// POST
fetch('http://localhost:3000/api/users', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    nom: 'Dupont',
    email: 'dupont@mail.com'
  })
})
  .then(response => response.json())
  .then(data => console.log(data));

// Avec async/await
async function getUsers() {
  const response = await fetch('http://localhost:3000/api/users');
  const users = await response.json();
  console.log(users);
}
```

---

### 5. **Serveurs de Test REST**

#### **JSON Server** (Node.js)
Créer une API REST complète en 30 secondes :

```bash
# Installation
npm install -g json-server

# Créer db.json
echo '{"users": [], "posts": []}' > db.json

# Lancer le serveur
json-server --watch db.json --port 3000
```

Vous obtenez automatiquement :
- GET /users
- POST /users
- PUT /users/:id
- PATCH /users/:id
- DELETE /users/:id

#### **Express.js** (Node.js)
Framework pour créer des APIs personnalisées :

```javascript
const express = require('express');
const app = express();

app.use(express.json());

let users = [];

app.get('/api/users', (req, res) => {
  res.json(users);
});

app.post('/api/users', (req, res) => {
  const user = { id: Date.now(), ...req.body };
  users.push(user);
  res.status(201).json(user);
});

app.put('/api/users/:id', (req, res) => {
  const id = parseInt(req.params.id);
  const index = users.findIndex(u => u.id === id);
  if (index !== -1) {
    users[index] = { id, ...req.body };
    res.json(users[index]);
  } else {
    res.status(404).json({ error: 'User not found' });
  }
});

app.delete('/api/users/:id', (req, res) => {
  const id = parseInt(req.params.id);
  users = users.filter(u => u.id !== id);
  res.status(204).send();
});

app.listen(3000, () => {
  console.log('Server running on port 3000');
});
```

#### **FastAPI** (Python)
```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

class User(BaseModel):
    nom: str
    email: str

users = []

@app.get("/api/users")
def get_users():
    return users

@app.post("/api/users", status_code=201)
def create_user(user: User):
    users.append(user.dict())
    return user

@app.delete("/api/users/{user_id}", status_code=204)
def delete_user(user_id: int):
    if user_id < len(users):
        users.pop(user_id)
        return
    raise HTTPException(status_code=404, detail="User not found")
```

---

### 6. **APIs de Test Publiques**

- **JSONPlaceholder** : https://jsonplaceholder.typicode.com
- **ReqRes** : https://reqres.in
- **HTTPBin** : https://httpbin.org (tester les requêtes HTTP)

**Exemple avec JSONPlaceholder** :
```bash
# GET tous les utilisateurs
curl https://jsonplaceholder.typicode.com/users

# GET un utilisateur spécifique
curl https://jsonplaceholder.typicode.com/users/1

# POST (simulation)
curl -X POST https://jsonplaceholder.typicode.com/users \
     -H "Content-Type: application/json" \
     -d '{"name":"John","email":"john@mail.com"}'
```

---

## REST et Sockets (Couche Transport)

### Comprendre les Couches

**Modèle OSI/TCP-IP** :
```
┌─────────────────────────────┐
│   Application (HTTP/REST)   │ ← Couche 7
├─────────────────────────────┤
│   Transport (TCP/UDP)       │ ← Couche 4 (Sockets)
├─────────────────────────────┤
│   Réseau (IP)               │ ← Couche 3
├─────────────────────────────┤
│   Liaison (Ethernet)        │ ← Couche 2
└─────────────────────────────┘
```

### REST utilise HTTP qui utilise TCP

**Flux d'une requête REST** :
```
Client REST
    ↓
HTTP Request (GET /api/users)
    ↓
TCP Socket (connexion vers serveur:port)
    ↓
Réseau (IP)
    ↓
Serveur TCP Socket
    ↓
Serveur HTTP
    ↓
Application REST
```

### Sockets TCP sous-jacents

Quand vous faites une requête REST :

```python
# Ce que vous écrivez (haut niveau)
import requests
response = requests.get('http://localhost:3000/api/users')

# Ce qui se passe en coulisses (bas niveau)
import socket

# 1. Créer un socket TCP
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# 2. Se connecter au serveur
sock.connect(('localhost', 3000))

# 3. Envoyer la requête HTTP
request = b"GET /api/users HTTP/1.1\r\nHost: localhost\r\n\r\n"
sock.sendall(request)

# 4. Recevoir la réponse
response = sock.recv(4096)

# 5. Fermer la connexion
sock.close()
```

---

## Architecture Client-Serveur Avancée

### 1. REST + WebSockets (Communication Bidirectionnelle)

**Cas d'usage** : Chat en temps réel, notifications push

**Architecture hybride** :
```
Client
  │
  ├─→ REST API (HTTP)      : Opérations CRUD
  │   GET /api/messages
  │   POST /api/messages
  │
  └─→ WebSocket            : Temps réel
      ws://server/chat     : Recevoir nouveaux messages
```

**Exemple avec Node.js** :

```javascript
// Serveur
const express = require('express');
const http = require('http');
const WebSocket = require('ws');

const app = express();
const server = http.createServer(app);
const wss = new WebSocket.Server({ server });

app.use(express.json());

let messages = [];

// REST API pour récupérer les messages
app.get('/api/messages', (req, res) => {
  res.json(messages);
});

// REST API pour poster un message
app.post('/api/messages', (req, res) => {
  const message = { id: Date.now(), ...req.body };
  messages.push(message);
  
  // Notifier tous les clients WebSocket
  wss.clients.forEach(client => {
    if (client.readyState === WebSocket.OPEN) {
      client.send(JSON.stringify(message));
    }
  });
  
  res.status(201).json(message);
});

// WebSocket pour temps réel
wss.on('connection', (ws) => {
  console.log('Nouveau client connecté');
  
  ws.on('message', (data) => {
    // Broadcaster à tous les clients
    wss.clients.forEach(client => {
      if (client !== ws && client.readyState === WebSocket.OPEN) {
        client.send(data);
      }
    });
  });
});

server.listen(3000);
```

**Client JavaScript** :
```javascript
// Utiliser REST pour charger l'historique
fetch('http://localhost:3000/api/messages')
  .then(res => res.json())
  .then(messages => console.log('Historique:', messages));

// WebSocket pour temps réel
const ws = new WebSocket('ws://localhost:3000');

ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  console.log('Nouveau message:', message);
  // Mettre à jour l'UI
};

// Envoyer un message
function sendMessage(text) {
  ws.send(JSON.stringify({ text, author: 'User1' }));
}
```

---

### 2. REST + Long Polling

**Technique** : Le client fait des requêtes HTTP longues que le serveur maintient ouvertes jusqu'à avoir des données

```javascript
// Serveur Node.js
const pendingRequests = [];

app.get('/api/events', (req, res) => {
  pendingRequests.push(res);
  
  // Timeout après 30 secondes
  req.setTimeout(30000, () => {
    const index = pendingRequests.indexOf(res);
    if (index > -1) {
      pendingRequests.splice(index, 1);
      res.json({ timeout: true });
    }
  });
});

// Quand un événement se produit
function notifyClients(event) {
  pendingRequests.forEach(res => {
    res.json(event);
  });
  pendingRequests.length = 0;
}

// Client
async function longPoll() {
  while (true) {
    try {
      const response = await fetch('http://localhost:3000/api/events');
      const event = await response.json();
      
      if (!event.timeout) {
        console.log('Événement reçu:', event);
        // Traiter l'événement
      }
    } catch (error) {
      console.error('Erreur:', error);
    }
    
    // Recommencer immédiatement
  }
}

longPoll();
```

---

### 3. REST + Server-Sent Events (SSE)

**Technique** : Le serveur envoie des événements au client via une connexion HTTP maintenue ouverte

```javascript
// Serveur
app.get('/api/stream', (req, res) => {
  res.setHeader('Content-Type', 'text/event-stream');
  res.setHeader('Cache-Control', 'no-cache');
  res.setHeader('Connection', 'keep-alive');
  
  // Envoyer un événement toutes les 2 secondes
  const interval = setInterval(() => {
    const data = { time: new Date().toISOString(), value: Math.random() };
    res.write(`data: ${JSON.stringify(data)}\n\n`);
  }, 2000);
  
  req.on('close', () => {
    clearInterval(interval);
  });
});

// Client
const eventSource = new EventSource('http://localhost:3000/api/stream');

eventSource.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Données reçues:', data);
};

eventSource.onerror = (error) => {
  console.error('Erreur SSE:', error);
  eventSource.close();
};
```

---

### 4. Architecture Microservices avec REST

**Pattern** : Plusieurs services REST communiquent entre eux

```
┌─────────────┐      REST      ┌─────────────┐
│   Client    │────────────────→│ API Gateway │
└─────────────┘                 └──────┬──────┘
                                       │
                    ┌──────────────────┼──────────────────┐
                    ↓                  ↓                  ↓
              ┌───────────┐      ┌───────────┐     ┌───────────┐
              │  Service  │      │  Service  │     │  Service  │
              │   Users   │      │   Orders  │     │  Products │
              └───────────┘      └───────────┘     └───────────┘
                    │                  │                  │
                    ↓                  ↓                  ↓
              ┌───────────┐      ┌───────────┐     ┌───────────┐
              │    DB     │      │    DB     │     │    DB     │
              └───────────┘      └───────────┘     └───────────┘
```

**Exemple d'API Gateway en Node.js** :

```javascript
const express = require('express');
const axios = require('axios');
const app = express();

// Routage vers les microservices
app.get('/api/users/*', async (req, res) => {
  try {
    const response = await axios.get(`http://users-service:3001${req.path}`);
    res.json(response.data);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

app.get('/api/orders/*', async (req, res) => {
  try {
    const response = await axios.get(`http://orders-service:3002${req.path}`);
    res.json(response.data);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Agrégation de plusieurs services
app.get('/api/user-profile/:id', async (req, res) => {
  try {
    const [user, orders] = await Promise.all([
      axios.get(`http://users-service:3001/users/${req.params.id}`),
      axios.get(`http://orders-service:3002/orders?userId=${req.params.id}`)
    ]);
    
    res.json({
      user: user.data,
      orders: orders.data
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

app.listen(3000);
```

---

### 5. Gestion des Connexions TCP Persistantes

**HTTP/1.1 Keep-Alive** : Réutiliser les connexions TCP

```javascript
// Node.js avec agent HTTP personnalisé
const http = require('http');
const https = require('https');

const agent = new http.Agent({
  keepAlive: true,
  keepAliveMsecs: 30000,  // 30 secondes
  maxSockets: 50,         // Max 50 connexions simultanées
  maxFreeSockets: 10      // Garder 10 connexions libres
});

// Utiliser avec fetch ou axios
const axios = require('axios');
const client = axios.create({
  httpAgent: agent,
  httpsAgent: new https.Agent({ keepAlive: true })
});

// Toutes les requêtes réutilisent les connexions
for (let i = 0; i < 100; i++) {
  await client.get('http://api.example.com/data');
}
```

---

### 6. Load Balancing et Haute Disponibilité

```
                    ┌─────────────┐
                    │ Load Balancer│
                    │   (Nginx)   │
                    └──────┬──────┘
                           │
        ┌──────────────────┼──────────────────┐
        ↓                  ↓                  ↓
  ┌──────────┐       ┌──────────┐      ┌──────────┐
  │ Server 1 │       │ Server 2 │      │ Server 3 │
  │ :3001    │       │ :3002    │      │ :3003    │
  └──────────┘       └──────────┘      └──────────┘
```

**Configuration Nginx** :
```nginx
upstream backend {
    least_conn;  # Algorithme de répartition
    server localhost:3001;
    server localhost:3002;
    server localhost:3003;
}

server {
    listen 80;
    
    location /api/ {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        
        # Keep-Alive
        proxy_http_version 1.1;
        proxy_set_header Connection "";
    }
}
```

---

## Bonnes Pratiques REST

### 1. Versioning d'API
```
/api/v1/users
/api/v2/users
```

### 2. Pagination
```
GET /api/users?page=1&limit=20
```

### 3. Filtrage et Tri
```
GET /api/users?age=25&sort=name&order=asc
```

### 4. Authentification
```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### 5. Rate Limiting
```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1637078400
```

### 6. HATEOAS (Hypermedia)
```json
{
  "id": 1,
  "nom": "Dupont",
  "_links": {
    "self": "/api/users/1",
    "orders": "/api/users/1/orders",
    "edit": "/api/users/1",
    "delete": "/api/users/1"
  }
}
```

---

## Conclusion

REST est un style d'architecture puissant basé sur HTTP et la couche transport TCP. La maîtrise des méthodes HTTP, des codes de statut, et l'utilisation d'outils comme Postman, cURL, et des frameworks comme Express ou FastAPI vous permettent de créer et consommer des APIs efficaces.

Pour des applications avancées, REST peut être combiné avec WebSockets, SSE, ou long polling pour ajouter des capacités temps réel tout en conservant la simplicité et la scalabilité des architectures REST classiques.
