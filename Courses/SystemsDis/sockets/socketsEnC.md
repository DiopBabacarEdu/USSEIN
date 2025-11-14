# Programmation par sockets en C

## Introduction

La programmation par sockets permet de connecter deux nœuds (processus) sur un réseau pour qu'ils échangent des données. Un nœud (socket serveur) écoute sur un port donné d'une adresse IP, tandis qu'un autre (client) se connecte à ce port. Ce mécanisme sert de base au modèle client-serveur : le client envoie des requêtes de service et le serveur les traite avant de renvoyer des réponses. Les sockets sont couramment utilisés dans les applications de messagerie instantanée, le streaming multimédia, la collaboration en ligne, etc.

## Exemple simple de communication client-serveur

Illustrons le principe par un mini-programme en C où le client et le serveur échangent un simple message « Hello ». Le serveur (fichier `server.c`) attend une connexion, lit un message et répond, tandis que le client (fichier `client.c`) envoie le message et affiche la réponse.

### server.c (serveur en C)

```c
#include <netinet/in.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <unistd.h>
#define PORT 8080

int main(int argc, char const* argv[])
{
    int server_fd, new_socket;
    ssize_t valread;
    struct sockaddr_in address;
    int opt = 1;
    socklen_t addrlen = sizeof(address);
    char buffer[1024] = { 0 };
    char* hello = "Hello from server";

    // 1. Création du socket
    if ((server_fd = socket(AF_INET, SOCK_STREAM, 0)) < 0) {
        perror("socket failed");
        exit(EXIT_FAILURE);
    }

    // 2. options (réutilisation d'adresse/port)
    if (setsockopt(server_fd, SOL_SOCKET, SO_REUSEADDR | SO_REUSEPORT,
                   &opt, sizeof(opt))) {
        perror("setsockopt");
        exit(EXIT_FAILURE);
    }

    // 3. Configuration de l'adresse du serveur
    address.sin_family = AF_INET;
    address.sin_addr.s_addr = INADDR_ANY;  // toutes les interfaces locales
    address.sin_port = htons(PORT);

    // 4. Liaison (bind) du socket à l'adresse et au port
    if (bind(server_fd, (struct sockaddr*)&address, sizeof(address)) < 0) {
        perror("bind failed");
        exit(EXIT_FAILURE);
    }
    
    // 5. Mise en écoute passive (listen)
    if (listen(server_fd, 3) < 0) {
        perror("listen");
        exit(EXIT_FAILURE);
    }
    
    // 6. Acceptation d'une connexion entrante
    if ((new_socket = accept(server_fd, (struct sockaddr*)&address,
                             &addrlen)) < 0) {
        perror("accept");
        exit(EXIT_FAILURE);
    }

    // 7. Lecture du message du client
    valread = read(new_socket, buffer, 1024 - 1);
    printf("Server reçu : %s\n", buffer);

    // 8. Envoi d'une réponse au client
    send(new_socket, hello, strlen(hello), 0);
    printf("Server: Hello message sent\n");

    // 9. Fermeture des sockets
    close(new_socket);
    close(server_fd);
    return 0;
}
```

### client.c (client en C)

```c
#include <arpa/inet.h>
#include <stdio.h>
#include <string.h>
#include <sys/socket.h>
#include <unistd.h>
#define PORT 8080

int main(int argc, char const* argv[])
{
    int status, valread, client_fd;
    struct sockaddr_in serv_addr;
    char* hello = "Hello from client";
    char buffer[1024] = { 0 };

    // 1. Création du socket
    if ((client_fd = socket(AF_INET, SOCK_STREAM, 0)) < 0) {
        printf("\nSocket creation error\n");
        return -1;
    }

    // 2. Configuration de l'adresse du serveur
    serv_addr.sin_family = AF_INET;
    serv_addr.sin_port = htons(PORT);

    // 3. Conversion de l'adresse du serveur (ex : "127.0.0.1")
    if (inet_pton(AF_INET, "127.0.0.1", &serv_addr.sin_addr) <= 0) {
        printf("\nAdresse invalide / non supportée\n");
        return -1;
    }

    // 4. Connexion au serveur
    if ((status = connect(client_fd, (struct sockaddr*)&serv_addr,
                          sizeof(serv_addr))) < 0) {
        printf("\nÉchec de la connexion\n");
        return -1;
    }

    // 5. Envoi d'un message au serveur
    send(client_fd, hello, strlen(hello), 0);
    printf("Client: Hello message sent\n");

    // 6. Lecture de la réponse du serveur
    valread = read(client_fd, buffer, 1024 - 1);
    printf("Client reçu : %s\n", buffer);

    // 7. Fermeture du socket
    close(client_fd);
    return 0;
}
```

