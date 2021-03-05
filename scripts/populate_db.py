import datetime
import os
import pathlib
import time
import random
import sys

import django
from django.contrib.auth import get_user_model
from django.utils.crypto import get_random_string
from django.utils.text import slugify
from faker import Faker

sys.path.append(str(pathlib.Path(__file__).parent.absolute().parent))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "blog.settings")
django.setup()

from blog_app.models import Post, Tag, Comment


def create_blogposts(number_of_objects):
    start_time = time.time()
    fake = Faker()

    for i in range(number_of_objects):

        number_of_symbols = random.randint(3000, 7000)

        sentences_list = fake.text(number_of_symbols).split('\n')
        sentences_list_len = len(sentences_list)

        index = 0
        min_linebreak_index = 9
        max_linebreak_index = 14
        while index < sentences_list_len - max_linebreak_index - 1:
            linebreak_index = random.randint(min_linebreak_index, max_linebreak_index)
            linebreak_index += random.randint(-2, 2)

            sentences_list.insert(index + linebreak_index, '\n\n')

            index += linebreak_index

            if index > sentences_list_len:
                break

        text = ''.join(sentences_list)

        with open('scripts/taglines', 'r') as reader:
            list_of_tags = reader.read().split('\n')

        number_of_tags = random.randint(0, 10)

        random.shuffle(list_of_tags)
        tags = random.sample(list_of_tags, number_of_tags)

        title = fake.sentence(nb_words=7)

        User = get_user_model()

        users = User.objects.all()

        while True:
            user = random.choice(users)
            if user.is_staff:
                continue
            break

        slug = slugify('{}-{}-{}'.format(
            title,
            user.username,
            datetime.datetime.now().strftime('%Y-%m-%d'))
        )
        while Post.objects.filter(slug=slug).exists():
            slug = '{}-{}'.format(slug, get_random_string(length=2))

        post = Post()
        post.title = title
        post.content = text
        post.author = user
        post.status = random.randint(0, 1)
        post.slug = slug
        post.save()

        list_of_tags = []
        for tag in tags:
            list_of_tags.append(Tag.objects.get_or_create(tagline=tag)[0])

        post.tags.add(*list_of_tags)

    print("--- %s seconds ---" % (time.time() - start_time))

    # List comprehension doesn't work if code is executed in shell
    # globals().update(locals())
    # for k in (Tag.objects.get_or_create(tagline=i)[0] for i in tags):
    #     print(i)
    # print([Tag.objects.get_or_create(tagline=tag)[0] for tag in tags])


def create_comment(number_of_objects):
    start_time = time.time()

    fake = Faker()
    posts = Post.objects.filter(status=1)

    for i in range(number_of_objects):

        number_of_symbols = random.randint(50, 500)

        text = fake.text(number_of_symbols).replace('\n', ' ')

        User = get_user_model()
        users = User.objects.all()

        while True:
            user = random.choice(users)
            if user.is_staff:
                continue
            break

        post = random.choice(posts)

        comment = Comment()
        comment.body = text
        comment.author = user
        comment.post = post
        comment.active = random.randint(0, 1)
        comment.save()

    print("--- %s seconds ---" % (time.time() - start_time))


# create_blogposts(100)
create_comment(3000)
