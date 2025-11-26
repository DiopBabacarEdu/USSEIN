# Service de Chat Multi-clients avec RPC

Je vais créer un système de chat où plusieurs clients peuvent communiquer via un serveur RPC.

## Étape 1 : Créer le fichier de définition RPC

Créez **`chat.x`** :

```c
/* ============================================================================
   FICHIER chat.x - DÉFINITION DE L'INTERFACE RPC
   ============================================================================
   Ce fichier est le CONTRAT entre le client et le serveur.
   Il définit :
   - Les structures de données échangées
   - Les fonctions (procédures) disponibles à distance
   - Les numéros d'identification du service
   
   IMPORTANT : Ce fichier est traité par 'rpcgen' qui génère automatiquement :
   - chat.h        : Les définitions de structures en C
   - chat_clnt.c   : Les fonctions pour appeler le serveur (côté client)
   - chat_svc.c    : Le code qui reçoit les appels (côté serveur)
   - chat_xdr.c    : Les fonctions pour sérialiser/désérialiser les données
   ============================================================================ */

/* ----------------------------------------------------------------------------
   CONSTANTES GLOBALES
   Ces constantes définissent les limites du système
   ---------------------------------------------------------------------------- */
const MAX_MSG_LEN = 256;        /* Longueur maximale d'un message de chat */
const MAX_USERNAME_LEN = 50;    /* Longueur maximale d'un nom d'utilisateur */
const MAX_MESSAGES = 100;       /* Nombre maximum de messages stockés */

/* ============================================================================
   DÉFINITION DES STRUCTURES DE DONNÉES
   ============================================================================
   Ces structures définissent le FORMAT des données échangées entre client 
   et serveur. Elles doivent être identiques des deux côtés.
   ============================================================================ */

/* ----------------------------------------------------------------------------
   STRUCTURE : message
   Représente UN message dans le chat avec toutes ses métadonnées
   ---------------------------------------------------------------------------- */
struct message {
    char username[MAX_USERNAME_LEN];  /* QUI a envoyé ce message ? */
    char contenu[MAX_MSG_LEN];        /* QUEL est le contenu du message ? */
    int timestamp;                     /* QUAND a-t-il été envoyé ? (temps Unix) */
};
/* 
   EXEMPLE D'UTILISATION :
   {
     username: "Alice",
     contenu: "Bonjour tout le monde !",
     timestamp: 1234567890
   }
*/

/* ----------------------------------------------------------------------------
   STRUCTURE : user_info
   Informations minimales sur un utilisateur (pour inscription/déconnexion)
   ---------------------------------------------------------------------------- */
struct user_info {
    char username[MAX_USERNAME_LEN];  /* Le nom d'utilisateur unique */
};
/*
   POURQUOI cette structure ?
   - Permet d'identifier un utilisateur lors de sa connexion
   - Permet de le retirer lors de sa déconnexion
   
   EXEMPLE :
   {
     username: "Bob"
   }
*/

/* ----------------------------------------------------------------------------
   STRUCTURE : chat_message
   Un message à envoyer (utilisateur + contenu)
   ---------------------------------------------------------------------------- */
struct chat_message {
    char username[MAX_USERNAME_LEN];  /* QUI envoie le message */
    char contenu[MAX_MSG_LEN];        /* QUOI est envoyé */
};
/*
   DIFFÉRENCE avec 'message' :
   - 'chat_message' = ce que le CLIENT envoie (pas encore de timestamp)
   - 'message' = ce qui est STOCKÉ sur le serveur (avec timestamp ajouté)
   
   FLUX :
   Client envoie chat_message → Serveur ajoute timestamp → Devient 'message'
*/

/* ----------------------------------------------------------------------------
   STRUCTURE : register_response
   Réponse du serveur lors d'une tentative d'inscription
   ---------------------------------------------------------------------------- */
struct register_response {
    int success;                      /* 1 = succès, 0 = échec */
    char message[MAX_MSG_LEN];        /* Message d'explication pour l'utilisateur */
};
/*
   POURQUOI cette structure ?
   - Permet au serveur de dire si l'inscription a réussi
   - Permet de donner une raison en cas d'échec
   
   EXEMPLES :
   Succès : { success: 1, message: "Bienvenue dans le chat !" }
   Échec :  { success: 0, message: "Nom d'utilisateur déjà pris !" }
*/

/* ----------------------------------------------------------------------------
   STRUCTURE : message_list
   Une liste DYNAMIQUE de messages (tableau de taille variable)
   ---------------------------------------------------------------------------- */
struct message_list {
    message messages<MAX_MESSAGES>;   /* Tableau DYNAMIQUE de messages */
    int count;                         /* Nombre réel de messages dans le tableau */
};
/*
   NOTATION SPÉCIALE : messages<MAX_MESSAGES>
   - Le '<>' indique un TABLEAU DE TAILLE VARIABLE (comme un pointeur)
   - MAX_MESSAGES est la limite maximale
   - 'count' indique combien sont réellement utilisés
   
   POURQUOI ?
   - Permet d'envoyer 0, 1, 5, 50... messages selon ce qui est disponible
   - Plus efficace que d'envoyer toujours 100 messages
   
   EXEMPLE :
   {
     messages: [msg1, msg2, msg3],
     count: 3
   }
*/

/* ----------------------------------------------------------------------------
   STRUCTURE : user_list
   Liste DYNAMIQUE de noms d'utilisateurs connectés
   ---------------------------------------------------------------------------- */
struct user_list {
    string usernames<MAX_MESSAGES>;   /* Tableau DYNAMIQUE de chaînes */
    int count;                         /* Nombre d'utilisateurs connectés */
};
/*
   NOTATION : string usernames<MAX_MESSAGES>
   - 'string' en RPC = chaîne de caractères de longueur variable
   - '<MAX_MESSAGES>' = tableau dynamique
   - Donc : tableau dynamique de chaînes dynamiques !
   
   EXEMPLE :
   {
     usernames: ["Alice", "Bob", "Charlie"],
     count: 3
   }
*/

/* ============================================================================
   DÉFINITION DU PROGRAMME RPC (LE SERVICE)
   ============================================================================
   Cette section définit le SERVICE offert par le serveur.
   C'est comme définir une API ou une interface.
   ============================================================================ */

program CHAT_PROG {              /* Nom du programme/service */
    version CHAT_VERS {          /* Version du service (permet l'évolution) */
        
        /* ====================================================================
           PROCÉDURE 1 : REGISTER_USER
           Permet à un utilisateur de s'inscrire au chat
           ==================================================================== */
        register_response REGISTER_USER(user_info) = 1;
        /*
           DÉCOMPOSITION :
           - register_response  : Type de RETOUR (ce que le serveur renvoie)
           - REGISTER_USER      : NOM de la fonction (en majuscules par convention)
           - (user_info)        : Type du PARAMÈTRE (ce que le client envoie)
           - = 1                : NUMÉRO de la procédure (identifiant unique)
           
           ÉQUIVALENT EN C :
           register_response* register_user_1_svc(user_info *argp, struct svc_req *rqstp);
           
           FLUX :
           1. Client appelle : register_user_1(&user, clnt)
           2. RPC transmet la requête au serveur
           3. Serveur exécute : register_user_1_svc(&user, ...)
           4. Serveur renvoie : register_response*
           5. Client reçoit le résultat
        */
        
        /* ====================================================================
           PROCÉDURE 2 : SEND_MESSAGE
           Permet d'envoyer un message au chat
           ==================================================================== */
        int SEND_MESSAGE(chat_message) = 2;
        /*
           - int              : Retourne un entier (1=succès, 0=échec)
           - SEND_MESSAGE     : Nom de la fonction
           - (chat_message)   : Prend un message à envoyer
           - = 2              : Numéro de procédure
           
           USAGE CLIENT :
           chat_message msg = {"Alice", "Bonjour!"};
           int *result = send_message_1(&msg, clnt);
           if (*result == 1) { printf("Message envoyé\n"); }
        */
        
        /* ====================================================================
           PROCÉDURE 3 : GET_MESSAGES
           Récupère les nouveaux messages depuis un index donné
           ==================================================================== */
        message_list GET_MESSAGES(int) = 3;
        /*
           - message_list   : Retourne une liste de messages
           - GET_MESSAGES   : Nom de la fonction
           - (int)          : Prend un index de départ (dernier message lu)
           - = 3            : Numéro de procédure
           
           POURQUOI un 'int' en paramètre ?
           - Le client dit : "Donne-moi tous les messages APRÈS le numéro X"
           - Permet de ne recevoir que les NOUVEAUX messages
           - Évite de re-télécharger tous les messages à chaque fois
           
           EXEMPLE :
           int last_index = 5;
           message_list *msgs = get_messages_1(&last_index, clnt);
           // Retourne les messages 6, 7, 8, 9... si disponibles
        */
        
        /* ====================================================================
           PROCÉDURE 4 : GET_USERS
           Récupère la liste des utilisateurs connectés
           ==================================================================== */
        user_list GET_USERS(void) = 4;
        /*
           - user_list    : Retourne la liste des utilisateurs
           - GET_USERS    : Nom de la fonction
           - (void)       : NE PREND AUCUN PARAMÈTRE
           - = 4          : Numéro de procédure
           
           USAGE :
           user_list *users = get_users_1(NULL, clnt);
           for (int i = 0; i < users->count; i++) {
               printf("- %s\n", users->usernames.usernames_val[i]);
           }
        */
        
        /* ====================================================================
           PROCÉDURE 5 : DISCONNECT_USER
           Déconnecte un utilisateur du chat
           ==================================================================== */
        int DISCONNECT_USER(user_info) = 5;
        /*
           - int          : Retourne 1 si succès, 0 sinon
           - DISCONNECT   : Nom de la fonction
           - (user_info)  : L'utilisateur à déconnecter
           - = 5          : Numéro de procédure
        */
        
    } = 1;  /* Numéro de VERSION (permet d'avoir plusieurs versions du même service) */
    
} = 0x20000002;  /* Numéro de PROGRAMME (identifiant UNIQUE du service) */

/*
   NUMÉRO DE PROGRAMME : 0x20000002
   - Doit être UNIQUE sur le système
   - Convention : 0x20000000 à 0x3fffffff pour les programmes utilisateur
   - Évite les conflits avec d'autres services RPC
   
   NUMÉRO DE VERSION : 1
   - Permet d'avoir plusieurs versions du même service
   - Si vous modifiez l'interface, incrémentez la version
   - Exemple : CHAT_VERS_1, CHAT_VERS_2...
*/
```

