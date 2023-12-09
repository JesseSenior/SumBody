import websocket
import base64
import json
import ssl
import _thread as thread
import os
from pydub import AudioSegment
from pydub.playback import play
from .APIClinetXF import APIClientXF


class TTSClient(object):
    def __init__(self, API_manager: APIClientXF, Text=""):
        self.API_manager = API_manager
        self.Text = Text

        self.audio_content = b""
        # 公共参数(common)
        self.CommonArgs = {"app_id": self.API_manager.APPID}
        # 业务参数(business)，更多个性化参数可在官网查看
        self.BusinessArgs = {
            "aue": "raw",
            "auf": "audio/L16;rate=16000",
            "vcn": "xiaoyan",
            "tte": "utf8",
        }
        self.Data = {
            "status": 2,
            "text": str(base64.b64encode(self.Text.encode("utf-8")), "UTF8"),
        }

    def synthesize(self, text: str) -> bytes:
        def on_open(ws):
            def run(*args):
                d = {
                    "common": self.CommonArgs,
                    "business": self.BusinessArgs,
                    "data": self.Data,
                }
                d = json.dumps(d)
                ws.send(d)
                if os.path.exists("./demo.pcm"):
                    os.remove("./demo.pcm")

            thread.start_new_thread(run, ())

        def on_message(ws, message):
            try:
                message = json.loads(message)
                code = message["code"]
                sid = message["sid"]
                audio = message["data"]["audio"]
                audio = base64.b64decode(audio)
                status = message["data"]["status"]
                if status == 2:
                    ws.close()
                if code != 0:
                    errMsg = message["message"]
                else:
                    with open("./demo.pcm", "ab") as f:
                        f.write(audio)
            except Exception as e:
                print("receive msg, but parse exception:", e)

        def on_error(ws, error):
            ...

        def on_close(ws):
            ...
            print("### closed ###")

        websocket.enableTrace(False)
        wsUrl = self.API_manager.get_url_tts()
        ws = websocket.WebSocketApp(
            wsUrl, on_message=on_message, on_error=on_error, on_close=on_close
        )
        ws.on_open = on_open
        ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})
        with open("demo.pcm", "rb") as f:
            data = f.read()
        audio = AudioSegment(data=data, sample_width=2, frame_rate=16000, channels=1)
        tmp_file = "tmp_audio.wav"
        audio.export(tmp_file, format="wav")
        play(audio)
