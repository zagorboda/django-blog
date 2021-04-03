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

from blog_app.models import Post, Tag, Comment, ReportPost, ReportComment


def create_blogposts(number_of_objects):
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

    # List comprehension doesn't work if code is executed in shell
    # globals().update(locals())
    # for k in (Tag.objects.get_or_create(tagline=i)[0] for i in tags):
    #     print(i)
    # print([Tag.objects.get_or_create(tagline=tag)[0] for tag in tags])


def create_comment(number_of_objects):
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


def create_users(number_of_objects):
    fake = Faker()
    User = get_user_model()
    for i in range(number_of_objects):
        username = fake.simple_profile()['username']
        email = username + '@djangoblog.com'
        password = get_random_string(32)
        user = User.objects.create_user(username, email, password)
        bio = fake.text(400).replace('\n', '')
        user.bio = bio
        user.save()


def create_likes_and_reports(number_of_objects):
    fake = Faker()
    posts = Post.objects.filter(status=1)
    comments = Comment.objects.filter(status=1)
    User = get_user_model()
    users = User.objects.filter(is_staff=False)

    for i in range(number_of_objects):
        post = random.choice(posts)
        user = random.choice(users)
        comment = random.choice(comments)

        post.likes.add(user)

        if i % 2 == 0:
            if ReportPost.objects.filter(post=post).exists():
                report = ReportPost.objects.get(post=post)
                if not report.reports.filter(username=user.username).exists():
                    report.total_reports += 1
                    report.reports.add(user)
                    report.save()
            else:
                report = ReportPost.objects.create(post=post)
                report.total_reports += 1
                report.reports.add(user)
                report.save()

        if i % 3 == 0:
            if ReportComment.objects.filter(comment=comment).exists():
                report = ReportComment.objects.get(comment=comment)
                if not report.reports.filter(username=user.username).exists():
                    report.total_reports += 1
                    report.reports.add(user)
                    report.save()
            else:
                report = ReportComment.objects.create(comment=comment)
                report.total_reports += 1
                report.reports.add(user)
                report.save()


print('1/4: Creating users')
create_users(20)
print('2/4: Creating posts')
create_blogposts(250)
print('3/4: Creating comments')
create_comment(750)
print('4/4: Creating likes and reports')
create_likes_and_reports(150)
