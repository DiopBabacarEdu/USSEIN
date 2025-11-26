# TP2: Service de Calcul RPC Complet

Je vais créer un service RPC qui expose plusieurs opérations mathématiques (addition, soustraction, multiplication, division, puissance).

## Étape 1 : Créer le fichier de définition RPC

Créez un fichier **`calcul.x`** :

```c
/* Fichier calcul.x - Définition du service de calcul RPC */

/* Structure pour passer deux entiers */
struct operandes {
    int a;
    int b;
};

/* Structure pour le résultat avec gestion d'erreur */
struct resultat {
    int valeur;
    int code_erreur;  /* 0 = OK, 1 = erreur division par zéro */
};

/* Définition du programme RPC */
program CALCUL_PROG {
    version CALCUL_VERS {
        int ADDITION(operandes) = 1;
        int SOUSTRACTION(operandes) = 2;
        int MULTIPLICATION(operandes) = 3;
        resultat DIVISION(operandes) = 4;
        int PUISSANCE(operandes) = 5;
        int MODULO(operandes) = 6;
    } = 1;  /* Version 1 */
} = 0x20000001;  /* Numéro de programme unique */
```

## Étape 2 : Générer les fichiers squelettes

```bash
rpcgen -a -C calcul.x
```

Cette commande génère automatiquement :
- `calcul.h` - Fichier d'en-tête
- `calcul_clnt.c` - Stubs client
- `calcul_svc.c` - Stubs serveur
- `calcul_xdr.c` - Fonctions de sérialisation
- `calcul_client.c` - Squelette du client (à compléter)
- `calcul_server.c` - Squelette du serveur (à compléter)
- `Makefile.calcul` - Makefile

## Étape 3 : Modifier le Makefile

Éditez **`Makefile.calcul`** pour ajouter le support de `libtirpc` :

```makefile
# Makefile.calcul
CLIENT = calcul_client
SERVER = calcul_server
SOURCES_CLNT.c =
SOURCES_CLNT.h =
SOURCES_SVC.c =
SOURCES_SVC.h =
SOURCES.x = calcul.x
TARGETS_SVC.c = calcul_svc.c calcul_server.c calcul_xdr.c
TARGETS_CLNT.c = calcul_clnt.c calcul_client.c calcul_xdr.c
TARGETS = calcul.h calcul_xdr.c calcul_clnt.c calcul_svc.c calcul_client.c calcul_server.c
OBJECTS_CLNT = $(SOURCES_CLNT.c:%.c=%.o) $(TARGETS_CLNT.c:%.c=%.o)
OBJECTS_SVC = $(SOURCES_SVC.c:%.c=%.o) $(TARGETS_SVC.c:%.c=%.o)

# Compiler flags
CFLAGS += -g -I/usr/include/tirpc
LDLIBS += -ltirpc
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

Créez/modifiez **`calcul_server.c`** :

```c
#include "calcul.h"
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

/* Fonction pour l'addition */
int *
addition_1_svc(operandes *argp, struct svc_req *rqstp)
{
    static int result;
    
    printf("\n=== ADDITION ===\n");
    printf("Paramètres : %d + %d\n", argp->a, argp->b);
    
    result = argp->a + argp->b;
    
    printf("Résultat : %d\n", result);
    printf("================\n");
    
    return &result;
}

/* Fonction pour la soustraction */
int *
soustraction_1_svc(operandes *argp, struct svc_req *rqstp)
{
    static int result;
    
    printf("\n=== SOUSTRACTION ===\n");
    printf("Paramètres : %d - %d\n", argp->a, argp->b);
    
    result = argp->a - argp->b;
    
    printf("Résultat : %d\n", result);
    printf("====================\n");
    
    return &result;
}

/* Fonction pour la multiplication */
int *
multiplication_1_svc(operandes *argp, struct svc_req *rqstp)
{
    static int result;
    
    printf("\n=== MULTIPLICATION ===\n");
    printf("Paramètres : %d * %d\n", argp->a, argp->b);
    
    result = argp->a * argp->b;
    
    printf("Résultat : %d\n", result);
    printf("======================\n");
    
    return &result;
}

/* Fonction pour la division avec gestion d'erreur */
resultat *
division_1_svc(operandes *argp, struct svc_req *rqstp)
{
    static resultat result;
    
    printf("\n=== DIVISION ===\n");
    printf("Paramètres : %d / %d\n", argp->a, argp->b);
    
    if (argp->b == 0) {
        printf("ERREUR : Division par zéro !\n");
        result.valeur = 0;
        result.code_erreur = 1;
    } else {
        result.valeur = argp->a / argp->b;
        result.code_erreur = 0;
        printf("Résultat : %d\n", result.valeur);
    }
    
    printf("================\n");
    
    return &result;
}

