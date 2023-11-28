import argparse
from sumbody.services import TextSummary

def parse_arguments():
    parser = argparse.ArgumentParser(description='A unit test for generating a summary for a given text.')
    parser.add_argument('text', type=str, help='The text to summarize.')
    parser.add_argument('api_key', type=str, help='The API key for the TextSummary service.')
    parser.add_argument('--chunk_size', type=int, default=1000, help='The chunk size for the TextSummary service. Default is 1000.')
    parser.add_argument('--summary_max_len', type=int, default=1000, help='The maximum length of the summary. Default is 1000.')
    return parser.parse_args()

def summay_main(text: str, api_key, chunk_size=1000, summary_max_len=1000):
    tsum = TextSummary(chunk_size, summary_max_len, api_key=api_key)
    summary = tsum.forward(text)
    print("总结后文本长度为：" + str(len(summary)))
    print("总结内容:" + summary)

if __name__ == "__main__":
    args = parse_arguments()
    summay_main(args.text, args.api_key, args.chunk_size, args.summary_max_len)
