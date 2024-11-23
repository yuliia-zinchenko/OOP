# load_quotes.py
import os
import django

# Налаштовуємо Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "library.settings")
django.setup()

from book.models import Quote

quotes = [
    {"text": "Not all those who wander are lost.", "book_title": "The Lord of the Rings"},
    {"text": "It is only with the heart that one can see rightly; what is essential is invisible to the eye.", "book_title": "The Little Prince"},
    {"text": "So we beat on, boats against the current, borne back ceaselessly into the past.", "book_title": "The Great Gatsby"},
    {"text": "It is only with the heart that one can see rightly; what is essential is invisible to the eye.", "book_title": "The Little Prince"},
    {"text": "The only limit to our realization of tomorrow is our doubts of today.", "book_title": "Inaugural Address"},
    {"text": "In three words I can sum up everything I've learned about life: it goes on.", "book_title": "The Poetry of Robert Frost"},
    {"text": "To be, or not to be, that is the question.", "book_title": "Hamlet"},
    {"text": "We are all in the gutter, but some of us are looking at the stars.", "book_title": "Lady Windermere's Fan"},
    {"text": "I am not afraid of storms, for I am learning how to sail my ship.", "book_title": "Little Women"},
    {"text": "The truth will set you free, but first it will make you miserable.", "book_title": "Inaugural Address"},
    {"text": "Whatever you are, be a good one.", "book_title": "Letters of Abraham Lincoln"},
    {"text": "There is no greater agony than bearing an untold story inside you.", "book_title": "I Know Why the Caged Bird Sings"},
    
]

for quote in quotes:
    Quote.objects.create(**quote)

print("added successfully")
