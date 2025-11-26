# TP RPC avec rpcbind sur Linux
## Introduction
Ce TP explique comment installer et utiliser ``` rpcbind ``` sur une machine virtuelle Linux pour créer une application client-serveur RPC (Remote Procedure Call) simple qui effectue l'addition de deux nombres.

## Contexte et Évolution de RPC

### Contexte Historique

RPC (Remote Procedure Call) est un protocole historique développé dans les années 1980 par Sun Microsystems (maintenant Oracle). Il permet à un programme d'exécuter une procédure sur une machine distante comme si elle était locale, masquant ainsi la complexité des communications réseau. Pendant des décennies, RPC a été la pierre angulaire des systèmes distribués dans les environnements UNIX/Linux.

### Qui utilise encore RPC aujourd'hui ?

**Legacy et systèmes embarqués :**
- **NFS (Network File System)** : La version v3 utilise encore RPC
- **Systèmes financiers et bancaires** : Certains systèmes legacy
- **Environnements industriels** : Automatisation, SCADA
- **Calcul haute performance** : Quelques clusters scientifiques

### Évolutions et Remplacements

**gRPC (Google RPC)** : La révolution moderne
- Développé par Google en 2015
- Utilise HTTP/2 et Protocol Buffers
- Multiplateforme, multilingage
- Performances bien supérieures

**Autres alternatives modernes :**
- **Apache Thrift** (Facebook)
- **JSON-RPC** / **REST APIs**
- **WebSocket** pour les communications temps réel

### Pourquoi l'étudier aujourd'hui ?

Bien que considéré comme "legacy", RPC reste essentiel à comprendre car :

1. **Fondations conceptuelles** : Les concepts de RPC sous-tendent les technologies modernes
2. **Maintenance de systèmes existants** : De nombreux systèmes critiques l'utilisent encore
3. **Pédagogie** : Excellent pour comprendre les principes des appels de procédure distants
4. **Transition** : Comprendre RPC aide à apprécier les avantages des solutions modernes

RPCbind représente donc une pièce importante de l'histoire de l'informatique distribuée, dont les principes fondamentaux continuent d'influencer les technologies contemporaines.


## Partie I : Installation de rpcbind sur Linux

### Vérification/Installation de rpcbind

Ouvrez un terminal et tapez la commande suivante :

```bash
$ rpcinfo
```

Si rpcbind est installé, vous verrez une liste des services RPC enregistrés.

Si rpcbind n'est pas installé, utilisez les commandes suivantes (adaptées selon votre distribution) :

**Pour les distributions basées sur Debian/Ubuntu :**
```bash
$ sudo apt-get update
$ sudo apt-get install rpcbind
```

**Pour les distributions basées sur Red Hat/CentOS :**
```bash
$ sudo yum update
$ sudo yum install rpcbind
# ou pour les versions récentes
$ sudo dnf install rpcbind
```

**Pour les distributions basées sur Arch Linux :**
```bash
$ sudo pacman -Syu
$ sudo pacman -S rpcbind
```

Vérifiez à nouveau l'installation avec :
```bash
$ rpcinfo
```

### Création du projet

Créez un répertoire pour votre projet :

```bash
$ cd /home
$ sudo mkdir newrpc
$ cd newrpc
```

### Création du fichier de définition RPC

Créez un fichier `add.x` avec le contenu suivant :

```c
struct numbers {
    int num1;
    int num2;
};

program ADDITION {
    version ADDITION_1 {
        int ADD(numbers) = 1;
    } = 1;
} = 0x2fffffff;
```

**Note importante :** Respectez bien l'indentation et les espaces.

### Compilation du fichier add.x

Assurez-vous d'être dans le répertoire `newrpc` :

```bash
$ pwd
```

Si nécessaire, revenez au répertoire :
```bash
$ cd
$ cd newrpc
```

Compilez le fichier add.x :

```bash
$ rpcgen -a -C add.x
```

L'option `-C` indique à rpcgen de générer du code C conforme à la norme ANSI C.

### Fichiers générés

rpcgen génère plusieurs fichiers :

- **add.h** : Fichier d'en-tête contenant les définitions de structures et constantes
- **add_server.c** : Code squelette du serveur
- **add_client.c** : Code squelette du client
- **add_xdr.c** : Code pour la sérialisation/désérialisation des données
- **Makefile.add** : Makefile pour la compilation

### Compilation des fichiers

Compilez les fichiers générés :

```bash
$ make -f Makefile.add
```

Vous devriez voir une sortie similaire à :

```bash
cc -g    -c -o add_clnt.o add_clnt.c
cc -g    -c -o add_client.o add_client.c
cc -g    -c -o add_xdr.o add_xdr.c
cc -g    -o add_client add_clnt.o add_client.o add_xdr.o -lnsl
cc -g    -c -o add_svc.o add_svc.c
cc -g    -c -o add_server.o add_server.c
cc -g    -o add_server add_svc.o add_server.o add_xdr.o -lnsl
```

### Exécution des programmes

**Terminal 1 (Serveur) :**
```bash
$ sudo ./add_server
```

**Terminal 2 (Client) :**
```bash
$ sudo ./add_client localhost
```

## Partie II : Personnalisation de l'application

### Modification du fichier add_client.c

Remplacez le contenu de `add_client.c` par :

