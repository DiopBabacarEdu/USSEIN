# Projet : Conception d'un Système de Vote Distribué avec RPC (rpcgen)

## Contexte

Dans les systèmes distribués modernes, plusieurs utilisateurs peuvent interagir simultanément avec une application distante. Les mécanismes comme RPC (Remote Procedure Call) permettent d'appeler des fonctions sur un serveur comme si elles étaient locales.

Dans ce projet, vous allez concevoir un système de vote distribué, permettant à plusieurs clients de voter à distance via un serveur RPC.

---

## Objectifs du Projet

À la fin de ce projet, vous serez capable de :
- Comprendre le fonctionnement de RPC et de rpcgen
- Définir une interface de service RPC avec fichiers .x
- Implémenter un serveur RPC multiclients
- Développer des clients RPC pour consommer le service
- Gérer la concurrence et la synchronisation dans un système distribué
- Tester et déboguer une application distribuée

---

## Architecture Générale

```
┌─────────────┐         RPC         ┌──────────────┐
│   Client 1  │ ◄────────────────►  │              │
└─────────────┘                     │   Serveur    │
                                    │   RPC        │
┌─────────────┐                     │              │
│   Client 2  │ ◄────────────────►  │  (Port 9999) │
└─────────────┘                     │              │
                                    └──────────────┘
┌─────────────┐
│   Client n  │ ◄────────────────►
└─────────────┘
```

## Spécifications Fonctionnelles

### Fonctionnalités Requises

1. **Authentification Client**
   - Chaque client doit fournir un identifiant unique (ID utilisateur)
   - Vérification que l'utilisateur n'a pas déjà voté

2. **Gestion des Scrutins**
   - Créer un scrutin avec plusieurs options de vote
   - Exemple : scrutin présidentiel avec 3 candidats

3. **Enregistrement des Votes**
   - Un client peut voter une seule fois par scrutin
   - Le serveur enregistre le vote de manière sécurisée

4. **Consultation des Résultats**
   - Afficher les résultats en temps réel
   - Format : nombre de votes par option

5. **Gestion d'Erreurs**
   - Refuser un vote en double
   - Gérer les erreurs de communication réseau

---

## 🔧 Phase 1 : Définition de l'Interface RPC

### Fichier : `vote.x`

```c
/* vote.x - Définition de l'interface RPC */

const MAX_CANDIDATS = 5;
const MAX_ID_LENGTH = 50;
const MAX_CANDIDAT_LENGTH = 50;

/* Structure pour représenter un candidat */
struct Candidat {
    int id;
    char nom[MAX_CANDIDAT_LENGTH];
    int votes;
};

/* Structure pour un scrutin */
struct Scrutin {
    int scrutin_id;
    char titre[MAX_CANDIDAT_LENGTH];
    int nb_candidats;
    Candidat candidats[MAX_CANDIDATS];
    int total_votes;
};

/* Structure pour réponse du serveur */
struct ResultatVote {
    int success;      /* 1 = succès, 0 = erreur */
    char message[100];
};

/* Structure pour réponse des résultats */
struct Resultats {
    Scrutin scrutin;
    int est_termine;
};

/* Définition des procédures RPC */
program VOTE_PROG {
    version VOTE_VERS {
        /* Initialiser un nouveau scrutin */
        Scrutin INITIALISER_SCRUTIN(int) = 1;
        
        /* Voter pour un candidat */
        ResultatVote VOTER(int, int, string) = 2;
        
        /* Obtenir les résultats */
        Resultats OBTENIR_RESULTATS(int) = 3;
        
        /* Réinitialiser le scrutin */
        int REINITIALISER(int) = 4;
        
    } = 1;
} = 0x20000001;
```

---

## Phase 2 : Implémentation du Serveur RPC

### Fichier : `vote_server.c`

