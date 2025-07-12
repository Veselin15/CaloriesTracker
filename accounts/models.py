from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    """
    Custom user model extending Django's AbstractUser.
    Uses 'Users' as the database table name.
    """
    class Meta:
        db_table = 'Users'