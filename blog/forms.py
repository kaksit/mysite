
from tkinter.tix import Form
from django import forms
from .models import Comment

class EmailPostForm(forms.Form):
    name=forms.CharField(max_length=50)
    email=forms.EmailField()
    to=forms.EmailField()
    comments=forms.CharField(widget=forms.Textarea,required=False)

class CommentForm(forms.ModelForm):
    class Meta :
        model=Comment
        fields=('name','email','body')
        