Voici 10 exercices progressifs sur la récursivité, allant des bases aux problèmes plus avancés. Ils couvrent différents domaines d'application.

---

### **Exercice 1 : La Base - Factorielle**
Écrire une fonction récursive `factorielle(n)` qui calcule la factorielle d'un entier positif `n`.
*   **Rappel :** `n! = n * (n-1)!` avec `0! = 1`.
*   **Exemple :** `factorielle(5)` doit retourner `120`.

### **Exercice 2 : Suite de Fibonacci**
Écrire une fonction récursive `fibonacci(n)` qui retourne le `n`-ième terme de la suite de Fibonacci.
*   **Définition :** `F(0) = 0`, `F(1) = 1`, `F(n) = F(n-1) + F(n-2)` pour `n > 1`.
*   **Exemple :** `fibonacci(7)` doit retourner `13`.

### **Exercice 3 : Somme des éléments d'une liste**
Écrire une fonction récursive `somme_liste(liste)` qui calcule la somme de tous les éléments d'une liste d'entiers.
*   **Indice :** Penser à décomposer la liste en `premier_élément + reste_de_la_liste`.
*   **Exemple :** `somme_liste([1, 2, 3, 4])` doit retourner `10`.

### **Exercice 4 : Longueur d'une liste**
Écrire une fonction récursive `longueur(liste)` qui retourne le nombre d'éléments d'une liste **sans utiliser la fonction `len()`**.
*   **Exemple :** `longueur(['a', 'b', 'c', 'd', 'e'])` doit retourner `5`.

### **Exercice 5 : Recherche d'un élément dans une liste**
Écrire une fonction récursive `contient(liste, valeur)` qui retourne `True` si `valeur` est présente dans `liste`, et `False` sinon.
*   **Exemple :** `contient([5, 2, 9, 1], 9)` doit retourner `True`. `contient([5, 2, 9, 1], 4)` doit retourner `False`.

### **Exercice 6 : Inversion de chaîne**
Écrire une fonction récursive `inverser(chaine)` qui retourne la chaîne de caractères passée en argument à l'envers.
*   **Indice :** `inverser("monde") = "e" + inverser("mond")`
*   **Exemple :** `inverser("recursif")` doit retourner `"fisrucer"`.

### **Exercice 7 : Calcul de la puissance**
Écrire une fonction récursive `puissance(x, n)` qui calcule `x` à la puissance `n` (avec `n` entier positif ou nul).
*   **Rappel :** `x^n = x * x^(n-1)` avec `x^0 = 1`.
*   **Exemple :** `puissance(2, 5)` doit retourner `32`.

### **Exercice 8 : Tours de Hanoï (Problème classique)**
Écrire une procédure récursive `hanoi(n, depart, intermediaire, arrivee)` qui affiche les instructions pour résoudre le problème des tours de Hanoï avec `n` disques.
*   **Règles :** On ne peut déplacer qu'un disque à la fois, et on ne peut pas placer un disque plus grand sur un disque plus petit.
*   **Exemple pour n=2 :** L'appel `hanoi(2, 'A', 'B', 'C')` doit afficher :
    ```
    Déplacer le disque 1 de A vers B
    Déplacer le disque 2 de A vers C
    Déplacer le disque 1 de B vers C
    ```

### **Exercice 9 : Parcours d'arborescence (simulée)**
On représente un système de fichiers par un dictionnaire. Les clés sont des noms de dossiers/fichiers. Si la valeur associée est un dictionnaire, c'est un sous-dossier, sinon (une chaîne), c'est un fichier.
Écrire une fonction récursive `afficher_arborescence(racine, prefixe="")` qui affiche l'arborescence de manière indentée.
*   **Exemple :**
    ```python
    fs = {
        "Documents": {
            "Travail": {"rapport.txt": "contenu"},
            "Perso": {"vacances.jpg": "contenu"}
        },
        "Telechargements": {"logiciel.exe": "contenu"}
    }
    afficher_arborescence(fs)
    ```
    Doit afficher (par exemple) :
    ```
    Documents/
        Travail/
            rapport.txt
        Perso/
            vacances.jpg
    Telechargements/
        logiciel.exe
    ```

### **Exercice 10 : Génération de toutes les combinaisons de parenthèses valides (Défi)**
Écrire une fonction récursive `generer_parentheses(n)` qui génère toutes les combinaisons bien formées de `n` paires de parenthèses.
*   **Règle :** Une combinaison est valide si elle est non vide, et si tout préfixe contient au moins autant de `(` que de `)`. On a exactement `n` parenthèses ouvrantes et `n` parenthèses fermantes.
*   **Exemple pour n=3 :** `generer_parentheses(3)` doit retourner une liste contenant, entre autres : `["((()))", "(()())", "(())()", "()(())", "()()()"]`.

---

### **Conseils pédagogiques à donner aux étudiants :**
1.  **Identifier le cas de base :** C'est la condition qui arrête la récursion (ex: `n == 0` pour la factorielle).
2.  **Définir le cas récursif :** Il doit se ramener à un problème **identique mais plus petit** (ex: `factorielle(n) = n * factorielle(n-1)`).
3.  **Vérifier la convergence :** Chaque appel récursif doit se rapprocher du cas de base, sous peine de récursivité infinie.
4.  **Penser à la pile d'appels :** Chaque appel est empilé en mémoire. Pour les problèmes profonds, cela peut causer un débordement de pile (*stack overflow*). C'est le cas classique de `fibonacci(n)` naïve.
5.  **Pour optimiser :** On peut utiliser la **mémoïsation** (stocker les résultats des sous-problèmes déjà calculés, comme pour Fibonacci).

Ces exercices permettent de bien comprendre le principe de décomposition et l'utilisation de la pile d'exécution. Bon courage à vos étudiants