/* Fonction pour la puissance */
int *
puissance_1_svc(operandes *argp, struct svc_req *rqstp)
{
    static int result;
    int i;
    
    printf("\n=== PUISSANCE ===\n");
    printf("Paramètres : %d ^ %d\n", argp->a, argp->b);
    
    result = 1;
    for (i = 0; i < argp->b; i++) {
        result *= argp->a;
    }
    
    printf("Résultat : %d\n", result);
    printf("=================\n");
    
    return &result;
}

/* Fonction pour le modulo */
int *
modulo_1_svc(operandes *argp, struct svc_req *rqstp)
{
    static int result;
    
    printf("\n=== MODULO ===\n");
    printf("Paramètres : %d %% %d\n", argp->a, argp->b);
    
    if (argp->b == 0) {
        printf("ERREUR : Modulo par zéro !\n");
        result = 0;
    } else {
        result = argp->a % argp->b;
        printf("Résultat : %d\n", result);
    }
    
    printf("==============\n");
    
    return &result;
}
```

## Étape 5 : Implémenter le client

Créez/modifiez **`calcul_client.c`** :

```c
#include "calcul.h"
#include <stdio.h>
#include <stdlib.h>

void afficher_menu() {
    printf("\n╔════════════════════════════════════════╗\n");
    printf("║     SERVICE DE CALCUL RPC              ║\n");
    printf("╚════════════════════════════════════════╝\n");
    printf("  1. Addition\n");
    printf("  2. Soustraction\n");
    printf("  3. Multiplication\n");
    printf("  4. Division\n");
    printf("  5. Puissance\n");
    printf("  6. Modulo\n");
    printf("  0. Quitter\n");
    printf("────────────────────────────────────────\n");
}

void calcul_prog_1(char *host)
{
    CLIENT *clnt;
    int *result_int;
    resultat *result_div;
    operandes args;
    int choix;
    
    /* Création du client RPC */
    clnt = clnt_create(host, CALCUL_PROG, CALCUL_VERS, "tcp");
    if (clnt == NULL) {
        clnt_pcreateerror(host);
        exit(1);
    }
    
    printf("✓ Connexion établie avec le serveur %s\n", host);
    
    while (1) {
        afficher_menu();
        printf("Votre choix : ");
        scanf("%d", &choix);
        
        if (choix == 0) {
            printf("\n👋 Au revoir !\n");
            break;
        }
        
        printf("\nEntrez le premier nombre : ");
        scanf("%d", &args.a);
        printf("Entrez le deuxième nombre : ");
        scanf("%d", &args.b);
        
        switch (choix) {
            case 1:  /* Addition */
                result_int = addition_1(&args, clnt);
                if (result_int == NULL) {
                    clnt_perror(clnt, "Erreur lors de l'appel addition");
                } else {
                    printf("\n✓ Résultat : %d + %d = %d\n", 
                           args.a, args.b, *result_int);
                }
                break;
                
            case 2:  /* Soustraction */
                result_int = soustraction_1(&args, clnt);
                if (result_int == NULL) {
                    clnt_perror(clnt, "Erreur lors de l'appel soustraction");
                } else {
                    printf("\n✓ Résultat : %d - %d = %d\n", 
                           args.a, args.b, *result_int);
                }
                break;
                
            case 3:  /* Multiplication */
                result_int = multiplication_1(&args, clnt);
                if (result_int == NULL) {
                    clnt_perror(clnt, "Erreur lors de l'appel multiplication");
                } else {
                    printf("\n✓ Résultat : %d * %d = %d\n", 
                           args.a, args.b, *result_int);
                }
                break;
                
            case 4:  /* Division */
                result_div = division_1(&args, clnt);
                if (result_div == NULL) {
                    clnt_perror(clnt, "Erreur lors de l'appel division");
                } else {
                    if (result_div->code_erreur == 0) {
                        printf("\n✓ Résultat : %d / %d = %d\n", 
                               args.a, args.b, result_div->valeur);
                    } else {
                        printf("\n✗ ERREUR : Division par zéro !\n");
                    }
                }
                break;
                
            case 5:  /* Puissance */
                result_int = puissance_1(&args, clnt);
                if (result_int == NULL) {
                    clnt_perror(clnt, "Erreur lors de l'appel puissance");
                } else {
                    printf("\n✓ Résultat : %d ^ %d = %d\n", 
                           args.a, args.b, *result_int);
                }
                break;
                
            case 6:  /* Modulo */
                result_int = modulo_1(&args, clnt);
                if (result_int == NULL) {
                    clnt_perror(clnt, "Erreur lors de l'appel modulo");
                } else {
                    printf("\n✓ Résultat : %d %% %d = %d\n", 
                           args.a, args.b, *result_int);
                }
                break;
                
            default:
                printf("\n✗ Choix invalide !\n");
        }
        
        printf("\nAppuyez sur Entrée pour continuer...");
        getchar();
        getchar();
    }
    
    clnt_destroy(clnt);
}

