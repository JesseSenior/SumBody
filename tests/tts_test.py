from sumbody.services import APIClinetXF
from sumbody.services import TTSClient
from argparse import ArgumentParser

def parse_xf_api(parser: ArgumentParser) -> ArgumentParser:
    """
    Add Xunfei API requirements to parser.
    """
    parser.add_argument("--xf_appid", type=str, required=True, help="Xunfei API Info.")
    parser.add_argument(
        "--xf_api_secret", type=str, required=True, help="Xunfei API Info."
    )
    parser.add_argument(
        "--xf_api_key", type=str, required=True, help="Xunfei API Info."
    )
    return parser
if __name__ == "__main__":
    parser = ArgumentParser(
        description="A unit test for speech-to-text to the Audio2Face plugin."
    )
    parser = parse_xf_api(parser)
    args = parser.parse_args()
    xf_appid: str = args.xf_appid
    xf_api_secret: str = args.xf_api_secret
    xf_api_key: str = args.xf_api_key
    api_manager = APIClientXF(
        APPID=xf_appid,
        APISecret=xf_api_secret,
        APIKey=xf_api_key,
    )
    TTS_client = TTSClient(api_manager)
    txt="原神，启动";
    TTS_client.synthesize(txt)
