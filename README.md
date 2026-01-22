# Force Poetry à créer le dossier .venv à l'intérieur de votre projet
poetry config virtualenvs.in-project true
# créer notre nouveau projet
poetry new poetry_project
# le paramètre config permet de nommer le répertoire de configuration du projet autrement que le nom du projet lui-même
# le paramètre . permet de faire l'installation dans le répertpire courant sans en créer un nouveau
poetry run django-admin startproject config .
# Pour la suite
poetry run python manage.py migrate
poetry run python manage.py runserver

poetry run python manage.py startapp authentication
poetry run python manage.py startapp support