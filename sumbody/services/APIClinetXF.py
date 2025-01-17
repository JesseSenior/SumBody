# -*- coding: utf-8 -*-

import hmac
import hashlib
from base64 import b64encode
from datetime import datetime
from time import mktime
from urllib.parse import urlencode
from wsgiref.handlers import format_date_time


class APIClientXF:
    STT_HOST = "iat-api.xfyun.cn"
    TTS_HOST = "tts-api.xfyun.cn"

    def __init__(self, APPID: str, APISecret: str, APIKey: str) -> None:
        super().__init__()

        # 讯飞API设置
        self.APPID = APPID
        self.APISecret = APISecret
        self.APIKey = APIKey

    def construct_url(self, host: str, dir: str) -> str:
        # 生成RFC1123格式的时间戳
        time = format_date_time(mktime(datetime.now().timetuple()))
        signature_origin = f"host: {host}\ndate: {time}\nGET {dir} HTTP/1.1"
        # 进行hmac-sha256进行加密
        signature_sha = hmac.new(
            self.APISecret.encode("utf-8"),
            signature_origin.encode("utf-8"),
            digestmod=hashlib.sha256,
        ).digest()
        signature_sha = b64encode(signature_sha).decode(encoding="utf-8")
        authorization_origin = (
            'api_key="%s", algorithm="%s", headers="%s", signature="%s"'
            % (self.APIKey, "hmac-sha256", "host date request-line", signature_sha)
        )
        authorization = b64encode(authorization_origin.encode("utf-8")).decode("utf-8")
        # 鉴权方法：将请求的鉴权参数组合为字典
        # @see https://www.xfyun.cn/doc/asr/voicedictation/API.html#鉴权方法
        v = {"authorization": authorization, "date": time, "host": host}
        # 拼接鉴权参数，生成url
        url = f"wss://{host}{dir}?{urlencode(v)}"
        return url

    def get_url_stt(self) -> str:
        return self.construct_url(self.STT_HOST, "/v2/iat")

    def get_url_tts(self) -> str:
        return self.construct_url(self.TTS_HOST, "/v2/tts")
