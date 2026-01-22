# Guide Docker pour étudiants : Java, MPI et Python

## Prérequis
- Docker installé sur votre machine
- Terminal/ligne de commande

---

## Exemple 1 : Image Java

### Méthode A : Téléchargement de l'image officielle

```bash
# Télécharger l'image Java OpenJDK
docker pull openjdk:17

# Vérifier que l'image est téléchargée
docker images | grep openjdk

# Tester l'image
docker run --rm openjdk:17 java -version

# Exécuter un conteneur interactif
docker run -it --name java-container openjdk:17 bash
```

**Exercice pratique :**
```bash
# Créer un fichier Hello.java
echo 'public class Hello { public static void main(String[] args) { System.out.println("Bonjour depuis Docker!"); } }' > Hello.java

# Compiler et exécuter
docker run --rm -v $(pwd):/app -w /app openjdk:17 javac Hello.java
docker run --rm -v $(pwd):/app -w /app openjdk:17 java Hello
```

### Méthode B : Construction avec Dockerfile

**Créer un fichier `Dockerfile-java` :**
```dockerfile
# Image de base
FROM openjdk:17

# Informations de maintenance
LABEL maintainer="etudiant@universite.sn"
LABEL description="Image Java pour cours Licence Informatique"

# Installer des outils utiles
RUN apt-get update && apt-get install -y \
    maven \
    vim \
    git \
    && rm -rf /var/lib/apt/lists/*

# Créer un répertoire de travail
WORKDIR /workspace

# Copier un exemple de code (optionnel)
COPY HelloWorld.java /workspace/

# Message de bienvenue
RUN echo 'echo "Image Java prête pour le développement!"' >> ~/.bashrc

# Commande par défaut
CMD ["bash"]
```

**Créer `HelloWorld.java` :**
```java
public class HelloWorld {
    public static void main(String[] args) {
        System.out.println("=================================");
        System.out.println("Bienvenue dans votre environnement Java!");
        System.out.println("Java version: " + System.getProperty("java.version"));
        System.out.println("=================================");
    }
}
```

**Construire et utiliser :**
```bash
# Construire l'image
docker build -f Dockerfile-java -t java-student:1.0 .

# Lancer le conteneur
docker run -it --name mon-java -v $(pwd):/workspace java-student:1.0

# Compiler et exécuter dans le conteneur
javac HelloWorld.java
java HelloWorld
```

---

## Exemple 2 : Image MPI (Message Passing Interface)

### Méthode A : Téléchargement de l'image officielle

```bash
# Télécharger une image avec OpenMPI
docker pull nlknguyen/alpine-mpich

# Vérifier l'installation
docker run --rm nlknguyen/alpine-mpich mpirun --version

# Tester avec un exemple
docker run -it --name mpi-container nlknguyen/alpine-mpich
```

### Méthode B : Construction avec Dockerfile

**Créer un fichier `Dockerfile-mpi` :**
```dockerfile
# Image de base Ubuntu
FROM ubuntu:22.04

# Informations
LABEL maintainer="etudiant@universite.sn"
LABEL description="Image MPI pour calcul parallèle - Licence Agrotic"

# Éviter les prompts interactifs
ENV DEBIAN_FRONTEND=noninteractive

# Installer OpenMPI et outils de développement
RUN apt-get update && apt-get install -y \
    build-essential \
    openmpi-bin \
    openmpi-common \
    libopenmpi-dev \
    gcc \
    g++ \
    vim \
    nano \
    && rm -rf /var/lib/apt/lists/*

# Créer un répertoire de travail
WORKDIR /mpi-programs

# Copier des exemples de programmes
COPY hello_mpi.c /mpi-programs/
COPY pi_calculation.c /mpi-programs/

# Script de compilation
RUN echo '#!/bin/bash\n\
echo "Compilation des programmes MPI..."\n\
mpicc -o hello_mpi hello_mpi.c\n\
mpicc -o pi_calculation pi_calculation.c\n\
echo "Compilation terminée!"' > /mpi-programs/compile.sh \
&& chmod +x /mpi-programs/compile.sh

# Variables d'environnement
ENV OMPI_ALLOW_RUN_AS_ROOT=1
ENV OMPI_ALLOW_RUN_AS_ROOT_CONFIRM=1

CMD ["bash"]
```

