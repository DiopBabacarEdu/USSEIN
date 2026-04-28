# 💼 TP CORBA — **Mini Order Management System Distribué**

## 🎯 Objectif

L’objectif de ce TP est de concevoir une **application distribuée simple** simulant un système de gestion de commandes (type e-commerce), en utilisant **CORBA** pour la communication entre services et **JavaFX** pour l’interface graphique.

Les étudiants devront comprendre comment **plusieurs services distants coopèrent** pour traiter une commande.

## 🧠 Contexte

Dans une application e-commerce réelle, plusieurs composants interviennent lors d’une commande :

* vérification du stock
* validation du paiement
* création et suivi de la commande

Dans ce TP, chaque composant sera implémenté comme un **service CORBA indépendant**.

## 🏗️ Architecture attendue

```
[ Client JavaFX ]
        |
      ORB
        |
-------------------------------
|        |         |
Order  Inventory  Payment
```


## 🔧 Services à implémenter

### 📦 1. OrderService

* `placeOrder(product, quantity)`
* `getOrderStatus()`

👉 Rôle : gérer la création de commande

### 📊 2. InventoryService

* `checkStock(product)`
* `updateStock(product, quantity)`

👉 Rôle : vérifier la disponibilité

### 💳 3. PaymentService

* `processPayment(amount)`

👉 Rôle : simuler un paiement (accepté/refusé)

## 🔗 IDL (à compléter)

```idl
module OrderSystem {
  interface OrderService {
    string placeOrder(in string product, in long quantity);
    string getOrderStatus();
  };

  interface InventoryService {
    boolean checkStock(in string product, in long quantity);
  };

  interface PaymentService {
    boolean processPayment(in float amount);
  };
};
```


## 🖥️ Interface JavaFX

L’interface doit permettre de :

* saisir un produit et une quantité
* lancer une commande
* afficher le statut :

  * ✅ validée
  * ❌ refusée (stock ou paiement)

👉 Un bouton **“Commander”** est suffisant


## ⚙️ Contraintes techniques

* Utiliser CORBA (IDL + `idlj`)
* Utiliser le Naming Service (`orbd`)
* Implémenter **au moins 3 services distincts**
* Le client doit appeler les services via l’ORB
* Simulation simple (pas de base de données requise)


## 🎓 Compétences visées

* Comprendre l’architecture CORBA (ORB, IDL, Naming Service)
* Implémenter des services distribués
* Faire communiquer plusieurs composants
* Concevoir une interface simple connectée à des services distants


## 💡 Bonus (optionnel)

* messages d’erreur plus détaillés
* simulation aléatoire du paiement
* ajout d’un historique de commandes


## ✅ Résultat attendu

Une application fonctionnelle où :

1. L’utilisateur saisit une commande
2. Le système vérifie le stock
3. Le paiement est simulé
4. Le résultat est affiché dans l’interface
