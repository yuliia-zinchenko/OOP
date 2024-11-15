from django import forms


class BookSearchForm(forms.Form):
    query = forms.CharField(max_length=255, required=True, widget=forms.TextInput(attrs={
        'placeholder': 'Search for books...'
    }))