**Créer `hello_mpi.c` :**
```c
#include <mpi.h>
#include <stdio.h>

int main(int argc, char** argv) {
    MPI_Init(&argc, &argv);
    
    int world_size, world_rank;
    MPI_Comm_size(MPI_COMM_WORLD, &world_size);
    MPI_Comm_rank(MPI_COMM_WORLD, &world_rank);
    
    char processor_name[MPI_MAX_PROCESSOR_NAME];
    int name_len;
    MPI_Get_processor_name(processor_name, &name_len);
    
    printf("Bonjour du processus %d sur %d (machine: %s)\n", 
           world_rank, world_size, processor_name);
    
    MPI_Finalize();
    return 0;
}
```

**Créer `pi_calculation.c` :**
```c
#include <mpi.h>
#include <stdio.h>
#include <math.h>

int main(int argc, char** argv) {
    int n = 1000000; // Nombre d'intervalles
    double h, sum, pi, x;
    int i, rank, size;
    
    MPI_Init(&argc, &argv);
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &size);
    
    h = 1.0 / (double)n;
    sum = 0.0;
    
    for (i = rank; i < n; i += size) {
        x = h * ((double)i + 0.5);
        sum += 4.0 / (1.0 + x * x);
    }
    sum *= h;
    
    MPI_Reduce(&sum, &pi, 1, MPI_DOUBLE, MPI_SUM, 0, MPI_COMM_WORLD);
    
    if (rank == 0) {
        printf("Valeur approximative de Pi = %.16f\n", pi);
        printf("Erreur = %.16f\n", fabs(pi - M_PI));
    }
    
    MPI_Finalize();
    return 0;
}
```

**Construire et utiliser :**
```bash
# Construire l'image
docker build -f Dockerfile-mpi -t mpi-student:1.0 .

# Lancer le conteneur
docker run -it --name mon-mpi mpi-student:1.0

# Dans le conteneur, compiler et exécuter
./compile.sh
mpirun -np 4 ./hello_mpi
mpirun -np 4 ./pi_calculation
```

---

## Exemple 3 : Image Python

### Méthode A : Téléchargement de l'image officielle

```bash
# Télécharger Python 3.11
docker pull python:3.11

# Vérifier la version
docker run --rm python:3.11 python --version

# Tester avec un script simple
docker run --rm python:3.11 python -c "print('Bonjour Python!')"

# Mode interactif
docker run -it --name python-container python:3.11 python
```

**Exercice avec un script :**
```bash
# Créer un script Python
echo "import sys; print(f'Python {sys.version}'); print('Docker fonctionne!')" > test.py

# Exécuter le script
docker run --rm -v $(pwd):/app -w /app python:3.11 python test.py
```

### Méthode B : Construction avec Dockerfile

**Créer un fichier `Dockerfile-python` :**
```dockerfile
# Image de base
FROM python:3.11-slim

# Informations
LABEL maintainer="etudiant@universite.sn"
LABEL description="Image Python pour Data Science - Licence Informatique/Agrotic"

# Installer des dépendances système
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    git \
    vim \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Mettre à jour pip
RUN pip install --no-cache-dir --upgrade pip

# Installer les bibliothèques scientifiques courantes
RUN pip install --no-cache-dir \
    numpy \
    pandas \
    matplotlib \
    scipy \
    scikit-learn \
    jupyter \
    requests \
    beautifulsoup4

# Créer un répertoire de travail
WORKDIR /projects

# Copier des scripts d'exemple
COPY analyse_donnees.py /projects/
COPY requirements.txt /projects/

# Installer les dépendances supplémentaires
RUN pip install --no-cache-dir -r requirements.txt

# Exposer le port pour Jupyter
EXPOSE 8888

# Message de bienvenue
RUN echo 'echo "=== Environnement Python Data Science ==="' >> ~/.bashrc && \
    echo 'echo "Bibliothèques installées: numpy, pandas, matplotlib, scikit-learn"' >> ~/.bashrc && \
    echo 'echo "Lancez Jupyter: jupyter notebook --ip=0.0.0.0 --allow-root"' >> ~/.bashrc

CMD ["bash"]
```

**Créer `requirements.txt` :**
```
seaborn==0.12.2
plotly==5.18.0
openpyxl==3.1.2
xlrd==2.0.1
```

