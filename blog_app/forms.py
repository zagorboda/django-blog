from django import forms
from .models import Comment


class NewPostForm(forms.Form):
    title = forms.CharField(label='Title', max_length=200)
    # slug = forms.SlugField(label='Slug', max_length=200)
    content = forms.CharField(label='Text', widget=forms.Textarea)
    tags = forms.CharField(label='Tags', widget=forms.Textarea, required=False)
    # author = forms.TextInput()
    # created_on = forms.DateField()


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('body',)
