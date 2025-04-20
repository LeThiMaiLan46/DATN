import pyarrow.parquet as pq
import numpy as np
import scipy.io.wavfile as wav
from num2words import num2words
from scipy.io import wavfile
import csv
import re
import os


def convert_byte_to_audio(byte_data, output_filename):
    # Convert byte data to numpy array of int16
    audio_data = np.frombuffer(byte_data, dtype=np.int16)
    
    # # Make sure audio data is a 1D array for mono audio
    # if audio_data.ndim > 1:
    #     audio_data = audio_data.flatten()
    
    # # Set sample rate (16000 Hz)
    sample_rate = 48000
    
    # Write the audio data to a .wav file
    wavfile.write(output_filename, sample_rate, audio_data)


def replace_numbers_with_vietnamese_words(sentence):
    # Ensure the input is a string
    if not isinstance(sentence, str):
        raise ValueError("The input sentence must be a string.")
    numbers = re.findall(r'\d+', sentence)
    
    for number in numbers:
        vietnamese_word = num2words(int(number), lang='vi') 
        sentence = sentence.replace(number, vietnamese_word)
        
    return sentence


def processing_parquet_file(parquet_path):
    # Read the Parquet file
    table = pq.read_table(parquet_path)

    # Convert to a Pandas DataFrame (optional)
    df = table.to_pandas()

    audio = df['audio']
    transcription = df['transcription']
    output_file = 'workspace/text2speech/datasets/metadata.csv'
    path_audio_dir = 'workspace/text2speech/datasets/infore1_25hours/wav_48k'

    with open(output_file, mode='a', newline='', encoding='utf-8') as outfile:
        csv_writer = csv.writer(outfile, delimiter='|')
        for index, line in enumerate(audio):
            audio_bytes = audio[index]['bytes']
            path_audio = 'doof_' + audio[index]['path']
            audio_filename = os.path.join(path_audio_dir,path_audio)
            audio_transcription = transcription[index]
            
            convert_byte_to_audio(audio_bytes,audio_filename)
            
            identifier = path_audio
            text_cleaned = audio_transcription
            text_transformed = replace_numbers_with_vietnamese_words(audio_transcription)
            csv_writer.writerow([identifier, text_cleaned, text_transformed])
        


dir = 'workspace/text2speech/datasets/infore1_25hours/data'

for index,file in enumerate(os.listdir(dir)):
    path_file = os.path.join(dir,file)
    
    processing_parquet_file(path_file)

    print(f'==== done - {index} : ',path_file)
