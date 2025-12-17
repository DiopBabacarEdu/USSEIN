# Les Conteneurs

<p align="center">
  <img src="https://www.docker.com/wp-content/uploads/2022/03/container-what-is-container.png" alt="Container illustration" width="300"/>
</p>

Un conteneur est un **environnement isolé et léger** qui contient tout ce dont une application a besoin pour fonctionner, sans avoir besoin d'une machine virtuelle complète.

## L'analogie du conteneur maritime

Comme les conteneurs de transport maritime, les conteneurs informatiques sont :
- **Standardisés** : Même format partout
- **Portables** : Peuvent être déplacés facilement
- **Isolés** : Le contenu d'un conteneur n'affecte pas les autres
- **Empilables** : Vous pouvez en exécuter plusieurs sur la même machine

## Conteneur vs Machine Virtuelle

**Machine Virtuelle (VM)**
- Contient un système d'exploitation complet
- Lourde (plusieurs Go)
- Démarre en minutes
- Consomme beaucoup de ressources

**Conteneur**
- Partage le noyau du système hôte
- Léger (quelques Mo)
- Démarre en secondes
- Consomme peu de ressources

## Concrètement, un conteneur contient :

- Votre application (code)
- Les dépendances (bibliothèques Python, Node.js, etc.)
- Les fichiers de configuration
- Les outils système nécessaires

## Exemple pratique

```bash
# Lancer un serveur web Nginx dans un conteneur
docker run -p 80:80 nginx

# En une seconde, vous avez un serveur web qui tourne !
```

Sans conteneur, il faudrait installer Nginx, configurer le système, gérer les dépendances... Avec Docker, c'est instantané et ça fonctionne de la même façon partout.
