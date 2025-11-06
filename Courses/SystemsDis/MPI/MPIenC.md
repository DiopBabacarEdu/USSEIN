
# MPI par l'exemple 

- Compilation : ``` mpicc Exercice.c -o Exercice ```
- Exécution : ``` mpirun -np 4 ./Exercice ```

## 📚 Liste des exercices
<img width="600" height="300" alt="image" src="https://github.com/user-attachments/assets/936453a5-6588-40eb-a3da-b634da92a8b8" />

## Installation de MPI
<img width="1000" height="900" alt="image" src="https://github.com/user-attachments/assets/3a3906d3-da3a-4abb-98d9-764c6a060192" />

##      
## Exercice 1 : Hello World parallèle
### Objectif - Comprendre $rank$, $size$, et $SPMD$

```C
#include <mpi.h>
#include <stdio.h>

int main(int argc, char** argv) {
    // Initialisation de MPI (obligatoire)
    MPI_Init(&argc, &argv);
    
    int rank, size;
    
    // Obtenir l'identifiant du processus
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    
    // Obtenir le nombre total de processus
    MPI_Comm_size(MPI_COMM_WORLD, &size);
    
    // Chaque processus affiche son rang
    printf("Bonjour ! Je suis le processus %d parmi %d\n", rank, size);
    
    // Finalisation de MPI (obligatoire)
    MPI_Finalize();
    return 0;
}
```
### Concepts clés :

- ```MPI_Init()``` : Initialise l'environnement MPI
- ```MPI_Comm_rank()``` : Donne l'identifiant unique du processus (0 à size-1)
- ```MPI_Comm_size()``` : Donne le nombre total de processus
- ```MPI_COMM_WORLD``` : Le communicateur par défaut (tous les processus)
- ```MPI_Finalize()``` : Nettoie l'environnement MPI
  

##      
## Exercice 2 : Processus maître-esclave
### Objectif - Différencier les rôles des processus

```C
#include <mpi.h>
#include <stdio.h>

int main(int argc, char** argv) {
    MPI_Init(&argc, &argv);
    
    int rank, size;
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &size);
    
    if (rank == 0) {
        // Le processus 0 est le maître
        printf("Je suis le MAÎTRE (processus 0)\n");
        printf("J'ai %d esclaves sous mes ordres\n", size - 1);
    } else {
        // Tous les autres sont des esclaves
        printf("Je suis un esclave (processus %d)\n", rank);
    }
    
    MPI_Finalize();
    return 0;
}
```
### Point important : 
Le modèle maître-esclave est très courant en MPI pour coordonner le travail.


##      
## Exercice 3 : Premier envoi/réception
### Objectif - Communication $point-à-point$ simple

```C
#include <mpi.h>
#include <stdio.h>

int main(int argc, char** argv) {
    MPI_Init(&argc, &argv);
    
    int rank;
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    
    int message;
    
    if (rank == 0) {
        // Processus 0 envoie
        message = 42;
        printf("Processus 0 : J'envoie %d au processus 1\n", message);
        MPI_Send(&message, 1, MPI_INT, 1, 0, MPI_COMM_WORLD);
    } 
    else if (rank == 1) {
        // Processus 1 reçoit
        MPI_Recv(&message, 1, MPI_INT, 0, 0, MPI_COMM_WORLD, MPI_STATUS_IGNORE);
        printf("Processus 1 : J'ai reçu %d\n", message);
    }
    
    MPI_Finalize();
    return 0;
}
```
### Paramètres de MPI_Send :

- ```&message``` : adresse des données à envoyer
- ```1``` : nombre d'éléments
- ```MPI_INT``` : type de données
- ```1``` : destination (rang du processus)
- ```0``` : tag (étiquette pour différencier les messages)
- ```MPI_COMM_WORLD``` : communicateur

### ⚠️Attention deadlock ! 
Si deux processus font Send en même temps vers l'autre, ils se bloqueront mutuellement.


##      
## Exercice 4 : Passage de jeton en anneau
### Objectif - Communications en chaîne
### Schéma :
<img width="1710" height="145" alt="image" src="https://github.com/user-attachments/assets/8e004357-aea1-46da-8313-6161fc044ba3" />

