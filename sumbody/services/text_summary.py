import openai
import time


class TextSummary:
    def __init__(
        self,
        api_key,
        api_base=None,
        model="gpt-3.5-turbo",
        chunk_size=1024,
        summary_max_len=1024,
    ) -> None:
        """
        Args:
            api_key (str): OpenAI's api key
            api_base (str, optional): ObenAI's base url
            chunk_size (int, optional): 对gpt prompt的长度.
            summary_max_len (int, optional): 总结内容的最大长度（若超出则继续总结）.
        """
        self.chunk_size = chunk_size
        self.summary_max_len = summary_max_len
        self.model = model
        if api_base is not None:
            openai.api_base = api_base
        openai.api_key = api_key

    def split_text_into_chunks(self, text: list, chunk_size: int) -> list:
        chunks = [text[i : i + chunk_size] for i in range(0, len(text), chunk_size)]
        return chunks

    def get_completion(self, chunk, model="gpt-3.5-turbo") -> str:
        messages = [
            {"role": "system", "content": "You are a helpful text summarizer"},
            {
                "role": "user",
                "content": "请使用中文总结以下内容，总结的开头不要出现来源范围以及如：“这段内容”，“该内容”，“无法概括”等概括总述的词汇：",
            },
            {"role": "user", "content": chunk},
        ]
        response = openai.ChatCompletion.create(model=model, messages=messages)
        message: str = response.choices[0].message["content"]
        time.sleep(0.1)
        return message

    def forward(self, text) -> list:
        summary = []
        chunks = self.split_text_into_chunks(text, self.chunk_size)
        for chunk in chunks:
            summary.append(self.get_completion(chunk, self.model))
        result = "".join(summary)
        while len(result) > self.summary_max_len:
            result = self.forward(result)
        return result

    def question(self, que: str, text: list):
        chunks = self.split_text_into_chunks(text, self.chunk_size)
        answers = []
        for chunk in chunks:
            messages = [
                {
                    "role": "system",
                    "content": "You are a helpful text summarizer",
                },
                {
                    "role": "user",
                    "content": "请根据以下一段切片材料回答以下提问，切片内容将在下一次输入中给出\
                    回答的开头不要出现来源范围以及如：“这段内容”，“该内容”，“无法回答”等概括总述的词汇，\
                    请注意，提问的内容可能本切片未提供，对于此类提问，请回答：“该片段未回答相关信息”",
                },
                {"role": "user", "content": "切片内容为：%s" % chunk},
                {"role": "user", "content": "提问：%s" % que},
            ]
            response = openai.ChatCompletion.create(model=self.model, messages=messages)
            answers.append(response.choices[0].message["content"])
            time.sleep(0.1)
        answers = [i for i in answers if "该片段未" not in i]
        return answers
