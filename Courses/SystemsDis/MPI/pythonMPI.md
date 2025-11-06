# 🐍 Tutoriel MPI en Python avec mpi4py

> Série d'exercices progressifs pour apprendre la programmation parallèle avec mpi4py

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Language: Python](https://img.shields.io/badge/Language-Python-blue.svg)](https://www.python.org/)


## Introduction

Ce git est une adaptation en Python des exercices MPI originalement écrits en C. Python avec mpi4py offre une syntaxe plus simple et plus rapide à écrire tout en conservant les performances pour les calculs intensifs.

### Pourquoi Python + MPI ?

- **Syntaxe simple** : Moins de code boilerplate qu'en C
- **Productivité** : Développement plus rapide
- **Écosystème riche** : NumPy, SciPy, Matplotlib intégrés
- **Performances** : Comparables au C pour les calculs numériques

## Prérequis

### Connaissances requises
- Bases en Python
- Compréhension des listes et dictionnaires
- Notions de NumPy (facultatif mais recommandé)

### Logiciels nécessaires
- Python 3.7+
- pip (gestionnaire de paquets Python)
- Une implémentation MPI (Open MPI ou MPICH)

## Installation

### Étape 1 : Installer MPI

#### Sur Ubuntu/Debian
```bash
sudo apt-get update
sudo apt-get install openmpi-bin openmpi-common libopenmpi-dev
```

#### Sur macOS
```bash
brew install open-mpi
```

#### Sur Windows (avec WSL)
```bash
wsl --install
# Puis dans WSL :
sudo apt-get install openmpi-bin openmpi-common libopenmpi-dev
```

### Étape 2 : Installer mpi4py

```bash
# Installation avec pip
pip install mpi4py

# Ou avec conda
conda install -c conda-forge mpi4py

# Vérifier l'installation
python -c "from mpi4py import MPI; print(MPI.Get_version())"
```

### Étape 3 : Tester l'installation

Créez un fichier `test_mpi.py` :

```python
from mpi4py import MPI

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

print(f"Hello from process {rank} out of {size}")
```

Exécutez-le :

```bash
mpirun -np 4 python test_mpi.py
```

Si vous voyez 4 messages, tout fonctionne ! ✅

## 🔄 Différences C vs Python

| Aspect | C | Python |
|--------|---|--------|
| **Initialisation** | `MPI_Init(&argc, &argv)` | Automatique à l'import |
| **Finalisation** | `MPI_Finalize()` | Automatique |
| **Obtenir rank** | `MPI_Comm_rank(MPI_COMM_WORLD, &rank)` | `rank = comm.Get_rank()` |
| **Send/Recv** | Pointeurs + types explicites | Objets Python natifs |
| **Tableaux** | Manipulation manuelle | NumPy arrays |
| **Compilation** | `mpicc` nécessaire | Interprété |
| **Typage** | Statique | Dynamique |

### Avantages de Python
✅ **Pas de gestion mémoire manuelle**
✅ **Sérialisation automatique** des objets
✅ **Syntaxe concise**
✅ **Debugging plus facile**

### Inconvénients
❌ Légèrement plus lent pour les petits messages
❌ Consommation mémoire plus élevée

## 📚 Liste des exercices

| # | Exercice | Concepts | Difficulté |
|---|----------|----------|------------|
| 1 | Hello World parallèle | Bases mpi4py | ⭐ |
| 2 | Maître-esclave | Différenciation des rôles | ⭐ |
| 3 | Premier send/recv | `send()`, `recv()` | ⭐⭐ |
| 4 | Passage de jeton en anneau | Communications en chaîne | ⭐⭐ |
| 5 | Broadcast | `bcast()` | ⭐⭐ |
| 6 | Scatter | `scatter()` | ⭐⭐ |
| 7 | Gather | `gather()` | ⭐⭐ |
| 8 | Reduce | `reduce()` | ⭐⭐⭐ |
| 9 | Calcul de π (Monte Carlo) | Application complète | ⭐⭐⭐⭐ |
| 10 | Mesure de performance | `Wtime()`, speedup | ⭐⭐⭐ |

## 📖 Exercices détaillés

### Exercice 1 : Hello World parallèle

**Objectif** : Comprendre les concepts de base

```python
# exercice01_hello.py
from mpi4py import MPI

# Obtenir le communicateur par défaut
comm = MPI.COMM_WORLD

# Obtenir l'identifiant du processus (rank)
rank = comm.Get_rank()

# Obtenir le nombre total de processus (size)
size = comm.Get_size()

# Chaque processus affiche son rang
print(f"Bonjour ! Je suis le processus {rank} parmi {size}")
```

**Exécution** :
```bash
mpirun -np 4 python exercice01_hello.py
```

**Résultat attendu** :
```
Bonjour ! Je suis le processus 0 parmi 4
Bonjour ! Je suis le processus 2 parmi 4
Bonjour ! Je suis le processus 1 parmi 4
Bonjour ! Je suis le processus 3 parmi 4
```

**Concepts clés** :
- `MPI.COMM_WORLD` : Communicateur par défaut
- `comm.Get_rank()` : Identifiant unique (0 à size-1)
- `comm.Get_size()` : Nombre total de processus
- **Pas besoin de Init/Finalize** : automatique !

---

### Exercice 2 : Processus maître-esclave

**Objectif** : Différencier les rôles des processus

```python
# exercice02_master_slave.py
from mpi4py import MPI

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

if rank == 0:
    # Le processus 0 est le maître
    print(f"Je suis le MAÎTRE (processus 0)")
    print(f"J'ai {size - 1} esclaves sous mes ordres")
else:
    # Tous les autres sont des esclaves
    print(f"Je suis un esclave (processus {rank})")
```

**Exécution** :
```bash
mpirun -np 4 python exercice02_master_slave.py
```

---

### Exercice 3 : Premier envoi/réception

**Objectif** : Communication point-à-point simple

```python
# exercice03_send_recv.py
from mpi4py import MPI

comm = MPI.COMM_WORLD
rank = comm.Get_rank()

if rank == 0:
    # Processus 0 envoie
    message = 42
    print(f"Processus 0 : J'envoie {message} au processus 1")
    comm.send(message, dest=1, tag=0)
    
elif rank == 1:
    # Processus 1 reçoit
    message = comm.recv(source=0, tag=0)
    print(f"Processus 1 : J'ai reçu {message}")
```

**Méthodes importantes** :

#### send() - Petits objets Python
```python
comm.send(obj, dest, tag=0)
# Envoie n'importe quel objet Python sérialisable
# Utilise pickle automatiquement
```

#### Send() - Grands tableaux NumPy
```python
import numpy as np
data = np.array([1, 2, 3])
comm.Send([data, MPI.INT], dest=1)
# Plus rapide pour les gros tableaux
```

**Types de données supportés** :
- Entiers, floats, strings
- Listes, tuples, dictionnaires
- Objets NumPy (avec `Send`/`Recv` majuscules)
- Objets personnalisés (avec pickle)

---

### Exercice 4 : Passage de jeton en anneau

**Objectif** : Communications en chaîne

```python
# exercice04_ring.py
from mpi4py import MPI

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

# Déterminer les voisins dans l'anneau
next_rank = (rank + 1) % size
prev_rank = (rank - 1) % size

if rank == 0:
    # Le processus 0 initie le jeton
    jeton = 0
    print(f"Processus 0 : J'initie le jeton avec valeur {jeton}")
    comm.send(jeton, dest=next_rank)
    jeton = comm.recv(source=prev_rank)
    print(f"Processus 0 : Le jeton est revenu avec valeur {jeton}")
else:
    # Les autres processus reçoivent, modifient et transmettent
    jeton = comm.recv(source=prev_rank)
    print(f"Processus {rank} : J'ai reçu le jeton = {jeton}")
    jeton += 1
    comm.send(jeton, dest=next_rank)
    print(f"Processus {rank} : J'ai envoyé le jeton = {jeton}")
```

**Schéma** :
```
P0(0) → P1(1) → P2(2) → P3(3) → P0(4)
```

**Exécution** :
```bash
mpirun -np 4 python exercice04_ring.py
```

---

### Exercice 5 : Broadcast (diffusion)

**Objectif** : Communication collective 1-vers-tous

```python
# exercice05_broadcast.py
from mpi4py import MPI

comm = MPI.COMM_WORLD
rank = comm.Get_rank()

# Initialisation
if rank == 0:
    valeur = 777
    print(f"Processus 0 : Je diffuse la valeur {valeur}")
else:
    valeur = None

# Broadcast : TOUS les processus appellent cette fonction
valeur = comm.bcast(valeur, root=0)

# Maintenant tous ont la même valeur
print(f"Processus {rank} : valeur = {valeur}")
```

**Important** :
- `bcast()` doit être appelé par **TOUS** les processus
- Le processus `root` envoie, les autres reçoivent
- Retourne la valeur (ne modifie pas en place)

**Avec NumPy** :
```python
import numpy as np

if rank == 0:
    data = np.array([1.0, 2.0, 3.0])
else:
    data = np.empty(3, dtype=float)

comm.Bcast(data, root=0)  # Majuscule pour NumPy
```

---

### Exercice 6 : Scatter (distribution)

**Objectif** : Distribuer des données différentes à chaque processus

```python
# exercice06_scatter.py
from mpi4py import MPI

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

# Préparation des données (seulement sur le processus 0)
if rank == 0:
    # Créer un tableau avec une valeur pour chaque processus
    data = list(range(10, 10 + size * 10, 10))  # [10, 20, 30, 40]
    print(f"Processus 0 : Je distribue {data}")
else:
    data = None

# Scatter : chaque processus reçoit un élément
local_data = comm.scatter(data, root=0)

print(f"Processus {rank} : J'ai reçu {local_data}")
```

**Résultat avec 4 processus** :
```
Processus 0 : Je distribue [10, 20, 30, 40]
Processus 0 : J'ai reçu 10
Processus 1 : J'ai reçu 20
Processus 2 : J'ai reçu 30
Processus 3 : J'ai reçu 40
```

**Avec NumPy** :
```python
import numpy as np

if rank == 0:
    sendbuf = np.arange(size * 4).reshape(size, 4)
else:
    sendbuf = None

recvbuf = np.empty(4, dtype=int)
comm.Scatter(sendbuf, recvbuf, root=0)
```

---

### Exercice 7 : Gather (collecte)

**Objectif** : Rassembler les résultats de tous les processus

```python
# exercice07_gather.py
from mpi4py import MPI

comm = MPI.COMM_WORLD
rank = comm.Get_rank()

# Chaque processus calcule son carré
local_value = (rank + 1) ** 2
print(f"Processus {rank} : Mon carré est {local_value}")

# Gather : collecter tous les résultats sur le processus 0
all_values = comm.gather(local_value, root=0)

if rank == 0:
    print(f"Processus 0 : Tous les carrés = {all_values}")
    print(f"Somme totale = {sum(all_values)}")
```

**Résultat avec 4 processus** :
```
Processus 0 : Mon carré est 1
Processus 1 : Mon carré est 4
Processus 2 : Mon carré est 9
Processus 3 : Mon carré est 16
Processus 0 : Tous les carrés = [1, 4, 9, 16]
Somme totale = 30
```

**Variantes** :
- `gather()` : collecte sur un processus
- `allgather()` : collecte distribuée à tous

---

### Exercice 8 : Reduce (réduction)

**Objectif** : Calculer une opération sur toutes les valeurs

```python
# exercice08_reduce.py
from mpi4py import MPI

comm = MPI.COMM_WORLD
rank = comm.Get_rank()

# Chaque processus a une valeur
local_value = rank + 1
print(f"Processus {rank} : Ma valeur est {local_value}")

# Réduction : somme de toutes les valeurs
total_sum = comm.reduce(local_value, op=MPI.SUM, root=0)

if rank == 0:
    print(f"Somme totale : {total_sum}")

# Autres opérations disponibles
max_value = comm.reduce(local_value, op=MPI.MAX, root=0)
min_value = comm.reduce(local_value, op=MPI.MIN, root=0)
product = comm.reduce(local_value, op=MPI.PROD, root=0)

if rank == 0:
    print(f"Maximum : {max_value}")
    print(f"Minimum : {min_value}")
    print(f"Produit : {product}")
```

**Opérations disponibles** :
- `MPI.SUM` : somme
- `MPI.MAX` : maximum
- `MPI.MIN` : minimum
- `MPI.PROD` : produit
- `MPI.LAND` : ET logique
- `MPI.LOR` : OU logique

**Variante allreduce** :
```python
# Tous les processus obtiennent le résultat
total_sum = comm.allreduce(local_value, op=MPI.SUM)
```

---

### Exercice 9 : Calcul parallèle de π

**Objectif** : Application complète avec Monte Carlo

```python
# exercice09_pi_monte_carlo.py
from mpi4py import MPI
import numpy as np

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

# Nombre total de points
total_points = 10_000_000
points_per_process = total_points // size

# Générer des points aléatoires (seed différente par processus)
np.random.seed(rank)
x = np.random.random(points_per_process)
y = np.random.random(points_per_process)

# Compter les points dans le cercle (x² + y² ≤ 1)
inside_circle = np.sum(x**2 + y**2 <= 1.0)

print(f"Processus {rank} : {inside_circle}/{points_per_process} points dans le cercle")

# Réduction : somme des points dans le cercle
total_inside = comm.reduce(inside_circle, op=MPI.SUM, root=0)

if rank == 0:
    # Estimation de π
    pi_estimate = 4.0 * total_inside / total_points
    pi_actual = np.pi
    error = abs(pi_estimate - pi_actual)
    
    print(f"\n{'='*50}")
    print(f"Estimation de π : {pi_estimate:.10f}")
    print(f"Valeur réelle   : {pi_actual:.10f}")
    print(f"Erreur          : {error:.10f}")
    print(f"Erreur relative : {error/pi_actual*100:.6f}%")
    print(f"{'='*50}")
```

**Exécution** :
```bash
mpirun -np 4 python exercice09_pi_monte_carlo.py
```

**Résultat typique** :
```
Processus 0 : 1963745/2500000 points dans le cercle
Processus 1 : 1963891/2500000 points dans le cercle
Processus 2 : 1963512/2500000 points dans le cercle
Processus 3 : 1963624/2500000 points dans le cercle

==================================================
Estimation de π : 3.1418704000
Valeur réelle   : 3.1415926536
Erreur          : 0.0002777464
Erreur relative : 0.008839%
==================================================
```

---

### Exercice 10 : Mesure de performance

**Objectif** : Comprendre le speedup et l'efficacité

```python
# exercice10_performance.py
from mpi4py import MPI
import numpy as np
import time

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

# Taille du problème
n = 100_000_000
local_n = n // size

# Début du chronométrage
start_time = MPI.Wtime()

# Calcul intensif : somme des carrés
np.random.seed(rank)
data = np.random.random(local_n)
local_sum = np.sum(data ** 2)

# Fin du calcul local
local_time = MPI.Wtime() - start_time

# Réduction pour obtenir la somme totale
total_sum = comm.reduce(local_sum, op=MPI.SUM, root=0)

# Temps maximum (processus le plus lent)
max_time = comm.reduce(local_time, op=MPI.MAX, root=0)

if rank == 0:
    print(f"\n{'='*60}")
    print(f"Résultats de performance avec {size} processus")
    print(f"{'='*60}")
    print(f"Somme totale        : {total_sum:.6f}")
    print(f"Temps max           : {max_time:.6f} secondes")
    print(f"Éléments par proc   : {local_n:,}")
    print(f"Éléments totaux     : {n:,}")
    print(f"{'='*60}\n")

# Script de test pour différents nombres de processus
print(f"Processus {rank} : Temps = {local_time:.6f}s")
```

**Script pour tester le speedup** :

```bash
#!/bin/bash
# test_speedup.sh

echo "Test de speedup pour le calcul parallèle"
echo "=========================================="

for np in 1 2 4 8; do
    echo ""
    echo "Avec $np processus :"
    mpirun -np $np python exercice10_performance.py
done
```

**Calcul du speedup** :

```python
# exercice10_speedup_analysis.py
from mpi4py import MPI
import numpy as np

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

n = 50_000_000
local_n = n // size

# Mesure du temps
start = MPI.Wtime()

np.random.seed(rank)
data = np.random.random(local_n)
local_sum = np.sum(data ** 2)

total_sum = comm.reduce(local_sum, op=MPI.SUM, root=0)

end = MPI.Wtime()
time_taken = end - start

# Collecter tous les temps
all_times = comm.gather(time_taken, root=0)

if rank == 0:
    max_time = max(all_times)
    avg_time = np.mean(all_times)
    
    print(f"\nProcessus : {size}")
    print(f"Temps max : {max_time:.6f}s")
    print(f"Temps moy : {avg_time:.6f}s")
    
    # Si on a le temps séquentiel (à mesurer séparément)
    # speedup = T1 / Tn
    # efficiency = speedup / n
```

---

## 🧠 Concepts clés mpi4py

### Communications point-à-point

| Méthode | Description | Usage |
|---------|-------------|-------|
| `send(obj, dest, tag)` | Envoie un objet Python | Petits objets |
| `recv(source, tag)` | Reçoit un objet Python | Petits objets |
| `Send(buf, dest, tag)` | Envoie un buffer NumPy | Gros tableaux |
| `Recv(buf, source, tag)` | Reçoit un buffer NumPy | Gros tableaux |
| `isend()` / `irecv()` | Non-bloquant | Communications asynchrones |

### Communications collectives

| Méthode | Description | Exemple |
|---------|-------------|---------|
| `bcast(obj, root)` | Diffusion 1→tous | `val = comm.bcast(val, root=0)` |
| `scatter(list, root)` | Distribution | `val = comm.scatter(data, root=0)` |
| `gather(obj, root)` | Collecte | `all = comm.gather(val, root=0)` |
| `reduce(obj, op, root)` | Réduction | `sum = comm.reduce(val, MPI.SUM, 0)` |
| `allreduce(obj, op)` | Réduction+diffusion | `sum = comm.allreduce(val, MPI.SUM)` |
| `allgather(obj)` | Collecte distribuée | `all = comm.allgather(val)` |

### Minuscule vs Majuscule

**Minuscule (pickle)** : objets Python génériques
```python
data = {"key": "value"}
comm.send(data, dest=1)  # Utilise pickle
```

**Majuscule (buffer)** : tableaux NumPy (plus rapide)
```python
data = np.array([1, 2, 3])
comm.Send(data, dest=1)  # Accès direct mémoire
```

---

## ⚠️ Erreurs courantes en Python

### 1. Oublier que bcast/scatter/etc. retournent une valeur

```python
# ❌ FAUX
data = [1, 2, 3]
comm.bcast(data, root=0)  # data n'est pas modifié !

# ✅ CORRECT
data = comm.bcast(data, root=0)
```

### 2. Mélanger minuscule et majuscule

```python
# ❌ FAUX
comm.send(np_array, dest=1)  # Lent avec pickle

# ✅ CORRECT
comm.Send(np_array, dest=1)  # Rapide avec buffer
```

### 3. Utiliser la même seed pour random

```python
# ❌ Tous génèrent les mêmes nombres
np.random.seed(42)

# ✅ Chaque processus a une seed différente
np.random.seed(rank)
# ou
np.random.seed(int(time.time()) + rank)
```

### 4. Deadlock avec send/recv

```python
# ❌ DEADLOCK
if rank == 0:
    data = comm.recv(source=1)  # Attend de 1
    comm.send(data, dest=1)
if rank == 1:
    data = comm.recv(source=0)  # Attend de 0
    comm.send(data, dest=0)

# ✅ SOLUTION 1 : Ordre alterné
if rank == 0:
    comm.send(data, dest=1)
    result = comm.recv(source=1)
if rank == 1:
    data = comm.recv(source=0)
    comm.send(result, dest=0)

# ✅ SOLUTION 2 : Communications non-bloquantes
req1 = comm.isend(data, dest=other)
req2 = comm.irecv(source=other)
result = req2.wait()
req1.wait()
```

---

## 📊 Exemple complet : Multiplication matrice-vecteur

```python
# matrix_vector_parallel.py
from mpi4py import MPI
import numpy as np

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

# Dimensions
n = 1000  # Taille de la matrice (doit être divisible par size)
local_n = n // size

# Processus 0 crée les données
if rank == 0:
    A = np.random.random((n, n))
    x = np.random.random(n)
    print(f"Matrice {n}x{n} créée")
else:
    A = None
    x = None

# Distribuer le vecteur à tous
x = comm.bcast(x, root=0)

# Distribuer les lignes de la matrice
local_A = np.empty((local_n, n), dtype=float)
comm.Scatter(A, local_A, root=0)

# Calcul local : multiplication de local_A par x
start = MPI.Wtime()
local_result = np.dot(local_A, x)
local_time = MPI.Wtime() - start

# Collecter les résultats
result = np.empty(n, dtype=float) if rank == 0 else None
comm.Gather(local_result, result, root=0)

# Afficher les temps
max_time = comm.reduce(local_time, op=MPI.MAX, root=0)

if rank == 0:
    print(f"Temps de calcul : {max_time:.6f}s")
    print(f"Résultat: y[0:5] = {result[:5]}")
```

---

## 📚 Ressources supplémentaires

### Documentation
- [mpi4py Documentation](https://mpi4py.readthedocs.io/)
- [MPI Forum](https://www.mpi-forum.org/)
- [NumPy Documentation](https://numpy.org/doc/)

### Tutoriels
- [mpi4py Tutorial officiel](https://mpi4py.readthedocs.io/en/stable/tutorial.html)
- [Python HPC avec mpi4py](https://github.com/jbornschein/mpi4py-examples)