```C
#include <mpi.h>
#include <stdio.h>

void Jeton() {
    int rank, size;
    int jeton;
    
    MPI_Init(NULL, NULL);
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &size);
    
    if (rank == 0) {
        // Le processus 0 initialise le jeton
        jeton = 100;
        printf("Processus 0 : Je démarre le jeton avec valeur %d\n", jeton);
        
        // Envoie au suivant (processus 1)
        MPI_Send(&jeton, 1, MPI_INT, 1, 0, MPI_COMM_WORLD);
        
        // Reçoit du dernier processus (boucle l'anneau)
        MPI_Recv(&jeton, 1, MPI_INT, size - 1, 0, MPI_COMM_WORLD, MPI_STATUS_IGNORE);
        printf("Processus 0 : Le jeton est revenu avec valeur %d\n", jeton);
        
    } else {
        // Reçoit du processus précédent
        MPI_Recv(&jeton, 1, MPI_INT, rank - 1, 0, MPI_COMM_WORLD, MPI_STATUS_IGNORE);
        printf("Processus %d : J'ai reçu le jeton valeur %d\n", rank, jeton);
        
        // Incrémente le jeton
        jeton += rank;
        
        // Envoie au processus suivant (avec modulo pour boucler)
        int next = (rank + 1) % size;
        MPI_Send(&jeton, 1, MPI_INT, next, 0, MPI_COMM_WORLD);
    }
    
    MPI_Finalize();
}

int main(int argc, char** argv) {
    Jeton();  // Passage de jeton
    return 0;
}
```


##      
## Exercice 5 : Broadcast (diffusion)
### Objectif - Communication collective 1-vers-tous
### Schéma :
<img width="1712" height="322" alt="image" src="https://github.com/user-attachments/assets/1b90ed6c-8ded-4071-beec-3c1062fe4a87" />

```C
#include <mpi.h>
#include <stdio.h>

void CollectiveCommunication() {
    int rank, size;
    int valeur;
    
    MPI_Init(NULL, NULL);
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &size);
    
    if (rank == 0) {
        valeur = 777;
        printf("Processus 0 : Je broadcast la valeur %d à tous\n", valeur);
    }
    
    // MPI_Bcast diffuse la valeur depuis le processus 0 vers tous les autres
    // TOUS les processus doivent appeler MPI_Bcast (c'est une opération collective)
    MPI_Bcast(&valeur, 1, MPI_INT, 0, MPI_COMM_WORLD);
    
    // Maintenant tous les processus ont la même valeur
    printf("Processus %d : J'ai reçu la valeur %d par broadcast\n", rank, valeur);
    
    MPI_Finalize();
}

int main(int argc, char** argv) {
    CollectiveCommunication();  // Broadcast 
    return 0;
}
```
### Point clé : 
Les opérations collectives doivent être appelées par TOUS les processus.


##      
## Exercice 6 : Scatter (distribution)
### Objectif - Distribuer des données différentes
### Schéma:
<img width="1717" height="435" alt="image" src="https://github.com/user-attachments/assets/4d7fdc06-0c6e-4847-9f83-7f28e10347e7" />

```C
#include <mpi.h>
#include <stdio.h>

void ScatterExemple() {
    int rank, size;
    int data[4];      // Tableau sur le processus 0
    int local_data;   // Donnée reçue par chaque processus
    
    MPI_Init(NULL, NULL);
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &size);
    
    if (rank == 0) {
        // Le processus 0 prépare les données à distribuer
        data[0] = 10;
        data[1] = 20;
        data[2] = 30;
        data[3] = 40;
        printf("Processus 0 : Je distribue [10, 20, 30, 40]\n");
    }
    
    // MPI_Scatter distribue les données : processus i reçoit data[i]
    MPI_Scatter(data, 1, MPI_INT, &local_data, 1, MPI_INT, 0, MPI_COMM_WORLD);
    
    printf("Processus %d : J'ai reçu la valeur %d\n", rank, local_data);
    
    MPI_Finalize();
}
int main(int argc, char** argv) {
    ScatterExemple();  // DIstribution 
    return 0;
}
```

##      
## Exercice 7 : Gather (collecte)
### Objectif - Rassembler des résultats
### Schéma:
<img width="1705" height="445" alt="image" src="https://github.com/user-attachments/assets/44585045-9d0d-4ece-a07b-5f838b098f0a" />

