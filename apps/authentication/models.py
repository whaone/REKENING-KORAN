#from django.contrib.auth.models import AbstractUser
from django.db import models

"""
class User(AbstractUser):
    #class Role(models.TextChoices):
        # SUPER_ADMIN = "SUPER_ADMIN", "Super Admin"
       # FINANCE_ADMIN = "FINANCE_ADMIN", "Admin Keuangan"
       # OPERATOR = "OPERATOR", "Operator"
        #AUDITOR = "AUDITOR", "Auditor"
        #USER = "USER", "User"

    #role = models.CharField(
        #max_length=20, 
        #choices=Role.choices, 
        default=Role.USER
    )

    def __str__(self):
        return f"{self.username} ({self.role})"
"""