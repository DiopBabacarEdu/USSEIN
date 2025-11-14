# Programmation par sockets en Java

## Introduction

La programmation par sockets permet de connecter deux nœuds (processus) sur un réseau pour qu'ils échangent des données. En Java, les sockets sont gérés par les classes du package `java.net`, notamment `ServerSocket` pour le serveur et `Socket` pour le client. Ce mécanisme sert de base au modèle client-serveur : le client envoie des requêtes de service et le serveur les traite avant de renvoyer des réponses. Les sockets sont couramment utilisés dans les applications de messagerie instantanée, le streaming multimédia, la collaboration en ligne, etc.

## Exemple simple de communication client-serveur

Illustrons le principe par un mini-programme en Java où le client et le serveur échangent un simple message « Hello ». Le serveur attend une connexion, lit un message et répond, tandis que le client envoie le message et affiche la réponse.

### Server.java (serveur en Java)

```java
import java.io.*;
import java.net.*;

public class Server {
    private static final int PORT = 8080;
    
    public static void main(String[] args) {
        ServerSocket serverSocket = null;
        Socket clientSocket = null;
        
        try {
            // 1. Création du ServerSocket sur le port spécifié
            serverSocket = new ServerSocket(PORT);
            System.out.println("Serveur démarré sur le port " + PORT);
            System.out.println("En attente de connexion...");
            
            // 2. Acceptation d'une connexion entrante (bloquant)
            clientSocket = serverSocket.accept();
            System.out.println("Client connecté : " + clientSocket.getInetAddress());
            
            // 3. Création des flux d'entrée/sortie
            BufferedReader in = new BufferedReader(
                new InputStreamReader(clientSocket.getInputStream())
            );
            PrintWriter out = new PrintWriter(
                clientSocket.getOutputStream(), true
            );
            
            // 4. Lecture du message du client
            String messageClient = in.readLine();
            System.out.println("Serveur reçu : " + messageClient);
            
            // 5. Envoi d'une réponse au client
            String reponse = "Hello from server";
            out.println(reponse);
            System.out.println("Serveur : Message envoyé");
            
        } catch (IOException e) {
            System.err.println("Erreur serveur : " + e.getMessage());
            e.printStackTrace();
        } finally {
            // 6. Fermeture des ressources
            try {
                if (clientSocket != null) clientSocket.close();
                if (serverSocket != null) serverSocket.close();
                System.out.println("Serveur fermé");
            } catch (IOException e) {
                System.err.println("Erreur lors de la fermeture : " + e.getMessage());
            }
        }
    }
}
```

### Client.java (client en Java)

```java
import java.io.*;
import java.net.*;

public class Client {
    private static final String SERVER_ADDRESS = "127.0.0.1";
    private static final int SERVER_PORT = 8080;
    
    public static void main(String[] args) {
        Socket socket = null;
        
        try {
            // 1. Connexion au serveur
            socket = new Socket(SERVER_ADDRESS, SERVER_PORT);
            System.out.println("Connecté au serveur " + SERVER_ADDRESS + ":" + SERVER_PORT);
            
            // 2. Création des flux d'entrée/sortie
            PrintWriter out = new PrintWriter(
                socket.getOutputStream(), true
            );
            BufferedReader in = new BufferedReader(
                new InputStreamReader(socket.getInputStream())
            );
            
            // 3. Envoi d'un message au serveur
            String message = "Hello from client";
            out.println(message);
            System.out.println("Client : Message envoyé");
            
            // 4. Lecture de la réponse du serveur
            String reponse = in.readLine();
            System.out.println("Client reçu : " + reponse);
            
        } catch (UnknownHostException e) {
            System.err.println("Hôte inconnu : " + e.getMessage());
        } catch (IOException e) {
            System.err.println("Erreur I/O : " + e.getMessage());
            e.printStackTrace();
        } finally {
            // 5. Fermeture du socket
            try {
                if (socket != null) socket.close();
                System.out.println("Client déconnecté");
            } catch (IOException e) {
                System.err.println("Erreur lors de la fermeture : " + e.getMessage());
            }
        }
    }
}
```

### Compilation et exécution

Compilez les deux fichiers avec javac :

```bash
javac Server.java
javac Client.java
```

Lancez ensuite le serveur sur un terminal :

