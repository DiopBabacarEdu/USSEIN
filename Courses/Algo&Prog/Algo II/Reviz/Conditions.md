# TRAVAUX PRATIQUES
## Structures de Contrôle en C (if/else et switch)
### Pour étudiants MPI 2ème année

---

## 🎯 BIENVENUE !

Ce document est un TP complet avec **20 exercices** :
- **Partie 1** : Les structures if/else avec 10 exercices
- **Partie 2** : Les structures switch avec 5 exercices
- **Partie 3** : Fondamentaux des booléens et conditions complexes avec 5 exercices

Lisez attentivement chaque exercice, complétez le code, et testez votre solution !

---

# PARTIE 1 : LES STRUCTURES IF/ELSE

## 📚 CONCEPT : LA STRUCTURE IF/ELSE

La structure `if/else` permet à votre programme de prendre des décisions.

### Syntaxe de base

```c
if (condition) {
    // Code exécuté si la condition est VRAIE
} else {
    // Code exécuté si la condition est FAUSSE
}
```

### Exemple simple

```c
int age = 20;

if (age >= 18) {
    printf("Vous êtes majeur\n");
} else {
    printf("Vous êtes mineur\n");
}
```

### Variante : if/else if/else

```c
if (note >= 90) {
    printf("Excellent\n");
} else if (note >= 80) {
    printf("Très bien\n");
} else if (note >= 70) {
    printf("Bien\n");
} else {
    printf("Insuffisant\n");
}
```

### ⚠️ IMPORTANT

- L'ordre des `if/else if` compte ! Mettez les conditions les plus restrictives en premier
- Les accolades `{ }` sont **OBLIGATOIRES**
- Ne confondez pas `=` (attribution) avec `==` (comparaison)
- Testez **TOUJOURS** votre code avec des cas vrais ET faux

---

## 📝 EXERCICE 1.1 : Vérifier la majorité

### Objectif
Écrire un programme qui demande l'âge d'une personne et affiche si elle est majeure ou mineure.

### Spécifications
- Demander à l'utilisateur son âge
- Si l'âge >= 18, afficher `"Vous êtes majeur"`
- Sinon, afficher `"Vous êtes mineur"`

### Exemple d'exécution
```
Entrez votre âge : 15
Vous êtes mineur
```

### Code à compléter

```c
#include <stdio.h>

int main() {
    int age;
    
    printf("Entrez votre âge : ");
    scanf("%d", &age);
    
    // À COMPLÉTER : if/else pour vérifier si age >= 18

    return 0;
}
```

### Aide
- Utilisez `scanf("%d", &age)` pour lire l'entrée
- La structure `if/else` doit contenir la comparaison `age >= 18`
- Utilisez `printf()` pour afficher le résultat

---

## 📝 EXERCICE 1.2 : Classifier une note

### Objectif
Convertir une note numérique en note littérale.

### Spécifications
- Lire une note entre 0 et 100
- Afficher la note littérale correspondante :
  - **90-100** : `"Excellent"`
  - **80-89** : `"Très bien"`
  - **70-79** : `"Bien"`
  - **60-69** : `"Passable"`
  - **0-59** : `"Insuffisant"`

### Exemple d'exécution
```
Entrez votre note : 85
Très bien
```

### Code à compléter

```c
#include <stdio.h>

int main() {
    int note;
    
    printf("Entrez votre note (0-100) : ");
    scanf("%d", &note);
    
    // À COMPLÉTER : if/else if/else pour les notes

    return 0;
}
```

### Aide
- Utilisez `if/else if/else` pour les multiples conditions
- **L'ORDRE EST IMPORTANT** : mettez d'abord la condition la plus haute (`>= 90`)
- Pensez à tester avec : `95, 85, 75, 65, 55`

---

## 📝 EXERCICE 1.3 : Déterminer le signe d'un nombre

### Objectif
Lire un nombre et afficher s'il est positif, négatif ou zéro.

### Spécifications
- Lire un nombre entier
- Afficher `"Positif"` si nombre > 0
- Afficher `"Négatif"` si nombre < 0
- Afficher `"Zéro"` si nombre == 0