```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <pthread.h>
#include "vote.h"

#define NB_SCRUTINS_MAX 10

/* Structure interne pour gérer les votes */
typedef struct {
    Scrutin scrutin;
    char* electeurs_ayant_vote[1000];  /* Liste des IDs ayant voté */
    int nb_electeurs;
    pthread_mutex_t lock;               /* Verrou pour concurrence */
} ScrutinGere;

ScrutinGere scrutins[NB_SCRUTINS_MAX];
int nb_scrutins = 0;
pthread_mutex_t scrutins_lock = PTHREAD_MUTEX_INITIALIZER;

/* Vérifier si un électeur a déjà voté */
int a_deja_vote(int scrutin_id, const char* id_electeur) {
    ScrutinGere* s = &scrutins[scrutin_id];
    for (int i = 0; i < s->nb_electeurs; i++) {
        if (strcmp(s->electeurs_ayant_vote[i], id_electeur) == 0) {
            return 1;
        }
    }
    return 0;
}

/* Enregistrer un électeur */
void enregistrer_electeur(int scrutin_id, const char* id_electeur) {
    ScrutinGere* s = &scrutins[scrutin_id];
    s->electeurs_ayant_vote[s->nb_electeurs] = 
        malloc(strlen(id_electeur) + 1);
    strcpy(s->electeurs_ayant_vote[s->nb_electeurs], id_electeur);
    s->nb_electeurs++;
}

/* RPC : Initialiser un scrutin */
Scrutin * initialiser_scrutin_1_svc(int scrutin_id, 
                                     struct svc_req *rqstp) {
    static Scrutin resultat;
    
    pthread_mutex_lock(&scrutins_lock);
    
    if (scrutin_id < 0 || scrutin_id >= NB_SCRUTINS_MAX) {
        pthread_mutex_unlock(&scrutins_lock);
        return NULL;
    }
    
    resultat.scrutin_id = scrutin_id;
    strcpy(resultat.titre, "Élection Présidentielle 2024");
    resultat.nb_candidats = 3;
    
    /* Initialiser les candidats */
    resultat.candidats[0].id = 1;
    strcpy(resultat.candidats[0].nom, "Alice");
    resultat.candidats[0].votes = 0;
    
    resultat.candidats[1].id = 2;
    strcpy(resultat.candidats[1].nom, "Bob");
    resultat.candidats[1].votes = 0;
    
    resultat.candidats[2].id = 3;
    strcpy(resultat.candidats[2].nom, "Charlie");
    resultat.candidats[2].votes = 0;
    
    resultat.total_votes = 0;
    
    /* Initialiser la structure scrutin géré */
    scrutins[scrutin_id].scrutin = resultat;
    scrutins[scrutin_id].nb_electeurs = 0;
    pthread_mutex_init(&scrutins[scrutin_id].lock, NULL);
    
    pthread_mutex_unlock(&scrutins_lock);
    return &resultat;
}

/* RPC : Voter */
ResultatVote * voter_1_svc(int scrutin_id, int candidat_id, 
                            char** id_electeur, 
                            struct svc_req *rqstp) {
    static ResultatVote resultat;
    
    if (scrutin_id < 0 || scrutin_id >= nb_scrutins) {
        resultat.success = 0;
        strcpy(resultat.message, "Scrutin introuvable");
        return &resultat;
    }
    
    pthread_mutex_lock(&scrutins[scrutin_id].lock);
    
    /* Vérifier si le client a déjà voté */
    if (a_deja_vote(scrutin_id, *id_electeur)) {
        resultat.success = 0;
        strcpy(resultat.message, "Vous avez déjà voté!");
        pthread_mutex_unlock(&scrutins[scrutin_id].lock);
        return &resultat;
    }
    
    /* Vérifier que le candidat existe */
    if (candidat_id < 1 || candidat_id > scrutins[scrutin_id].scrutin.nb_candidats) {
        resultat.success = 0;
        strcpy(resultat.message, "Candidat inexistant");
        pthread_mutex_unlock(&scrutins[scrutin_id].lock);
        return &resultat;
    }
    
    /* Enregistrer le vote */
    scrutins[scrutin_id].scrutin.candidats[candidat_id - 1].votes++;
    scrutins[scrutin_id].scrutin.total_votes++;
    enregistrer_electeur(scrutin_id, *id_electeur);
    
    resultat.success = 1;
    strcpy(resultat.message, "Vote enregistré avec succès");
    
    printf("[SERVEUR] Électeur %s a voté pour %s\n", 
           *id_electeur, 
           scrutins[scrutin_id].scrutin.candidats[candidat_id - 1].nom);
    
    pthread_mutex_unlock(&scrutins[scrutin_id].lock);
    return &resultat;
}

/* RPC : Obtenir les résultats */
Resultats * obtenir_resultats_1_svc(int scrutin_id, 
                                     struct svc_req *rqstp) {
    static Resultats resultat;
    
    if (scrutin_id < 0 || scrutin_id >= nb_scrutins) {
        return NULL;
    }
    
    pthread_mutex_lock(&scrutins[scrutin_id].lock);
    resultat.scrutin = scrutins[scrutin_id].scrutin;
    resultat.est_termine = 0;  /* À implémenter selon besoin */
    pthread_mutex_unlock(&scrutins[scrutin_id].lock);
    
    return &resultat;
}

/* RPC : Réinitialiser */
int * reinitialiser_1_svc(int scrutin_id, struct svc_req *rqstp) {
    static int resultat = 0;
    
    if (scrutin_id < 0 || scrutin_id >= nb_scrutins) {
        return &resultat;
    }
    
    pthread_mutex_lock(&scrutins[scrutin_id].lock);
    
    /* Réinitialiser tous les votes */
    for (int i = 0; i < scrutins[scrutin_id].scrutin.nb_candidats; i++) {
        scrutins[scrutin_id].scrutin.candidats[i].votes = 0;
    }
    scrutins[scrutin_id].scrutin.total_votes = 0;
    scrutins[scrutin_id].nb_electeurs = 0;
    
    resultat = 1;
    printf("[SERVEUR] Scrutin %d réinitialisé\n", scrutin_id);
    
    pthread_mutex_unlock(&scrutins[scrutin_id].lock);
    return &resultat;
}

/* Fonction principale du serveur */
int main(int argc, char *argv[]) {
    register SVCXPRT *transp;
    
    pmap_unset(VOTE_PROG, VOTE_VERS);
    
    transp = svcudp_create(RPC_ANYSOCK);
    if (transp == NULL) {
        fprintf(stderr, "Impossible de créer le service UDP\n");
        exit(1);
    }
    
    if (!svc_register(transp, VOTE_PROG, VOTE_VERS, 
                      vote_prog_1, IPPROTO_UDP)) {
        fprintf(stderr, "Impossible d'enregistrer le service\n");
        exit(1);
    }
    
    printf("[SERVEUR] Serveur de vote démarré sur le port 9999\n");
    printf("[SERVEUR] En attente de clients...\n");
    
    svc_run();
    fprintf(stderr, "svc_run retournée\n");
    exit(1);
}
```

