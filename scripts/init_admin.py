import django
import os
import pathlib
import sys

from django.contrib.auth import get_user_model

sys.path.append(str(pathlib.Path(__file__).parent.absolute().parent))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "blog.settings")
django.setup()

User = get_user_model()

User.objects.create_superuser('admin', '', 'admin')