### Exemple d'exécution
```
Entrez un nombre : 42
Positif
```

### Code à compléter

```c
#include <stdio.h>

int main() {
    int nombre;
    
    printf("Entrez un nombre : ");
    scanf("%d", &nombre);
    
    // À COMPLÉTER : if/else if/else pour le signe

    return 0;
}
```

### Aide
- Trois cas à traiter : `>`, `<`, `==`
- Pensez à tester avec : `5, -10, 0`

---

## 📝 EXERCICE 1.4 : Vérifier une année bissextile

### Objectif
Vérifier si une année donnée est bissextile.

### Spécifications
Une année est bissextile si :
- Elle est divisible par 400, **OU**
- Elle est divisible par 4 **MAIS pas par 100**

### Exemple d'exécution
```
Entrez une année : 2020
L'année 2020 est bissextile

Entrez une année : 2021
L'année 2021 n'est pas bissextile
```

### Code à compléter

```c
#include <stdio.h>

int main() {
    int annee;
    
    printf("Entrez une année : ");
    scanf("%d", &annee);
    
    // À COMPLÉTER : vérifier si l'année est bissextile
    // (divisible par 400) OU (divisible par 4 ET pas par 100)

    return 0;
}
```

### Aide
- Pour vérifier si divisible : utilisez l'opérateur modulo `%`
- `annee % 400 == 0` : divisible par 400
- `annee % 4 == 0 && annee % 100 != 0` : divisible par 4 mais pas 100
- Testez avec : `2000, 2004, 2020, 1900, 2021`

---

## 📝 EXERCICE 1.5 : Classer un triangle

### Objectif
Lire trois côtés et déterminer le type de triangle.

### Spécifications
- **Équilatéral** : les trois côtés sont égaux
- **Isocèle** : deux côtés sont égaux
- **Scalène** : tous les côtés sont différents
- **Invalide** : les trois côtés ne forment pas un triangle

### Exemple d'exécution
```
Entrez le côté 1 : 5
Entrez le côté 2 : 5
Entrez le côté 3 : 5
Triangle équilatéral
```

### Code à compléter

```c
#include <stdio.h>

int main() {
    int cote1, cote2, cote3;
    
    printf("Entrez le côté 1 : ");
    scanf("%d", &cote1);
    printf("Entrez le côté 2 : ");
    scanf("%d", &cote2);
    printf("Entrez le côté 3 : ");
    scanf("%d", &cote3);
    
    // À COMPLÉTER : classer le triangle

    return 0;
}
```

### Aide
- Équilatéral : `cote1 == cote2 && cote2 == cote3`
- Isocèle : `(cote1 == cote2) || (cote2 == cote3) || (cote1 == cote3)` **MAIS pas équilatéral**
- Pensez à l'ordre des conditions !

---

## 📝 EXERCICE 1.6 : Imbrication de conditions

### Objectif
Déterminer si une personne peut voter.

### Spécifications
- Doit avoir au moins 18 ans
- Doit être citoyen français (oui/non)
- Doit ne pas avoir été condamné (oui/non)

Si une condition n'est pas remplie, afficher le motif du refus. Sinon, afficher `"Vous pouvez voter"`

### Exemple d'exécution
```
Êtes-vous majeur (1=oui, 0=non) ? 1
Êtes-vous français (1=oui, 0=non) ? 1
Avez-vous été condamné (1=oui, 0=non) ? 0
Vous pouvez voter
```

### Code à compléter

```c
#include <stdio.h>

int main() {
    int majeur, francais, condamne;
    
    printf("Êtes-vous majeur (1=oui, 0=non) ? ");
    scanf("%d", &majeur);
    printf("Êtes-vous français (1=oui, 0=non) ? ");
    scanf("%d", &francais);
    printf("Avez-vous été condamné (1=oui, 0=non) ? ");
    scanf("%d", &condamne);
    
    // À COMPLÉTER : vérifier les trois conditions

    return 0;
}
```

### Aide
- Vérifiez d'abord si `majeur == 1`
- Puis vérifiez `francais == 1`
- Puis vérifiez `condamne == 0`
- Utilisez des `if/else` imbriqués

---

## 📝 EXERCICE 1.7 : L'opérateur ternaire (raccourci)