## Étape 2 : Générer les fichiers squelettes

```bash
rpcgen -a -C chat.x
```

## Étape 3 : Modifier le Makefile

Créez/modifiez **`Makefile.chat`** :

```makefile
# Makefile.chat
CLIENT = chat_client
SERVER = chat_server
SOURCES_CLNT.c =
SOURCES_CLNT.h =
SOURCES_SVC.c =
SOURCES_SVC.h =
SOURCES.x = chat.x
TARGETS_SVC.c = chat_svc.c chat_server.c chat_xdr.c
TARGETS_CLNT.c = chat_clnt.c chat_client.c chat_xdr.c
TARGETS = chat.h chat_xdr.c chat_clnt.c chat_svc.c chat_client.c chat_server.c
OBJECTS_CLNT = $(SOURCES_CLNT.c:%.c=%.o) $(TARGETS_CLNT.c:%.c=%.o)
OBJECTS_SVC = $(SOURCES_SVC.c:%.c=%.o) $(TARGETS_SVC.c:%.c=%.o)

# Compiler flags
CFLAGS += -g -I/usr/include/tirpc
LDLIBS += -ltirpc -lpthread
RPCGENFLAGS = -C

# Targets
all : $(CLIENT) $(SERVER)

$(TARGETS) : $(SOURCES.x)
	rpcgen $(RPCGENFLAGS) $(SOURCES.x)

$(OBJECTS_CLNT) : $(SOURCES_CLNT.c) $(SOURCES_CLNT.h) $(TARGETS_CLNT.c)

$(OBJECTS_SVC) : $(SOURCES_SVC.c) $(SOURCES_SVC.h) $(TARGETS_SVC.c)

$(CLIENT) : $(OBJECTS_CLNT)
	$(LINK.c) -o $(CLIENT) $(OBJECTS_CLNT) $(LDLIBS)

$(SERVER) : $(OBJECTS_SVC)
	$(LINK.c) -o $(SERVER) $(OBJECTS_SVC) $(LDLIBS)

clean:
	$(RM) core $(TARGETS) $(OBJECTS_CLNT) $(OBJECTS_SVC) $(CLIENT) $(SERVER)
```

