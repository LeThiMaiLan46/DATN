import re
import csv
from num2words import num2words

def process_line(line):
    # Split the line by the delimiter '|'
    parts = line.split('|')

    # Extract the first and last fields (remove duration and [VI] tags)
    identifier = parts[0]
    text = parts[3]

    # Remove '[VI]' tags from the text
    text_cleaned = re.sub(r'\[VI\]', '', text).strip()

    return f"{identifier}| {text_cleaned}"

def extract_and_replace_numbers(text):
    def replace_with_words(match):
        num_str = match.group(0)
        
        if num_str[-1].isalpha():
            num_part = num_str[:-1]
            letter_part = num_str[-1]
            num_word = num2words(float(num_part), lang='vi')
            return num_word + ' ' + letter_part

        elif num_str[0].isalpha():
            letter_part = num_str[0]
            num_part = num_str[1:]
            num_word = num2words(float(num_part), lang='vi')
            return letter_part + ' ' + num_word

        else:
            if '.' in num_str:
                num_word = num2words(float(num_str), lang='vi')
            else:
                num_word = num2words(int(num_str), lang='vi')
            return ' ' + num_word

    updated_text = re.sub(r'-?\d+\.?\d*[\w]*', replace_with_words, text)
    
    return updated_text



