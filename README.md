# Foodgram - «Grocery assistant»

### Description
This is an online service that allows users to publish recipes, subscribe to other users' publications, add recipes to a favorites list and upload a summary list of products needed to prepare one or more selected dishes before going to the store.

### User roles and access permissions
- Guest (not authenticated user) — can view recipes filtering them by tags, view user pages;
- Authenticated user — can view everything, add recipes to a favorite list, add a shopping list and upload a file with the necessary ingredients for recipes, subscribe to recipe authors. This role is assigned by default to each new user;
- Admin — all permissions to manage all project content. Can create, block and delete users. Can add, update and delete recipes, ingredients, and tags;
- Supepuser Django must always have administrator permissions. A superuser is always an administrator, but an administrator is not necessarily a superuser.

### Run project:
Automation of software deployment on servers is provided by the Docker virtualization environment, as well as the Docker Compose tool.
Instructions for deploying the Docker containers are provided in the Dockerfiles.

Template for filling variables in the .env file:
```
type of the database
DB_ENGINE=

name of the database
DB_NAME=

login to connect to the database
POSTGRES_USER=

password to connect to the database
POSTGRES_PASSWORD=

name of the contaimer
DB_HOST=

port for connecting to the database
DB_PORT=
```

To run the project in containers, run the command:
```
docker compose up -d --build
```

After completing the build process and starting the project, you should apply migrations, create a superuser and collect static:
```
docker-compose exec backend python manage.py migrate
docker-compose exec backend python manage.py createsuperuser
docker-compose exec backend python manage.py collectstatic --no-input
```

To upload ingredients to databases from a .csv file, run the command:
```
docker-compose exec backend python manage.py uploadcsv
```

### Technologies
Python 3 <br>
Django <br>
Django REST Framework <br>
Docker <br>
Gunicorn <br>
nginx <br>
PostgreSQL <br>
Simple JWT <br>

### Author
Anton Akulov - https://github.com/Nekustetnaz
