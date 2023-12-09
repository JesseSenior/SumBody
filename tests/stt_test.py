from sumbody.services import APIClientXF
from sumbody.services import STTClient
from argparse import ArgumentParser


def parse_xf_api(parser: ArgumentParser) -> ArgumentParser:
    """
    Add Xunfei API requirements to parser.
    """
    parser.add_argument("--xf-appid", type=str, required=True, help="Xunfei API Info.")
    parser.add_argument(
        "--xf-apisecret", type=str, required=True, help="Xunfei API Info."
    )
    parser.add_argument(
        "--xf-apikey", type=str, required=True, help="Xunfei API Info."
    )
    return parser


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
    input("Press Any Key to start...")
    client = STTClient(api_manager)
    client.start()
    input()
    client.stop()
    client.join()
    print(client.message)