## Étape 4 : Implémenter le serveur

Créez **`chat_server.c`** :

```c
#include "chat.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#define MAX_USERS 50
#define MAX_STORED_MESSAGES 100

/* Stockage global des messages et utilisateurs */
static message messages_history[MAX_STORED_MESSAGES];
static int message_count = 0;

static char connected_users[MAX_USERS][MAX_USERNAME_LEN];
static int user_count = 0;

/* Fonction pour enregistrer un nouvel utilisateur */
register_response *
register_user_1_svc(user_info *argp, struct svc_req *rqstp)
{
    static register_response result;
    int i;
    
    printf("\n[SERVEUR] Demande d'inscription de : %s\n", argp->username);
    
    /* Vérifier si le nom d'utilisateur est vide */
    if (strlen(argp->username) == 0) {
        result.success = 0;
        strcpy(result.message, "Nom d'utilisateur vide !");
        return &result;
    }
    
    /* Vérifier si l'utilisateur existe déjà */
    for (i = 0; i < user_count; i++) {
        if (strcmp(connected_users[i], argp->username) == 0) {
            result.success = 0;
            strcpy(result.message, "Nom d'utilisateur déjà pris !");
            printf("[SERVEUR] Inscription refusée : nom déjà utilisé\n");
            return &result;
        }
    }
    
    /* Vérifier si on a atteint la limite */
    if (user_count >= MAX_USERS) {
        result.success = 0;
        strcpy(result.message, "Serveur plein !");
        return &result;
    }
    
    /* Ajouter l'utilisateur */
    strcpy(connected_users[user_count], argp->username);
    user_count++;
    
    result.success = 1;
    strcpy(result.message, "Bienvenue dans le chat !");
    
    printf("[SERVEUR] ✓ %s connecté(e) (%d utilisateurs)\n", 
           argp->username, user_count);
    
    /* Message système */
    if (message_count < MAX_STORED_MESSAGES) {
        strcpy(messages_history[message_count].username, "SYSTÈME");
        snprintf(messages_history[message_count].contenu, MAX_MSG_LEN,
                "%s a rejoint le chat", argp->username);
        messages_history[message_count].timestamp = time(NULL);
        message_count++;
    }
    
    return &result;
}

/* Fonction pour envoyer un message */
int *
send_message_1_svc(chat_message *argp, struct svc_req *rqstp)
{
    static int result;
    
    printf("[MESSAGE] %s: %s\n", argp->username, argp->contenu);
    
    /* Stocker le message */
    if (message_count < MAX_STORED_MESSAGES) {
        strcpy(messages_history[message_count].username, argp->username);
        strcpy(messages_history[message_count].contenu, argp->contenu);
        messages_history[message_count].timestamp = time(NULL);
        message_count++;
        result = 1;
    } else {
        /* Si le buffer est plein, décaler les messages */
        int i;
        for (i = 0; i < MAX_STORED_MESSAGES - 1; i++) {
            messages_history[i] = messages_history[i + 1];
        }
        strcpy(messages_history[MAX_STORED_MESSAGES - 1].username, argp->username);
        strcpy(messages_history[MAX_STORED_MESSAGES - 1].contenu, argp->contenu);
        messages_history[MAX_STORED_MESSAGES - 1].timestamp = time(NULL);
        result = 1;
    }
    
    return &result;
}

/* Fonction pour récupérer les messages depuis un index */
message_list *
get_messages_1_svc(int *argp, struct svc_req *rqstp)
{
    static message_list result;
    int start_index = *argp;
    int i, j;
    
    /* Libérer l'ancienne mémoire si nécessaire */
    if (result.messages.messages_val != NULL) {
        free(result.messages.messages_val);
    }
    
    /* Calculer le nombre de nouveaux messages */
    if (start_index < 0) start_index = 0;
    if (start_index > message_count) start_index = message_count;
    
    result.count = message_count - start_index;
    
    if (result.count > 0) {
        result.messages.messages_len = result.count;
        result.messages.messages_val = (message *)malloc(result.count * sizeof(message));
        
        for (i = start_index, j = 0; i < message_count; i++, j++) {
            result.messages.messages_val[j] = messages_history[i];
        }
    } else {
        result.messages.messages_len = 0;
        result.messages.messages_val = NULL;
    }
    
    return &result;
}

/* Fonction pour obtenir la liste des utilisateurs connectés */
user_list *
get_users_1_svc(void *argp, struct svc_req *rqstp)
{
    static user_list result;
    int i;
    
    /* Libérer l'ancienne mémoire */
    if (result.usernames.usernames_val != NULL) {
        for (i = 0; i < result.usernames.usernames_len; i++) {
            free(result.usernames.usernames_val[i]);
        }
        free(result.usernames.usernames_val);
    }
    
    result.count = user_count;
    result.usernames.usernames_len = user_count;
    
    if (user_count > 0) {
        result.usernames.usernames_val = (char **)malloc(user_count * sizeof(char *));
        
        for (i = 0; i < user_count; i++) {
            result.usernames.usernames_val[i] = strdup(connected_users[i]);
        }
    } else {
        result.usernames.usernames_val = NULL;
    }
    
    return &result;
}

/* Fonction pour déconnecter un utilisateur */
int *
disconnect_user_1_svc(user_info *argp, struct svc_req *rqstp)
{
    static int result = 0;
    int i, j;
    
    printf("\n[SERVEUR] Déconnexion de : %s\n", argp->username);
    
    /* Trouver et supprimer l'utilisateur */
    for (i = 0; i < user_count; i++) {
        if (strcmp(connected_users[i], argp->username) == 0) {
            /* Décaler les utilisateurs suivants */
            for (j = i; j < user_count - 1; j++) {
                strcpy(connected_users[j], connected_users[j + 1]);
            }
            user_count--;
            result = 1;
            
            printf("[SERVEUR] ✓ %s déconnecté(e) (%d utilisateurs restants)\n", 
                   argp->username, user_count);
            
            /* Message système */
            if (message_count < MAX_STORED_MESSAGES) {
                strcpy(messages_history[message_count].username, "SYSTÈME");
                snprintf(messages_history[message_count].contenu, MAX_MSG_LEN,
                        "%s a quitté le chat", argp->username);
                messages_history[message_count].timestamp = time(NULL);
                message_count++;
            }
            
            break;
        }
    }
    
    return &result;
}
```

