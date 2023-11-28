from sumbody.services import TextSummary


def summay_main(text: str, chunk_size=1000, summary_max_len=1000):
    # ### 读取测试文本并预处理
    # with open("珠峰班宣讲会会议纪要.txt","r",encoding='UTF-8') as f:
    #     text = f.readlines()
    # final_text = []
    # for sentence in text:
    #     final_text.append(re.sub(r'\[[^\]]*\]', '', sentence.strip()))
    # final_text = "".join(final_text)
    # ###
    tsum = TextSummary(chunk_size, summary_max_len, api_key="")
    summary = tsum.forward(text)
    print("总结后文本长度为：" + str(len(summary)))
    print("总结内容:" + summary)


summay_main(text="")
