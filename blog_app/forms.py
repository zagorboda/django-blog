from django import forms
from .models import Comment
from .image_processing import check_image_size


class NewPostForm(forms.Form):
    title = forms.CharField(label='Title', max_length=200)
    image = forms.ImageField(label='Image', required=False, validators=[check_image_size])
    # slug = forms.SlugField(label='Slug', max_length=200)
    content = forms.CharField(label='Text', widget=forms.Textarea)
    tags = forms.CharField(label='Tags', widget=forms.Textarea, required=False)
    # author = forms.TextInput()
    # created_on = forms.DateField()


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('body',)