```C
#include <mpi.h>
#include <stdio.h>

void GatherExemple() {
    int rank, size;
    int local_value;
    int results[4];  // Tableau pour collecter (seulement sur processus 0)
    
    MPI_Init(NULL, NULL);
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &size);
    
    // Chaque processus calcule sa propre valeur
    local_value = rank * rank;
    printf("Processus %d : Ma valeur est %d\n", rank, local_value);
    
    // MPI_Gather collecte toutes les valeurs sur le processus 0
    MPI_Gather(&local_value, 1, MPI_INT, results, 1, MPI_INT, 0, MPI_COMM_WORLD);
    
    if (rank == 0) {
        printf("Processus 0 : J'ai collecté les valeurs : ");
        for (int i = 0; i < size; i++) {
            printf("%d ", results[i]);
        }
        printf("\n");
    }
    
    MPI_Finalize();
}
int main(int argc, char** argv) {
    GatherExemple();  // Rassembler les résultats 
    return 0;
}
```

##      
## Exercice 8 : Reduce (réduction)
### Objectif - Calculer une opération (somme, max, min, etc.) sur toutes les valeurs
### Opérations disponibles :
- ```MPI_SUM``` : somme
- ```MPI_MAX``` : maximum
- ```MPI_MIN``` : minimum
- ```MPI_PROD``` : produit

```C
#include <mpi.h>
#include <stdio.h>

void ReduceExemple() {
    int rank, size;
    int local_value;
    int sum;
    
    MPI_Init(NULL, NULL);
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &size);
    
    // Chaque processus a une valeur locale
    local_value = rank + 1;  // Processus 0 a 1, processus 1 a 2, etc.
    printf("Processus %d : Ma contribution est %d\n", rank, local_value);
    
    // MPI_Reduce calcule la somme de toutes les valeurs locales
    // Le résultat est stocké sur le processus 0
    MPI_Reduce(&local_value, &sum, 1, MPI_INT, MPI_SUM, 0, MPI_COMM_WORLD);
    
    if (rank == 0) {
        printf("Processus 0 : La somme totale est %d\n", sum);
        // Avec 4 processus : 1+2+3+4 = 10
    }
    
    MPI_Finalize();
}
int main(int argc, char** argv) {
    ReduceExemple();  // Aggréger les résultats en une valeur 
    return 0;
}
```

##      
## Exercice 9 : Calcul parallèle de π
### Objectif - Projet intégrateur complet
#### Méthode : Monte Carlo
- Générer des points aléatoires dans un carré ```[0,1] × [0,1]```
- Compter combien sont dans le quart de cercle ```(x² + y² ≤ 1)```
- ```π ≈ 4 × (points dans le cercle / total de points)```
<img width="500" height="250" alt="image" src="https://github.com/user-attachments/assets/26e4877f-dd0e-4acc-9aa3-149c71b5383d" />

```C
#include <stdlib.h>
#include <time.h>
#include <mpi.h>
#include <stdio.h>

void MonteCarlo() {
    int rank, size;
    long long int local_count = 0;  // Points dans le cercle (local)
    long long int global_count = 0; // Points dans le cercle (total)
    long long int N = 10000000;      // Nombre de points par processus
    double x, y, pi_estimate;
    
    MPI_Init(NULL, NULL);
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &size);
    
    // Chaque processus initialise son générateur aléatoire différemment
    srand(time(NULL) + rank);
    
    // Chaque processus génère N points aléatoires
    for (long long int i = 0; i < N; i++) {
        // Générer un point aléatoire dans le carré [0,1] x [0,1]
        x = (double)rand() / RAND_MAX;
        y = (double)rand() / RAND_MAX;
        
        // Vérifier si le point est dans le quart de cercle
        if (x * x + y * y <= 1.0) {
            local_count++;
        }
    }
    
    printf("Processus %d : %lld points dans le cercle sur %lld\n", 
           rank, local_count, N);
    
    // Réduire pour obtenir le compte total
    MPI_Reduce(&local_count, &global_count, 1, MPI_LONG_LONG_INT, 
               MPI_SUM, 0, MPI_COMM_WORLD);
    
    if (rank == 0) {
        // π ≈ 4 * (nombre de points dans le cercle / nombre total de points)
        pi_estimate = 4.0 * global_count / (N * size);
        printf("\n=================================\n");
        printf("Estimation de π = %.10f\n", pi_estimate);
        printf("Valeur réelle    = 3.1415926536\n");
        printf("Erreur           = %.10f\n", pi_estimate - 3.1415926536);
        printf("=================================\n");
    }
    
    MPI_Finalize();
}
int main(int argc, char** argv) {
    MonteCarlo();  // Calculo de Pi
    return 0;
}
```

##      
## Exercice 10 : Mesure de performance
### Objectif - Comprendre le speedup et l'overhead
### Concepts :
- Speedup : ```T₁/Tₙ``` (idéalement égal à n)
- Efficacité : ```Speedup / n```
- Overhead : temps perdu en communications

