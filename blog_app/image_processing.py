import os
from PIL import Image
from django.core.exceptions import ValidationError
from django.dispatch import receiver
from django.db.models.signals import post_save, pre_save
from .models import Post


def delete_image(path):
    """ Deletes file from filesystem. """
    if os.path.isfile(path):
        os.remove(path)


def resize_image(image_path):
    """ Resize image """
    size = 1000, 1000

    im = Image.open(image_path)
    im.thumbnail(size, Image.ANTIALIAS)
    im.save(image_path)


def check_image_size(image):
    """ Return True if image size less than 5mb """
    if image.size > 5242880:
        raise ValidationError('Maximum file size is 5mb. Selected image size is {:.2f} mb'.format(
            image.size / 1024**2
        ))


# @receiver(pre_save, sender=Post)
# def pre_process_image(sender, instance, **kwargs):
#     if instance.id is not None:
#         current = instance
#         previous = Post.objects.get(id=instance.id)
#         if current.image != previous.image:  # if image was changed
#
#             if previous.image:
#                 delete_image(previous.image.path)
#
#
# @receiver(post_save, sender=Post)
# def post_process_image(sender, instance, created, **kwargs):
#     if instance.image:
#         resize_image(instance.image.path)


# post_save.connect(post_process_image, sender=Post)  # dispatch_uid="resize_post_image"
