# -*- coding: utf-8 -*-

"""
讯飞语音转文字客户端类
"""

from base64 import b64encode
import logging
import websocket  # websocket-client
import json
import pyaudio
import time
import ssl
from threading import Thread
from .APIClinetXF import APIClientXF


class STTClient(Thread):
    # fmt: off
    HOST = "iat-api.xfyun.cn"
    REQUEST_URL = "wss://" + HOST + "/v2/iat"

    # 帧标识
    STATUS_FIRST_FRAME = 0  # 第一帧的标识
    STATUS_CONTINUE_FRAME = 1  # 中间帧标识
    STATUS_LAST_FRAME = 2  # 最后一帧的标识
    
    # 录音参数
    CHUNK = 520   # 定义数据流块
    RATE = 16000  # 16000采样频率

    # 业务参数
    # @see https://www.xfyun.cn/doc/asr/voicedictation/API.html#业务参数
    business_params = {
        "language": "zh_cn",    # 语种
        "domain": "iat",        # 应用领域
        "accent": "mandarin",   # 方言，当前仅在language为中文时，支持方言选择
        "vad_eos": 10000,       # 用于设置端点检测的静默时间，单位是毫秒，即静默多长时间后引擎认为音频结束
        # "dwa": "wpgs",        # 动态修正（仅中文普通话支持），设置为wpgs开启流式结果返回功能
        # "pd": "game",         # 领域个性化参数（仅中文支持）
        "ptt": 1,               # 是否开启标点符号添加（仅中文支持）
        "rlang": "zh-cn",       # 字体（仅中文支持），设置为zh-cn表示简体中文，zh-hk为繁体中文
        "vinfo": 1,             # 返回子句结果对应的起始和结束的端点帧偏移值。端点帧偏移值表示从音频开头起已过去的帧长度
        "nunum": 1,             # 将返回结果的数字格式规则为阿拉伯数字格式（中文普通话和日语支持）
        # "speex_size": 70,       # speex音频帧长，仅在speex音频时使用
        # "nbest": 3,             # 取值范围[1,5]，通过设置此参数，获取在发音相似时的句子多侯选结果
        # "wbest": 5,             # 取值范围[1,5]，通过设置此参数，获取在发音相似时的词语多侯选结果。
    }
    # fmt: on

    def __init__(self, API_manager: APIClientXF) -> None:
        super().__init__(daemon=True)

        self.message = ""

        # 讯飞API设置
        self.API_manager: APIClientXF = API_manager

        self.ws_app = websocket.WebSocketApp(
            self.API_manager.get_url_stt(),
            on_message=self.on_message,
            on_open=self.on_open,
            on_error=self.on_error,
            on_close=self.on_close,
        )

        # 录音设备设置
        self.status = self.STATUS_FIRST_FRAME  # 音频的状态信息，标识音频是第一帧，还是中间帧、最后一帧
        # 实例化pyaudio对象
        self.p = pyaudio.PyAudio()  # 录音
        # 创建音频流
        # 使用这个对象去打开声卡，设置采样深度、通道数、采样率、输入和采样点缓存数量
        self.stream = self.p.open(
            format=pyaudio.paInt16,  # 音频流wav格式
            channels=1,  # 单声道
            rate=self.RATE,  # 采样率16000
            frames_per_buffer=self.CHUNK,  # 数据流块
            input=True,
            start=False,
        )

    def listen(self):
        """循环监听麦克风并进行实时语音识别"""
        self.stream.start_stream()
        print("\n-------------- Start Recording --------------")

        while True:
            # 读出声卡缓冲区的音频数据
            buf = self.stream.read(self.CHUNK)
            if not buf:
                self.status = STTClient.STATUS_LAST_FRAME
            # 第一帧
            if self.status == STTClient.STATUS_FIRST_FRAME:
                d = {
                    "common": {"app_id": "2c31e4f9"},
                    "business": STTClient.business_params,
                    "data": {
                        "status": 0,
                        "format": "audio/L16;rate=16000",
                        "audio": str(b64encode(buf), "utf-8"),
                        "encoding": "raw",
                    },
                }
                d = json.dumps(d)
                self.ws_app.send(d)
                self.status = STTClient.STATUS_CONTINUE_FRAME
            # 中间帧处理
            elif self.status == STTClient.STATUS_CONTINUE_FRAME:
                d = {
                    "data": {
                        "status": 1,
                        "format": "audio/L16;rate=16000",
                        "audio": str(b64encode(buf), "utf-8"),
                        "encoding": "raw",
                    }
                }
                self.ws_app.send(json.dumps(d))

            # 最后一帧处理
            elif self.status == STTClient.STATUS_LAST_FRAME:
                d = {
                    "data": {
                        "status": 2,
                        "format": "audio/L16;rate=16000",
                        "audio": str(b64encode(buf), "utf-8"),
                        "encoding": "raw",
                    }
                }
                self.ws_app.send(json.dumps(d))
                time.sleep(1)
                break
        self.stream.close()  # 终止流
        self.p.terminate()  # 终止pyaudio会话
        self.ws_app.close()

    def on_open(self, _):
        self.listener_thread = Thread(target=self.listen, daemon=True)
        self.listener_thread.start()

    @staticmethod
    def on_error(_: websocket.WebSocketApp, error) -> None:
        logging.error(error)

    def on_close(self, *_) -> None:
        logging.info("Websocket Closed")

    def on_message(self, _: websocket.WebSocketApp, message) -> None:
        """接收到服务器返回的消息"""
        try:
            code = json.loads(message)["code"]
            sid = json.loads(message)["sid"]
            if code != 0:
                errMsg = json.loads(message)["message"]
                print("sid:%s call error:%s code is:%s" % (sid, errMsg, code))

            else:
                data = json.loads(message)["data"]["result"]["ws"]
                result = ""
                for i in data:
                    for w in i["cw"]:
                        result += w["w"]
                self.message += result
                print(result, end="")
        except Exception as e:
            logging.exception("receive msg, but parse exception:", e)

    def run(self) -> None:
        self.ws_app.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE}, ping_timeout=2)

    def stop(self) -> None:
        self.status = STTClient.STATUS_LAST_FRAME