```bash
java Server
```

Et le client sur un autre terminal :

```bash
java Client
```

Vous obtiendrez un échange de messages. Exemple de sortie console :

**Terminal serveur :**
```
Serveur démarré sur le port 8080
En attente de connexion...
Client connecté : /127.0.0.1
Serveur reçu : Hello from client
Serveur : Message envoyé
Serveur fermé
```

**Terminal client :**
```
Connecté au serveur 127.0.0.1:8080
Client : Message envoyé
Client reçu : Hello from server
Client déconnecté
```

## Composants de la programmation par sockets en Java

Le fonctionnement repose sur plusieurs concepts clés :

### Socket

Un socket est l'extrémité d'une communication réseau. En Java, la classe `Socket` représente un socket client qui se connecte à un serveur. C'est une paire (adresse IP : numéro de port) agissant comme point d'accès pour envoyer ou recevoir des données.

### ServerSocket

La classe `ServerSocket` représente un socket serveur qui écoute les connexions entrantes sur un port spécifique. Elle attend passivement que les clients se connectent via la méthode `accept()`.

### Types de sockets

Java supporte principalement deux types de communication réseau :

- **Socket TCP** : communication fiable et orientée connexion (protocole TCP) via les classes `Socket` et `ServerSocket`
- **Socket UDP** : communication sans connexion, plus rapide mais non garantie (protocole UDP) via les classes `DatagramSocket` et `DatagramPacket`

### Modèle client-serveur

Dans ce modèle d'architecture, un serveur attend les requêtes d'un ou plusieurs clients. Le client envoie une requête de service (par exemple, demander des données), et le serveur répond après traitement. Les rôles sont distincts : le serveur crée un `ServerSocket` d'écoute, le client initie la connexion avec un `Socket`.

## Création du serveur

Pour établir un serveur en Java, on suit ces étapes :

### 1. Création du ServerSocket

On crée une instance de `ServerSocket` en spécifiant le port d'écoute :

```java
ServerSocket serverSocket = new ServerSocket(PORT);
```

Le constructeur peut également accepter un paramètre `backlog` pour définir la taille de la file d'attente de connexions :

```java
ServerSocket serverSocket = new ServerSocket(PORT, 50); // backlog de 50
```

On peut aussi spécifier une adresse IP locale si la machine possède plusieurs interfaces réseau :

```java
ServerSocket serverSocket = new ServerSocket(PORT, 50, InetAddress.getByName("192.168.1.100"));
```

### 2. Accept (acceptation)

La méthode `accept()` attend qu'un client se connecte. Elle bloque l'exécution jusqu'à ce qu'une connexion soit établie :

```java
Socket clientSocket = serverSocket.accept();
```

Cette méthode renvoie un objet `Socket` représentant la connexion avec le client. Chaque client nécessite son propre `Socket`.

### 3. Création des flux d'entrée/sortie

Pour communiquer avec le client, on crée des flux à partir du socket :

**Pour lire les données du client :**
```java
InputStream inputStream = clientSocket.getInputStream();
BufferedReader in = new BufferedReader(new InputStreamReader(inputStream));
```

**Pour envoyer des données au client :**
```java
OutputStream outputStream = clientSocket.getOutputStream();
PrintWriter out = new PrintWriter(outputStream, true); // true = auto-flush
```

On peut aussi utiliser `DataInputStream` et `DataOutputStream` pour des données binaires :

```java
DataInputStream dis = new DataInputStream(clientSocket.getInputStream());
DataOutputStream dos = new DataOutputStream(clientSocket.getOutputStream());
```

### 4. Communication (lecture/écriture)

Une fois les flux créés, le serveur peut communiquer avec le client :

**Lecture :**
```java
String message = in.readLine(); // Lit une ligne de texte
```

**Écriture :**
```java
out.println("Message du serveur"); // Envoie une ligne de texte
```

Pour des données binaires :
```java
int data = dis.readInt();
dos.writeInt(42);
dos.flush();
```

### 5. Fermeture

Une fois la communication terminée, on ferme les ressources dans l'ordre inverse de leur création :

```java
in.close();
out.close();
clientSocket.close();
serverSocket.close();
```

Il est recommandé d'utiliser un bloc `finally` ou un try-with-resources pour garantir la fermeture :