```C
void Exercice10() {
    int rank, size;
    double start_time, end_time, local_time, max_time;
    long long int sum = 0;
    
    MPI_Init(NULL, NULL);
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &size);
    
    // Barrière pour synchroniser tous les processus avant de commencer
    MPI_Barrier(MPI_COMM_WORLD);
    start_time = MPI_Wtime();  // Temps de début
    
    // Calcul intensif : somme des carrés
    long long int N = 100000000 / size;  // Diviser le travail
    for (long long int i = rank * N; i < (rank + 1) * N; i++) {
        sum += i * i;
    }
    
    end_time = MPI_Wtime();  // Temps de fin
    local_time = end_time - start_time;
    
    // Trouver le temps maximum (le processus le plus lent)
    MPI_Reduce(&local_time, &max_time, 1, MPI_DOUBLE, MPI_MAX, 0, MPI_COMM_WORLD);
    
    if (rank == 0) {
        printf("Temps d'exécution avec %d processus : %.6f secondes\n", 
               size, max_time);
        printf("Exécutez avec différents nombres de processus pour voir le speedup!\n");
    }
    
    printf("Processus %d : somme locale = %lld (temps: %.6f s)\n", 
           rank, sum, local_time);
    
    MPI_Finalize();
}
```
### Expérience : 
Exécutez avec 1, 2, 4, 8 processus et comparez les temps d'éxécution.

## Résumé de quelques commandes essentielles
```C
# Configuration système
lscpu                              # Info CPU
nproc                              # Nombre de cœurs
free -h                            # Mémoire disponible
uname -a                           # Info système

# MPI
mpicc --version                    # Version compilateur
mpirun --version                   # Version runtime
ompi_info                          # Info détaillées OpenMPI

# Compilation
mpicc -Wall -O3 prog.c -o prog    # Optimisé
mpicc -g prog.c -o prog           # Debug

# Exécution
mpirun -np 4 ./prog               # Standard
mpirun -np 4 --report-bindings    # Voir placement
mpirun -np 4 -v                   # Verbose

# Monitoring
htop                              # Interactif
top                               # Classique
time mpirun -np 4 ./prog         # Mesurer temps
perf stat mpirun -np 4 ./prog    # Statistiques CPU

# Debug
gdb ./prog                        # Debugger
valgrind ./prog                   # Fuites mémoire
mpirun -np 2 valgrind ./prog     # MPI + valgrind

# Performance
perf record mpirun -np 4 ./prog  # Enregistrer profil
perf report                       # Analyser profil
```

##      
## NOTES PÉDAGOGIQUES

### 1. Ordre d'apprentissage recommandé :
   - Exercices 1-2 : Comprendre le modèle SPMD
   - Exercice 3-4 : Communications point-à-point
   - Exercices 5-8 : Communications collectives
   - Exercice 9 : Application réelle
   - Exercice 10 : Analyse de performance

### 2. Erreurs courantes à éviter :
   - Oublier ```MPI_Init()``` ou ```MPI_Finalize()```
     <img width="1720" height="912" alt="image" src="https://github.com/user-attachments/assets/277263f3-f04a-476c-a431-49b0b026ed8b" />

   - Deadlock dans ```Send/Recv``` (tous attendent de recevoir)
     <img width="1712" height="1257" alt="image" src="https://github.com/user-attachments/assets/33023a56-6263-4aa4-80bd-9a67ecc3bcad" />

   - Ne pas appeler les opérations collectives par TOUS les processus
     <img width="1710" height="570" alt="image" src="https://github.com/user-attachments/assets/ceae55d0-166f-4d95-b54d-d263e66e5dd0" />

   - Utiliser la même seed pour ```rand()``` dans tous les processus
     <img width="1715" height="445" alt="image" src="https://github.com/user-attachments/assets/8eeac5d9-5542-4ef4-afef-589395188312" />


### 3. Pour aller plus loin
   - Utiliser ```MPI_Isend``` et ```MPI_Irecv``` (non-bloquants)
   - Créer des types de données personnalisés (```MPI_Type_create```)
   - Utiliser des communicateurs personnalisés
   - Implémenter des topologies (cartésiennes, graphes)

### 4. Exercices supplémentaires utiles
   - Multiplication matrice-vecteur parallèle
   - Tri fusion parallèle
   - Résolution de l'équation de la chaleur (Jacobi)
   - Recherche du minimum dans un grand tableau
