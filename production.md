# Installation en mode Production 

## Description

Pour le déploiement en mode production :

* les données sont stockées dans une base de données séparée
* le frontend est géré par un serveur web dédié

Détails : 

* Base de données :
   * base de Données MariaDB
* API :
   * utilise Flask
   * interrogation via des requètes HTTP.
   * se connecte la base de données
   * expose les endpoints REST "/api" et "/geojson"
* Frontend :
   * utilise le serveur WEB Nginx
   * application statique
   * envoie des requetes vers l'API depuis le navigateur de l'utilisateur

## Préparation du système

* mise à jour du système
``` bash
sudo apt update && sudo apt upgrade -y
```

* Création de l'utilisateur "app-vapormap"
``` bash
sudo useradd \
   -m -d /home/app-vapormap \
   -r -c 'Vaportmap App system-user' \
   -s /bin/bash \
   app-vapormap
```

* Installation des pré-requis
``` bash
sudo apt -y install git vim nano
```

---

## Installation de la base de données

Installation de MariaDB (10.3.31)
```bash
sudo apt install -y software-properties-common mariadb-server
```

Création de l'utilisateur et de la base de données pour l'application
```bash
sudo mysql -e "CREATE DATABASE db_vapormap;"
sudo mysql -e "GRANT ALL PRIVILEGES ON db_vapormap.* TO 'user_vapormap'@'localhost' IDENTIFIED BY 'vapormap';"
sudo mysql -e "GRANT ALL PRIVILEGES ON db_vapormap.* TO 'user_vapormap'@'%'         IDENTIFIED BY 'vapormap';"
sudo mysql -e "FLUSH PRIVILEGES;"
```

Test de connexion
```bash
mysql -h localhost -u user_vapormap -pvapormap -D db_vapormap
# MariaDB [db_vapormap]>
```

``` sql
quit;
# Bye
```

---

## Déploiement de l'API


### Installation des pré-requis

* Environnement Python :
``` bash
sudo apt -y install python3 python3-pip python3-venv
```
* Librairie client mysql
``` bash
sudo apt -y install mariadb-client libmariadb-dev
```

### Initialisation de l'environnement

* Connexion an tant qu'utilisateur app-vapormap
``` bash
sudo -i -u app-vapormap
``` 
* Vérification
``` bash
id 
# uid=998(app-vapormap) gid=998(app-vapormap) groups=998(app-vapormap)
``` 

### Installation de l'application

* Récupération du dépot
``` bash
cd $HOME
git clone https://gitlab.imt-atlantique.fr/vapormap/vapormap-app.git vapormap-prod
```
* Création d'un environnement Python virtuel et activation
``` bash
cd $HOME/vapormap-prod
mkdir venv
python3 -m venv ./venv/app
source venv/app/bin/activate
```
* Initialisation du module de gestion de package "Wheel". Ne peut être fait dans le "requirement.txt"
``` bash
pip install wheel
```
* Installation des dépendances Python
``` bash
cd app
pip install -r requirements/production.txt
```

### Configuration de la base de données 

Déclaration des variables de configuration pour la BDD et `migrate`
``` bash
cd $HOME/vapormap-prod/app/api
export VAPOR_DBNAME=db_vapormap
export VAPOR_DBUSER=user_vapormap
export VAPOR_DBPASS=vapormap
export VAPOR_DBHOST=localhost
export FLASK_APP=app
export SETTINGS_FILE="production"
```
Initialisation de la base de données (migrate) :
``` bash
flask db upgrade
```

## Test de l'application

* Lancement avec Gunicorn
``` bash
cd $HOME/vapormap-prod/app
export PYTHONPATH=$HOME/vapormap-prod/app

# python
export PYTHONDONTWRITEBYTECODE=1
export PYTHONUNBUFFERED=1

#vapormap
export VAPOR_DBNAME=db_vapormap
export VAPOR_DBUSER=user_vapormap
export VAPOR_DBPASS=vapormap
export VAPOR_DBHOST=localhost

#export FLASK_APP=app
export SETTINGS_FILE="production"

gunicorn --bind 0.0.0.0:5000 wsgi:app
```

* Résultat
``` bash
 [INFO] Starting gunicorn 20.1.0
 [INFO] Listening at: http://0.0.0.0:5000
 [INFO] Using worker: sync
 [INFO] Booting worker with pid: 9889
```

A ce stade, seule l'API est disponible.

Pour tester : 