### Objectif
Utiliser l'opérateur ternaire pour simplifier les conditions simples.

### Spécifications
L'opérateur ternaire a cette syntaxe :
```c
variable = (condition) ? valeur_si_vrai : valeur_si_faux;
```

### Exemple
```c
int age = 20;
char* statut = (age >= 18) ? "Adulte" : "Mineur";
printf("%s\n", statut);  // Affiche "Adulte"
```

### Exercice
Écrivez un programme qui demande un nombre et affiche s'il est pair ou impair.

### Code à compléter

```c
#include <stdio.h>

int main() {
    int nombre;
    char* parite;
    
    printf("Entrez un nombre : ");
    scanf("%d", &nombre);
    
    // À COMPLÉTER : utiliser l'opérateur ternaire
    // parite = (nombre % 2 == 0) ? "Pair" : "Impair";
    
    printf("%d est %s\n", nombre, parite);
    
    return 0;
}
```

---

## 📝 EXERCICE 1.8 : Prix avec réduction

### Objectif
Calculer le prix final avec réduction selon le montant.

### Spécifications
- Si montant >= 100€ : réduction de 10%
- Si montant >= 50€ : réduction de 5%
- Sinon : pas de réduction

### Exemple d'exécution
```
Entrez le montant : 75
Montant original : 75.00 €
Réduction : 5%
Montant final : 71.25 €
```

### Code à compléter

```c
#include <stdio.h>

int main() {
    float montant;
    float reduction = 0;
    float montant_final;
    
    printf("Entrez le montant : ");
    scanf("%f", &montant);
    
    // À COMPLÉTER : déterminer la réduction

    return 0;
}
```

### Aide
- Utilisez `if/else if` pour les conditions
- Calculez le montant final : `montant_final = montant - (montant * reduction / 100)`
- Testez avec : `120, 75, 30`

---

## 📝 EXERCICE 1.9 : Jours du mois

### Objectif
Déterminer le nombre de jours dans un mois.

### Spécifications
- Lire un numéro de mois (1-12)
- Afficher le nombre de jours (ignorer les années bissextiles)
  - Janvier, Mars, Mai, Juillet, Août, Octobre, Décembre : **31 jours**
  - Avril, Juin, Septembre, Novembre : **30 jours**
  - Février : **28 jours**

### Exemple d'exécution
```
Entrez le mois (1-12) : 4
Le mois 4 a 30 jours
```

### Code à compléter

```c
#include <stdio.h>

int main() {
    int mois;
    int jours = 0;
    
    printf("Entrez le mois (1-12) : ");
    scanf("%d", &mois);
    
    // À COMPLÉTER : déterminer le nombre de jours

    return 0;
}
```

### Aide
- Utilisez `if/else if` pour les différents cas
- Vous pouvez regrouper les mois avec les mêmes jours : `(mois == 1 || mois == 3 || ...)`

---

## 📝 EXERCICE 1.10 : Calculatrice simple

### Objectif
Créer une calculatrice qui effectue une opération simple (+, -, *, /).

### Spécifications
- Demander deux nombres
- Demander une opération (+, -, *, /)
- Effectuer le calcul ET gérer la division par zéro
- Afficher le résultat

### Exemple d'exécution
```
Entrez le premier nombre : 15
Entrez le deuxième nombre : 3
Entrez l'opération (+, -, *, /) : /
15 / 3 = 5

Entrez le premier nombre : 10
Entrez le deuxième nombre : 0
Entrez l'opération (+, -, *, /) : /
Erreur : division par zéro !
```

### Code à compléter

```c
#include <stdio.h>

int main() {
    float num1, num2;
    char operation;
    float resultat;
    
    printf("Entrez le premier nombre : ");
    scanf("%f", &num1);
    printf("Entrez le deuxième nombre : ");
    scanf("%f", &num2);
    printf("Entrez l'opération (+, -, *, /) : ");
    scanf(" %c", &operation);
    
    // À COMPLÉTER : calculer selon l'opération
    // Attention à la division par zéro !

    return 0;
}
```

