from django import forms


class BookSearchForm(forms.Form):
    query = forms.CharField(required=True, max_length=100, label="Search")
    search_by = forms.ChoiceField(
        choices=[('intitle', 'Title'), ('inauthor', 'Author'), ('subject', 'Genre')],
        required=True
    )


class ManualBookForm(forms.Form):
    STATUS_CHOICES = [
        ('mark_as_read', 'Mark as Read'),
        ('currently_reading', 'Currently Reading'),
        ('read_later', 'Read later'),
    ]
    title = forms.CharField(max_length=30, required=True, label="Title")
    author = forms.CharField(max_length=30, required=True, label="Author")
    genre = forms.CharField(max_length=50, required=True, label="Genre")
    status = forms.ChoiceField(choices=STATUS_CHOICES, required=True, label="Status")






