
# 3️⃣ Initalize a pipeline
from kokoro import KPipeline
from IPython.display import display, Audio
import soundfile as sf
import torch
# 🇺🇸 'a' => American English, 🇬🇧 'b' => British English
# 🇯🇵 'j' => Japanese: pip install misaki[ja]
# 🇨🇳 'z' => Mandarin Chinese: pip install misaki[zh]
# from src.sevices.text2speech import KPipeline_TTS

# pipeline = KPipeline(model= '/app/tts_services/Kokoro-82M', lang_code='j') # <= make sure lang_code matches voice

# # This text is for demonstration purposes only, unseen during training

# text = '「もしおれがただ偶然、そしてこうしようというつもりでなくここに立っているのなら、ちょっとばかり絶望するところだな」と、そんなことが彼の頭に思い浮かんだ。'

# # generator = pipeline(
# #     text, voice='af_heart', # <= change voice here
# #     speed=1, split_pattern=r'\n+'
# # )

# # Alternatively, load voice tensor directly:
# import time
# start = time.time()
# voice_tensor = torch.load('/app/tts_services/voices/jf_alpha.pt', weights_only=True)
# print('======== time : ',time.time() - start)
# generator = pipeline(
#     text, voice=voice_tensor,
#     speed=1, split_pattern=r'\n+'
# )

# for i, (gs, ps, audio) in enumerate(generator):
#     print(i)  # i => index
#     print(gs) # gs => graphemes/text
#     print(ps) # ps => phonemes
#     display(Audio(data=audio, rate=24000, autoplay=i==0))
#     sf.write(f'{i}.wav', audio, 24000) # save each audio file
    
    
# from src.sevices.text2speech import KPipeline_TTS
from src.sevices.kokoro_pipeline import KPipeline
from src.sevices.kokoro_pipeline.model import KModel
import os 
import json 

path_config = os.path.join(os.environ.get('KOKORO_PATH_MODEL'),'config.json')
with open(path_config, 'r') as file:
    config = json.load(file)

device = 'cuda' if torch.cuda.is_available() else 'cpu'

kmodel = KModel(config=config,model=os.path.join(os.environ.get('KOKORO_PATH_MODEL'),'kokoro-v1_0.pth'))

import time
start = time.time()
kpipeline_tts = KPipeline(
                            lang_code='j',
                            model=kmodel,
                            device=device,
                            )
print('======== loading model time : ',time.time() - start)
text = '「もしおれがただ偶然、そしてこうしようというつもりでなくここに立っているのなら、ちょっとばかり絶望するところだな」と、そんなことが彼の頭に思い浮かんだ。'

start = time.time()


voice_tensor = torch.load('/app/tts_services/voices/jf_alpha.pt', weights_only=True)
generator = kpipeline_tts(
    text, voice=voice_tensor,
    speed=1, split_pattern=r'\n+'
)
print('======== inferences time  : ',time.time() - start)


for i, (gs, ps, audio) in enumerate(generator):
    print(i)  # i => index
    print(gs) # gs => graphemes/text
    print(ps) # ps => phonemes
    display(Audio(data=audio, rate=24000, autoplay=i==0))
    sf.write(f'{i}.wav', audio, 24000) # save each audio filegi