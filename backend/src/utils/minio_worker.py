import boto3
import os
import re
from typing import List


class Minio_Worker():
    def __init__(self,minio_hostname, access_key, secret_key, bucket_name):
        self.client = boto3.resource('s3', 
                            endpoint_url=minio_hostname,
                            aws_access_key_id=access_key,
                            aws_secret_access_key=secret_key,
                            aws_session_token=None,
                            config=boto3.session.Config(signature_version='s3v4'),
                        )   
        self.bucket = bucket_name  
       
    def get_file_from_minio_server(self, path_audio_stogare, original_name, language):
        if not os.path.exists(path_audio_stogare):
            os.makedirs(path_audio_stogare)
            
        file_name = original_name + '.wav'
        audio_path_language = os.path.join(path_audio_stogare,language)
        try:
            if not os.path.exists(audio_path_language):
                os.makedirs(audio_path_language)
            audio_dir = os.path.join(audio_path_language,file_name)
            if os.path.isfile(audio_dir):
                return {
                    'status':200,
                    'audio_dir':audio_dir
                }
            else:
                path_audio_bucket = os.path.join(language,file_name)
                self.client.Bucket(self.bucket).download_file(path_audio_bucket,audio_dir)
                return {
                    'status':200,
                    'audio_dir':audio_dir
                }
        except:
            return {
                'status':400,
                'messages':f'Could not find voice id {original_name}'
            }