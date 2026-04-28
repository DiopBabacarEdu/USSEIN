# 💼 TP CORBA — **Order Management System Distribué (Java + Python)**

## 🎯 Objectif

Réaliser une **application distribuée simple** de gestion de commandes en utilisant **CORBA**, avec :

* des **services en Java**
* un **client principal en JavaFX**
* un **client secondaire en Python** (interopérabilité)


## 🧠 Contexte

Une commande e-commerce suit 3 étapes :

1. Vérification du stock
2. Paiement
3. Validation

Chaque étape sera un **service CORBA indépendant**.


## 🏗️ Architecture

```
Client JavaFX  ─────┐
                    │
                (ORB + Naming Service)
                    │
Client Python  ─────┘
       |
-----------------------------------
|        |           |
Order  Inventory   Payment
(Java)   (Java)     (Java)
```


## 🔧 Étape 1 — Définir l’IDL

Créer `OrderSystem.idl` :

```idl
module OrderSystem {
  interface OrderService {
    string placeOrder(in string product, in long quantity);
  };

  interface InventoryService {
    boolean checkStock(in string product, in long quantity);
  };

  interface PaymentService {
    boolean processPayment(in float amount);
  };
};
```

➡️ Générer le code Java :

```bash
idlj -fall OrderSystem.idl
```


## 🔧 Étape 2 — Implémenter les services (Java)

Créer 3 classes :

### InventoryService

* stock fixe (ex : 10 unités)
* retourne true/false

### PaymentService

* simulation simple :

```java
return Math.random() > 0.3;
```

### OrderService

* appelle :

  * InventoryService
  * PaymentService
* retourne :

  * "VALIDEE"
  * "REFUSEE"


## 🔧 Étape 3 — Lancer le serveur CORBA

Dans un terminal :

```bash
start orbd -ORBInitialPort 1050
```

Dans Java :

* enregistrer les services dans le Naming Service :

  * "OrderService"
  * "InventoryService"
  * "PaymentService"


## 🖥️ Étape 4 — Client JavaFX

Créer une interface simple avec :

* champ texte : produit
* champ texte : quantité
* bouton : **Commander**
* label : résultat

👉 Au clic :

* appel CORBA → `placeOrder()`
* afficher :

  * ✅ VALIDEE
  * ❌ REFUSEE


## 🐍 Étape 5 — Client Python (interopérabilité)

Installer **omniORBpy**

Générer les stubs :

```bash
omniidl -bpython OrderSystem.idl
```

Créer `client.py` :

```python
import sys
from omniORB import CORBA
import CosNaming, OrderSystem

orb = CORBA.ORB_init(sys.argv, CORBA.ORB_ID)

obj = orb.resolve_initial_references("NameService")
ncRef = obj._narrow(CosNaming.NamingContext)

order = ncRef.resolve_str("OrderService")

result = order.placeOrder("PC", 1)
print("Résultat :", result)
```


## ✅ Résultat attendu

* Le client JavaFX permet de passer une commande
* Le système appelle plusieurs services CORBA
* Le résultat est affiché
* Le client Python obtient **le même résultat**