### Aide
- Utilisez `if/else if` pour les différentes opérations
- Pour la division, vérifiez d'abord que `num2 != 0`
- Note : `scanf(" %c", &operation)` avec un espace avant `%c`
- Testez avec : `10+5, 10-5, 10*5, 10/5, 10/0`

---

# PARTIE 2 : LES STRUCTURES SWITCH

## 📚 CONCEPT : LA STRUCTURE SWITCH

La structure `switch` est utilisée pour comparer une variable à plusieurs valeurs. C'est une alternative plus lisible aux multiples `if/else if`.

### Syntaxe de base

```c
switch (variable) {
    case valeur1:
        // Code exécuté si variable == valeur1
        break;
    
    case valeur2:
        // Code exécuté si variable == valeur2
        break;
    
    default:
        // Code exécuté si aucun case ne correspond
        break;
}
```

### Exemple

```c
int jour = 3;

switch (jour) {
    case 1:
        printf("Lundi\n");
        break;
    case 2:
        printf("Mardi\n");
        break;
    case 3:
        printf("Mercredi\n");
        break;
    default:
        printf("Jour invalide\n");
}
```

### ⚠️ IMPORTANT : LE BREAK EST OBLIGATOIRE !

Sans `break`, l'exécution continue au case suivant (phénomène de "chute") :

#### ❌ MAUVAIS (sans break)

```c
switch (x) {
    case 1:
        printf("Un\n");      // Affiché
        // Pas de break !
    case 2:
        printf("Deux\n");    // AUSSI affiché ! (Erreur !)
        break;
}
```

#### ✅ BON (avec break)

```c
switch (x) {
    case 1:
        printf("Un\n");
        break;
    case 2:
        printf("Deux\n");
        break;
}
```

### Chute intentionnelle

Vous pouvez utiliser la chute intentionnellement pour regrouper plusieurs cases :

```c
switch (mois) {
    case 1:
    case 3:
    case 5:
    case 7:
    case 8:
    case 10:
    case 12:
        printf("31 jours\n");
        break;
    case 4:
    case 6:
    case 9:
    case 11:
        printf("30 jours\n");
        break;
}
```

---

## 📝 EXERCICE 2.1 : Jours de la semaine

### Objectif
Afficher le nom d'un jour selon son numéro.

### Spécifications
- Lire un numéro de jour (1-7)
- Afficher le nom du jour correspondant
- Afficher `"Jour invalide"` pour d'autres valeurs

### Exemple d'exécution
```
Entrez le numéro du jour (1-7) : 3
Mercredi
```

### Code à compléter

```c
#include <stdio.h>

int main() {
    int jour;
    
    printf("Entrez le numéro du jour (1-7) : ");
    scanf("%d", &jour);
    
    // À COMPLÉTER : switch pour afficher le jour

    return 0;
}
```

### Aide
- Utilisez `switch` avec les cases 1 à 7
- **N'OUBLIEZ PAS LES break !**
- Ajoutez un `default` pour les valeurs invalides
- Testez avec : `1, 4, 7, 8, 0`

---

## 📝 EXERCICE 2.2 : Menu de restaurant

### Objectif
Créer un menu de restaurant avec switch.

### Spécifications
Menu principal :
- 1 = Entrées
- 2 = Plats
- 3 = Desserts
- 4 = Boissons
- 5 = Quitter

### Exemple d'exécution
```
Menu principal :
1. Entrées
2. Plats
3. Desserts
4. Boissons
5. Quitter

Votre choix : 2
Vous avez choisi : Plats
```

### Code à compléter

```c
#include <stdio.h>

int main() {
    int choix;
    
    printf("Menu principal :\n");
    printf("1. Entrées\n");
    printf("2. Plats\n");
    printf("3. Desserts\n");
    printf("4. Boissons\n");
    printf("5. Quitter\n");
    printf("Votre choix : ");
    scanf("%d", &choix);
    
    // À COMPLÉTER : switch pour afficher le choix

    return 0;
}
```

### Aide
- Utilisez `switch` avec les cases 1 à 5
- Pour le choix 5, afficher `"Au revoir"`
- N'oubliez pas les `break`
- Ajoutez un `default` pour les choix invalides

---

## 📝 EXERCICE 2.3 : Grades militaires

