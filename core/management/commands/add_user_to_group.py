from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group
from core.models import User


class Command(BaseCommand):
    help = 'Add user to group'

    def add_arguments(self, parser):
        parser.add_argument('user_id', type=int, help='User ID')
        parser.add_argument('group_id', type=int, help='Group ID')

    def handle(self, *args, **options):
        user_id = options['user_id']
        group_id = options['group_id']

        try:
            user = User.objects.get(id=user_id)
            group = Group.objects.get(id=group_id)
            
            user.groups.add(group)
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully added user {user.mobile_number} (ID: {user_id}) to group {group.name} (ID: {group_id})'
                )
            )
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'User with ID {user_id} does not exist'))
        except Group.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Group with ID {group_id} does not exist'))