import random
from newsman.config.settings import MEDIA_LOCAL_DIR
from newsman.config.settings import MEDIA_PUBLIC_DIR
from newsman.processor import tts_provider

random_code = random.randint(0, 1000000000)
tts_web_path = '%s%s_%s.mp3' % (MEDIA_PUBLIC_DIR, 'en', 'tests')
tts_local_path = '%s%s_%s.mp3' % (MEDIA_LOCAL_DIR, 'en', 'tests')

print tts_local_path
print tts_web_path
tts_provider.google(
    'en', "Senators meeting on Obama nominees ends without deal",
    tts_local_path)