**Créer `analyse_donnees.py` :**
```python
#!/usr/bin/env python3
"""
Script d'exemple pour l'analyse de données
Cours de Licence Informatique/Agrotic
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def generer_donnees_agricoles():
    """Génère des données agricoles simulées"""
    np.random.seed(42)
    
    mois = ['Jan', 'Fev', 'Mar', 'Avr', 'Mai', 'Jun', 
            'Jul', 'Aou', 'Sep', 'Oct', 'Nov', 'Dec']
    
    data = {
        'Mois': mois,
        'Precipitation_mm': np.random.randint(20, 200, 12),
        'Temperature_C': np.random.randint(20, 35, 12),
        'Rendement_tonnes': np.random.uniform(2.5, 5.0, 12)
    }
    
    return pd.DataFrame(data)

def analyser_donnees(df):
    """Analyse statistique basique"""
    print("=== ANALYSE DES DONNÉES AGRICOLES ===\n")
    print("Aperçu des données:")
    print(df.head())
    print("\nStatistiques descriptives:")
    print(df.describe())
    print(f"\nMois le plus pluvieux: {df.loc[df['Precipitation_mm'].idxmax(), 'Mois']}")
    print(f"Rendement moyen: {df['Rendement_tonnes'].mean():.2f} tonnes")

def visualiser_donnees(df):
    """Crée des visualisations"""
    fig, axes = plt.subplots(2, 1, figsize=(10, 8))
    
    # Graphique 1: Précipitations
    axes[0].bar(df['Mois'], df['Precipitation_mm'], color='steelblue')
    axes[0].set_title('Précipitations mensuelles')
    axes[0].set_ylabel('Précipitations (mm)')
    
    # Graphique 2: Rendement
    axes[1].plot(df['Mois'], df['Rendement_tonnes'], 
                 marker='o', color='green', linewidth=2)
    axes[1].set_title('Rendement agricole mensuel')
    axes[1].set_ylabel('Rendement (tonnes)')
    axes[1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('analyse_agricole.png', dpi=300, bbox_inches='tight')
    print("\nGraphique sauvegardé: analyse_agricole.png")

if __name__ == "__main__":
    print("Génération des données...\n")
    donnees = generer_donnees_agricoles()
    
    analyser_donnees(donnees)
    visualiser_donnees(donnees)
    
    print("\n✓ Analyse terminée avec succès!")
```

**Construire et utiliser :**
```bash
# Construire l'image
docker build -f Dockerfile-python -t python-student:1.0 .

# Lancer le conteneur
docker run -it --name mon-python -v $(pwd):/projects python-student:1.0

# Dans le conteneur, exécuter le script
python analyse_donnees.py

# Lancer Jupyter (optionnel)
docker run -it -p 8888:8888 python-student:1.0 \
    jupyter notebook --ip=0.0.0.0 --allow-root --no-browser
```

---

## Commandes Docker utiles

```bash
# Lister toutes les images
docker images

# Lister les conteneurs actifs
docker ps

# Lister tous les conteneurs (actifs et arrêtés)
docker ps -a

# Arrêter un conteneur
docker stop <nom-conteneur>

# Supprimer un conteneur
docker rm <nom-conteneur>

# Supprimer une image
docker rmi <nom-image>

# Nettoyer les ressources inutilisées
docker system prune -a

# Voir les logs d'un conteneur
docker logs <nom-conteneur>

# Copier des fichiers vers/depuis un conteneur
docker cp fichier.txt mon-conteneur:/workspace/
docker cp mon-conteneur:/workspace/resultat.txt ./
```

---

## Exercices pratiques pour les étudiants

### Exercice 1 : Java
Créez une application Java qui calcule la factorielle d'un nombre et exécutez-la dans votre conteneur Docker.

### Exercice 2 : MPI
Modifiez le programme MPI pour calculer la somme des N premiers nombres en parallèle.

### Exercice 3 : Python
Créez un script qui analyse un fichier CSV de données agricoles réelles et génère des visualisations.

---

## Conseils

1. **Volumes** : Utilisez toujours `-v` pour monter vos fichiers locaux dans le conteneur
2. **Nettoyage** : Supprimez régulièrement les conteneurs et images inutilisés
3. **Documentation** : Commentez vos Dockerfiles pour faciliter la compréhension
4. **Sécurité** : Ne lancez pas les conteneurs en mode root en production
5. **Optimisation** : Ordonnez les commandes dans le Dockerfile du moins au plus changeant

---

**Bon apprentissage avec Docker ! 🐳**
