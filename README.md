# # SoftDesk Support

SoftDesk, une société d'édition de logiciels de collaboration, a décidé de publier une application permettant de remonter et suivre des problèmes techniques. Cette solution, SoftDesk Support, s’adresse à des entreprises en B2B (Business to Business).

Etapes à suivre pour installer localement l'application :

1. **Cloner le repository GitHuh du projet**
    * `git clone https://github.com/meridien22/Project_SoftDesk_v2.git`
2. **Aller dans le répsertoire du projet**
    * `cd Project_SoftDesk_v2/`
3. **Si vous n'avez pas poetry sur votre machine, installez-le avec cette commande**
    * `curl -sSL https://install.python-poetry.org | python3 -`
4. **Créer l'environnement virtuel et installer les bilbiothèques**
    * `poetry install`
5. **Lancer le serveur Django**
    * `poetry run python manage.py runserver`
6. **Tester cette URL dans votre navigareur pour valider l'installation**
    * `http://127.0.0.1:8000/api/user_inscription/`

![install ok](/image/install_ok.png)