import uuid
import subprocess
import os
from typing import List, Tuple

import numpy as np
import soundfile


class Audio2Chunks:
    @staticmethod
    def split_audio_to_chunks(
        audio: bytes, audio_type: str = "mp3", framerate=None
    ) -> Tuple[List[bytes], int]:
        """
        Split the audio into chunks
        :param audio: the audio to be split
        :param audio_type: the audio type("mp3" or "wav"), default is "mp3".
        :param framerate: framerate of wav file.
        :param chunk_size: the size of each chunk
        :return: a list of chunks and the sample rate
        """
        if audio_type == "mp3":
            # Generate an id for the audio files
            audio_id = uuid.uuid4().hex
            mp3_file = "{name}.mp3".format(name=audio_id)
            wav_file = "{name}.wav".format(name=audio_id)

            # Save audio content to an mp3 file
            with open(mp3_file, "wb") as out:
                out.write(audio)

            # Convert MP3 to WAV
            subprocess.call(["ffmpeg", "-i", mp3_file, wav_file])

            # Extract the audio data and the sample rate
            data, sample_rate = soundfile.read(wav_file)

            # Clean up the files
            os.remove(mp3_file)
            os.remove(wav_file)
        elif audio_type == "wav":
            data, sample_rate = audio, framerate
        else:
            raise "Unknown datatype"

        if len(data.shape) > 1:
            data = np.average(data, axis=1)

        # Split the audio into chunks
        chunk_size = sample_rate // 10
        data = [
            data[i * chunk_size : i * chunk_size + chunk_size]
            for i in range(len(data) // chunk_size + 1)
        ]

        # Return the chunks and the sample rate
        return data, sample_rate