```c
/*
 * Code client RPC pour effectuer une addition distante
 * Généré par rpcgen et modifié pour l'exemple
 */

#include "add.h"   // Contient les définitions RPC (ADDITION, ADDITION_1, structures)
#include <stdio.h>

/**
 * Fonction principale du client RPC
 * @param host : adresse du serveur distant
 */
void add_prog_1(char *host)
{
    CLIENT *clnt;        // Handle du client RPC
    int *result_1;       // Pointeur vers le résultat de l'addition
    numbers add_1_arg;   // Structure contenant les deux nombres à additionner

#ifndef DEBUG
    // Création du client RPC avec le protocole UDP
    // ADDITION : identifiant du programme RPC
    // ADDITION_1 : version du programme
    clnt = clnt_create(host, ADDITION, ADDITION_1, "udp");
    
    // Vérification de la création du client
    if (clnt == NULL) {
        clnt_pcreateerror(host);  // Affiche l'erreur de création
        exit(1);
    }
#endif /* DEBUG */

    // Préparation des données à envoyer au serveur
    add_1_arg.num1 = 123;  // Premier nombre
    add_1_arg.num2 = 100;  // Deuxième nombre
    
    // Appel de la procédure distante add_1() sur le serveur
    // Envoie la structure add_1_arg et reçoit un pointeur vers le résultat
    result_1 = add_1(&add_1_arg, clnt);
    
    // Vérification du résultat de l'appel RPC
    if (result_1 == (int *) NULL) {
        // L'appel a échoué
        clnt_perror(clnt, "call failed");
    } else {
        // L'appel a réussi, affichage du résultat (devrait être 223)
        printf("Résultat de l'addition : %d\n", *result_1);
    }

#ifndef DEBUG
    // Libération des ressources allouées au client RPC
    clnt_destroy(clnt);
#endif /* DEBUG */
}

/**
 * Point d'entrée du programme
 * @param argc : nombre d'arguments
 * @param argv : tableau des arguments (argv[1] = adresse du serveur)
 */
int main(int argc, char *argv[])
{
    char *host;

    // Vérification du nombre d'arguments
    // Le programme nécessite l'adresse du serveur en paramètre
    if (argc < 2) {
        printf("Usage: %s server_host\n", argv[0]);
        exit(1);
    }
    
    // Récupération de l'adresse du serveur depuis les arguments
    host = argv[1];
    
    // Appel de la fonction principale du client RPC
    add_prog_1(host);
    
    exit(0);  // Fin normale du programme
}
```

### Modification du fichier add_server.c

Remplacez le contenu de `add_server.c` par :

```c
/*
 * This is sample code generated by rpcgen.
 * These are only templates and you can use them
 * as a guideline for developing your own functions.
 */

#include "add.h"
#include <stdio.h>

int *add_1_svc(numbers *argp, struct svc_req *rqstp)
{
    static int result;

    printf("Addition de deux entiers\n");
    printf("Paramètres : %d, %d\n", argp->num1, argp->num2);
    result = argp->num1 + argp->num2;
    printf("Résultat = %d\n", result);
    return &result;
}
```

### Recompilation

Recompilez les fichiers modifiés :

```bash
$ make -f Makefile.add
```

### Test de l'application

**Terminal 1 (Serveur) :**
```bash
$ ./add_server
```

**Terminal 2 (Client) :**
```bash
$ ./add_client localhost
```

Vous devriez voir le résultat de l'addition s'afficher.

## Partie III : Versions à jour et bonnes pratiques

### Commandes modernes pour rpcbind

**Vérification du statut de rpcbind :**
```bash
$ sudo systemctl status rpcbind
```

**Démarrage de rpcbind :**
```bash
$ sudo systemctl start rpcbind
```

**Activation au démarrage :**
```bash
$ sudo systemctl enable rpcbind
```

### Sécurité et bonnes pratiques

1. **Configuration du firewall :**
```bash
$ sudo ufw allow 111/tcp
$ sudo ufw allow 111/udp
```

2. **Vérification des services RPC :**
```bash
$ rpcinfo -p
```

3. **Utilisation de TCP au lieu d'UDP** (plus fiable) :
Modifiez la ligne dans `add_client.c` :
```c
clnt = clnt_create(host, ADDITION, ADDITION_1, "tcp");
```

### Script de compilation amélioré

Créez un fichier `compile.sh` :

```bash
#!/bin/bash

echo "Nettoyage des anciens fichiers..."
make -f Makefile.add clean

echo "Génération du code RPC..."
rpcgen -a -C add.x

echo "Compilation..."
make -f Makefile.add

echo "Vérification des exécutables..."
if [ -f "add_client" ] && [ -f "add_server" ]; then
    echo "Compilation réussie!"
    echo "Pour tester :"
    echo "Terminal 1: ./add_server"
    echo "Terminal 2: ./add_client localhost"
else
    echo "Erreur lors de la compilation"
fi
```

Rendez-le exécutable :
```bash
$ chmod +x compile.sh
```

### Dépannage

**Erreurs courantes et solutions :**

1. **"rpcbind: command not found"** : Réinstallez rpcbind
2. **"Connection refused"** : Vérifiez que le serveur est démarré
3. **"Program not registered"** : Redémarrez le serveur
4. **Problèmes de compilation** : Vérifiez que les packages de développement sont installés
   ```bash
   $ sudo apt-get install build-essential
   ```

## Conclusion

Ce TP vous a guidé à travers l'installation de rpcbind, la création d'une application client-serveur RPC simple, et la personnalisation du code généré. Les principes présentés ici peuvent être étendus pour créer des applications RPC plus complexes.

Pour aller plus loin, consultez la documentation de rpcgen avec :
```bash
$ man rpcgen
```
