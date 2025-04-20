import os
import shutil

# Specify the source and destination folders
source_folder = '/workspace/text2speech/datasets/vi/vivos/data/vivos/train/waves'
destination_folder = '/workspace/text2speech/datasets/vi/totals'

# Make sure the destination folder exists, if not, create it
if not os.path.exists(destination_folder):
    os.makedirs(destination_folder)

# Iterate through all the files in the source folder
for folder_id in os.listdir(source_folder):
    foler_auidio = os.path.join(source_folder, folder_id)
    for filename in os.listdir(foler_auidio):
        if filename.endswith('.wav'):  # Check if the file is a .wav file
            source_file = os.path.join(foler_auidio, filename)
            destination_file = os.path.join(destination_folder, filename)
            
            # Copy the file to the destination folder
            shutil.copy(source_file, destination_file)
            print(f'Copied: {filename}')