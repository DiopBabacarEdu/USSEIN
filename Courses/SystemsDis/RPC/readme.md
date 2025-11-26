# TP1: Développement d'une Application Client-Serveur avec RPC sur Linux

## Prérequis
- Une machine Linux (physique ou virtuelle)
- Accès aux droits administrateur (sudo)
- Connexion Internet pour l'installation des paquets

---

## Partie I : Installation et Configuration de rpcbind

### Étape 1 : Vérification de l'installation de rpcbind

Ouvrez un terminal et exécutez la commande suivante :

```bash
rpcinfo
```

**Commentaire :** Cette commande liste les services RPC enregistrés. Si rpcbind est installé et actif, vous verrez une liste des services disponibles.

### Étape 2 : Installation de rpcbind (si nécessaire)

Si la commande précédente retourne une erreur, installez rpcbind :

```bash
# Mise à jour de la liste des paquets disponibles
sudo apt-get update

# Installation du paquet rpcbind
sudo apt-get install rpcbind
```

**Commentaire :** 
- `apt-get update` : Met à jour l'index des paquets
- `apt-get install rpcbind` : Installe le service rpcbind nécessaire pour RPC

### Étape 3 : Vérification finale

```bash
rpcinfo
```

**Commentaire :** Vérifiez que la commande fonctionne correctement maintenant.

---

## Partie II : Création du Projet Client-Serveur

### Objectif du Projet
Créer une application client-serveur qui effectue l'addition de deux nombres via RPC.

### Étape 1 : Création de l'arborescence du projet

```bash
# Retour au répertoire home de l'utilisateur
cd ~

# Création du répertoire du projet
sudo mkdir newrpc

# Attribution des droits d'écriture (IMPORTANT pour éviter les problèmes de permissions)
sudo chmod 777 newrpc

# Déplacement dans le répertoire
cd newrpc
```

**Commentaire :** 
- `cd ~` : Retourne au répertoire personnel (/home/votre_utilisateur)
- `chmod 777` : Donne tous les droits sur le dossier (lecture, écriture, exécution)
- Cette étape évite les erreurs de permissions lors de la compilation

### Étape 2 : Création du fichier de définition RPC (add.x)

```bash
# Création du fichier avec gedit (ou nano si vous préférez)
gedit add.x
```

**Contenu du fichier add.x :**

```c
/* 
 * Fichier de définition RPC pour l'addition de deux nombres
 * IMPORTANT : Respectez scrupuleusement l'indentation et les espaces
 */

/* Définition de la structure qui contient les deux nombres à additionner */
struct numbers {
    int num1;  /* Premier nombre */
    int num2;  /* Deuxième nombre */
};

/* Définition du programme RPC */
program ADDITION {
    /* Définition de la version du programme */
    version ADDITION_1 {
        /* Déclaration de la procédure distante ADD
         * Elle prend en paramètre une structure 'numbers'
         * Elle retourne un entier (int)
         * Le numéro 1 identifie cette procédure
         */
        int ADD(numbers) = 1;
    } = 1;  /* Numéro de version */
} = 0x2fffffff;  /* Numéro de programme (doit être unique) */
```

**⚠️ ATTENTION - Points critiques :**
1. Utilisez des espaces, PAS de tabulations
2. Respectez exactement les espaces avant et après les signes `=`
3. N'oubliez pas les points-virgules (`;`)
4. Sauvegardez le fichier dans le répertoire `newrpc`

### Étape 3 : Compilation du fichier add.x avec rpcgen

```bash
# Assurez-vous d'être dans le bon répertoire
pwd  # Devrait afficher : /home/votre_utilisateur/newrpc

# Si vous n'y êtes pas :
cd ~/newrpc

# Génération des fichiers stubs avec rpcgen
rpcgen -a -C add.x
```

**Commentaire :** 
- `-a` : Génère tous les fichiers (client, serveur, Makefile)
- `-C` : Génère du code conforme au standard ANSI C
- Cette commande crée automatiquement 5 fichiers essentiels

### Étape 4 : Fichiers générés (explication détaillée)

Après la compilation, vous devriez voir ces fichiers :

1. **add.h** : Fichier d'en-tête
   - Contient les définitions de structures
   - Définit les constantes (numéros de programme et version)
   - Déclare les prototypes de fonctions

2. **add_client.c** : Programme client
   - Contient le stub client
   - Gère la connexion au serveur
   - Appelle les procédures distantes

3. **add_server.c** : Programme serveur
   - Contient le stub serveur
   - Reçoit les appels RPC
   - Dirige vers les fonctions appropriées

4. **add_xdr.c** : Routines de sérialisation
   - Convertit les données en format XDR (External Data Representation)
   - Assure la compatibilité entre différentes architectures

