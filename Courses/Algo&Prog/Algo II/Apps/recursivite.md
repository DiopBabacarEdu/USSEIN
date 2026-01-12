# Tutoriel Complet sur la Récursivité

## 1. Qu'est-ce que la Récursivité ?

La récursivité est une technique de programmation où une fonction s'appelle elle-même pour résoudre un problème en le décomposant en sous-problèmes plus simples.

**Analogie de la vie réelle :** Imaginez que vous cherchez un livre dans une bibliothèque organisée en sections. Votre stratégie pourrait être : "Si je suis dans la bonne section, je cherche le livre. Sinon, j'entre dans une sous-section et je répète le processus."

## 2. Structure d'une Fonction Récursive

Toute fonction récursive doit contenir deux éléments essentiels :

### 2.1 Le Cas de Base (Condition d'arrêt)
C'est la condition qui arrête la récursion. Sans elle, la fonction s'appellerait indéfiniment.

### 2.2 Le Cas Récursif
C'est l'appel de la fonction à elle-même avec des paramètres modifiés, se rapprochant du cas de base.

```python
def fonction_recursive(parametre):
    # Cas de base
    if condition_arret:
        return valeur_simple
    
    # Cas récursif
    return fonction_recursive(parametre_modifie)
```

## 3. Exemples Progressifs

### 3.1 Exemple Simple : Compte à Rebours

```python
def compte_a_rebours(n):
    # Cas de base
    if n == 0:
        print("Décollage !")
        return
    
    # Affichage et cas récursif
    print(n)
    compte_a_rebours(n - 1)

# Utilisation
compte_a_rebours(5)
# Affiche : 5, 4, 3, 2, 1, Décollage !
```

**Trace d'exécution :**
```
compte_a_rebours(5)
  → print(5)
  → compte_a_rebours(4)
      → print(4)
      → compte_a_rebours(3)
          → print(3)
          → compte_a_rebours(2)
              → print(2)
              → compte_a_rebours(1)
                  → print(1)
                  → compte_a_rebours(0)
                      → print("Décollage !")
```

### 3.2 La Factorielle

Le calcul de n! = n × (n-1) × (n-2) × ... × 1

```python
def factorielle(n):
    # Cas de base
    if n == 0 or n == 1:
        return 1
    
    # Cas récursif
    return n * factorielle(n - 1)

# Exemples
print(factorielle(5))  # 120
print(factorielle(0))  # 1
```

**Décomposition pour factorielle(5) :**
```
factorielle(5) = 5 × factorielle(4)
               = 5 × (4 × factorielle(3))
               = 5 × (4 × (3 × factorielle(2)))
               = 5 × (4 × (3 × (2 × factorielle(1))))
               = 5 × (4 × (3 × (2 × 1)))
               = 120
```

### 3.3 La Suite de Fibonacci

Chaque nombre est la somme des deux précédents : 0, 1, 1, 2, 3, 5, 8, 13...

```python
def fibonacci(n):
    # Cas de base
    if n == 0:
        return 0
    if n == 1:
        return 1
    
    # Cas récursif
    return fibonacci(n - 1) + fibonacci(n - 2)

# Exemples
print(fibonacci(6))  # 8
print(fibonacci(10)) # 55
```

**Arbre d'appels pour fibonacci(5) :**
```
                    fib(5)
                   /      \
              fib(4)      fib(3)
             /     \      /     \
        fib(3)   fib(2) fib(2) fib(1)
       /    \    /   \   /   \
   fib(2) fib(1) ...  ... ... ...
```

## 4. Récursivité vs Itération

### Version Récursive : Somme des N premiers entiers
```python
def somme_recursive(n):
    if n == 0:
        return 0
    return n + somme_recursive(n - 1)
```

### Version Itérative
```python
def somme_iterative(n):
    total = 0
    for i in range(1, n + 1):
        total += i
    return total
```

**Comparaison :**
- **Récursivité** : Plus élégante, suit naturellement la définition mathématique
- **Itération** : Plus efficace en mémoire, plus rapide pour des valeurs élevées

## 5. Types de Récursivité

