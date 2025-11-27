# Pratique REST : Manipulation de l'API JSONPlaceholder

## Objectif
Maîtriser les opérations CRUD (Create, Read, Update, Delete) sur une API REST en utilisant Postman et curl.

---

## Prérequis
- Postman installé sur votre machine
- Terminal avec curl installé
- URL de base : `https://jsonplaceholder.typicode.com`

---

## Partie 1 : Opérations GET (Lecture)

### Exercice 1.1 : Récupérer tous les posts

**Avec Postman :**
- Méthode : GET
- URL : `https://jsonplaceholder.typicode.com/posts`
- Cliquez sur "Send"

**Avec curl :**
```bash
curl https://jsonplaceholder.typicode.com/posts
```

**Question :** Combien de posts sont retournés ?

---

### Exercice 1.2 : Récupérer un post spécifique

**Avec Postman :**
- Méthode : GET
- URL : `https://jsonplaceholder.typicode.com/posts/1`

**Avec curl :**
```bash
curl https://jsonplaceholder.typicode.com/posts/1
```

**Question :** Quel est le titre du post n°1 ?

---

### Exercice 1.3 : Filtrer les posts par userId

**Avec Postman :**
- Méthode : GET
- URL : `https://jsonplaceholder.typicode.com/posts?userId=1`

**Avec curl :**
```bash
curl "https://jsonplaceholder.typicode.com/posts?userId=1"
```

**Question :** Combien de posts appartiennent à l'utilisateur 1 ?

---

### Exercice 1.4 : Récupérer les commentaires d'un post

**Avec Postman :**
- Méthode : GET
- URL : `https://jsonplaceholder.typicode.com/posts/1/comments`

**Avec curl :**
```bash
curl https://jsonplaceholder.typicode.com/posts/1/comments
```

---

## Partie 2 : Opérations POST (Création)

### Exercice 2.1 : Créer un nouveau post

**Avec Postman :**
- Méthode : POST
- URL : `https://jsonplaceholder.typicode.com/posts`
- Headers : 
  - Key: `Content-Type`, Value: `application/json`
- Body (raw, JSON) :
```json
{
  "title": "Mon nouveau post",
  "body": "Ceci est le contenu de mon post",
  "userId": 1
}
```

**Avec curl :**
```bash
curl -X POST https://jsonplaceholder.typicode.com/posts \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Mon nouveau post",
    "body": "Ceci est le contenu de mon post",
    "userId": 1
  }'
```

**Question :** Quel est l'ID retourné pour ce nouveau post ?

---

### Exercice 2.2 : Créer un nouveau commentaire

**Avec Postman :**
- Méthode : POST
- URL : `https://jsonplaceholder.typicode.com/comments`
- Headers : `Content-Type: application/json`
- Body :
```json
{
  "postId": 1,
  "name": "Jean Dupont",
  "email": "jean.dupont@example.com",
  "body": "Excellent article !"
}
```

**Avec curl :**
```bash
curl -X POST https://jsonplaceholder.typicode.com/comments \
  -H "Content-Type: application/json" \
  -d '{
    "postId": 1,
    "name": "Jean Dupont",
    "email": "jean.dupont@example.com",
    "body": "Excellent article !"
  }'
```

---

## Partie 3 : Opérations PUT (Mise à jour complète)

### Exercice 3.1 : Mettre à jour un post entier

**Avec Postman :**
- Méthode : PUT
- URL : `https://jsonplaceholder.typicode.com/posts/1`
- Headers : `Content-Type: application/json`
- Body :
```json
{
  "id": 1,
  "title": "Post mis à jour",
  "body": "Contenu complètement modifié",
  "userId": 1
}
```

**Avec curl :**
```bash
curl -X PUT https://jsonplaceholder.typicode.com/posts/1 \
  -H "Content-Type: application/json" \
  -d '{
    "id": 1,
    "title": "Post mis à jour",
    "body": "Contenu complètement modifié",
    "userId": 1
  }'
```

---

## Partie 4 : Opérations PATCH (Mise à jour partielle)

### Exercice 4.1 : Modifier uniquement le titre d'un post

**Avec Postman :**
- Méthode : PATCH
- URL : `https://jsonplaceholder.typicode.com/posts/1`
- Headers : `Content-Type: application/json`
- Body :
```json
{
  "title": "Titre modifié partiellement"
}
```

**Avec curl :**
```bash
curl -X PATCH https://jsonplaceholder.typicode.com/posts/1 \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Titre modifié partiellement"
  }'
```

**Question :** Quelle est la différence entre PUT et PATCH ?

---

## Partie 5 : Opérations DELETE (Suppression)

### Exercice 5.1 : Supprimer un post

**Avec Postman :**
- Méthode : DELETE
- URL : `https://jsonplaceholder.typicode.com/posts/1`

**Avec curl :**
```bash
curl -X DELETE https://jsonplaceholder.typicode.com/posts/1
```

**Question :** Quel code de statut HTTP recevez-vous ?

---

## Partie 6 : Exercices Avancés

### Exercice 6.1 : Récupérer un utilisateur et tous ses posts

**Étape 1 - Récupérer l'utilisateur :**
```bash
curl https://jsonplaceholder.typicode.com/users/1
```

**Étape 2 - Récupérer ses posts :**
```bash
curl https://jsonplaceholder.typicode.com/users/1/posts
```

---

### Exercice 6.2 : Récupérer les todos d'un utilisateur

**Avec curl :**
```bash
curl "https://jsonplaceholder.typicode.com/todos?userId=1&completed=false"
```

**Question :** Combien de todos non complétées a l'utilisateur 1 ?

---

### Exercice 6.3 : Récupérer les albums et leurs photos

**Albums :**
```bash
curl https://jsonplaceholder.typicode.com/albums/1
```

**Photos de l'album :**
```bash
curl https://jsonplaceholder.typicode.com/albums/1/photos
```

---

## Partie 7 : Mini-Projet Final

Créez un scénario complet qui :

1. Crée un nouvel utilisateur (POST sur /users)
2. Récupère l'ID de cet utilisateur
3. Crée 3 posts pour cet utilisateur
4. Ajoute 2 commentaires sur le premier post
5. Modifie le titre du deuxième post
6. Supprime le troisième post
7. Récupère tous les posts restants de l'utilisateur

**Bonus :** Écrivez un script bash qui automatise ce scénario.

---

## Points Importants à Retenir

- **JSONPlaceholder** est une API factice : les modifications ne sont pas persistées
- Les codes de statut HTTP :
  - 200 : OK
  - 201 : Created
  - 404 : Not Found
  - 500 : Server Error
- Toujours spécifier `Content-Type: application/json` pour POST/PUT/PATCH
- Les requêtes GET peuvent utiliser des query parameters (`?key=value&key2=value2`)

---

## Ressources

- Documentation officielle : https://jsonplaceholder.typicode.com/guide/
- Liste des endpoints disponibles :
  - /posts (100 posts)
  - /comments (500 comments)
  - /albums (100 albums)
  - /photos (5000 photos)
  - /todos (200 todos)
  - /users (10 users)

---