### Objectif
Afficher la description d'un grade militaire selon son numéro.

### Spécifications
- 1 = Soldat
- 2 = Caporal
- 3 = Sergent
- 4 = Lieutenant
- 5 = Capitaine
- 6 = Commandant
- Autre = Grade inconnu

### Code à compléter

```c
#include <stdio.h>

int main() {
    int grade;
    
    printf("Entrez le numéro du grade (1-6) : ");
    scanf("%d", &grade);
    
    // À COMPLÉTER : switch pour afficher le grade

    return 0;
}
```

### Aide
- Switch simple avec cases 1 à 6
- N'oubliez pas `break` et `default`

---

## 📝 EXERCICE 2.4 : Conversion de notes (A, B, C, D, F)

### Objectif
Lire un caractère représentant une note et afficher sa description.

### Spécifications
- A = Excellent
- B = Très bien
- C = Bien
- D = Passable
- F = Échoué
- Autre = Note invalide

### Exemple d'exécution
```
Entrez votre note (A, B, C, D, F) : B
Très bien
```

### Code à compléter

```c
#include <stdio.h>

int main() {
    char note;
    
    printf("Entrez votre note (A, B, C, D, F) : ");
    scanf(" %c", &note);
    
    // À COMPLÉTER : switch pour afficher la description

    return 0;
}
```

### Aide
- Utilisez `switch` avec des caractères : `case 'A':`
- Attention : `scanf(" %c", &note)` avec un espace
- Testez avec : `A, B, C, D, F, Z`

---

## 📝 EXERCICE 2.5 : Nombre de jours (avec chute intentionnelle)

### Objectif
Déterminer le nombre de jours dans un mois en utilisant la chute intentionnelle.

### Spécifications
- **31 jours** : 1, 3, 5, 7, 8, 10, 12
- **30 jours** : 4, 6, 9, 11
- **28 jours** : 2

### Exemple d'exécution
```
Entrez le mois (1-12) : 4
Le mois 4 a 30 jours
```

### Code à compléter

```c
#include <stdio.h>

int main() {
    int mois;
    
    printf("Entrez le mois (1-12) : ");
    scanf("%d", &mois);
    
    // À COMPLÉTER : switch avec chute intentionnelle

    return 0;
}
```

### Aide
- La "chute intentionnelle" signifie laisser plusieurs cases sans break
- Exemple :
```c
case 1:
case 3:
case 5:
    printf("31 jours\n");
    break;
```

---

# PARTIE 3 : FONDAMENTAUX DES BOOLÉENS ET CONDITIONS COMPLEXES

## 📚 LES BOOLÉENS EN C

### Qu'est-ce qu'un booléen ?

Un booléen est une valeur qui peut être soit **VRAIE** soit **FAUSSE**.

En C, il n'existe pas de type booléen natif avant C99, donc on utilise :
- **0** = FAUX
- **1** (ou toute valeur non-zéro) = VRAI

### Exemples

```c
int resultat = (5 > 3);    // Vaut 1 (VRAI)
int echec = (5 < 3);       // Vaut 0 (FAUX)
```

### Opérateurs de comparaison

Ces opérateurs comparent deux valeurs et retournent 1 (vrai) ou 0 (faux).

| Opérateur | Signification | Exemple |
|-----------|---------------|---------|
| `==` | Égal | `5 == 5` → 1 (vrai) |
| `!=` | Différent | `5 != 3` → 1 (vrai) |
| `<` | Inférieur | `3 < 5` → 1 (vrai) |
| `>` | Supérieur | `5 > 3` → 1 (vrai) |
| `<=` | Inférieur ou égal | `5 <= 5` → 1 (vrai) |
| `>=` | Supérieur ou égal | `5 >= 5` → 1 (vrai) |

### Exemple

```c
int age = 20;

if (age >= 18) {
    printf("Majeur\n");
} else {
    printf("Mineur\n");
}
```

### ⚠️ ATTENTION : = vs ==

#### ❌ ERREUR FRÉQUENTE

```c
if (age = 18) {  // Ceci ATTRIBUE 18 à age, ne compare pas !
    printf("Vous avez 18 ans\n");
}
```

