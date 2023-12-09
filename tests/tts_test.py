from sumbody.services import APIClientXF
from sumbody.services import TTSClient
from argparse import ArgumentParser
from stt_test import parse_xf_api


if __name__ == "__main__":
    parser = ArgumentParser(
        description="A unit test for speech-to-text to the Audio2Face plugin."
    )
    parser = parse_xf_api(parser)
    args = parser.parse_args()
    xf_appid: str = args.xf_appid
    xf_api_secret: str = args.xf_apisecret
    xf_api_key: str = args.xf_apikey
    api_manager = APIClientXF(
        APPID=xf_appid,
        APISecret=xf_api_secret,
        APIKey=xf_api_key,
    )
    TTS_client = TTSClient(api_manager)
    txt = "城里烟火幢幢，灯光下的人热情相拥，阴影里的人压下悸动。最亮的地方嘉然小姐浅笑起舞，光影从她袖间散落，像是雨天花伞轻旋，摇曳间洒下泪色的流珠。忽然眼睛有点模糊。我小声说：“新年好啊，嘉然小姐。”不爱嘉然小姐十年了。十年里，爱过的每个人都像她。"
    TTS_client.synthesize(txt)
