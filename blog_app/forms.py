from django import forms
from .models import Comment
from .image_processing import check_image_size
from ckeditor.widgets import CKEditorWidget

from scripts import filter_html


class NewPostForm(forms.Form):
    title = forms.CharField(label='Title', max_length=200)
    # image = forms.ImageField(label='Image', required=False, validators=[check_image_size])
    # content = forms.CharField(label='Text', widget=forms.Textarea)
    # content = forms.CharField(widget=SummernoteWidget())
    content = forms.CharField(widget=CKEditorWidget())
    tags = forms.CharField(label='Tags', widget=forms.Textarea, required=False, help_text='Tags are determined by #. Examples: #sport #tech #regular life')

    def clean_content(self):
        content = self.cleaned_data['content']
        content = filter_html.filter_html_input(content)
        return content


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('body',)
