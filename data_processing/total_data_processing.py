import pandas as pd

# Define the audio directory path
audio_directory = "/workspace/text2speech/datasets/vi_datasets/wavs/"

# Load the CSV file
df = pd.read_csv('/workspace/text2speech/datasets/vi_datasets/metadata.csv', sep='|', header=None, names=["wav", "text", "transcription"])

def ensure_wav_extension(file_name):
    if not file_name.endswith('.wav'):
        return file_name + '.wav'
    return file_name
df['audio_path'] = df['wav'].apply(lambda x: audio_directory + ensure_wav_extension(x))

# Keep only the 'audio_path' column
df_audio_path = df[['audio_path']]

# Save the result to a new CSV file if needed
df_audio_path.to_csv('/workspace/text2speech/datasets/vi_datasets/metadata_train.csv', index=False)

# Print the result (optional)
print(df_audio_path)