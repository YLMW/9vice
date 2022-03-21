<img src="https://github.com/YLMW/9vice/blob/main/9vice-FlaskServer/static/logo.svg" alt="logo 9vice" width="80"/>

# 9vice

## Introduction 📘

Dans le cadre du développement d'une application sécurisée, nous avons implémenté un service permettant la gestion ainsi que la mise en relation, d'utilisateurs et leurs devices. Un device pouvant être représenté par un système de fichier, un flux vidéo et/ou un flux audio. L'aspect sécurité du service doit être explicité et à une place importante dans ce projet.



## Installation 🛠️

Pour pouvoir utiliser notre application il vous sera necessaire de réunir les technologies suivantes :

1. Un serveur herbergeant l'API avec un OS Unix
2. Une base de données PostgreSQL accessible par l'API
3. Un serveur à installer sur chacun des devices à utiliser
4. Un navigateur web récent pour accéder à l'API

---

### Base de données :floppy_disk:

Afin d'assurer une persistence sur les données de l'API, il est nécessaire de mettre en place une base de données. Nous utiliserons une base de données PostgreSQL ainsi qu'une machine sous Debian 11.

#### PostgreSQL 

Pour installer les composants nécessaire à sa mise en place :

```shell
$> sudo apt-get update
$> sudo apt-get install postgresql	
```

Pour démarrer le service postgresql :

```shell
$> sudo systemctl start postgresql.service
```

Vous pouvez également configurer le redémarrage automatique du service, en cas de redémarrage du système, avec la commande suivante :

```shell
$> sudo systemctl enable postgresql.service
```

À présent, postgresql est actif, nous sommes alors capable de créer la base de données nécessaire au bon fonctionnement de l'API.


#### Mise en place de la base de données

Pour déployer la base de données, nous avons créé des scripts d'automatisation qui sont les suivants :

- 00-init.sql : 
- 01-users.sql :
- 02-devices.sql :
- 03-history.sql :

Il suffit alors de suivre les commandes suivantes :

```shell
# On s'identifie en tant que l'utilisateur postgres administrateur du service
$> sudo -i -u postgres

# On ouvre le CLI pour communiquer avec le service postgresql
$> psql
	 
# Si il s'agit d'une première utilisation du service, il faut définir un mot de passe pour l'utilisateur postgres avec la commande intéractive suivante
\passwd

# On se déplace dans le dossier contenant les scripts d'automatisation
psql> \cd /path/to/folder/scripts

# On importe les scripts
psql> \i 00-init.sql
```

Si tout à fonctionner, les différentes tables devraient être affichée dans le terminal. Vous pouvez également afficher les tables de la base de données comme suit :

```shell
psql> \dt device.*
```

*[Optionnel] À noter qu'il est tout à fait possible, voir préférable, de creer un nouvel utilisateur avec des droits d'accès à la base de données établie uniquement. L'utilisation de l'utilisateur postgres est déprécié. Le tutoriel suivant explique la démarche à suivre https://quillevere.net/programmation/bdd/postgresql/creer-utilisateur-attribuer-droits-postgresql_59458.htm*

Il sera nécessaire, plus tard, de mettre à jour les données d'utilisateurs que l'on souhaite mettre admin à l'aide de la requête suivante :

```shell
# Par ID d'utilisateur

psql> UPDATE device.users SET isAdmin=true WHERE id_user=IdToChange;
	
# Par username

psql> UPDATE device.users SET isAdmin=true WHERE username=UsernameToChange;
```

**:warning: Veillez à remplacer les variables finissant par ToChange par les valeurs de l'utilisateur concerné.**

---
### API - 9vice-FlaskServer :computer:

#### Variables d'environnement

Pour un soucis de sécurité, certaines variables ne sont pas directement stockées dans le code source. On les spécifie dans un fichier nommé *.env* placé au même niveau d'arborescence que le *app.py*. Ce fichier doit contenir les variables suivantes. À vous de spécifier leur valeur.

- SALT=
> Correspond au sel utilisé par les différentes fonctions de hachage de l'application afin d'éviter les attaques arc-en-ciel et éviter la fuite de données en clair.
- SECRET=
> Il s'agit de la clé secrète utilisée par la fonction de chiffrement
- DB_USERNAME=
> Le nom de l'utilisateur configurer pour accéder à la base de données (par défaut : postgres) 
- DB_PASSWORD=œ
> Le mot correspondant à l'utilisateur 


#### Executer le projet

Pour mettre en place l'API, après avoir téléchargé son code source, il faut disposer d'une version de python3 ainsi que de l'utilitaire pip correspondant. 
Pour installer les modules utilisés par python, un fichier *requirements.txt* a été écrit, il suffit donc d'exécuter la commande suivante :



```shell
$> pip install -r requirements.txt
```

Vous êtes alors capable d'exécuter le projet :

```shell
$> python3 app.py
```
Ou bien avec flask run

```shell
$> flask run
```

À présent l'API fonctionne et est accessible.

---

### Serveur des devices - 9vice-device :video_camera:

À présent, l'API est fonctionnel et est accessible par les utilisateurs. Il faut désormais mettre en place le serveur responsable de la gestion des devices. Pour cela, nous utiliserons le code prévu à cet effet.

#### Variables d'environnement

À l'image du serveur de l'API, certaines variables ne sont pas stockées en clair dans le code source. Il faut donc également spécifier un fichier nommé *.env*, dans le même dossier contenant le script de l'application, avec les variables suivantes :

- ACCOUNT_ID=
> L'utilisateur saisit l'id de son compte au sein de l'API

- DEVICE_NAME=
> Le nom du device

- SERVER_KEY=
> La clé d'authentification du device au près du serveur

- CLIENT_KEY=
> La clé de chiffrement pour la communication client/device 

- FILE_PATH=
> Chemin du dossier partagé.

#### Executer le programme

Une fois l'environnement mis en place, il faut installer les dépendances spécifiées dans le fichier *requirements.txt* du device serveur :

```shell
$> pip install -r requirements.txt
```

On peut désormais executer le *device.py* du projet et le device va automatiquement initier sa connexion.