## Étape 5 : Implémenter le client

Créez **`chat_client.c`** :

```c
#include "chat.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <pthread.h>
#include <time.h>

#define CLEAR_SCREEN "\033[2J\033[H"
#define COLOR_RESET "\033[0m"
#define COLOR_GREEN "\033[32m"
#define COLOR_BLUE "\033[34m"
#define COLOR_YELLOW "\033[33m"
#define COLOR_CYAN "\033[36m"
#define COLOR_RED "\033[31m"

static CLIENT *clnt;
static char my_username[MAX_USERNAME_LEN];
static int last_message_index = 0;
static int running = 1;

/* Fonction pour afficher l'heure */
void print_time(int timestamp) {
    time_t t = timestamp;
    struct tm *tm_info = localtime(&t);
    printf("%s[%02d:%02d:%02d]%s ", 
           COLOR_CYAN, tm_info->tm_hour, tm_info->tm_min, tm_info->tm_sec, COLOR_RESET);
}

/* Thread pour récupérer les nouveaux messages */
void *receive_messages(void *arg) {
    message_list *messages;
    int i;
    
    while (running) {
        messages = get_messages_1(&last_message_index, clnt);
        
        if (messages != NULL && messages->count > 0) {
            for (i = 0; i < messages->messages.messages_len; i++) {
                message *msg = &messages->messages.messages_val[i];
                
                print_time(msg->timestamp);
                
                if (strcmp(msg->username, "SYSTÈME") == 0) {
                    printf("%s[%s]%s %s\n", 
                           COLOR_YELLOW, msg->username, COLOR_RESET, msg->contenu);
                } else if (strcmp(msg->username, my_username) == 0) {
                    printf("%s[Moi]%s %s\n", 
                           COLOR_GREEN, COLOR_RESET, msg->contenu);
                } else {
                    printf("%s[%s]%s %s\n", 
                           COLOR_BLUE, msg->username, COLOR_RESET, msg->contenu);
                }
                
                last_message_index++;
            }
            fflush(stdout);
        }
        
        sleep(1);  /* Vérifier toutes les secondes */
    }
    
    return NULL;
}

/* Fonction pour afficher les utilisateurs connectés */
void show_users() {
    user_list *users = get_users_1(NULL, clnt);
    int i;
    
    if (users != NULL && users->count > 0) {
        printf("\n%s╔═══════════════════════════════╗%s\n", COLOR_CYAN, COLOR_RESET);
        printf("%s║   Utilisateurs connectés (%d)  ║%s\n", COLOR_CYAN, users->count, COLOR_RESET);
        printf("%s╚═══════════════════════════════╝%s\n", COLOR_CYAN, COLOR_RESET);
        
        /* IMPORTANT: Selon chat.x, la structure est:
         * struct user_list {
         *     struct {
         *         u_int usernames_len;
         *         char **usernames_val;
         *     } usernames;
         *     int count;
         * };
         */
        for (i = 0; i < users->usernames.usernames_len; i++) {
            if (strcmp(users->usernames.usernames_val[i], my_username) == 0) {
                printf("  %s• %s (vous)%s\n", 
                       COLOR_GREEN, users->usernames.usernames_val[i], COLOR_RESET);
            } else {
                printf("  %s• %s%s\n", 
                       COLOR_BLUE, users->usernames.usernames_val[i], COLOR_RESET);
            }
        }
        printf("\n");
    }
}

/* Fonction principale du chat */
void chat_prog_1(char *host)
{
    user_info user;
    register_response *reg_response;
    chat_message msg;
    pthread_t receive_thread;
    char input[MAX_MSG_LEN];
    
    /* Création du client RPC */
    clnt = clnt_create(host, CHAT_PROG, CHAT_VERS, "tcp");
    if (clnt == NULL) {
        clnt_pcreateerror(host);
        exit(1);
    }
    
    /* Demander le nom d'utilisateur */
    printf("%s╔═══════════════════════════════════════╗%s\n", COLOR_CYAN, COLOR_RESET);
    printf("%s║        CHAT RPC - CONNEXION           ║%s\n", COLOR_CYAN, COLOR_RESET);
    printf("%s╚═══════════════════════════════════════╝%s\n", COLOR_CYAN, COLOR_RESET);
    printf("\nEntrez votre nom d'utilisateur : ");
    fgets(my_username, MAX_USERNAME_LEN, stdin);
    my_username[strcspn(my_username, "\n")] = 0;  /* Enlever le \n */
    
    /* S'enregistrer sur le serveur */
    strcpy(user.username, my_username);
    reg_response = register_user_1(&user, clnt);
    
    if (reg_response == NULL) {
        clnt_perror(clnt, "Erreur lors de l'inscription");
        exit(1);
    }
    
    if (!reg_response->success) {
        printf("%s✗ Erreur : %s%s\n", COLOR_RED, reg_response->message, COLOR_RESET);
        exit(1);
    }
    
    printf("%s✓ %s%s\n", COLOR_GREEN, reg_response->message, COLOR_RESET);
    sleep(1);
    
    /* Effacer l'écran */
    printf(CLEAR_SCREEN);
    
    /* Afficher le header */
    printf("%s╔═══════════════════════════════════════╗%s\n", COLOR_CYAN, COLOR_RESET);
    printf("%s║            CHAT RPC - ACTIF           ║%s\n", COLOR_CYAN, COLOR_RESET);
    printf("%s╚═══════════════════════════════════════╝%s\n", COLOR_CYAN, COLOR_RESET);
    printf("%sCommandes : /users (liste), /quit (quitter)%s\n\n", 
           COLOR_YELLOW, COLOR_RESET);
    
    /* Démarrer le thread de réception */
    pthread_create(&receive_thread, NULL, receive_messages, NULL);
    
    /* Boucle principale pour envoyer des messages */
    strcpy(msg.username, my_username);
    
    while (running) {
        printf("%s> %s", COLOR_GREEN, COLOR_RESET);
        fflush(stdout);
        
        if (fgets(input, MAX_MSG_LEN, stdin) == NULL) {
            break;
        }
        
        input[strcspn(input, "\n")] = 0;  /* Enlever le \n */
        
        if (strlen(input) == 0) {
            continue;
        }
        
        /* Commandes spéciales */
        if (strcmp(input, "/quit") == 0) {
            printf("\n%sDéconnexion...%s\n", COLOR_YELLOW, COLOR_RESET);
            break;
        }
        
        if (strcmp(input, "/users") == 0) {
            show_users();
            continue;
        }
        
        /* Envoyer le message */
        strcpy(msg.contenu, input);
        int *result = send_message_1(&msg, clnt);
        
        if (result == NULL) {
            clnt_perror(clnt, "Erreur lors de l'envoi du message");
        }
    }
    
    /* Déconnexion */
    running = 0;
    pthread_join(receive_thread, NULL);
    
    disconnect_user_1(&user, clnt);
    clnt_destroy(clnt);
    
    printf("%s✓ Déconnecté du serveur. Au revoir !%s\n", COLOR_GREEN, COLOR_RESET);
}

int main(int argc, char *argv[])
{
    char *host;
    
    if (argc < 2) {
        printf("Usage: %s <serveur>\n", argv[0]);
        printf("Exemple: %s localhost\n", argv[0]);
        exit(1);
    }
    
    host = argv[1];
    chat_prog_1(host);
    
    return 0;
}
```

