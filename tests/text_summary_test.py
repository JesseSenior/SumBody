import argparse
from sumbody.services import TextSummary


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="A unit test for generating a summary for a given text."
    )
    parser.add_argument("--text", type=str, help="The text to summarize.")
    parser.add_argument("--file", type=str, help="The file to read the text from.")
    parser.add_argument(
        "--api_key", type=str, help="The API key for the TextSummary service."
    )
    parser.add_argument("--api_base", type=str, help="The API key base url.")
    parser.add_argument(
        "--chunk_size",
        type=int,
        default=1000,
        help="The chunk size for the TextSummary service. Default is 1000.",
    )
    parser.add_argument(
        "--summary_max_len",
        type=int,
        default=1000,
        help="The maximum length of the summary. Default is 1000.",
    )
    return parser.parse_args()


def read_file(file_path):
    with open(file_path, "r", encoding="utf8") as file:
        return file.read()


def summay_main(text: str, api_key, api_base, chunk_size=1000, summary_max_len=1000):
    tsum = TextSummary(
        api_key=api_key,
        api_base=api_base,
        chunk_size=chunk_size,
        summary_max_len=summary_max_len,
    )
    summary = tsum.forward(text)
    print("总结后文本长度为：" + str(len(summary)))
    print("总结内容:" + summary)


if __name__ == "__main__":
    args = parse_arguments()
    if args.file:
        text = read_file(args.file)
    else:
        text = args.text
    summay_main(
        text, args.api_key, args.api_base, args.chunk_size, args.summary_max_len
    )
