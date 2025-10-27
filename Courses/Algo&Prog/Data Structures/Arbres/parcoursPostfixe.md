# Parcours postfixé d'un arbre binaire
## Programme en C pour le parcours postfixé d'un arbre binaire
Les éléments de l'arbre sont parcourus en ordre suivant
1. Sous-arbre gauche 
2. Sous-arbre droit
3. Racine

## Code-source

```c
#include <stdio.h> 
#include <stdlib.h> 
  
/* Définition des noeuds de l'Arbre Binaire */
struct node 
{ 
     int valeur; 
     struct node* gauche; 
     struct node* droite; 
}; 
  
/* Fonction qui alloue un nouveau nœud avec la donnée
et affecte à NULL aux pointeurs gauche et droit. */

struct node* nouveauNoeud(int dataInput) 
{ 
     struct node* node = (struct node*) 
                                  malloc(sizeof(struct node)); 
     node->data = dataInput; 
     node->gauche = NULL; 
     node->droite = NULL; 
  
     return(node); 
} 
  
/* Étant donné un arbre binaire, afficher ses nœuds en utilisant la
   traversée post-ordre "ascendante". */
void parcoursPostfixe(struct node* node) 
{ 
     if (node == NULL) 
        return; 
  
     // Appel récursif sous-arbre gauche
     parcoursPostfixe(node->gauche); 
  
     // Appel récursif sous-arbre droit 
     parcoursPostfixe(node->droite); 
  
     // Afficher la valeur du noeud
     printf("%d ", node->data); 
} 
  
/* Programme principal*/
int main() 
{ 
     struct node *root  = nouveauNoeud(1); 
     root->gauche             = nouveauNoeud(67); 
     root->droite           = nouveauNoeud(54); 
     root->gauche->gauche     = nouveauNoeud(0); 
     root->gauche->droite   = nouveauNoeud(5);   
  
     printf("\nParcours en Postfixé: \n"); 
     parcoursPostfixe(root); 
  
     getchar(); 
     return 0; 
} 
```
