# VaporMap

--- 

## Description

VaporMap est une application web permettant de référencer des points GPS dans une base de données. 
Ces points peuvent être affichés sur une carte.

Techniquement, c'est une application écrite en python, qui utilise le framework Flask.

>Cette application est une maquette développée rapidement dans un but pédagogique par Tristan Le Toullec.


---


# Installation


## Architecture de l'application

L'application "VaporMap" est constituée de 2 parties : 

- Le frontend, chargé de l'interface avec l'utilisateur dans le navigateur.
- L'API REST, chargée de : 
  - gérer les données  (création des points de relevé)
  - de fournir les informations sur les points au format "geojson" [https://fr.wikipedia.org/wiki/GeoJSON](https://fr.wikipedia.org/wiki/GeoJSON)


L'utilisateur final de l'application interragit avec le frontend.

**Le frontend ** est composé de fichiers statiques. Il execute du code javascript dans le navigateur de l'utilisateur, et effectue des requètes vers l'API. Il permet à l'utilisateur d'ajouter des points de relevés, et d'afficher les points saisis sur une carte.

**L'API **est interrogée par le navigateur de lutilisateur. Elle peut également être utilisée sans le frontend.
Elle est développée avec le framework Python Flask, un micro framework open-source de développement web en Python. 

Flask permet de définir des "routes", et d'y associer un traitement en python. Pour l'application Vapormap : 

 - "/geojson" : export de la liste des points au format geojson
 - "/api/points" : api de gestion des points


--- 

## Déploiement

Pour l'API, Flask permet de déployer les applications dans différents mode. 2 modes sont définis par défaut: d2veloppement et production.

En développement, l'application utilise serveur http intégré à Flask, et stocke ses données dans une base sqlite.
En production l'application utilise un serveur web externe (Nginx), et stocke ses données dans une base MariaDB.

Des environnements d'execution Python permettant de lancer l'application, mais indépendants du système hôte, sont mis en place avec l'outil "virtualenv".

Pour les différents modes opératoires, suivez les guides :

* [Installation en mode développement](./developpement.md)
* [Installation en mode production](./production.md)

---


