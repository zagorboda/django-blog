from django import forms


class NewPostForm(forms.Form):
    title = forms.CharField(label='Title', max_length=200)
    # slug = forms.SlugField(label='Slug', max_length=200)
    content = forms.CharField(label='Text', widget=forms.Textarea)
    # author = forms.TextInput()
    # created_on = forms.DateField()