* accès à l'API
``` bash
curl http://localhost:5000/api/points/?format=json
```
* Réponse
``` bash
[]
```

* arrêter gunicorn : "<CTRL-C>"
``` bash
  [INFO] Handling signal: int
  [INFO] Worker exiting (pid: 22935)
  [INFO] Shutting down: Master
```

Une fois l'application installé, initialisée,  et testée, revenir à l'utilisateur initial.
``` bash
deactivate
exit
```


### Lancement de l'API en tant que service 

Afin de garantir le fonctionnement de l'API en cas de redémarrage du serveur, il convient de créer un service géré par le serveur pour le lancement de Gunicorn. 

* Génération du fichier de service : `vapormap-api.service`.
``` bash
export VAPORMAP_USER=app-vapormap
export VAPORMAP_GROUP=app-vapormap
export VAPORMAP_DIR=/home/app-vapormap/vapormap-prod/app
export VAPORMAP_PATH=/home/app-vapormap/vapormap-prod/venv/app/bin
export VAPOR_DBUSER=user_vapormap
export VAPOR_DBPASS=vapormap
export VAPOR_DBHOST=localhost
export VAPOR_DBNAME=db_vapormap
export VAPORMAP_API_PORT=8001
envsubst '${VAPORMAP_USER},${VAPORMAP_GROUP},${VAPORMAP_DIR},${VAPORMAP_PATH}, ${VAPOR_DBUSER},${VAPOR_DBPASS},${VAPOR_DBHOST},${VAPOR_DBNAME},${VAPORMAP_API_PORT}' < api-systemd.conf.template > /tmp/api-systemd.conf

cat /tmp/api-systemd.conf
```

* La mise en place du service nécéssite des droits "sudo", que l'utilisateur 'app-vapormap' n'a pas :
``` bash
exit
``` 

* Mise en place du fichier de configuration dans systemd
``` bash
sudo cp /tmp/api-systemd.conf /etc/systemd/system/vapormap-api.service
sudo chmod 755 /etc/systemd/system/vapormap-api.service
```

* Activation du service, et démarrage de Gunicorn
```bash
sudo systemctl enable vapormap-api.service
sudo systemctl start vapormap-api.service
sudo systemctl status vapormap-api.service
```

* Tester l'accès à l'API, comme lors du lancement manuel
---

## Déploiement du frontend

### Installation du serveur WEB Nginx

``` bash
sudo apt -y install nginx-light
```

### Initialisation de l'environnement

* Connexion an tant qu'utilisateur app-vapormap
``` bash
sudo -i -u app-vapormap

cd $HOME/vapormap-prod
cd frontend
pwd
```

### Configuration de l'accès à l'API

``` bash
export VAPORMAP_BACKEND=<PUBLIC_API_ENDPOINT_HOST>
export VAPORMAP_BACKEND_PORT=8001
envsubst '${VAPORMAP_BACKEND},${VAPORMAP_BACKEND_PORT}' < config.json.template > config.json
```
Attention, pour `VAPORMAP_BACKEND` vous devez indiquer une adresse accessible depuis le navigateur. `localhost` ne fonctionne que si vous travaillez sur votre machine locale, sinon il faut indiquer l'adresse IP publique de votre VM, ou de votre instance Cloud.

### Génération du fichier de configuration du serveur Nginx

``` bash
export VAPORMAP_URL_SERVERNAME=0.0.0.0
export VAPORMAP_URL_PORT=8000
export VAPORMAP_FRONTEND_ROOT=${PWD}
envsubst '${VAPORMAP_URL_SERVERNAME},${VAPORMAP_URL_PORT},${VAPORMAP_FRONTEND_ROOT}' < nginx.conf.template > nginx.conf
cp nginx.conf /tmp
```

### Mise en place des pages

Nécéssite des droits "sudo", que l'utilisateur 'app-vapormap' n'a pas.
``` bash
exit
```

Ajout de l'utilisateur app-vapormap au groupe www-data
``` bash
sudo usermod -a -G app-vapormap www-data
```

Mise en place du fichier de configuration
``` bash
sudo cp /tmp/nginx.conf /etc/nginx/sites-available/vapormap
sudo ln -s /etc/nginx/sites-available/vapormap /etc/nginx/sites-enabled/
sudo systemctl restart nginx 
```

### Test de l'accès à l'application

Depuis un navigateur : [http://localhost:8000](http://localhost:8000)

> Rem : si vous ne travaillez pas sur votre machine locale, l'adresse IP publique de votre VM, ou de votre instance Cloud.