5. **Makefile.add** : Fichier de compilation
   - Contient les instructions pour compiler le projet

### Étape 5 : Compilation initiale

```bash
# Compilation avec make
make -f Makefile.add
```

**Commentaire :** 
- Cette commande compile tous les fichiers source
- Génère les exécutables `add_client` et `add_server`
- Si des erreurs apparaissent, vérifiez le fichier add.x

### Étape 6 : Test de base

**Terminal 1 (Serveur) :**
```bash
# Démarrage du serveur (nécessite sudo pour bind sur les ports RPC)
sudo ./add_server
```

**Terminal 2 (Client) :**
```bash
# Exécution du client (se connecte au serveur)
sudo ./add_client localhost
```

**Commentaire :** 
- Le serveur doit être démarré EN PREMIER
- Si aucun message d'erreur n'apparaît, la compilation est réussie
- `localhost` indique que le serveur est sur la même machine

---

## Partie III : Implémentation de la Logique Métier

### Étape 1 : Modification du fichier client (add_client.c)

```bash
# Ouverture du fichier avec nano ou gedit
nano add_client.c
```

**Remplacez tout le contenu par :**

```c
/*
 * Programme Client RPC - Addition de deux nombres
 * Ce client envoie deux nombres au serveur et reçoit leur somme
 */

#include "add.h"

void
add_prog_1(char *host)
{
    CLIENT *clnt;           /* Pointeur vers la structure client RPC */
    int *result_1;          /* Pointeur pour stocker le résultat */
    intpair add_1_arg;      /* Structure contenant les arguments (a et b) */

#ifndef DEBUG
    /* 
     * Création de la connexion client RPC
     * - host : adresse du serveur
     * - ADD_PROG : numéro du programme (défini dans add.h)
     * - ADD_VERS : version du programme
     * - "udp" : protocole de transport
     */
    clnt = clnt_create(host, ADD_PROG, ADD_VERS, "udp");
    
    /* Vérification de la connexion */
    if (clnt == NULL) {
        clnt_pcreateerror(host);  /* Affiche l'erreur de connexion */
        exit(1);
    }
#endif /* DEBUG */

    /* 
     * Initialisation des valeurs à envoyer au serveur
     * Vous pouvez modifier ces valeurs pour tester
     */
    add_1_arg.a = 123;  /* Premier nombre */
    add_1_arg.b = 100;  /* Deuxième nombre */

    /* 
     * Appel de la procédure distante ADD
     * - add_1 : fonction stub générée par rpcgen
     * - &add_1_arg : pointeur vers la structure avec les arguments
     * - clnt : handle du client
     */
    result_1 = add_1(&add_1_arg, clnt);
    
    /* Vérification du résultat */
    if (result_1 == (int *)NULL) {
        /* L'appel RPC a échoué */
        clnt_perror(clnt, "call failed");
    }
    else {
        /* Affichage du résultat */
        printf("Résultat de l'addition : %d\n", *result_1);
    }

#ifndef DEBUG
    /* Libération des ressources RPC */
    clnt_destroy(clnt);
#endif /* DEBUG */
}

int
main(int argc, char *argv[])
{
    char *host;

    /* 
     * Vérification des arguments de ligne de commande
     * Le programme attend l'adresse du serveur en argument
     */
    if (argc < 2) {
        printf("Usage: %s server_host\n", argv[0]);
        printf("Exemple: %s localhost\n", argv[0]);
        exit(1);
    }
    
    /* Récupération de l'adresse du serveur */
    host = argv[1];
    
    /* Appel de la fonction principale du client */
    add_prog_1(host);
    
    exit(0);
}
```

### Étape 2 : Modification du fichier serveur (add_server.c)

```bash
# Ouverture du fichier
nano add_server.c
```

**Recherchez la fonction `add_1_svc` et remplacez-la par :**

```c
/*
 * Programme Serveur RPC - Addition de deux nombres
 * Cette fonction est appelée automatiquement quand le client invoque ADD
 */

#include "add.h"

int *
add_1_svc(intpair *argp, struct svc_req *rqstp)
{
    /* 
     * Variable statique pour stocker le résultat
     * IMPORTANT : doit être static car on retourne son adresse
     * Une variable locale serait détruite à la fin de la fonction
     */
    static int result;

    /* Affichage côté serveur */
    printf("========================================\n");
    printf("Demande d'addition reçue du client\n");
    printf("Paramètres reçus : %d + %d\n", argp->a, argp->b);
    
    /* 
     * Calcul de l'addition
     * argp->a : premier nombre (provient de la structure intpair)
     * argp->b : deuxième nombre
     */
    result = argp->a + argp->b;
    
    /* Affichage du résultat côté serveur */
    printf("Résultat calculé : %d\n", result);
    printf("========================================\n");
    
    /* 
     * Retour de l'adresse du résultat
     * Le système RPC se charge de renvoyer cette valeur au client
     */
    return &result;
}
```

