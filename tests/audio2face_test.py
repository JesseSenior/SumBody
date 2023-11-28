import argparse
import soundfile
from sumbody.services import Audio2Chunks, Audio2Face

parser = argparse.ArgumentParser(
    description="A unit test for clipping audio files and streaming them to the Audio2Face plugin."
)

parser.add_argument(
    "--audio_file_path", type=str, required=True, help="Path to the audio file."
)
parser.add_argument(
    "--endpoint",
    type=str,
    default="localhost:50051",
    help="The endpoint of the server.",
)
parser.add_argument(
    "--instance_name",
    type=str,
    default="/World/audio2face/audio_player_streaming",
    help="The instance name.",
)

args = parser.parse_args()

data, sample_rate = soundfile.read(args.audio_file_path)

# Split the audio into chunks
audio_chunks, sample_rate = Audio2Chunks.split_audio_to_chunks(
    data, "wav", sample_rate
)

# Stream the audio to the Audio2Face plugin
Audio2Face.stream_chunk(
    audio=audio_chunks,
    endpoint=args.endpoint,
    sample_rate=sample_rate,
    instance_name=args.instance_name,
)