#### ✅ BON

```c
if (age == 18) {  // Ceci COMPARE age à 18
    printf("Vous avez exactement 18 ans\n");
}
```

---

## 📚 LES OPÉRATEURS LOGIQUES

Les opérateurs logiques permettent de combiner plusieurs conditions.

### && (ET logique)

**Syntaxe** : `condition1 && condition2`

Résultat **VRAI** si les **DEUX** conditions sont vraies.

#### Tableau de vérité

| condition1 | condition2 | condition1 && condition2 |
|------------|------------|--------------------------|
| 0 | 0 | 0 |
| 0 | 1 | 0 |
| 1 | 0 | 0 |
| 1 | 1 | **1** |

#### Exemple

```c
int age = 25;
int permis = 1;

if (age >= 18 && permis == 1) {
    printf("Vous pouvez conduire\n");
}
```

### || (OU logique)

**Syntaxe** : `condition1 || condition2`

Résultat **VRAI** si **AU MOINS UNE** condition est vraie.

#### Tableau de vérité

| condition1 | condition2 | condition1 \|\| condition2 |
|------------|------------|--------------------------|
| 0 | 0 | 0 |
| 0 | 1 | **1** |
| 1 | 0 | **1** |
| 1 | 1 | **1** |

#### Exemple

```c
int age = 10;

if (age < 12 || age > 80) {
    printf("Tarif réduit\n");
} else {
    printf("Tarif normal\n");
}
```

### ! (NON logique)

**Syntaxe** : `!condition`

Inverse la valeur d'une condition.

#### Tableau de vérité

| condition | !condition |
|-----------|-----------|
| 0 | **1** |
| 1 | **0** |

#### Exemple

```c
int condamne = 0;

if (!condamne) {
    printf("Vous pouvez voter\n");
}
```

### Combinaison de conditions

Vous pouvez combiner plusieurs opérateurs logiques.

#### Exemple complexe

```c
int age = 25;
int revenu = 800;
int emploi = 1;

if ((age >= 25 || revenu >= 1000) && emploi == 1) {
    printf("Prêt accordé\n");
}
```

### Ordre de priorité

1. `!` (NON) - le plus prioritaire
2. `&&` (ET)
3. `||` (OU) - le moins prioritaire

**Donc** : `!a || b && c` signifie : `(!a) || (b && c)`

### 💡 Utilisez les parenthèses pour clarifier !

- ✅ **BON** : `if ((a && b) || c)`
- ❌ **CONFUS** : `if (a && b || c)`

---

## 📝 EXERCICE 3.1 : Opérateur ET (&&)

### Objectif
Utiliser l'opérateur `&&` pour combiner deux conditions.

### Spécifications
Une personne peut accéder à une attraction si :
- Elle a au moins 12 ans
- **ET** elle a au moins 1,40 m de taille

Afficher `"Accès autorisé"` ou `"Accès refusé"`

### Exemple d'exécution
```
Entrez votre âge : 15
Entrez votre taille (en cm) : 160
Accès autorisé

Entrez votre âge : 10
Entrez votre taille (en cm) : 160
Accès refusé
```

### Code à compléter

```c
#include <stdio.h>

int main() {
    int age;
    int taille;
    
    printf("Entrez votre âge : ");
    scanf("%d", &age);
    printf("Entrez votre taille (en cm) : ");
    scanf("%d", &taille);
    
    // À COMPLÉTER : vérifier si age >= 12 ET taille >= 140

    return 0;
}
```

### Aide
- Utilisez : `if (age >= 12 && taille >= 140)`
- Les **DEUX** conditions doivent être vraies
- Testez avec : `(15, 160), (10, 160), (15, 130), (10, 130)`

---

## 📝 EXERCICE 3.2 : Opérateur OU (||)

### Objectif
Utiliser l'opérateur `||` pour combiner deux conditions.

### Spécifications
Une réduction s'applique si :
- La personne est étudiante, **OU**
- La personne est senior (>= 65 ans)