### Étape 3 : Recompilation du projet

```bash
# IMPORTANT : Utilisez Makefile.add, pas juste Makefile
make -f Makefile.add clean   # Nettoie les anciens fichiers compilés
make -f Makefile.add         # Recompile tout le projet
```

**Commentaire :**
- `clean` : Supprime les anciens fichiers objets (.o) et exécutables
- Cela évite les conflits avec d'anciennes versions compilées

---

## Partie IV : Exécution et Test de l'Application

### Étape 1 : Démarrage du serveur

**Terminal 1 :**
```bash
# Démarrage du serveur RPC
./add_server
```

**Commentaire :** 
- Le serveur se met en attente de connexions
- Il n'affiche rien tant qu'aucun client ne se connecte
- Laissez ce terminal ouvert

### Étape 2 : Exécution du client

**Terminal 2 :**
```bash
# Exécution du client (connexion à localhost)
./add_client localhost
```

**Résultat attendu :**

**Terminal Serveur :**
```
========================================
Demande d'addition reçue du client
Paramètres reçus : 123 + 100
Résultat calculé : 223
========================================
```

**Terminal Client :**
```
Résultat de l'addition : 223
```

---

## Résolution des Problèmes Courants

### Erreur 1 : "Cannot register service"

```bash
# Vérifier si rpcbind est actif
sudo systemctl status rpcbind

# Si inactif, le démarrer
sudo systemctl start rpcbind

# Pour qu'il démarre automatiquement au boot
sudo systemctl enable rpcbind
```

### Erreur 2 : "Permission denied"

```bash
# Donner les droits d'exécution
chmod +x add_server add_client

# Ou exécuter avec sudo
sudo ./add_server
```

### Erreur 3 : Erreurs de compilation "undefined reference"

```bash
# Recompiler en forçant le nettoyage
make -f Makefile.add clean
make -f Makefile.add

# Si le problème persiste, vérifier que add.h est bien inclus dans les .c
```

### Erreur 4 : "intpair undeclared"

**Solution :** 
- Le fichier add.h n'a pas défini `intpair`
- Régénérer les fichiers : `rpcgen -a -C add.x`
- Vérifier que `struct numbers` dans add.x est correct

### Erreur 5 : Serveur ne répond pas

```bash
# Vérifier que le serveur écoute
rpcinfo -p localhost

# Redémarrer rpcbind si nécessaire
sudo systemctl restart rpcbind
```

---

## Exercices d'Extension

### Exercice 1 : Modifier les valeurs
Modifiez les valeurs dans `add_client.c` (lignes avec `add_1_arg.a` et `add_1_arg.b`) pour tester d'autres additions.

### Exercice 2 : Ajouter une soustraction
1. Ajoutez une nouvelle procédure `SUB` dans `add.x`
2. Régénérez les fichiers avec `rpcgen`
3. Implémentez la fonction `sub_1_svc` dans le serveur

### Exercice 3 : Saisie interactive
Modifiez le client pour demander les nombres à l'utilisateur avec `scanf()`.

---

## Nettoyage Final

```bash
# Pour arrêter le serveur : Ctrl+C dans le terminal du serveur

# Pour supprimer tous les fichiers générés
cd ~/newrpc
make -f Makefile.add clean

# Pour supprimer complètement le projet
cd ~
rm -rf newrpc
```

---

## Résumé des Commandes Essentielles

| Commande | Description |
|----------|-------------|
| `rpcgen -a -C add.x` | Génère tous les fichiers nécessaires |
| `make -f Makefile.add` | Compile le projet |
| `make -f Makefile.add clean` | Nettoie les fichiers compilés |
| `./add_server` | Lance le serveur |
| `./add_client localhost` | Lance le client |
| `rpcinfo -p` | Liste les services RPC actifs |

---

## Conclusion

Vous avez maintenant une application client-serveur fonctionnelle utilisant RPC. Cette architecture permet à des programmes sur des machines différentes de communiquer facilement. RPC est utilisé dans de nombreux systèmes distribués modernes.

**Points clés à retenir :**
- Le fichier `.x` définit l'interface du service
- `rpcgen` génère automatiquement le code de communication
- Le serveur implémente la logique métier
- Le client appelle les fonctions distantes comme des fonctions locales
- XDR assure la compatibilité entre différentes architectures

---

**Auteur du tutoriel** | **Date de mise à jour :** 2025
