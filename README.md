# praktikum_new_diplom

## Описание проекта
## Foodgram - «Grocery assistant»
This is an online service that allows users to publish recipes, subscribe to other users' publications, add recipes to a favorites list and upload a summary list of products needed to prepare one or more selected dishes before going to the store.

The project uses a PostgreSQL database and runs in three containers (nginx, PostgreSQL and Django) via docker-compose on a server. The image with the project is uploaded to Docker Pub.

## Run project:
Automation of software deployment on servers is provided by the Docker virtualization environment, as well as the Docker Compose tool.
Instructions for deploying the Docker containers are provided in the Dockerfiles.

Template for filling variables in the .env file:
```
type of the database
DB_ENGINE=django.db.backends.postgresql

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

After completing the build process and starting the project, you shoulв apply migrations, create a superuser and collect static:
```
docker-compose exec backend python manage.py migrate
docker-compose exec backend python manage.py createsuperuser
docker-compose exec backend python manage.py collectstatic --no-input
```

To upload ingredients to databases from a .csv file, run the command:
```
docker-compose exec backend python manage.py uploadcsv
```

## Technologies
Python 3
Django
Django REST Framework
Docker
Gunicorn
nginx
PostgreSQL
Simple JWT

## The author of the project
Anton Akulov - https://github.com/Nekustetnaz
