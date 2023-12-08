import typer
from sumbody.services import APIClinetXF
from sumbody.services import STTClient


if __name__ == "__main__":
    xf_appid: str = typer.Option(
        ...,
        help="The STT Client APPID",
        envvar="STT_APPID",
        show_envvar=True,
    ),
    xf_apisecret: str = typer.Option(
        ...,
        help="The STT Client APISECRET",
        envvar="STT_APISECRET",
        show_envvar=True,
    ),
    xf_apikey: str = typer.Option(
        ...,
        help="The STT Client APIKEY",
        envvar="STT_APIKEY",
        show_envvar=True,
    ),
    api_manager = APIClinetXF(
        APPID=xf_appid,
        APISecret=xf_apisecret,
        APIKey=xf_apikey,
    )
    input("Press Any Key to start...")
    client = STTClient(api_manager)
    client.start()
    input()
    client.stop()
    client.join()
    print(client.message)
