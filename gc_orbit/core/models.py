from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.hashers import make_password

class Department(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class Organization(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    password = models.CharField(max_length=255)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def __str__(self):
        return self.name

class User(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('dean', 'Dean'),
        ('adviser', 'Adviser'),
        ('organization', 'Organization'),
    ]
    role = models.CharField(max_length=12, choices=ROLE_CHOICES)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, null=True, blank=True)  # Make it nullable temporarily
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, null=True, blank=True)

    @property
    def name(self):
        return f"{self.first_name} {self.last_name}".strip()

    def __str__(self):
        return self.username
