# Fonction pour rechercher un élément dans un arbre
Pour rechercher unélément dans un arbre binaire:
1. Commencer à partir de la racine.
2. Comparer l'élément à insérer avec la racine, 
3. S'il est inférieur à la racine, appel récursif pour gauche, 
    sinon récursif pour droite.
    
## Code-source:
```c
// Fonction pour chercher une valeur dans un arbre binaire
struct node* rechercher(struct node* root, int elementARechercher) 
{ 
    // Base Cases: root is null or key is present at root 
    if (root == NULL || root->valeur == elementARechercher) 
       return root; 
     
    // elementARecherche est supérieur à la valeur de root
    if (root->key < elementARechercher) 
       return rechercher(root->droite, elementARechercher); 
  
    // elementARecherche est inférieur à la valeur de root
    return rechercher(root->gauche, elementARechercher); 
} 
