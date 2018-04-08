from django import forms


class ContactForm(forms.Form):
    name = forms.CharField(label='Name', widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(label='E-Mail', widget=forms.TextInput(attrs={'class': 'form-control'}))
    comment = forms.CharField(label='Message', widget=forms.Textarea(attrs={'class': 'form-control'}))
