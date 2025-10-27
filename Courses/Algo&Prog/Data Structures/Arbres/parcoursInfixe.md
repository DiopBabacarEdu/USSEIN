
# Parcours Infixé d'un arbre binaire

## Programme en C pour le parcours infixé d'un arbre binaire
Les éléments de l'arbre sont parcourus en ordre suivant
1. Sous-arbre gauche
2. Racine
3. Sous-arbre droit

## Code-source 
```c
#include <stdio.h> 
#include <stdlib.h> 
  
/* Définition des noeuds de l'Arbre Binaire */
struct node 
{ 
     int data; 
     struct node* left; 
     struct node* right; 
}; 
  
/* Fonction qui alloue un nouveau nœud avec la donnée
et affecte à NULL aux pointeurs gauche et droit. */

struct node* newNode(int dataInput) 
{ 
     struct node* node = (struct node*) 
                                  malloc(sizeof(struct node)); 
     node->data = dataInput; 
     node->left = NULL; 
     node->right = NULL; 
  
     return(node); 
} 
  
/* Étant donné un arbre binaire, afficher ses nœuds dans l'ordre*/
void parcoursInfixe(struct node* node) 
{ 
     if (node == NULL) 
          return; 
  
     /* Appel récursif sous-arbre gauche */
     parcoursInfixe(node->left); 
  
     /* Afficher la valeur du noeud */
     printf("%d ", node->data);   
  
     /* Appel récursif sous-arbre droit */
     parcoursInfixe(node->right); 
}   
  
/* Programme principal*/
int main() 
{ 
     struct node *root  = newNode(1); 
     root->left             = newNode(67); 
     root->right           = newNode(54); 
     root->left->left     = newNode(0); 
     root->left->right   = newNode(5);  
  
     printf("\nParcours en Infixé  \n"); 
     parcoursInfixe(root); 
  
     getchar(); 
     return 0; 
} 