### 5.1 Récursivité Simple (ou Linéaire)
Un seul appel récursif par exécution.

```python
def puissance(base, exposant):
    if exposant == 0:
        return 1
    return base * puissance(base, exposant - 1)
```

### 5.2 Récursivité Multiple
Plusieurs appels récursifs par exécution.

```python
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)
```

### 5.3 Récursivité Terminale
L'appel récursif est la dernière opération de la fonction.

```python
def factorielle_terminale(n, accumulateur=1):
    if n == 0:
        return accumulateur
    return factorielle_terminale(n - 1, n * accumulateur)
```

## 6. Applications Pratiques

### 6.1 Parcours d'Arborescence de Fichiers

```python
import os

def lister_fichiers(chemin, indentation=0):
    # Cas de base : traiter le fichier/dossier actuel
    print("  " * indentation + os.path.basename(chemin))
    
    # Cas récursif : si c'est un dossier, explorer son contenu
    if os.path.isdir(chemin):
        try:
            for element in os.listdir(chemin):
                lister_fichiers(os.path.join(chemin, element), 
                              indentation + 1)
        except PermissionError:
            pass
```

### 6.2 Tours de Hanoï

Problème classique : déplacer n disques d'une tour à une autre.

```python
def tours_hanoi(n, source, destination, auxiliaire):
    if n == 1:
        print(f"Déplacer disque 1 de {source} vers {destination}")
        return
    
    # Déplacer n-1 disques vers l'auxiliaire
    tours_hanoi(n - 1, source, auxiliaire, destination)
    
    # Déplacer le plus grand disque vers la destination
    print(f"Déplacer disque {n} de {source} vers {destination}")
    
    # Déplacer les n-1 disques de l'auxiliaire vers la destination
    tours_hanoi(n - 1, auxiliaire, destination, source)

# Utilisation
tours_hanoi(3, 'A', 'C', 'B')
```

### 6.3 Recherche dans un Tableau Trié (Dichotomie)

```python
def recherche_dichotomique(tableau, element, debut=0, fin=None):
    if fin is None:
        fin = len(tableau) - 1
    
    # Cas de base : élément non trouvé
    if debut > fin:
        return -1
    
    milieu = (debut + fin) // 2
    
    # Cas de base : élément trouvé
    if tableau[milieu] == element:
        return milieu
    
    # Cas récursifs
    if tableau[milieu] > element:
        return recherche_dichotomique(tableau, element, debut, milieu - 1)
    else:
        return recherche_dichotomique(tableau, element, milieu + 1, fin)

# Exemple
tableau = [1, 3, 5, 7, 9, 11, 13, 15]
print(recherche_dichotomique(tableau, 7))  # 3
```

## 7. Pièges Courants et Bonnes Pratiques

### 7.1 Oubli du Cas de Base
```python
# ❌ ERREUR : Récursion infinie
def mauvaise_fonction(n):
    return mauvaise_fonction(n - 1)  # Pas de cas de base !

# ✅ CORRECT
def bonne_fonction(n):
    if n == 0:
        return 0
    return bonne_fonction(n - 1)
```

### 7.2 Cas de Base Jamais Atteint
```python
# ❌ ERREUR : Le cas de base n'est jamais atteint avec des nombres négatifs
def compte(n):
    if n == 0:
        return
    print(n)
    compte(n - 1)

compte(-5)  # Erreur !

# ✅ CORRECT
def compte(n):
    if n <= 0:
        return
    print(n)
    compte(n - 1)
```

### 7.3 Profondeur de Récursion Excessive

Python a une limite de récursion (environ 1000 appels par défaut).

```python
import sys

# Vérifier la limite
print(sys.getrecursionlimit())  # 1000 par défaut

# Modifier si nécessaire (avec précaution)
sys.setrecursionlimit(2000)
```

### 7.4 Optimisation avec Mémoïsation

Pour éviter les calculs redondants (comme dans Fibonacci) :

```python
def fibonacci_memo(n, memo={}):
    if n in memo:
        return memo[n]
    
    if n <= 1:
        return n
    
    memo[n] = fibonacci_memo(n - 1, memo) + fibonacci_memo(n - 2, memo)
    return memo[n]

# Beaucoup plus rapide !
print(fibonacci_memo(100))
```

