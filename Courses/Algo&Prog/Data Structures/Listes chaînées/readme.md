# Listes chaînées : fonctions de base
Ci-dessous l'implémentation des fonctions de base sur les listes chaînées.

```c
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <stdbool.h>

struct node {
   int valeur;
   struct node *suivant;
};

struct node *tete = NULL;
struct node *courant = NULL;
```

## afficher liste

```c
void afficherListe() {
   struct node *ptr = tete;
   printf("\n[ ");
	
   //commencer au début
   while(ptr != NULL) {
      printf("%d ",ptr->valeur);
      ptr = ptr->suivant;
   }
   printf(" ]\n");
}
```

## Insérer en tete
```c
void insererTete(int valeur) {
   //créer un noeud
   struct node *nouveauNoeud = (struct node*) malloc(sizeof(struct node));
	
   nouveauNoeud->valeur = valeur;
	
   //faire pointer son suivant sur l'ancinne tête de liste
   nouveauNoeud->suivant = tete;
	
   //... et devient la nouvelle tête de liste
   tete = nouveauNoeud;
}
```

## Supprimer en tête et queue
```c
struct node* supprimerTete() {

   //Sauvegarder l'actuelle tête de liste quelques part
   struct node *tempNouveauNoeud = tete;
	
   //Son suivant devient la nouvelle tête de liste
   tete = tete->suivant;
	
   //renvoie la tête sauvegardé (qui est supprimée de la liste)
   return tempNouveauNoeud;
}

int supprimerQueue() {
    int retval = 0;
    /* S'il y a un seul élément supprimez le */
    if (tete->suivant == NULL) {
        retval = tete->valeur;
        free(tete);
        return retval;
    }

    /* avancer jusqu'au dernier de la liste*/
    struct node * courant = tete;
    while (courant->suivant->suivant != NULL) {
        courant = courant->suivant;
    }

    /* courant pointe sur l'avant dernier élément, on peut supprimer le dernier */
    retval = courant->suivant->valeur;
    free(courant->suivant);
    courant->suivant = NULL;
    return retval;

}
```

## Liste vide et taille de liste
```c
bool estVide() {
   return tete == NULL;
}

int tailleListe() {
   int taille = 0;
   struct node *courant;
	
   for(courant = tete; courant != NULL; courant = courant->suivant) {
      taille++;
   }
	
   return taille;
}
```

## Rechercher un élément dans la liste
```c
struct node* rechercher(int key) {

   //Commencer par la tête
   struct node* courant = tete;

   //Si liste vide
   if(tete == NULL) {
      return NULL;
   }

   //parcourir la liste
   while(courant->valeur != key) {
	
      //Si c'est le dernier noeud
      if(courant->suivant == NULL) {
         return NULL;
      } else {
         //avancer vers le suivant
         courant = courant->suivant;
      }
   }      
	
   //Si trouvé, retourne le noeud courant
   return courant;
}
```

## Suppression dans une liste 
```c
struct node* supprimer(int key) {

   //Commencer ar la tête de liste
   struct node* courant = tete;
   struct node* precedent = NULL;
	
   //if list is empty
   if(tete == NULL) {
      return NULL;
   }

   //parcourir la liste 
   while(courant->valeur != key) {

      //Si c'est le dernier noeud
      if(courant->suivant == NULL) {
         return NULL;
      } else {
         //Sauvegarde le précédent
         precedent = courant;
         //Avance vers le suivant
         courant = courant->suivant;
      }
   }

   //Si trouvé, ...
   if(courant == tete) {
      //faire pointer la tête vers son suivant
      tete = tete->suivant;
   } else {
      //faire pointer le suivant du précédent sur les suivant du noeud courant
      precedent->suivant = courant->suivant;
   }    
	
   return courant;
}
```
## Trier une liste

```c
void trier() {

   int i, j, k, tempvaleur;
   struct node *courant;
   struct node *suivant;
	
   int size = tailleListe();
   k = size ;
	
   for ( i = 0 ; i < size - 1 ; i++, k-- ) {
      courant = tete;
      suivant = tete->suivant;
		
      for ( j = 1 ; j < k ; j++ ) {   

         if ( courant->valeur > suivant->valeur ) {
            tempvaleur = courant->valeur;
            courant->valeur = suivant->valeur;
            suivant->valeur = tempvaleur;
         }
         courant = courant->suivant;
         suivant = suivant->suivant;
      }
   }   
}
```

## Renverser une liste

```c
void renverser(struct node** tete_ref) {
   struct node* precedent   = NULL;
   struct node* courant = *tete_ref;
   struct node* suivant;
	
   while (courant != NULL) {
      suivant = courant->suivant;
      courant->suivant = precedent;   
      precedent = courant;
      courant = suivant;
   }
	
   *tete_ref = precedent;
}
```

## Fonction de test
```c
void main() {
   int elt, choix=1;
   int a=1;
   while (choix != 0){
           
               //printf("*****************************************\n");
               printf("CHOISIR UNE ACTION  : \n");
              // printf("*****************************************\n");
               printf("1. Insérer   2. Rechercher   3. Supprimer\n");
               printf("4. Trier     5. Renverser    6. Afficher \n");
               printf("*****************************************\n");
               scanf("%d",&choix);
           if (choix==0){
               printf("Saisir entre 1 et 6.\n");
               choix = 100;
           }
           else if (choix==1){
               int elementAInserer;
               printf("Saisir l'élément à insérer.\n");
               scanf("%d",&elementAInserer);
               insererTete(elementAInserer);
               afficherListe();
               printf("\n");
           }
           else if (choix==2){
               int elementARechercher;
               printf("Saisir l'élément à rechercher.\n");
               scanf("%d",&elementARechercher);
               struct node *resultatRecherche = rechercher(elementARechercher);
               
               if(resultatRecherche != NULL) {
                    printf("Element trouvé : \n");
                    printf("(%d ) ",resultatRecherche->valeur);
                    printf("\n");  
                } else {
                    printf("Element non trouvé.\n");
           }
               
           }
           else if (choix==3){
               int elementASupprimer;
               printf("Saisir l'élément à supprimer.\n");
               scanf("%d",&elementASupprimer);
               struct node *resultatSuppression = supprimer(elementASupprimer);
               printf("Liste après suppression : \n");
               afficherListe();
               printf("\n");
           }
           else if (choix==4){
               trier();
               printf("Liste après tri: \n");
               afficherListe();
               printf("\n");
           }
           else if (choix==5){
               renverser(&tete);
               printf("\nListe renversée: \n");
               afficherListe();
               printf("\n");
           }
           else if (choix==6){
               int retval = supprimerQueue();
               printf("\nListe après suppression queue: \n");
               afficherListe();
               printf("\n");
           }
   }
   
   printf("Program exit ...\n");
   getch();
   return;
 
}


