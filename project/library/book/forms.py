from django import forms


# class BookSearchForm(forms.Form):
#     query = forms.CharField(max_length=255, required=True, widget=forms.TextInput(attrs={
#         'placeholder': 'Search for books...'
#     }))

# class BookSearchForm(forms.Form):
#     query = forms.CharField(max_length=100, required=True, label='Search', widget=forms.TextInput(attrs={
#         'placeholder': 'Search for books...'
#     }))
class BookSearchForm(forms.Form):
    query = forms.CharField(max_length=100, required=False, label='Search', widget=forms.TextInput(attrs={
        'placeholder': 'Search by title, author or genre...'
    }))

class ManualBookForm(forms.Form):
    title = forms.CharField(max_length=255, required=True, label="Title")
    author = forms.CharField(max_length=255, required=True, label="Author")