## 8. Exercices Pratiques

### Niveau Débutant

**Exercice 1 :** Écrivez une fonction récursive qui calcule la somme des chiffres d'un nombre.
```
Exemple : somme_chiffres(1234) → 10
```

**Exercice 2 :** Créez une fonction récursive qui inverse une chaîne de caractères.
```
Exemple : inverser("hello") → "olleh"
```

### Niveau Intermédiaire

**Exercice 3 :** Implémentez une fonction récursive qui vérifie si un mot est un palindrome.
```
Exemple : est_palindrome("radar") → True
```

**Exercice 4 :** Écrivez une fonction récursive qui calcule le PGCD de deux nombres (algorithme d'Euclide).
```
Exemple : pgcd(48, 18) → 6
```

### Niveau Avancé

**Exercice 5 :** Créez une fonction qui génère toutes les permutations d'une liste.
```
Exemple : permutations([1, 2, 3]) → [[1,2,3], [1,3,2], [2,1,3], [2,3,1], [3,1,2], [3,2,1]]
```

**Exercice 6 :** Implémentez le tri fusion (merge sort) de manière récursive.

## 9. Solutions des Exercices

### Solution Exercice 1
```python
def somme_chiffres(n):
    if n == 0:
        return 0
    return n % 10 + somme_chiffres(n // 10)
```

### Solution Exercice 2
```python
def inverser(chaine):
    if len(chaine) <= 1:
        return chaine
    return chaine[-1] + inverser(chaine[:-1])
```

### Solution Exercice 3
```python
def est_palindrome(mot):
    if len(mot) <= 1:
        return True
    if mot[0] != mot[-1]:
        return False
    return est_palindrome(mot[1:-1])
```

### Solution Exercice 4
```python
def pgcd(a, b):
    if b == 0:
        return a
    return pgcd(b, a % b)
```

### Solution Exercice 5
```python
def permutations(liste):
    if len(liste) <= 1:
        return [liste]
    
    resultat = []
    for i in range(len(liste)):
        element = liste[i]
        reste = liste[:i] + liste[i+1:]
        for p in permutations(reste):
            resultat.append([element] + p)
    
    return resultat
```

### Solution Exercice 6
```python
def tri_fusion(liste):
    if len(liste) <= 1:
        return liste
    
    milieu = len(liste) // 2
    gauche = tri_fusion(liste[:milieu])
    droite = tri_fusion(liste[milieu:])
    
    return fusionner(gauche, droite)

def fusionner(gauche, droite):
    resultat = []
    i = j = 0
    
    while i < len(gauche) and j < len(droite):
        if gauche[i] < droite[j]:
            resultat.append(gauche[i])
            i += 1
        else:
            resultat.append(droite[j])
            j += 1
    
    resultat.extend(gauche[i:])
    resultat.extend(droite[j:])
    return resultat
```

## 10. Conseils pour Maîtriser la Récursivité

1. **Commencez par identifier le cas de base** : C'est le problème le plus simple à résoudre.

2. **Définissez la relation récursive** : Comment réduire le problème en un sous-problème plus simple ?

3. **Faites confiance à la récursion** : Supposez que l'appel récursif fonctionne correctement.

4. **Tracez l'exécution** : Dessinez l'arbre des appels pour les petites valeurs.

5. **Testez avec des cas simples** : Vérifiez d'abord avec les valeurs minimales.

6. **Pensez à l'optimisation** : Utilisez la mémoïsation si nécessaire.

7. **Considérez l'alternative itérative** : Parfois, une boucle est plus appropriée.


**Points clés à retenir :**
Avec de la pratique, vous développerez l'intuition nécessaire pour reconnaître quand utiliser la récursivité et comment l'implémenter efficacement. Voici quelques points essentiels 
à retenir

- Toujours avoir un cas de base clair
- S'assurer que la récursion progresse vers le cas de base
- Être conscient des limites de profondeur
- Considérer l'optimisation pour les cas complexes
