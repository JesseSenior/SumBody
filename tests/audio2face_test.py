from sumbody.services import Audio2Chunks, Audio2Face


# Split the audio into chunks
audio_chunks, sample_rate = Audio2Chunks.split_audio_to_chunks_raw(
    "C:/Users/jesse/Workspace/english_voice_male_p3_neutral.wav"
)

# Stream the audio to the Audio2Face plugin
Audio2Face.stream_chunk(
    audio=audio_chunks,
    endpoint="localhost:50051",
    sample_rate=sample_rate,
    instance_name="/World/audio2face/PlayerStreaming",
)