```java
try (ServerSocket serverSocket = new ServerSocket(PORT);
     Socket clientSocket = serverSocket.accept();
     BufferedReader in = new BufferedReader(new InputStreamReader(clientSocket.getInputStream()));
     PrintWriter out = new PrintWriter(clientSocket.getOutputStream(), true)) {
    
    // Communication ici
    
} catch (IOException e) {
    e.printStackTrace();
}
```

## Création du client

Le client suit des étapes similaires :

### 1. Création du Socket et connexion

On crée un `Socket` en spécifiant l'adresse du serveur et le port :

```java
Socket socket = new Socket(SERVER_ADDRESS, SERVER_PORT);
```

Cela établit automatiquement la connexion au serveur. Si la connexion échoue, une exception est levée.

On peut aussi utiliser un constructeur sans paramètre et se connecter ensuite :

```java
Socket socket = new Socket();
socket.connect(new InetSocketAddress(SERVER_ADDRESS, SERVER_PORT), 5000); // timeout de 5 secondes
```

### 2. Création des flux d'entrée/sortie

Comme pour le serveur, on crée des flux pour communiquer :

```java
BufferedReader in = new BufferedReader(
    new InputStreamReader(socket.getInputStream())
);
PrintWriter out = new PrintWriter(
    socket.getOutputStream(), true
);
```

### 3. Communication (envoi/réception)

Le client envoie des données au serveur et lit les réponses :

```java
// Envoi
out.println("Hello from client");

// Réception
String reponse = in.readLine();
System.out.println("Réponse reçue : " + reponse);
```

### 4. Fermeture

Enfin, on ferme les ressources :

```java
in.close();
out.close();
socket.close();
```

Ou avec try-with-resources :

```java
try (Socket socket = new Socket(SERVER_ADDRESS, SERVER_PORT);
     BufferedReader in = new BufferedReader(new InputStreamReader(socket.getInputStream()));
     PrintWriter out = new PrintWriter(socket.getOutputStream(), true)) {
    
    // Communication ici
    
} catch (IOException e) {
    e.printStackTrace();
}
```

## Serveur multi-clients avec threads

Le serveur basique présenté ci-dessus ne peut gérer qu'un seul client à la fois. Pour gérer plusieurs clients simultanément, on utilise des threads :

### ServerMultiThread.java

```java
import java.io.*;
import java.net.*;

public class ServerMultiThread {
    private static final int PORT = 8080;
    
    public static void main(String[] args) {
        try (ServerSocket serverSocket = new ServerSocket(PORT)) {
            System.out.println("Serveur multi-thread démarré sur le port " + PORT);
            
            while (true) {
                // Accepte une nouvelle connexion
                Socket clientSocket = serverSocket.accept();
                System.out.println("Nouveau client connecté : " + clientSocket.getInetAddress());
                
                // Crée un nouveau thread pour gérer ce client
                ClientHandler handler = new ClientHandler(clientSocket);
                new Thread(handler).start();
            }
        } catch (IOException e) {
            System.err.println("Erreur serveur : " + e.getMessage());
            e.printStackTrace();
        }
    }
}

// Classe pour gérer chaque client dans un thread séparé
class ClientHandler implements Runnable {
    private Socket clientSocket;
    
    public ClientHandler(Socket socket) {
        this.clientSocket = socket;
    }
    
    @Override
    public void run() {
        try (
            BufferedReader in = new BufferedReader(
                new InputStreamReader(clientSocket.getInputStream())
            );
            PrintWriter out = new PrintWriter(
                clientSocket.getOutputStream(), true
            )
        ) {
            String message;
            while ((message = in.readLine()) != null) {
                System.out.println("Reçu de " + clientSocket.getInetAddress() + " : " + message);
                
                // Traitement du message
                String reponse = "Echo: " + message;
                out.println(reponse);
                
                // Si le client envoie "bye", on termine
                if (message.equalsIgnoreCase("bye")) {
                    break;
                }
            }
        } catch (IOException e) {
            System.err.println("Erreur avec le client : " + e.getMessage());
        } finally {
            try {
                clientSocket.close();
                System.out.println("Client déconnecté : " + clientSocket.getInetAddress());
            } catch (IOException e) {
                System.err.println("Erreur lors de la fermeture : " + e.getMessage());
            }
        }
    }
}
```

