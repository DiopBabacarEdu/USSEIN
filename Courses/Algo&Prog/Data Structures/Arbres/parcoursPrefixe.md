# Parcours préfixé d'un arbre binaire
## Programme en C pour le parcours Infixé d'un arbre binaire
Les éléments de l'arbre sont parcourus en ordre suivant
1. Racine
2. Sous-arbre gauche 
3. Sous-arbre droit

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
     node->valeur = dataInput; 
     node->gauche = NULL; 
     node->droite = NULL; 
  
     return(node); 
} 
  
/* Étant donné un arbre binaire, afficher ses nœuds en utilisant un parcours préfixé */
void parcoursPrefixe(struct node* node) 
{ 
     if (node == NULL) 
          return; 
  
     /* Afficher la racine */
     printf("%d ", node->valeur);   
  
     /* Appel récursif sous-arbre gauche */
     parcoursPrefixe(node->gauche);   
  
     /* Appel récursif sous-arbre droit */
     parcoursPrefixe(node->droite); 
} 
  
/* Programme principal*/
int main() 
{ 
     struct node *root  = nouveauNoeud(1); 
     root->gauche             = nouveauNoeud(67); 
     root->droite           = nouveauNoeud(54); 
     root->gauche->gauche     = nouveauNoeud(0); 
     root->gauche->droite   = nouveauNoeud(5);   
  
     printf("\nParcours en Prefixé: \n"); 
     parcoursPrefixe(root); 
  
     getchar(); 
     return 0; 
} 
```
