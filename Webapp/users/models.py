from django.db import models

# Create your models here.
from django.contrib.auth.models import User


class UserProfile(models.Model):

    ROLE_CHOICES = [
        ("SENIOR_OFFICER", "Senior Officer"),
        ("INVESTIGATOR", "Investigator"),
        ("AUDITOR", "Auditor"),
    ]

    GENDER_CHOICES = [
        ("MALE", "Male"),
        ("FEMALE", "Female"),
        ("OTHER", "Other"),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)

    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)

    dob = models.DateField()
    age = models.IntegerField()

    def __str__(self):
        return self.user.username