---

## Phase 3 : Implémentation des Clients RPC

### Fichier : `vote_client.c`

```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "vote.h"

#define SERVEUR "localhost"

void afficher_resultats(Resultats* res) {
    printf("\n═══════════════════════════════════════════════════\n");
    printf("       RÉSULTATS DU SCRUTIN : %s\n", res->scrutin.titre);
    printf("═══════════════════════════════════════════════════\n");
    printf("Total de votes : %d\n\n", res->scrutin.total_votes);
    
    for (int i = 0; i < res->scrutin.nb_candidats; i++) {
        double pourcentage = (res->scrutin.total_votes > 0) ? 
            (res->scrutin.candidats[i].votes * 100.0) / res->scrutin.total_votes : 0;
        
        printf("%s : %d votes (%.1f%%)\n", 
               res->scrutin.candidats[i].nom,
               res->scrutin.candidats[i].votes,
               pourcentage);
    }
    printf("═══════════════════════════════════════════════════\n\n");
}

int main(int argc, char *argv[]) {
    CLIENT *clnt;
    ResultatVote *vote_result_p;
    Resultats *resultats_p;
    Scrutin *scrutin_p;
    char id_electeur[MAX_ID_LENGTH];
    int scrutin_id = 0;
    int candidat_id;
    int choix;
    
    if (argc > 1) {
        strncpy(id_electeur, argv[1], MAX_ID_LENGTH - 1);
        id_electeur[MAX_ID_LENGTH - 1] = '\0';
    } else {
        printf("Entrez votre identifiant d'électeur : ");
        fgets(id_electeur, MAX_ID_LENGTH, stdin);
        id_electeur[strcspn(id_electeur, "\n")] = '\0';
    }
    
    /* Créer une connexion RPC */
    clnt = clnt_create(SERVEUR, VOTE_PROG, VOTE_VERS, "udp");
    if (clnt == NULL) {
        clnt_pcreateerror(SERVEUR);
        exit(1);
    }
    
    printf("\n[CLIENT %s] Connecté au serveur de vote\n", id_electeur);
    
    /* Initialiser un scrutin */
    scrutin_p = initialiser_scrutin_1(scrutin_id, clnt);
    if (scrutin_p == NULL) {
        clnt_perror(clnt, "Erreur initialisation");
        exit(1);
    }
    
    printf("\nScrution : %s\n", scrutin_p->titre);
    printf("Candidats disponibles :\n");
    for (int i = 0; i < scrutin_p->nb_candidats; i++) {
        printf("  %d. %s\n", i + 1, scrutin_p->candidats[i].nom);
    }
    
    /* Menu principal */
    while (1) {
        printf("\n--- Menu ---\n");
        printf("1. Voter\n");
        printf("2. Voir les résultats\n");
        printf("3. Quitter\n");
        printf("Choix : ");
        scanf("%d", &choix);
        getchar();  /* Consommer le '\n' */
        
        switch (choix) {
            case 1:
                printf("Entrez le numéro du candidat (1-%d) : ", 
                       scrutin_p->nb_candidats);
                scanf("%d", &candidat_id);
                getchar();
                
                vote_result_p = voter_1(scrutin_id, candidat_id, 
                                       &id_electeur, clnt);
                if (vote_result_p == NULL) {
                    clnt_perror(clnt, "Erreur vote");
                } else {
                    if (vote_result_p->success) {
                        printf("✓ %s\n", vote_result_p->message);
                    } else {
                        printf("✗ Erreur : %s\n", vote_result_p->message);
                    }
                }
                break;
                
            case 2:
                resultats_p = obtenir_resultats_1(scrutin_id, clnt);
                if (resultats_p == NULL) {
                    clnt_perror(clnt, "Erreur résultats");
                } else {
                    afficher_resultats(resultats_p);
                }
                break;
                
            case 3:
                printf("[CLIENT] Déconnexion...\n");
                clnt_destroy(clnt);
                exit(0);
                
            default:
                printf("Choix invalide\n");
        }
    }
    
    return 0;
}
```
## Phase 4 : Compilation et Exécution

