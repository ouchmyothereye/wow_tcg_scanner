test_input = ['The Key to Freedom\nQuest\nOC\nPay to complete this quest\nReward: Draw a card.\nThe small brass key looks simple enough\nALLIANCE DK 31/32\nArt by Matt Dixon\ncada Fe']

def clean_text(text):
    return ''.join(e for e in text if e.isalnum() or e.isspace()).lower()

cleaned_test_input = clean_text(' '.join(test_input))
print(cleaned_test_input)


abbreviations = ['Alliance DK', 'Alliance Druid']
abbreviations_lower = [abbr.lower() for abbr in abbreviations]

for abbr in abbreviations_lower:
    if abbr in cleaned_test_input:
        print(f"Matched: {abbr}")
