from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models


# class CustomUserManager(BaseUserManager):
#     def create_user(self, email, first_name, last_name, password=None):
#         if not email:
#             raise ValueError("User must have an email")
#         if not password:
#             raise ValueError("User must have a password")
#         if not first_name:
#             raise ValueError("User must have a first name")
#         if not last_name:
#             raise ValueError("User must have a last name")
#
#         user = self.model(
#             email=self.normalize_email(email)
#         )
#         user.first_name = first_name
#         user.last_name = last_name
#         user.set_password(password)  # change password to hash
#         user.is_admin = False
#         user.is_staff = False
#         user.save(using=self._db)
#         return user
#
#     def create_superuser(self, email, first_name, last_name, password=None):
#         if not email:
#             raise ValueError("User must have an email")
#         if not password:
#             raise ValueError("User must have a password")
#         if not first_name:
#             raise ValueError("User must have a first name")
#         if not last_name:
#             raise ValueError("User must have a last name")
#
#         user = self.model(
#             email=self.normalize_email(email)
#         )
#         user.first_name = first_name
#         user.last_name = last_name
#         user.set_password(password)  # change password to hash
#         user.is_admin = True
#         user.is_staff = True
#         user.save(using=self._db)
#         return user
#
#     def create_staffuser(self, email, first_name, last_name,  password=None):
#         if not email:
#             raise ValueError("User must have an email")
#         if not password:
#             raise ValueError("User must have a password")
#         if not first_name:
#             raise ValueError("User must have a first name")
#         if not last_name:
#             raise ValueError("User must have a last name")
#
#         user = self.model(
#             email=self.normalize_email(email)
#         )
#         user.first_name = first_name
#         user.last_name = last_name
#         user.set_password(password)  # change password to hash
#         user.is_admin = False
#         user.is_staff = True
#         user.save(using=self._db)
#         return user


class User(AbstractUser):
    bio = models.TextField(max_length=500, blank=True)
