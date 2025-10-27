# Insertion dans un arbre binaire
Pour insérer une valeur dans un arbre, voici les étapes :
1. Commencer par la racine
2. Comparer l'élément à insérer avec la racine, s'il est inférieur à la racine, appel récursif pour sous-arbre gauche
3. Sinon s'il est supérieur à la racine, appelrécursif pour sous-arbre droit
4. Une fois atteint le bon emplacement, insérer simplement ce nœud à gauche (s'il est inférieur au courant), sinon à droite.

## Code source en C 
### Programme : Insertion dans un arbre de recherche

```c
// Programme pour inserer une valeur dans un Arbre binaire
#include<stdio.h> 
#include<stdlib.h> 
   
struct node 
{ 
    int valeur; 
    struct node *gauche;
    struct node *droit; 
}; 
   
// Fonction qui crée un nouveau noeud
struct node *nouveauNoeud(int item) 
{ 
    struct node *temp =  (struct node *)malloc(sizeof(struct node)); 
    temp->valeur = item; 
    temp->gauche = temp->droit = NULL; 
    return temp; 
} 
   
// parcours infixé(en ordre)
void infixe(struct node *root) 
{ 
    if (root != NULL) 
    { 
        infixe(root->gauche); 
        printf("%d \n", root->valeur); 
        infixe(root->droit); 
    } 
} 
   
/* Une fonction qui insère un nouveau nœud avec une valeur donnée dans un arbre */
struct node* inserer(struct node* node, int valeur) 
{ 
    /* Retourne un nouveau noeud si l'arbre est vide */
    if (node == NULL) return nouveauNoeud(valeur); 
  
    /* Sinon, appel récursif sous-arbre gauche ou droite */
    if (valeur < node->valeur) 
        node->gauche  = inserer(node->gauche, valeur); 
    else if (valeur > node->valeur) 
        node->droit = inserer(node->droit, valeur);    
  
    /* retourne un pointeur (non modifié)  */
    return node; 
} 
   
// Fonction principale
int main() 
{ 
    /* Considérons cet arbre suivant :
              50 
           /     \ 
          30      70 
         /  \    /  \ 
       20   40  60   80 */
       
    struct node *root = NULL; 
    root = inserer(root, 50); 
    inserer(root, 30); 
    inserer(root, 20); 
    inserer(root, 40); 
    inserer(root, 70); 
    inserer(root, 60); 
    inserer(root, 80); 
   
    // Affichage en ordre de l'arbre
    infixe(root); 
   
    return 0; 
} 
```

## Complexité 
La complexité au pire des cas des opérations de recherche et d'insertion est O(h),
où h est la hauteur de l'arbre de recherche binaire. 
### Question :
Quelle serait la complexité dans le cas d'un arbre asymétrique ?