## Étape 6 : Compilation

```bash
# Installer les dépendances si nécessaire
sudo apt-get install libtirpc-dev rpcbind

# Nettoyer
make -f Makefile.chat clean

# Compiler
make -f Makefile.chat
```

## Étape 7 : Démarrer rpcbind

```bash
sudo service rpcbind start
sudo service rpcbind status
```

## Étape 8 : Lancer le serveur

**Terminal 1 - Serveur** :
```bash
./chat_server
```

Vous verrez :
```
Waiting for requests...
```

## Étape 9 : Lancer plusieurs clients

**Terminal 2 - Client Alice** :
```bash
./chat_client localhost
```

```
╔═══════════════════════════════════════╗
║        CHAT RPC - CONNEXION           ║
╚═══════════════════════════════════════╝

Entrez votre nom d'utilisateur : Alice
✓ Bienvenue dans le chat !

╔═══════════════════════════════════════╗
║            CHAT RPC - ACTIF           ║
╚═══════════════════════════════════════╝
Commandes : /users (liste), /quit (quitter)

[14:23:15][SYSTÈME] Alice a rejoint le chat
> 
```

**Terminal 3 - Client Bob** :
```bash
./chat_client localhost
```

```
Entrez votre nom d'utilisateur : Bob
✓ Bienvenue dans le chat !

[14:23:20][SYSTÈME] Bob a rejoint le chat
> 
```

