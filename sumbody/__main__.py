# -*- coding: utf-8 -*-
import typer

from sumbody import logger
from sumbody.services import (
    TTSClient,
    Audio2Face,
    Audio2Chunks,
    TextSummary,
    STTClient,
    APIClientXF,
)

app = typer.Typer(
    name="sumbody",
    help="An intelligent meeting summary assistant that uses the Text-To-Speech, the Speech-to-Text, and the Generative AI technologies to generate summary and to stream the audio to the Nvidia Audio2Face plugin.",
)


@app.command()
def run_sumbody(
    # STT part
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
    # OpenAI part
    openai_key: str = typer.Option(
        ...,
        help="The OpenAI API key",
        envvar="OPENAI_KEY",
        show_envvar=True,
    ),
    openai_base: str = typer.Option(
        default=None,
        help="The OpenAI API base url",
        envvar="OPENAI_BASE",
        show_envvar=True,
    ),
    openai_model: str = typer.Option(
        default="gpt-3.5-turbo",
        help="The OpenAI model to be used",
        envvar="OPENAI_MODEL",
        show_envvar=True,
    ),
    # Audio2Face part
    grpc_server: str = typer.Option(
        default="localhost:50051", help="The endpoint of the gRPC server"
    ),
    instance_name: str = typer.Option(
        default="/World/audio2face/PlayerStreaming",
        help="Instance name to Audio2Face stream player.",
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
    logger.info(
        "openai_base: {}".format(openai_base if openai_base is not None else "DEFAULT")
    )
    logger.info("openai_model: {}".format(openai_model))

    logger.info("grpc_server: {}".format(grpc_server))
    logger.info("instance_name: {}".format(instance_name))

    managerXF = APIClientXF(
        APPID=stt_appid,
        APISecret=stt_apisecret,
        APIKey=stt_apikey,
    )

    stt_client = STTClient(managerXF)

    tsum = TextSummary(
        api_key=openai_key,
        api_base=openai_base,
        model=openai_model,
    )

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

        # Generate the summary by GPT
        ans = tsum.forward(text)
        logger.info("Summary: {}".format(ans))

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
            instance_name=instance_name,
        )


if __name__ == "__main__":
    app()
