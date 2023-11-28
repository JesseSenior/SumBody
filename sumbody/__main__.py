# -*- coding: utf-8 -*-
import typer

from sumbody import logger
from sumbody.domain import MicrophoneStream
from sumbody.services import (
    TextToSpeech,
    Audio2Face,
    Audio2Chunks,
    TextSummary,
    STTClient,
)

app = typer.Typer(
    name="sumbody",
    help="An intelligent meeting summary assistant that uses the Text-To-Speech, the Speech-to-Text, and the Generative AI technologies to generate summary and to stream the audio to the Nvidia Audio2Face plugin.",
)


@app.command()
def run_sumbody(
    stt_appid: str = typer.Option(
        ...,
        help="The STT Client APPID",
        envvar="STT_APPID",
        show_envvar=True,
    ),
    stt_apisecret: str = typer.Option(
        ...,
        help="The STT Client APISECRET",
        envvar="STT_APISECRET",
        show_envvar=True,
    ),
    stt_apikey: str = typer.Option(
        ...,
        help="The STT Client APIKEY",
        envvar="STT_APIKEY",
        show_envvar=True,
    ),
    openai_key: str = typer.Option(
        ...,
        help="The OpenAI API key",
        envvar="OPENAI_KEY",
        show_envvar=True,
    ),
    openai_model: str = typer.Option(
        default="davinci",
        help="The OpenAI model to be used",
        envvar="OPENAI_MODEL",
        show_envvar=True,
    ),
    grpc_server: str = typer.Option(
        default="localhost:50051", help="The endpoint of the gRPC server"
    ),
):
    """
    Run the meta-assistant
    :return:
    """
    microphone_rate = STTClient.RATE
    logger.info("Received arguments:")
    logger.info("microphone_rate: {}".format(microphone_rate))
    logger.info("stt_appid: {}".format(stt_appid))
    logger.info("stt_apisecret: {}".format(stt_apisecret))
    logger.info("stt_apikey: {}".format(stt_apikey))
    logger.info("openai_key: {}".format(openai_key))
    logger.info("openai_model: {}".format(openai_model))
    logger.info("grpc_server: {}".format(grpc_server))

    # 讯飞语音转文字客户端
    stt_client = STTClient(
        APPID=stt_appid,
        APISecret=stt_apisecret,
        APIKey=stt_apikey,
    )

    # Start the main loop
    while True:
        # 读取音频，并转成文字
        # 需要在控制台按任意键开始监听，然后按任意键结束监听
        # TODO: 这部分代码未经测试。后续是否需要一个图形界面？
        input("Press enter Key to start...")
        stt_client.start()
        input()
        stt_client.stop()
        stt_client.join()
        text = stt_client.message
        logger.info("Transcribed text: {}".format(text))

        # 再次调取语音转文字，获取文段主题
        audio_recording_theme = MicrophoneStream.get_audio(
            sample_rate=microphone_rate, duration=20
        )
        
        # theme = SpeechToText.transcribe(audio=audio_recording_theme)

        tsum = TextSummary(
            chunk_size=1024,
            summary_max_len=1024,
            model=openai_model,
            api_key=openai_key
        )
        ans = tsum.forward(text)
        logger.info("Summary: {}".format(ans))

        # # 再次调取语音转文字，获取问题
        # audio_recording_que = MicrophoneStream.get_audio(
        #     sample_rate=microphone_rate, duration=20
        # )
        # que = SpeechToText.transcribe(audio=audio_recording_que)
        # ans = tsum.question(que, text)
        # if len(ans) != 0:
        #     logger.info("Answer: {}".format("".join(ans)))
        # else:
        #     logger.info("未回答相关信息。")

        # Generate the speech audio from the response
        audio_synthesized = TextToSpeech.synthesize(text=ans)

        # Split the audio into chunks
        audio_chunks, sample_rate = Audio2Chunks.split_audio_to_chunks(
            audio=audio_synthesized
        )

        # Stream the audio to the Audio2Face plugin
        Audio2Face.stream_chunk(
            audio=audio_chunks,
            endpoint=grpc_server,
            sample_rate=sample_rate,
            instance_name="/World/audio2face/PlayerStreaming",
        )


if __name__ == "__main__":
    app()
