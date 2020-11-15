from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
# from django.contrib.auth import login
# from django.test import Client

from blog_app.models import Post
from datetime import datetime


def create_new_user(username, password):
    user = User.objects.create(username=username)
    user.set_password(password)
    user.save()
    return user


def create_new_post(title, text, slug,  author, status=0):
    date = datetime.now()
    return Post.objects.create(title=title,
                               slug=slug,
                               content=text,
                               author=author,
                               status=status,
                               created_on=date)


class UserDetailPageTests(TestCase):

    def test_user_page_existing_user(self):
        test_user = create_new_user('test_user',
                                    'test_password')
        response = self.client.get(reverse('user_app:profile', kwargs={'name': 'test_user'}))
        self.assertEqual(response.status_code, 200)

    def test_user_page_no_existing_user(self):
        response = self.client.get(reverse('user_app:profile', kwargs={'name': 'not_existing_user'}))
        self.assertEqual(response.status_code, 404)

    def test_user_page_user_without_posts(self):
        test_user = create_new_user('test_user',
                                    'test_password')
        response = self.client.get(reverse('user_app:profile', kwargs={'name': 'test_user'}))
        self.assertQuerysetEqual(
            response.context['posts_list'],
            []
        )

    def test_user_page_user_with_posts(self):
        test_user = create_new_user('test_user',
                                    'test_password')
        test_post = create_new_post('New title',
                                    'Some text',
                                    'some-text',
                                    test_user,
                                    status=1)
        response = self.client.get(reverse('user_app:profile', kwargs={'name': 'test_user'}))
        self.assertQuerysetEqual(
            response.context['posts_list'],
            ['<Post: New title>']
        )

    def test_user_page_user_with_draft_posts(self):
        test_user = create_new_user('test_user',
                                    'test_password')
        test_post = create_new_post('New title',
                                    'Some text',
                                    'some-text',
                                    test_user,
                                    status=0)
        response = self.client.get(reverse('user_app:profile', kwargs={'name': 'test_user'}))
        self.assertQuerysetEqual(
            response.context['posts_list'],
            []
        )