### Étapes de Compilation

```bash
# 1. Générer les fichiers stub avec rpcgen
rpcgen -C vote.x

# 2. Compiler le serveur
gcc -o vote_server vote_server.c vote_svc.c vote_xdr.c -lpthread

# 3. Compiler les clients
gcc -o vote_client vote_client.c vote_clnt.c vote_xdr.c

# 4. Lancer le serveur (Terminal 1)
./vote_server

# 5. Lancer les clients (Terminal 2, 3, etc.)
./vote_client Alice
./vote_client Bob
./vote_client Charlie
```

## Phase 5 : Tests et Scénarios

### Scénario 1 : Vote Basique
```
Électeur 1 (Alice)   → vote pour Alice
Électeur 2 (Bob)     → vote pour Bob
Électeur 3 (Charlie) → vote pour Alice
```
**Résultat attendu** : Alice 2 votes, Bob 1 vote, Charlie 0 vote

### Scénario 2 : Double Vote (Sécurité)
```
Électeur 1 → vote pour Alice
Électeur 1 → essaie de voter pour Bob
```
**Résultat attendu** : Erreur "Vous avez déjà voté!"

### Scénario 3 : Candidat Invalide
```
Électeur 1 → essaie de voter pour candidat 10
```
**Résultat attendu** : Erreur "Candidat inexistant"

### Scénario 4 : Charge (10 clients simultanés)
```
Lancer 10 clients différents simultanément et vérifier
que tous les votes sont correctement enregistrés.
```
**Résultat attendu** : Total votes = 10, répartition correcte


## Améliorations Possibles (Bonus)

1. **Authentification Sécurisée**
   - Implémenter un système de tokens
   - Validation des identifiants

2. **Persistance des Données**
   - Sauvegarder les résultats dans une base de données
   - Reprendre après redémarrage du serveur

3. **Interface Web**
   - Frontend JavaScript/HTML pour cliente RPC
   - Dashboard de visualisation des résultats en temps réel

4. **Chiffrement**
   - Implémenter HTTPS pour RPC
   - Chiffrer les communications

5. **Audit et Logs**
   - Enregistrer tous les votes dans un fichier
   - Logs détaillés du serveur

6. **Gestion de Multiples Scrutins**
   - Permettre plusieurs élections simultanées
   - Gestion d'électeurs par scrutin

## Livrables Attendus

**Code Source**
   - `vote.x` (interface RPC)
   - `vote_server.c` (serveur)
   - `vote_client.c` (clients)
   - `Makefile` pour compilation


## Questions de Réflexion

1. Pourquoi utiliser les verrous (mutex) dans le serveur ?
2. Comment garantir l'atomicité d'un vote en contexte distribué ?
3. Quels sont les problèmes potentiels avec UDP vs TCP pour RPC ?
4. Comment améliorer la sécurité du système ?
5. Comment supporter des millions d'électeurs simultanément ?

## Ressources Utiles

- Documentation rpcgen : `man rpcgen`
- Tutoriels RPC : https://docs.oracle.com/cd/E19683-01/816-1435/rpc/
