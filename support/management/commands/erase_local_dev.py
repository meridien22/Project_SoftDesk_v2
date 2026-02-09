from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

from support.models import Project, ProjectContributors, Issue, Comment
from client.models import Client

UserModel = get_user_model()


class Command(BaseCommand):

    help = 'Erase local development'



    def handle(self, *args, **options):
        self.stdout.write(self.style.MIGRATE_HEADING(self.help))

        Project.objects.all().delete()
        UserModel.objects.all().delete()
        
        super_user = UserModel.objects.create_superuser(
            username="meridien",
            password='meridien22',
            date_birth="1990-01-01",
            client_id=43,
        )

        self.stdout.write(self.style.SUCCESS("All Done !"))