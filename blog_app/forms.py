from django import forms
from .models import Comment
from .image_processing import check_image_size
from django_summernote.widgets import SummernoteWidget, SummernoteInplaceWidget
from ckeditor.widgets import CKEditorWidget


class NewPostForm(forms.Form):
    title = forms.CharField(label='Title', max_length=200)
    image = forms.ImageField(label='Image', required=False, validators=[check_image_size])
    # content = forms.CharField(label='Text', widget=forms.Textarea)
    # content = forms.CharField(widget=SummernoteWidget())
    content = forms.CharField(widget=CKEditorWidget())
    tags = forms.CharField(label='Tags', widget=forms.Textarea, required=False)


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('body',)
