# class CustomUser():
#     pass
    # username = models.CharField(max_length=50, unique=True)

    # some_new_field = models.CharField(max_length=50, default='Some value')

    # def __str__(self):
    #     return "{}".format(self.username)


# TODO: try this
# class User(AbstractUser):
#     bio = models.TextField(max_length=500, blank=True)
#     location = models.CharField(max_length=30, blank=True)
#     birth_date = models.DateField(null=True, blank=True)


# TODO: This breaks login
# @receiver(post_save, sender=User)
# def save_user_profile(sender, instance, **kwargs):
#     instance.Userprofile.save()


# @receiver(post_save, sender=User)
# def create_user_profile(sender, instance, created, **kwargs):
#     if created:
#         UserProfile.objects.create(user=instance)