### Compilation et exécution

Compilez séparément avec gcc :

```bash
gcc server.c -o server
gcc client.c -o client
```

Lancez ensuite le serveur sur un terminal (`./server`) et le client sur un autre (`./client`). Vous obtiendrez un échange de messages. Par exemple, la sortie console peut être :

```
Client: Hello message sent
Hello from server
Server: Hello from client
Hello message sent
```

## Composants de la programmation par sockets

Le fonctionnement repose sur plusieurs concepts clés :

### Socket

Un socket est l'extrémité d'une communication réseau. C'est une paire (adresse IP : numéro de port) agissant comme point d'accès pour envoyer ou recevoir des données. Par exemple, `192.168.1.1:8080` est un socket où `192.168.1.1` est l'IP et `8080` le port.

### Types de sockets

On distingue essentiellement deux types de sockets réseau :

- **Socket TCP (SOCK_STREAM)** : communication fiable et orientée connexion (protocole TCP)
- **Socket UDP (SOCK_DGRAM)** : communication sans connexion, plus rapide mais non garantie (protocole UDP)

### Modèle client-serveur

Dans ce modèle d'architecture, un serveur attend les requêtes d'un ou plusieurs clients. Le client envoie une requête de service (par exemple, demander des données), et le serveur répond après traitement. Les rôles sont distincts : le serveur crée un socket d'écoute, le client initie la connexion.

**Figure : Diagramme d'état du modèle client-serveur en programmation par sockets.**

Ce diagramme illustre les états typiques d'un serveur et d'un client. Le serveur démarre en état "LISTEN" (écoute) et attend une connexion entrante. Lorsqu'un client se connecte, le serveur passe à l'état "CONNECTED" (établi) et échange des données. Le client démarre inactif, puis crée un socket et tente une connexion. Une fois connecté, le client peut envoyer des données au serveur et attendre une réponse, puis se terminer en fermant la connexion.

## Création du serveur

Pour établir un serveur en C, on suit ces étapes :

### 1. Création du socket

Appel à la fonction `socket()` :

```c
sockfd = socket(domain, type, protocol);
```

Par exemple, `socket(AF_INET, SOCK_STREAM, 0)` crée un socket TCP IPv4. Le paramètre `domain` peut être `AF_INET` pour IPv4 ou `AF_INET6` pour IPv6 (et `AF_UNIX`/`AF_LOCAL` pour communication locale). `type` spécifie TCP (`SOCK_STREAM`) ou UDP (`SOCK_DGRAM`). `protocol` est généralement 0. Cette étape renvoie un descripteur `sockfd` utilisé pour les opérations suivantes.

### 2. Configuration optionnelle (setsockopt)

Avec `setsockopt()`, on peut définir des options sur le socket (par exemple permettre la réutilisation immédiate d'une adresse/port pour éviter l'erreur "address already in use" lors de redémarrages fréquents). Exemple :

```c
setsockopt(sockfd, SOL_SOCKET, SO_REUSEADDR | SO_REUSEPORT, &opt, sizeof(opt));
```

C'est facultatif mais souvent recommandé pour les serveurs.

### 3. Bind (liaison)

On associe le socket à une adresse IP et un port local via `bind(sockfd, addr, addrlen)`. Typiquement, on remplit une structure `struct sockaddr_in address` avec l'IP et le port (par exemple `INADDR_ANY` pour écouter sur toutes les interfaces locales) puis on appelle :

```c
bind(sockfd, (struct sockaddr*)&address, sizeof(address));
```

Cela lie `sockfd` à l'adresse IP/port donnés.

### 4. Listen (écoute)

