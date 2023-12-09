import uuid
import subprocess
import os
import tempfile
from typing import List, Tuple

import numpy as np
import soundfile


class Audio2Chunks:
    @staticmethod
    def split_audio_to_chunks(
        audio: bytes, audio_type: str = "mp3"
    ) -> Tuple[List[bytes], int]:
        """
        Split the audio into chunks
        :param audio: the audio to be split
        :param audio_type: the audio type("mp3" or "wav"), default is "mp3".
        :param chunk_size: the size of each chunk
        :return: a list of chunks and the sample rate
        """
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as audio_file:
            if audio_type == "mp3":
                with tempfile.NamedTemporaryFile(
                    suffix=".mp3", delete=False
                ) as original_audio_file:
                    audio_file.close()
                    original_audio_file.write(audio)
                    original_audio_file.close()
                    subprocess.call(
                        ["ffmpeg", "-i", original_audio_file.name, audio_file.name]
                    )
                    os.unlink(original_audio_file.name)
            elif audio_type == "wav":
                audio_file.write(audio)
                audio_file.close()
            else:
                raise TypeError("Unknown audio datatype")
            data, sample_rate = soundfile.read(audio_file.name)
            os.unlink(audio_file.name)

        if len(data.shape) > 1:
            data = np.average(data, axis=1)

        # Split the audio into chunks
        chunk_size = sample_rate // 10
        data = [
            data[i * chunk_size : i * chunk_size + chunk_size]
            for i in range(len(data) // chunk_size + 1)
        ]

        # Return the chunks and the sample rate
        return data, sample_rate  # type:ignore