### Exemple d'exécution
```
Êtes-vous étudiant ? (1=oui, 0=non) : 1
Quel est votre âge : 22
Réduction appliquée

Êtes-vous étudiant ? (1=oui, 0=non) : 0
Quel est votre âge : 70
Réduction appliquée

Êtes-vous étudiant ? (1=oui, 0=non) : 0
Quel est votre âge : 35
Pas de réduction
```

### Code à compléter

```c
#include <stdio.h>

int main() {
    int etudiant;
    int age;
    
    printf("Êtes-vous étudiant ? (1=oui, 0=non) : ");
    scanf("%d", &etudiant);
    printf("Quel est votre âge : ");
    scanf("%d", &age);
    
    // À COMPLÉTER : vérifier si etudiant == 1 OU age >= 65

    return 0;
}
```

### Aide
- Utilisez : `if (etudiant == 1 || age >= 65)`
- **AU MOINS UNE** des conditions doit être vraie
- Testez avec : `(1, 22), (0, 70), (0, 35)`

---

## 📝 EXERCICE 3.3 : Opérateur NON (!)

### Objectif
Utiliser l'opérateur `!` pour inverser une condition.

### Spécifications
Une personne peut voter si elle n'a pas été bannie des scrutins.

### Exemple d'exécution
```
Avez-vous été banni ? (1=oui, 0=non) : 0
Vous pouvez voter

Avez-vous été banni ? (1=oui, 0=non) : 1
Vous ne pouvez pas voter
```

### Code à compléter

```c
#include <stdio.h>

int main() {
    int banni;
    
    printf("Avez-vous été banni ? (1=oui, 0=non) : ");
    scanf("%d", &banni);
    
    // À COMPLÉTER : vérifier si !banni

    return 0;
}
```

### Aide
- Utilisez : `if (!banni)`
- `!0` devient **1** (vrai)
- `!1` devient **0** (faux)

---

## 📝 EXERCICE 3.4 : Combinaison complexe

### Objectif
Combiner plusieurs opérateurs logiques.

### Spécifications
Un prêt est accordé si :
- L'âge est entre 25 et 65 ans
- **ET** le revenu mensuel est >= 1500€
- **ET** la personne n'a pas de dettes

### Exemple d'exécution
```
Entrez votre âge : 35
Entrez votre revenu mensuel : 2000
Avez-vous des dettes ? (1=oui, 0=non) : 0
Prêt accordé

Entrez votre âge : 22
Entrez votre revenu mensuel : 2000
Avez-vous des dettes ? (1=oui, 0=non) : 0
Prêt refusé (âge insuffisant)
```

### Code à compléter

```c
#include <stdio.h>

int main() {
    int age;
    int revenu;
    int dettes;
    
    printf("Entrez votre âge : ");
    scanf("%d", &age);
    printf("Entrez votre revenu mensuel : ");
    scanf("%d", &revenu);
    printf("Avez-vous des dettes ? (1=oui, 0=non) : ");
    scanf("%d", &dettes);
    
    // À COMPLÉTER : vérifier les trois conditions avec && et !

    return 0;
}
```

### Aide
Conditions :
1. `age >= 25 && age <= 65`
2. `revenu >= 1500`
3. `!dettes` (pas de dettes)

Combinez avec `&&` : `(condition1) && (condition2) && (condition3)`

---

## 📝 EXERCICE 3.5 : Conditions multiples imbriquées

### Objectif
Gérer plusieurs conditions imbriquées avec des messages d'erreur détaillés.

### Spécifications
Pour un contrat de travail, la personne doit :
1. Être majeure (>= 18 ans)
2. Avoir un diplôme d'études (1=oui, 0=non)
3. Avoir une expérience (en années)
   - Si expérience >= 5 : **CDI**
   - Si expérience >= 2 : **CDD**
   - Si expérience >= 0 : **Stage**

Si une condition n'est pas remplie, afficher le motif du refus.

### Exemple d'exécution
```
Entrez votre âge : 20
Avez-vous un diplôme ? (1=oui, 0=non) : 1
Entrez vos années d'expérience : 6
Contrat : CDI

Entrez votre âge : 17
Avez-vous un diplôme ? (1=oui, 0=non) : 1
Entrez vos années d'expérience : 3
Vous êtes mineur, impossible de signer un contrat
```

### Code à compléter

