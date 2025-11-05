# Commandes système utiles pour la programmation MPI

Guide complet des commandes pour analyser votre système, optimiser vos programmes MPI et déboguer vos applications parallèles.

## Table des matières

- [Analyser votre CPU](#analyser-votre-cpu)
- [Commandes MPI essentielles](#commandes-mpi-essentielles)
- [Monitoring et performance](#monitoring-et-performance)
- [Compilation et debugging](#compilation-et-debugging)
- [Gestion de la mémoire](#gestion-de-la-mémoire)
- [Scripts utiles](#scripts-utiles)

---

## Analyser votre CPU

### `lscpu` - Informations complètes sur le CPU

```bash
lscpu
```

**Sortie typique** :
```
Architecture:            x86_64
  CPU op-mode(s):        32-bit, 64-bit
  Address sizes:         48 bits physical, 48 bits virtual
  Byte Order:            Little Endian
CPU(s):                  8                    ← Nombre total de CPUs logiques
  On-line CPU(s) list:   0-7
Vendor ID:               GenuineIntel
  Model name:            Intel(R) Core(TM) i7-10750H CPU @ 2.60GHz
    CPU family:          6
    Model:               165
    Thread(s) per core:  2                    ← Hyperthreading activé
    Core(s) per socket:  4                    ← 4 cœurs physiques
    Socket(s):           1
```

**Informations clés pour MPI** :
- **CPU(s)** : Nombre de processeurs logiques (8 dans cet exemple)
- **Core(s) per socket** : Cœurs physiques (4 ici)
- **Thread(s) per core** : Si = 2, hyperthreading activé
- **Socket(s)** : Nombre de processeurs physiques

**Recommandation pour MPI** :
```bash
# Nombre optimal de processus MPI = nombre de cœurs physiques
# Dans l'exemple ci-dessus : 4 cœurs × 1 socket = 4 processus

mpirun -np 4 ./mon_programme
```

### Commandes alternatives

```bash
# Nombre de CPUs logiques
nproc
# Sortie: 8

# Nombre de cœurs physiques
nproc --all
lscpu | grep "^Core(s) per socket" | awk '{print $4}'

# Informations détaillées sur chaque CPU
cat /proc/cpuinfo

# Filtrer pour voir seulement le modèle
cat /proc/cpuinfo | grep "model name" | uniq

# Architecture du processeur
uname -m
# Sortie: x86_64
```

---

## Commandes MPI essentielles

### Vérifier l'installation MPI

```bash
# Version du compilateur MPI
mpicc --version
mpic++ --version
mpif90 --version  # Pour Fortran

# Version de MPI
mpirun --version
# ou
ompi_info | grep "Open MPI"

# Localisation des binaires
which mpicc
which mpirun

# Informations complètes sur Open MPI
ompi_info
```

### Compiler avec options de débogage

```bash
# Compilation standard
mpicc programme.c -o programme

# Avec optimisation
mpicc -O3 programme.c -o programme

# Avec debugging
mpicc -g -Wall programme.c -o programme

# Avec bibliothèque mathématique
mpicc programme.c -o programme -lm

# Verbose (voir toutes les étapes)
mpicc -v programme.c -o programme

# Afficher les flags de compilation utilisés
mpicc --showme
# Sortie typique: gcc -I/usr/lib/x86_64-linux-gnu/openmpi/include ...
```

### Exécuter des programmes MPI

```bash
# Exécution basique avec 4 processus
mpirun -np 4 ./programme

# Spécifier les slots par nœud
mpirun -np 4 --map-by core ./programme

# Verbose (voir ce qui se passe)
mpirun -v -np 4 ./programme

# Afficher le binding (où sont les processus)
mpirun -np 4 --report-bindings ./programme

# Limiter à un socket spécifique
mpirun -np 4 --bind-to core --map-by socket ./programme

# Sur plusieurs machines (cluster)
mpirun -np 8 -hostfile machines.txt ./programme

# Exemple de fichier machines.txt:
# node1 slots=4
# node2 slots=4

# Avec timeout (en secondes)
timeout 30 mpirun -np 4 ./programme

# Rediriger la sortie
mpirun -np 4 ./programme > output.txt 2>&1
```

### Options avancées de mpirun

```bash
# Désactiver les messages de warning
mpirun --mca btl_base_warn_component_unused 0 -np 4 ./programme

# Utiliser uniquement la mémoire partagée (1 machine)
mpirun --mca btl self,sm -np 4 ./programme

# Afficher les variables d'environnement
mpirun -np 4 -x MY_VAR=value ./programme

# Lancer avec un profiler
mpirun -np 4 valgrind --leak-check=full ./programme

# Définir la politique de placement
mpirun -np 4 --map-by core:PE=2 ./programme
```

---

## Monitoring et performance

### `htop` - Monitoring interactif

```bash
# Installer htop si nécessaire
sudo apt-get install htop

# Lancer htop
htop

# Dans htop pendant l'exécution MPI:
# - F2 : Configuration
# - F4 : Filtrer par nom de processus
# - F5 : Vue arborescente
# - F9 : Tuer un processus
# - F10 : Quitter
```

**Astuce** : Lancez htop dans un terminal, votre programme MPI dans un autre

```bash
# Terminal 1
htop

# Terminal 2
mpirun -np 4 ./programme
```

### `top` - Monitoring basique

```bash
# Vue classique
top

# Trier par CPU (shift + P)
# Trier par mémoire (shift + M)
# Filtrer par utilisateur (u)
# Rafraîchir (espace)

# Avec mise à jour automatique
watch -n 1 'ps aux | grep "mon_programme"'
```

### `time` - Mesurer le temps d'exécution

```bash
# Temps basique
time mpirun -np 4 ./programme

# Sortie:
# real    0m2.345s    ← Temps total (horloge murale)
# user    0m8.123s    ← Temps CPU total
# sys     0m0.234s    ← Temps système

# Temps détaillé
/usr/bin/time -v mpirun -np 4 ./programme
# Affiche: CPU%, mémoire max, page faults, etc.
```

### Mesurer la performance CPU

```bash
# Température CPU (nécessite lm-sensors)
sudo apt-get install lm-sensors
sensors

# Fréquence des CPUs
watch -n 1 'cat /proc/cpuinfo | grep MHz'

# Charge du système
uptime
# Sortie: load average: 1.23, 0.89, 0.45
# Les 3 nombres = charge sur 1min, 5min, 15min

# Utilisation CPU en temps réel
mpstat 1 5
# Affiche les stats CPU toutes les 1 seconde, 5 fois
```

### `perf` - Profiling avancé

```bash
# Installer perf
sudo apt-get install linux-tools-generic

# Profiler un programme MPI
perf stat mpirun -np 4 ./programme

# Sortie typique:
#  Performance counter stats for 'mpirun -np 4 ./programme':
#           2345.67 msec task-clock
#              1234      context-switches
#              5678      cpu-migrations
#         12345678      cycles
#          8901234      instructions
#             0.67      IPC (instructions per cycle)

# Enregistrer le profiling
perf record mpirun -np 4 ./programme
perf report

# Analyser le cache
perf stat -e cache-references,cache-misses mpirun -np 4 ./programme
```

---

## Compilation et debugging

### Options de compilation utiles

```bash
# Debug complet
mpicc -g -O0 -Wall -Wextra programme.c -o programme

# Avec sanitizers (détection d'erreurs mémoire)
mpicc -g -fsanitize=address programme.c -o programme

# Détection de race conditions
mpicc -g -fsanitize=thread programme.c -o programme

# Générer des warnings utiles
mpicc -Wall -Wextra -Wpedantic -Wconversion programme.c -o programme

# Vérifier la syntaxe sans compiler
mpicc -fsyntax-only programme.c

# Préprocesseur uniquement
mpicc -E programme.c > programme.i
```

### Debugging avec GDB

```bash
# Compiler avec symboles de debug
mpicc -g programme.c -o programme

# Déboguer un seul processus
gdb ./programme

# Déboguer MPI (méthode 1: attacher manuellement)
# Terminal 1:
mpirun -np 4 xterm -e gdb ./programme

# Déboguer MPI (méthode 2: avec script)
cat > debug_mpi.sh << 'EOF'
#!/bin/bash
xterm -e gdb -ex run --args ./programme &
EOF
chmod +x debug_mpi.sh
mpirun -np 4 ./debug_mpi.sh

# Commandes GDB utiles:
# (gdb) run                    # Exécuter
# (gdb) break main             # Point d'arrêt
# (gdb) break 42               # Point d'arrêt ligne 42
# (gdb) continue               # Continuer
# (gdb) step                   # Pas à pas (entre dans les fonctions)
# (gdb) next                   # Pas à pas (saute les fonctions)
# (gdb) print variable         # Afficher une variable
# (gdb) backtrace              # Pile d'appels
# (gdb) quit                   # Quitter
```

### Valgrind - Détection de fuites mémoire

```bash
# Installation
sudo apt-get install valgrind

# Vérification basique
mpirun -np 2 valgrind --leak-check=full ./programme

# Vérification détaillée
mpirun -np 2 valgrind --leak-check=full --show-leak-kinds=all \
  --track-origins=yes --verbose ./programme

# Sauvegarder dans un fichier
mpirun -np 2 valgrind --leak-check=full \
  --log-file=valgrind-%p.log ./programme
# Crée valgrind-PID.log pour chaque processus

# Détecter les race conditions (plus lent)
mpirun -np 2 valgrind --tool=helgrind ./programme
```

### Vérifier les liens et dépendances

```bash
# Voir les bibliothèques liées
ldd ./programme
# Sortie:
# libmpi.so.40 => /usr/lib/x86_64-linux-gnu/libmpi.so.40
# libc.so.6 => /lib/x86_64-linux-gnu/libc.so.6

# Vérifier les symboles MPI
nm ./programme | grep MPI_

# Voir la taille des sections
size ./programme
```

---

## Gestion de la mémoire

### Informations mémoire système

```bash
# Mémoire totale disponible
free -h

# Sortie:
#               total        used        free      shared  buff/cache   available
# Mem:           15Gi       3.2Gi       8.1Gi       200Mi       4.0Gi        11Gi
# Swap:         2.0Gi          0B       2.0Gi

# Mises à jour continues
watch -n 1 free -h

# Détails sur la mémoire
cat /proc/meminfo

# Mémoire par processus
ps aux --sort=-%mem | head -10

# Mémoire d'un processus spécifique
ps -o pid,user,%mem,command -p <PID>
```

### Limites de ressources

```bash
# Voir les limites actuelles
ulimit -a

# Augmenter la taille de pile (stack)
ulimit -s unlimited

# Limiter la mémoire (en KB)
ulimit -m 1000000

# Pour un programme MPI
ulimit -s unlimited && mpirun -np 4 ./programme

# Définir les limites dans un script
cat > run_with_limits.sh << 'EOF'
#!/bin/bash
ulimit -s unlimited
ulimit -m 4000000
mpirun -np 4 ./programme
EOF
```

### Surveiller l'utilisation mémoire d'un programme

```bash
# Pendant l'exécution
# Terminal 1:
mpirun -np 4 ./programme &
PID=$!

# Terminal 2:
watch -n 1 "ps -o pid,vsz,rss,comm -p $PID"

# Avec un script automatique
cat > monitor_memory.sh << 'EOF'
#!/bin/bash
PROG=$1
LOGFILE="memory_usage.log"

mpirun -np 4 ./$PROG &
PID=$!

echo "Time,VSZ,RSS" > $LOGFILE
while kill -0 $PID 2>/dev/null; do
    ps -o vsz=,rss= -p $PID | \
    awk -v t="$(date +%s)" '{print t","$1","$2}' >> $LOGFILE
    sleep 0.1
done
EOF
chmod +x monitor_memory.sh
./monitor_memory.sh programme
```

---

## Scripts utiles

### Script de benchmark automatique

```bash
cat > benchmark_mpi.sh << 'EOF'
#!/bin/bash

PROGRAMME=$1
MAX_PROCS=$(nproc)

echo "Benchmark MPI pour $PROGRAMME"
echo "Nombre de cœurs: $MAX_PROCS"
echo "================================"
echo ""

for np in 1 2 4 8 16; do
    if [ $np -le $MAX_PROCS ]; then
        echo "Test avec $np processus:"
        /usr/bin/time -f "Temps réel: %E\nCPU: %P\nMémoire max: %M KB" \
            mpirun -np $np ./$PROGRAMME
        echo "---"
    fi
done
EOF

chmod +x benchmark_mpi.sh
./benchmark_mpi.sh mon_programme
```

### Script de vérification de l'environnement

```bash
cat > check_mpi_env.sh << 'EOF'
#!/bin/bash

echo "=== Vérification de l'environnement MPI ==="
echo ""

# Vérifier MPI
echo "1. Installation MPI:"
if command -v mpicc &> /dev/null; then
    echo "   ✓ mpicc trouvé: $(which mpicc)"
    mpicc --version | head -1
else
    echo "   ✗ mpicc non trouvé"
fi

if command -v mpirun &> /dev/null; then
    echo "   ✓ mpirun trouvé: $(which mpirun)"
    mpirun --version | head -1
else
    echo "   ✗ mpirun non trouvé"
fi

echo ""
echo "2. Informations CPU:"
echo "   - Cœurs logiques: $(nproc)"
echo "   - Architecture: $(uname -m)"
CORES=$(lscpu | grep "^Core(s) per socket" | awk '{print $4}')
SOCKETS=$(lscpu | grep "^Socket(s)" | awk '{print $2}')
echo "   - Cœurs physiques: $((CORES * SOCKETS))"

echo ""
echo "3. Mémoire disponible:"
free -h | grep "Mem:" | awk '{print "   - Total: "$2", Disponible: "$7}'

echo ""
echo "4. Test MPI basique:"
cat > test_mpi_tmp.c << 'EOFC'
#include <mpi.h>
#include <stdio.h>
int main() {
    MPI_Init(NULL, NULL);
    int rank;
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    printf("Process %d: OK\n", rank);
    MPI_Finalize();
    return 0;
}
EOFC

if mpicc test_mpi_tmp.c -o test_mpi_tmp 2>/dev/null; then
    echo "   ✓ Compilation réussie"
    if mpirun -np 2 ./test_mpi_tmp &>/dev/null; then
        echo "   ✓ Exécution réussie"
    else
        echo "   ✗ Erreur d'exécution"
    fi
    rm -f test_mpi_tmp test_mpi_tmp.c
else
    echo "   ✗ Erreur de compilation"
fi

echo ""
echo "=== Vérification terminée ==="
EOF

chmod +x check_mpi_env.sh
./check_mpi_env.sh
```

### Script de profiling complet

```bash
cat > profile_mpi.sh << 'EOF'
#!/bin/bash

PROGRAMME=$1
NP=${2:-4}

echo "Profiling de $PROGRAMME avec $NP processus"
echo "==========================================="

# 1. Temps d'exécution
echo "1. Temps d'exécution:"
/usr/bin/time -v mpirun -np $NP ./$PROGRAMME 2>&1 | \
    grep -E "Elapsed|Maximum resident|Percent of CPU"

# 2. Statistiques CPU
echo ""
echo "2. Statistiques CPU:"
perf stat mpirun -np $NP ./$PROGRAMME 2>&1 | \
    grep -E "seconds|instructions|cycles"

# 3. Utilisation mémoire
echo ""
echo "3. Pic d'utilisation mémoire par processus:"
mpirun -np $NP valgrind --tool=massif --massif-out-file=massif.%p ./$PROGRAMME \
    2>/dev/null
for f in massif.*; do
    grep mem_heap_B $f | sed -e 's/mem_heap_B=\(.*\)/\1/' | \
    sort -g | tail -1 | awk '{print "   "$1/1024/1024" MB"}'
done
rm -f massif.*

echo ""
echo "Profiling terminé!"
EOF

chmod +x profile_mpi.sh
./profile_mpi.sh mon_programme 4
```

### Générer un rapport de performance

```bash
cat > generate_report.sh << 'EOF'
#!/bin/bash

PROGRAMME=$1
OUTPUT="performance_report.txt"

{
    echo "RAPPORT DE PERFORMANCE"
    echo "======================"
    echo "Programme: $PROGRAMME"
    echo "Date: $(date)"
    echo "Machine: $(hostname)"
    echo ""
    
    echo "CONFIGURATION SYSTÈME"
    echo "---------------------"
    lscpu | grep -E "Model name|CPU\(s\)|Core|Thread"
    echo ""
    free -h
    echo ""
    
    echo "BENCHMARKS"
    echo "----------"
    for np in 1 2 4 8; do
        if [ $np -le $(nproc) ]; then
            echo "Avec $np processus:"
            time mpirun -np $np ./$PROGRAMME 2>&1 | grep real
        fi
    done
    
} > $OUTPUT

echo "Rapport généré: $OUTPUT"
EOF

chmod +x generate_report.sh
./generate_report.sh mon_programme
```

---

## Commandes de comparaison de performance

### Comparer différentes configurations

```bash
# Script de comparaison
cat > compare_configs.sh << 'EOF'
#!/bin/bash

PROG=$1

echo "Config,Processus,Temps(s),Speedup"

# Temps de référence (séquentiel)
T1=$(mpirun -np 1 ./$PROG 2>&1 | grep -oP '(?<=real\t).*' | \
     sed 's/m/*60+/; s/s//; s/^/scale=3;/' | bc)

# Tests parallèles
for np in 2 4 8 16; do
    if [ $np -le $(nproc) ]; then
        T=$(mpirun -np $np ./$PROG 2>&1 | grep -oP '(?<=real\t).*' | \
            sed 's/m/*60+/; s/s//; s/^/scale=3;/' | bc)
        SPEEDUP=$(echo "scale=2; $T1 / $T" | bc)
        echo "Parallel,$np,$T,$SPEEDUP"
    fi
done
EOF

chmod +x compare_configs.sh
./compare_configs.sh mon_programme | column -t -s,
```

---

## Commandes de diagnostic rapide

```bash
# Tout-en-un: statut système pour MPI
alias mpicheck='echo "=== CPU ==="; lscpu | grep -E "CPU\(s\)|Core"; \
                echo "=== Mémoire ==="; free -h | grep Mem; \
                echo "=== MPI ==="; mpirun --version | head -1'

# Voir les processus MPI actifs
alias mpiprocs='ps aux | grep -E "mpirun|[m]pi"'

# Tuer tous les processus MPI
alias mpikill='pkill -9 -f mpirun; pkill -9 -f "\.\/.*"'

# Nettoyage rapide
alias mpiclean='rm -f *.o *.out core.* massif.* valgrind-*.log'
```

---

## Fichier .bashrc utile

Ajoutez ces lignes à votre `~/.bashrc` :

```bash
# Ajouter à ~/.bashrc

# Alias MPI
alias mpic='mpicc -Wall -O3'
alias mpicd='mpicc -g -Wall -O0'
alias mpir='mpirun -np 4'

# Variables d'environnement
export OMPI_MCA_btl_base_warn_component_unused=0

# Fonction pour compiler et exécuter
mpirun_quick() {
    mpicc $1 -o ${1%.c} && mpirun -np ${2:-4} ./${1%.c}
}

# Fonction pour profiler rapidement
mpiprof() {
    perf stat mpirun -np ${2:-4} ./$1
}

# Recharger: source ~/.bashrc
```

---

## Résolution de problèmes courants

### "Cannot find lscpu"

```bash
# Installer les outils système
sudo apt-get install util-linux
```

### "mpirun not found"

```bash
# Vérifier l'installation
dpkg -l | grep -i openmpi

# Réinstaller si nécessaire
sudo apt-get install --reinstall openmpi-bin
```

### Erreur "btl_tcp_if_include"

```bash
# Ajouter à votre commande:
mpirun --mca btl_tcp_if_include lo -np 4 ./programme
```

### Programme bloqué/deadlock

```bash
# Envoyer un signal pour voir où il est bloqué
kill -QUIT <PID>

# Ou utiliser timeout
timeout 10 mpirun -np 4 ./programme

# Debug avec stack trace
mpirun -np 4 gdb -batch -ex "run" -ex "thread apply all bt" ./programme
```

---

## 📚 Résumé des commandes essentielles

```bash
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
