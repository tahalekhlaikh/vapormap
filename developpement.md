# Déploiement en mode développement

## Description

En mode développement, l'application s'appuie sur une base de données locale Sqlite3.

Flask propose un serveur http de developpement (run) qui permet de vérifier rapidement le fonctionnement du programme. Il permet également de développer sans installer un serveur http sur la machine de développement: 

-  Par défaut, le serveur fonctionne sur le port 5000 à l’adresse IP 127.0.0.1.
-  Vous pouvez lui transmettre explicitement une adresse IP et un numéro de port.
-  Le serveur de développement recharge automatiquement le code Python lors de chaque requête si nécessaire. 
-  N’UTILISEZ PAS CE SERVEUR DANS UN ENVIRONNEMENT DE PRODUCTION. Il n’a pas fait l’objet d’audits de sécurité ni de tests de performance. 

Pour le frontend, le module "http" de python est utilisé.

----

## Préparation du système

* mise à jour du système (optionnel)
``` bash
sudo apt update && sudo apt upgrade -y
```

* Installation des prérequis (optionnel)
```
sudo apt -y install git sudo vim python3-pip
```
---

## Initialisation de l'application

### Pré-requis Python

* Installer python3, pip3 et venv

``` bash
sudo apt -y install python3 python3-pip python3-venv
```
* Vérifier
``` bash
python3 --version
# Python 3.10.6

pip3 --version
# pip 22.0.2 from /usr/lib/python3/dist-packages/pip (python 3.10)

python3 -m venv -h
# ...
# Creates virtual Python environments in one or more target directories.
# ...
```

### Récupération du projet
```
cd $HOME
git clone https://gitlab.com/vapormap/vapormap-flask.git vapormap-dev
cd vapormap-dev
```

###  Création d'un environnement Python virtuel
``` bash
cd $HOME/vapormap-dev
mkdir venv
python3 -m venv ./venv
```
---

## Lancement de l'API

* Initialisation de l'environnement Python
``` bash
cd $HOME/vapormap-dev
source venv/bin/activate
```

* Installation des "requirements" de l'application
```
cd $HOME/vapormap-dev/app
pip install -r requirements/development.txt
```

* Création de la DB sqlite
```
cd $HOME/vapormap-dev/app/api
export SETTINGS_FILE="development"
export FLASK_APP=app
flask db upgrade
```

* Lancement de l'application
``` bash
export SETTINGS_FILE="development"
cd $HOME/vapormap-dev/app/api
flask run
```

* Test : 
  * accès à l'API : dans une autre fenêtre de terminal
``` bash
curl http://localhost:5000/api/points/?format=json
```
   * Réponse
``` bash
[]
```

* A la fin des tests : 
  * pour arrêter le serveur 
``` bash
CONTROL-C.
```
  * pour sortir du venv
``` bash
deactivate
```

### Lancement du frontend 

* Ouvrir un autre terminal, et initialiser l'environnement python
``` bash
cd $HOME/vapormap-dev
source venv/bin/activate
```

* Configurer l'accès à l'API
``` bash
cd $HOME/vapormap-dev/frontend/
export VAPORMAP_BACKEND=<PUBLIC_API_ENDPOINT_HOST>
export VAPORMAP_BACKEND_PORT=5000
envsubst '${VAPORMAP_BACKEND},${VAPORMAP_BACKEND_PORT}' < config.json.template > config.json
```
Attention, pour `VAPORMAP_BACKEND` vous devez indiquer une adresse accessible depuis le navigateur. `localhost` ne fonctionne que si vous travaillez sur votre machine locale, sinon il faut indiquer l'adresse IP publique de votre VM, ou de votre instance Cloud.


* Lancer le frontend
``` bash
cd $HOME/vapormap-dev/frontend/
python -m http.server
```

* Test de l'accès à l'application
  * Depuis un navigateur : [http://localhost:8000](http://localhost:8000)
  * _Rem : si vous ne travaillez pas sur votre machine locale, l'adresse IP publique de votre VM, ou de votre instance Cloud._

* A la fin des tests : 
  * pour arrêter le serveur 
``` bash
CONTROL-C.
```
  * pour sortir du venv
``` bash
deactivate
```
