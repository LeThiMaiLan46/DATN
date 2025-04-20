import os 
import csv


def resampling(audio_path, target_path):
    cmd_str = f'ffmpeg -i {audio_path} -ac 1 -ar 22050 {target_path}'
    os.system(cmd_str)
    
    
path_dir_48k = 'workspace/text2speech/datasets/total_datasets/wavs'
path_dir_16k = 'workspace/text2speech/datasets/vi_datasets/wavs'


# Open and read the file
with open('workspace/text2speech/datasets/total_datasets/metadata.csv', 'r', encoding='utf-8') as file:
    for line in file:
        # Split each line by the pipe character
        parts = line.strip().split('|')
        # Print each part
        path_audio = os.path.join(path_dir_48k, parts[0])
        new_path_audio = os.path.join(path_dir_16k, parts[0])
        
        # filename.append(parts[0])
        identifier = parts[0]
        text_cleaned = parts[1]
        # text_cleaned.append(parts[1])
        
        text_transformed = parts[2]
        
        if '.wav' not in path_audio:
            path_audio = path_audio +'.wav'
            new_path_audio += '.wav'
        
        resampling(path_audio, new_path_audio)
        
