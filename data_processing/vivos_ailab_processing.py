# Path to the CSV file
import re
import csv
from num2words import num2words
#import function from file to use 
from replace_number_to_word import extract_and_replace_numbers

input_file = '/home/dht/dev_training_tts/datasets/vivos/test/audio_ann_sum.csv'  # Replace with your actual file path
output_file = 'output.csv'  # The file where the processed result will be saved

# Open the input CSV file for reading and the output CSV file for writing
with open(input_file, mode='r', newline='', encoding='utf-8') as infile, open(output_file, mode='w', newline='', encoding='utf-8') as outfile:
    csv_reader = csv.reader(infile, delimiter='|')
    csv_writer = csv.writer(outfile, delimiter='|')

    # Process each row in the input file
    for row in csv_reader:
        # Skip empty rows
        if not row:
            continue

        # Process the row (remove duration and [VI] tags)
        identifier = row[0]
        text = row[3]

        # Remove '[VI]' tags
        text_cleaned = re.sub(r'\[VI\]', '', text).strip()

        # Apply the number-to-word transformation
        text_transformed = extract_and_replace_numbers(text_cleaned)

        # Write the cleaned and transformed row to the output file
        csv_writer.writerow([identifier, text_cleaned, text_transformed])

print(f"Processed CSV saved to {output_file}")