int main(int argc, char *argv[])
{
    char *host;
    
    if (argc < 2) {
        printf("Usage: %s <nom_serveur>\n", argv[0]);
        printf("Exemple: %s localhost\n", argv[0]);
        exit(1);
    }
    
    host = argv[1];
    calcul_prog_1(host);
    
    return 0;
}
```

## Étape 6 : Compilation

```bash
# Nettoyer les anciens fichiers
make -f Makefile.calcul clean

# Compiler le client et le serveur
make -f Makefile.calcul
```

Vous devriez voir :
```
rpcgen -C calcul.x
cc -g -I/usr/include/tirpc   -c -o calcul_clnt.o calcul_clnt.c
cc -g -I/usr/include/tirpc   -c -o calcul_client.o calcul_client.c
cc -g -I/usr/include/tirpc   -c -o calcul_xdr.o calcul_xdr.c
cc   calcul_clnt.o calcul_client.o calcul_xdr.o  -ltirpc -o calcul_client
cc -g -I/usr/include/tirpc   -c -o calcul_svc.o calcul_svc.c
cc -g -I/usr/include/tirpc   -c -o calcul_server.o calcul_server.c
cc   calcul_svc.o calcul_server.o calcul_xdr.o  -ltirpc -o calcul_server
```

## Étape 7 : Préparation de l'environnement

Avant de lancer les programmes, démarrez le service `rpcbind` :

```bash
sudo service rpcbind start
# ou
sudo systemctl start rpcbind
```

Vérifiez que le service est actif :
```bash
sudo service rpcbind status
```

## Étape 8 : Exécution

### Terminal 1 - Lancer le serveur

```bash
./calcul_server
```

Vous devriez voir :
```
Waiting for requests...
```

### Terminal 2 - Lancer le client

```bash
./calcul_client localhost
```

Vous verrez le menu interactif :
```
✓ Connexion établie avec le serveur localhost

╔════════════════════════════════════════╗
║     SERVICE DE CALCUL RPC              ║
╚════════════════════════════════════════╝
  1. Addition
  2. Soustraction
  3. Multiplication
  4. Division
  5. Puissance
  6. Modulo
  0. Quitter
────────────────────────────────────────
Votre choix :
```

## Étape 9 : Test des opérations

### Test 1 : Addition
```
Votre choix : 1
Entrez le premier nombre : 45
Entrez le deuxième nombre : 23

✓ Résultat : 45 + 23 = 68
```

**Côté serveur**, vous verrez :
```
=== ADDITION ===
Paramètres : 45 + 23
Résultat : 68
================
```

### Test 2 : Division normale
```
Votre choix : 4
Entrez le premier nombre : 100
Entrez le deuxième nombre : 5

✓ Résultat : 100 / 5 = 20
```

### Test 3 : Division par zéro
```
Votre choix : 4
Entrez le premier nombre : 50
Entrez le deuxième nombre : 0

✗ ERREUR : Division par zéro !
```

### Test 4 : Puissance
```
Votre choix : 5
Entrez le premier nombre : 2
Entrez le deuxième nombre : 10

✓ Résultat : 2 ^ 10 = 1024
```

## Étape 10 : Arrêt propre

1. **Quitter le client** : Choisissez l'option `0`
2. **Arrêter le serveur** : Appuyez sur `Ctrl+C` dans le terminal du serveur

## Résumé des étapes

| Étape | Commande | Description |
|-------|----------|-------------|
| 1 | Créer `calcul.x` | Définir l'interface RPC |
| 2 | `rpcgen -a -C calcul.x` | Générer les squelettes |
| 3 | Modifier `Makefile.calcul` | Ajouter flags tirpc |
| 4 | Créer `calcul_server.c` | Implémenter les fonctions serveur |
| 5 | Créer `calcul_client.c` | Implémenter le client |
| 6 | `make -f Makefile.calcul` | Compiler |
| 7 | `sudo service rpcbind start` | Démarrer rpcbind |
| 8 | `./calcul_server` | Lancer le serveur |
| 9 | `./calcul_client localhost` | Lancer le client |

## Dépannage

**Si le serveur ne démarre pas** :
```bash
# Vérifier si un autre serveur utilise le port
sudo netstat -tulpn | grep calcul_server

# Nettoyer les enregistrements RPC
rpcinfo -p
```

**Si la connexion échoue** :
```bash
# Vérifier que rpcbind fonctionne
sudo service rpcbind status

# Vérifier l'enregistrement du service
rpcinfo -p localhost
```

Voilà ! Vous avez maintenant un service RPC complet avec 6 opérations différentes ! 🎉
