import re

def clean_text(text):
    return ''.join(e for e in text if e.isalnum() or e.isspace()).lower()