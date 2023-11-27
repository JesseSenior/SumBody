import soundfile
import numpy as np

from sumbody.services import Audio2Chunks, Audio2Face


test_wav_file_path = r"tests\asset\english_voice_male_p3_neutral.wav"

data, sample_rate = soundfile.read(test_wav_file_path)

if len(data.shape) > 1:
    data = np.average(data, axis=1)


# Split the audio into chunks
audio_chunks, sample_rate = Audio2Chunks.split_audio_to_chunks(data, "wav", sample_rate)

# Stream the audio to the Audio2Face plugin
Audio2Face.stream_chunk(
    audio=audio_chunks,
    endpoint="localhost:50051",
    sample_rate=sample_rate,
    instance_name="/World/audio2face/audio_player_streaming",
)