### Utilisation d'un ExecutorService

Pour une meilleure gestion des threads, on peut utiliser un `ExecutorService` :

```java
import java.util.concurrent.*;

public class ServerWithExecutor {
    private static final int PORT = 8080;
    private static final int MAX_THREADS = 10;
    
    public static void main(String[] args) {
        ExecutorService executor = Executors.newFixedThreadPool(MAX_THREADS);
        
        try (ServerSocket serverSocket = new ServerSocket(PORT)) {
            System.out.println("Serveur démarré avec pool de " + MAX_THREADS + " threads");
            
            while (true) {
                Socket clientSocket = serverSocket.accept();
                System.out.println("Nouveau client connecté");
                executor.execute(new ClientHandler(clientSocket));
            }
        } catch (IOException e) {
            System.err.println("Erreur serveur : " + e.getMessage());
        } finally {
            executor.shutdown();
        }
    }
}
```

## Options avancées des sockets

### Timeout de connexion

On peut définir un timeout pour éviter d'attendre indéfiniment :

```java
socket.setSoTimeout(5000); // Timeout de 5 secondes pour les opérations de lecture
```

### Keep-alive

Active les paquets keep-alive TCP pour détecter les connexions mortes :

```java
socket.setKeepAlive(true);
```

### TCP_NODELAY (désactivation de l'algorithme de Nagle)

Désactive le buffering pour envoyer les données immédiatement :

```java
socket.setTcpNoDelay(true);
```

### Taille des buffers

Configure la taille des buffers d'envoi et de réception :

```java
socket.setSendBufferSize(65536);    // 64 KB
socket.setReceiveBufferSize(65536); // 64 KB
```

### Réutilisation d'adresse

Permet de réutiliser immédiatement un port après fermeture :

```java
serverSocket.setReuseAddress(true);
```

## Problèmes courants et solutions

### Échec de connexion (Connection refused)

**Causes possibles :**
- Le serveur n'est pas démarré
- Le serveur écoute sur un port différent
- Un firewall bloque la connexion
- Mauvaise adresse IP

**Solution :**
Vérifiez que le serveur est lancé avant le client et qu'ils utilisent le même port. Vérifiez aussi les paramètres du firewall.

### Port déjà utilisé (BindException: Address already in use)

**Cause :**
Un autre processus utilise déjà le port spécifié, ou le port est encore en état TIME_WAIT après une fermeture récente.

**Solution :**
```java
serverSocket.setReuseAddress(true);
```
Ou choisissez un autre port, ou attendez quelques minutes que le port se libère.

### Timeout lors de la lecture (SocketTimeoutException)

**Cause :**
Aucune donnée n'a été reçue dans le délai spécifié par `setSoTimeout()`.

**Solution :**
Augmentez le timeout ou gérez l'exception pour réessayer :

```java
try {
    socket.setSoTimeout(10000); // 10 secondes
    String data = in.readLine();
} catch (SocketTimeoutException e) {
    System.out.println("Timeout - aucune donnée reçue");
}
```

### Connexion perdue (Connection reset)

**Cause :**
Le client ou le serveur a fermé brusquement la connexion sans procédure de fermeture propre.

**Solution :**
Utilisez toujours des blocs try-finally ou try-with-resources pour garantir la fermeture propre des ressources.

### Données tronquées ou incomplètes

**Cause :**
TCP est un protocole de flux, les données peuvent arriver par morceaux.

**Solution :**
Utilisez un protocole de délimitation (comme des retours à la ligne avec `readLine()`) ou un en-tête de longueur :

```java
// Envoi avec longueur
DataOutputStream dos = new DataOutputStream(socket.getOutputStream());
byte[] data = message.getBytes();
dos.writeInt(data.length); // Envoie d'abord la longueur
dos.write(data);           // Puis les données

// Réception
DataInputStream dis = new DataInputStream(socket.getInputStream());
int length = dis.readInt(); // Lit la longueur
byte[] buffer = new byte[length];
dis.readFully(buffer);      // Lit exactement 'length' octets
String message = new String(buffer);
```

## Exemple complet : Chat simple

### ChatServer.java