```c
#include <stdio.h>

int main() {
    int age;
    int diplome;
    int experience;
    
    printf("Entrez votre âge : ");
    scanf("%d", &age);
    printf("Avez-vous un diplôme ? (1=oui, 0=non) : ");
    scanf("%d", &diplome);
    printf("Entrez vos années d'expérience : ");
    scanf("%d", &experience);
    
    // À COMPLÉTER : vérifier les conditions dans l'ordre

    return 0;
}
```

### Aide
- Vérifiez d'abord si `age >= 18`
- Puis si `diplome == 1`
- Enfin, classez par expérience avec `if/else if`
- Utilisez des `if/else` imbriqués

---

# 📋 RÉSUMÉ ET CONSEILS

## Points importants à retenir

### 1. LES IF/ELSE
- Utilisez pour les **conditions complexes** ou les **plages**
- Ne confondez pas `=` et `==`
- Les accolades `{ }` sont **obligatoires**
- Mettez les conditions les plus restrictives en **premier**

### 2. LES SWITCH
- Utilisez pour **comparer** une variable à plusieurs valeurs
- Le `break` est **OBLIGATOIRE** (sauf chute intentionnelle)
- Toujours ajouter un `default`
- Plus lisible que de nombreux `if/else if`

### 3. LES BOOLÉENS
- **0** = faux, **1** = vrai
- Utilisez les opérateurs de comparaison : `==, !=, <, >, <=, >=`
- Combinez avec `&&, ||, !`

### 4. COMBINER LES CONDITIONS
- `&&` : **TOUS** les conditions doivent être vraies
- `||` : **AU MOINS UNE** condition doit être vraie
- `!` : inverse la condition
- Utilisez les **parenthèses** pour clarifier

### 5. TESTER SON CODE
- Testez **TOUJOURS** avec des cas vrais ET faux
- Testez les **valeurs limites**
- Compilez sans avertissements : `gcc -Wall -Wextra`

---

## ✅ CHECKLIST AVANT DE SOUMETTRE

- ☐ Tout `if` a des accolades `{ }`
- ☐ Pas de `=` au lieu de `==` dans les conditions
- ☐ Tous les `break;` sont présents dans les `switch`
- ☐ Un `default` dans chaque `switch`
- ☐ Indentation cohérente (4 espaces par niveau)
- ☐ Logique testée avec des cas vrais ET faux
- ☐ Noms de variables clairs
- ☐ Code compile sans avertissements
- ☐ Résultats corrects selon l'exemple fourni

---

## ❌ ERREURS COURANTES À ÉVITER

### ❌ Oublier les accolades dans les if/else

```c
if (age >= 18)
    printf("Adulte\n");
    printf("Bienvenue\n");  // Exécuté peu importe la condition !
```

### ✅ Toujours utiliser les accolades

```c
if (age >= 18) {
    printf("Adulte\n");
    printf("Bienvenue\n");
}
```

---

### ❌ Confondre = et ==

```c
if (age = 18) {  // Ceci attribue 18 à age !
    printf("Vous avez 18 ans\n");
}
```

### ✅ Utiliser ==

```c
if (age == 18) {  // Ceci compare age à 18
    printf("Vous avez exactement 18 ans\n");
}
```

---

### ❌ Oublier break dans un switch

```c
switch (x) {
    case 1:
        printf("Un\n");
        // Pas de break !
    case 2:
        printf("Deux\n");  // Aussi affiché !
}
```

### ✅ Toujours ajouter break

```c
switch (x) {
    case 1:
        printf("Un\n");
        break;
    case 2:
        printf("Deux\n");
        break;
}
```

---

### ❌ Imbrication excessive

```c
if (a) {
    if (b) {
        if (c) {
            if (d) {
                if (e) {
                    // Trop imbriqué !
                }
            }
        }
    }
}
```

### ✅ Utiliser switch au lieu de nombreux if/else

```c
switch (type) {
    case A: ... break;
    case B: ... break;
    case C: ... break;
}
```

---

# 🎉 FIN DU TP

Félicitations d'avoir complété ce TP ! Vous maîtrisez maintenant les structures de contrôle en C.

**Bon travail ! 🚀**
