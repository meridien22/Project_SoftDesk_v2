# Force Poetry à créer le dossier .venv à l'intérieur de votre projet
poetry config virtualenvs.in-project true
# créer notre nouveau projet
poetry new poetry_project
# Ajoute Django aux dépendances de production
poetry add django
poetry add djangorestframework-simplejwt
# Ajoute Django aux dépendances de production
poetry add djangorestframework
# Ajoute des outils de développement
poetry add --group dev black flake8
# le paramètre config permet de nommer le répertoire de configuration du projet autrement que le nom du projet lui-même
# le paramètre . permet de faire l'installation dans le répertpire courant sans en créer un nouveau
poetry run django-admin startproject config .




# Pour la suite
poetry run python manage.py migrate


poetry run python manage.py startapp authentication
poetry run python manage.py startapp support

<!-- # Pour lancer la commande de management qui va créer un jeu de donnée pour le développement locel -->
poetry run python manage.py init_local_dev

poetry run python manage.py erase_local_dev