```java
import java.io.*;
import java.net.*;
import java.util.*;
import java.util.concurrent.*;

public class ChatServer {
    private static final int PORT = 8080;
    private static Set<PrintWriter> clientWriters = ConcurrentHashMap.newKeySet();
    
    public static void main(String[] args) {
        System.out.println("Serveur de chat démarré sur le port " + PORT);
        ExecutorService executor = Executors.newCachedThreadPool();
        
        try (ServerSocket serverSocket = new ServerSocket(PORT)) {
            while (true) {
                Socket clientSocket = serverSocket.accept();
                executor.execute(new ChatClientHandler(clientSocket));
            }
        } catch (IOException e) {
            System.err.println("Erreur serveur : " + e.getMessage());
        } finally {
            executor.shutdown();
        }
    }
    
    static class ChatClientHandler implements Runnable {
        private Socket socket;
        private PrintWriter out;
        
        public ChatClientHandler(Socket socket) {
            this.socket = socket;
        }
        
        @Override
        public void run() {
            try (
                BufferedReader in = new BufferedReader(
                    new InputStreamReader(socket.getInputStream())
                )
            ) {
                out = new PrintWriter(socket.getOutputStream(), true);
                clientWriters.add(out);
                
                System.out.println("Nouveau client connecté : " + socket.getInetAddress());
                broadcast("Un nouveau client a rejoint le chat");
                
                String message;
                while ((message = in.readLine()) != null) {
                    System.out.println("Message reçu : " + message);
                    broadcast(socket.getInetAddress().getHostAddress() + " : " + message);
                }
            } catch (IOException e) {
                System.err.println("Erreur avec le client : " + e.getMessage());
            } finally {
                if (out != null) {
                    clientWriters.remove(out);
                }
                try {
                    socket.close();
                } catch (IOException e) {
                    System.err.println("Erreur lors de la fermeture : " + e.getMessage());
                }
                broadcast("Un client a quitté le chat");
            }
        }
        
        private void broadcast(String message) {
            for (PrintWriter writer : clientWriters) {
                writer.println(message);
            }
        }
    }
}
```

### ChatClient.java

```java
import java.io.*;
import java.net.*;
import java.util.Scanner;

public class ChatClient {
    private static final String SERVER_ADDRESS = "127.0.0.1";
    private static final int SERVER_PORT = 8080;
    
    public static void main(String[] args) {
        try (
            Socket socket = new Socket(SERVER_ADDRESS, SERVER_PORT);
            BufferedReader in = new BufferedReader(
                new InputStreamReader(socket.getInputStream())
            );
            PrintWriter out = new PrintWriter(socket.getOutputStream(), true);
            Scanner scanner = new Scanner(System.in)
        ) {
            System.out.println("Connecté au serveur de chat");
            
            // Thread pour recevoir les messages
            new Thread(() -> {
                try {
                    String message;
                    while ((message = in.readLine()) != null) {
                        System.out.println(message);
                    }
                } catch (IOException e) {
                    System.err.println("Connexion perdue");
                }
            }).start();
            
            // Thread principal pour envoyer les messages
            System.out.println("Tapez vos messages (Ctrl+C pour quitter) :");
            while (scanner.hasNextLine()) {
                String message = scanner.nextLine();
                out.println(message);
            }
            
        } catch (IOException e) {
            System.err.println("Erreur de connexion : " + e.getMessage());
        }
    }
}
```

## Résumé

La programmation par sockets en Java utilise les classes `Socket` et `ServerSocket` pour implémenter le modèle client-serveur. Le serveur crée un `ServerSocket` qui écoute sur un port, accepte les connexions avec `accept()`, et communique via des flux d'entrée/sortie. Le client crée un `Socket` pour se connecter au serveur et utilise également des flux pour échanger des données.

Java simplifie considérablement la programmation réseau comparé au C, avec une gestion automatique de nombreux détails bas niveau et une meilleure gestion des exceptions. L'utilisation de threads ou d'`ExecutorService` permet de créer des serveurs capables de gérer plusieurs clients simultanément.

Les bonnes pratiques incluent :
- Utiliser try-with-resources pour garantir la fermeture des ressources
- Gérer correctement les exceptions réseau
- Implémenter des timeouts pour éviter les blocages
- Utiliser des threads pour les serveurs multi-clients
- Définir un protocole clair pour délimiter les messages