**Terminal 4 - Client Charlie** :
```bash
./chat_client localhost
```

## Étape 10 : Utilisation

### Envoyer un message
Dans n'importe quel terminal client, tapez simplement votre message :
```
> Bonjour tout le monde !
```

**Tous les autres clients verront** :
```
[14:23:25][Alice] Bonjour tout le monde !
```

### Voir les utilisateurs connectés
```
> /users

╔═══════════════════════════════╗
║   Utilisateurs connectés (3)  ║
╚═══════════════════════════════╝
  • Alice (vous)
  • Bob
  • Charlie
```

### Conversation exemple

**Alice** :
```
> Salut, quelqu'un est là ?
```

**Bob voit** :
```
[14:24:10][Alice] Salut, quelqu'un est là ?
```

**Bob répond** :
```
> Oui je suis là ! Ça va ?
```

**Alice voit** :
```
[14:24:15][Bob] Oui je suis là ! Ça va ?
```

**Charlie rejoint** :
```
[14:24:20][SYSTÈME] Charlie a rejoint le chat
```

**Charlie** :
```
> Coucou les amis !
```

**Tout le monde voit** :
```
[14:24:25][Charlie] Coucou les amis !
```

### Quitter le chat
```
> /quit

Déconnexion...
✓ Déconnecté du serveur. Au revoir !
```