On place le socket en mode écoute passive avec `listen(sockfd, backlog)`. Le paramètre `backlog` définit la taille maximale de la file d'attente de connexions en attente. Tant que `accept()` n'est pas appelé, les nouvelles connexions restent dans cette file (ou sont refusées si pleine).

### 5. Accept (acceptation)

On extrait la première requête de connexion dans la file d'attente et on crée un nouveau socket connecté avec `accept()`. En pratique :

```c
new_socket = accept(sockfd, (struct sockaddr*)&address, &addrlen);
```

- `sockfd` est le socket initial en écoute
- `address` et `addrlen` récupèrent l'adresse du client

Cette fonction bloque (attend) jusqu'à ce qu'un client se connecte. Si un client se connecte, `accept()` renvoie un nouveau descripteur (`new_socket`) correspondant à la connexion établie. Serveur et client peuvent alors communiquer via `new_socket`.

### 6. Communication (send/recv)

Une fois connecté, le serveur peut recevoir des données du client (avec `recv()` ou `read()`) et lui envoyer des données (avec `send()`). Par exemple, pour lire du client :

```c
valread = read(new_socket, buffer, sizeof(buffer));
```

Et pour envoyer :

```c
send(new_socket, msg, strlen(msg), 0);
```

Les paramètres sont le descripteur (`new_socket`), un pointeur vers les données, leur longueur, et des flags (0 par défaut). La fonction `recv()` fonctionne de façon similaire.

### 7. Fermeture

Une fois l'échange terminé, on ferme les sockets avec `close()`, libérant les ressources système. On ferme d'abord `new_socket` (connexion avec le client) puis, si nécessaire, on peut refermer `sockfd` (écoute). Exemple :

```c
close(new_socket);
close(sockfd);
```

Cela termine proprement le serveur et libère ses ports et mémoires.

## Création du client

Le client suit des étapes similaires, en inversant les rôles :

### 1. Création du socket

Appel à `socket(AF_INET, SOCK_STREAM, 0)`, comme pour le serveur.

### 2. Configuration de l'adresse du serveur

On remplit une structure `sockaddr_in` avec l'IP du serveur et le même port que celui écouté. Par exemple :

```c
serv_addr.sin_family = AF_INET;
serv_addr.sin_port = htons(PORT);
// Conversion de "127.0.0.1" en format binaire
inet_pton(AF_INET, "127.0.0.1", &serv_addr.sin_addr);
```

Ici `inet_pton` convertit l'IP littérale en format binaire utilisable par les sockets.

### 3. Connect

On tente de connecter le socket client au serveur avec :

```c
connect(sockfd, (struct sockaddr*)&serv_addr, sizeof(serv_addr));
```

La fonction `connect()` prend le socket, l'adresse du serveur et sa taille comme paramètres. Si elle réussit, la connexion est établie.

### 4. Communication (send/recv)

Après connexion, le client envoie des données au serveur avec `send()` et peut lire la réponse avec `recv()` ou `read()`, de la même manière que le serveur. Par exemple :

```c
send(sockfd, hello, strlen(hello), 0);
valread = read(sockfd, buffer, sizeof(buffer));
```

### 5. Fermeture

Enfin, on ferme le socket client avec `close(sockfd)`. Cela termine la connexion côté client.

## Problèmes courants et solutions

Quelques écueils fréquents en socket programming :

### Échec de connexion

Vérifiez que le client utilise bien la bonne adresse IP et le port du serveur. Si le serveur n'est pas lancé ou écoute sur un autre port, `connect()` échouera.

### Port déjà utilisé

Lors du `bind()` du serveur, l'erreur "Address already in use" signifie qu'un autre processus utilise le port spécifié. Choisissez un port libre ou arrêtez l'autre service.

### Sockets bloquants

Par défaut, les appels comme `accept()` ou `recv()` sont bloquants : ils attendent indéfiniment une connexion ou des données. Si ce comportement est indésirable, on peut passer le socket en mode non-bloquant ou utiliser des mécanismes asynchrones (select/poll) pour éviter un blocage complet.

## Résumé

En résumé, la programmation par sockets en C suit le modèle client-serveur décrit ci-dessus, avec des étapes bien définies pour créer, lier, écouter, accepter, communiquer et fermer les sockets.
