import websocket
import datetime
import hashlib
import base64
import hmac
import json
from urllib.parse import urlencode
import time
import ssl
from wsgiref.handlers import format_date_time
from datetime import datetime
from time import mktime
import _thread as thread
import os
from pydub import AudioSegment
from pydub.playback import play
from wsgiref.handlers import format_date_time


class APIClientXF():
    STT_HOST = "iat-api.xfyun.cn"
    def __init__(self, APPID: str, APISecret: str, APIKey: str) -> None:
        super().__init__()

        self.APPID = APPID
        self.APISecret = APISecret
        self.APIKey = APIKey
class TTSClient(object):
    def __init__(self, API_manager: APIClientXF, Text=""):
        self.APPID = API_manager.APPID
        self.APIKey = API_manager.APIKey
        self.APISecret = API_manager.APISecret
        self.Text = Text
    class WsParam:
        # 初始化
        def __init__(self, APPID, APIKey, APISecret, Text):
            self.APPID = APPID
            self.APIKey = APIKey
            self.APISecret = APISecret
            self.Text = Text
            self.audio_content = b''
            # 公共参数(common)
            self.CommonArgs = {"app_id": self.APPID}
            # 业务参数(business)，更多个性化参数可在官网查看
            self.BusinessArgs = {"aue": "raw", "auf": "audio/L16;rate=16000", "vcn": "xiaoyan", "tte": "utf8"}
            self.Data = {"status": 2, "text": str(base64.b64encode(self.Text.encode('utf-8')), "UTF8")}

        # 生成url
        def create_url(self):
            url = 'wss://tts-api.xfyun.cn/v2/tts'
            # 生成RFC1123格式的时间戳
            now = datetime.now()
            date = format_date_time(mktime(now.timetuple()))

            # 拼接字符串
            signature_origin = "host: " + "ws-api.xfyun.cn" + "\n"
            signature_origin += "date: " + date + "\n"
            signature_origin += "GET " + "/v2/tts " + "HTTP/1.1"
            # 进行hmac-sha256进行加密
            signature_sha = hmac.new(self.APISecret.encode('utf-8'), signature_origin.encode('utf-8'),
                                     digestmod=hashlib.sha256).digest()
            signature_sha = base64.b64encode(signature_sha).decode(encoding='utf-8')

            authorization_origin = "api_key=\"%s\", algorithm=\"%s\", headers=\"%s\", signature=\"%s\"" % (
                self.APIKey, "hmac-sha256", "host date request-line", signature_sha)
            authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode(encoding='utf-8')
            # 将请求的鉴权参数组合为字典
            v = {
                "authorization": authorization,
                "date": date,
                "host": "ws-api.xfyun.cn"
            }
            # 拼接鉴权参数，生成url
            url = url + '?' + urlencode(v)
            return url

    @staticmethod
    def synthesize(text: str) -> bytes:
        def on_open(ws):
            def run(*args):
                if wsParam is not None:
                    d = {"common": wsParam.CommonArgs,
                         "business": wsParam.BusinessArgs,
                         "data": wsParam.Data,
                         }
                    d = json.dumps(d)
                    ws.send(d)
                    if os.path.exists('./demo.pcm'):
                        os.remove('./demo.pcm')

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
                    with open('./demo.pcm', 'ab') as f:
                        f.write(audio)
            except Exception as e:
                print("receive msg, but parse exception:", e)

        def on_error(ws, error):
            ...

        def on_close(ws):
            ...
            print("### closed ###")

        wsParam = TTSClient.WsParam(APPID=TTS_client.APPID, APISecret=TTS_client.APISecret,
                                   APIKey=TTS_client.APIKey,
                                   Text=text)
        websocket.enableTrace(False)
        wsUrl = wsParam.create_url()
        ws = websocket.WebSocketApp(wsUrl, on_message=on_message, on_error=on_error, on_close=on_close)
        ws.on_open = on_open
        ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})
        with open('demo.pcm', 'rb') as f:
            data = f.read()
        audio = AudioSegment(data=data, sample_width=2, frame_rate=16000, channels=1)
        tmp_file = "tmp_audio.wav"
        audio.export(tmp_file, format="wav")
        play(audio)   

if __name__ == "__main__":
    api_manager = APIClientXF(
        APPID="**",
        APISecret="**",
        APIKey="**",
    )

    TTS_client = TTSClient(api_manager)
    txt="你说的对，但是《原神》是由米哈游自主研发的一款全新开放世界冒险游戏。游戏发生在一个被称作「提瓦特」的幻想世界，在这里，被神选中的人将被授予「神之眼」，导引元素之力。你将扮演一位名为「旅行者」的神秘角色，在自由的旅行中邂逅性格各异、能力独特的同伴们，和他们一起击败强敌，找回失散的亲人——同时，逐步发掘「原神」的真相。";
    TTS_client.synthesize(txt)