**Les autres clients voient** :
```
[14:25:00][SYSTÈME] Alice a quitté le chat
```

## Côté serveur - Logs

Le serveur affiche tous les événements :
```
[SERVEUR] Demande d'inscription de : Alice
[SERVEUR] ✓ Alice connecté(e) (1 utilisateurs)

[SERVEUR] Demande d'inscription de : Bob
[SERVEUR] ✓ Bob connecté(e) (2 utilisateurs)

[MESSAGE] Alice: Salut, quelqu'un est là ?
[MESSAGE] Bob: Oui je suis là ! Ça va ?

[SERVEUR] Demande d'inscription de : Charlie
[SERVEUR] ✓ Charlie connecté(e) (3 utilisateurs)

[MESSAGE] Charlie: Coucou les amis !

[SERVEUR] Déconnexion de : Alice
[SERVEUR] ✓ Alice déconnecté(e) (2 utilisateurs restants)
```

## Résumé des étapes

| Étape | Action | Commande |
|-------|--------|----------|
| 1 | Créer `chat.x` | - |
| 2 | Générer squelettes | `rpcgen -a -C chat.x` |
| 3 | Modifier Makefile | Ajouter flags tirpc et pthread |
| 4 | Créer `chat_server.c` | Implémenter logique serveur |
| 5 | Créer `chat_client.c` | Implémenter interface client |
| 6 | Compiler | `make -f Makefile.chat` |
| 7 | Démarrer rpcbind | `sudo service rpcbind start` |
| 8 | Lancer serveur | `./chat_server` |
| 9 | Lancer clients | `./chat_client localhost` |
| 10 | Chatter ! | Tapez vos messages |

## Fonctionnalités

✅ Multi-clients simultanés  
✅ Messages en temps réel  
✅ Liste des utilisateurs connectés  
✅ Messages système (connexion/déconnexion)  
✅ Horodatage des messages  
✅ Interface colorée  
✅ Historique des messages  
✅ Commandes spéciales (/users, /quit)

## Dépannage

**Si "nom d'utilisateur déjà pris"** : Choisissez un autre nom

**Si les messages n'arrivent pas** : Vérifiez que rpcbind fonctionne

**Pour arrêter proprement** :
1. Clients : `/quit`
2. Serveur : `Ctrl+C`

Voilà ! Vous avez maintenant un chat multi-clients fonctionnel avec RPC ! 🎉💬
