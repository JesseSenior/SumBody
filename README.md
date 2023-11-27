# SumBody

An intelligent meeting summary assistant based on ChatGPT.

## Setup

### Local development

To install the application locally, you need to have [poetry](python-poetry.org) installed. To install the dependencies, run the following command:

```bash
poetry install
```

Before running the application, remember to open [Nvidia Omniverse Audio2Face](https://developer.nvidia.com/omniverse-audio2face)
and to activate the streaming gRPC server.

In addition, you have to have a Google Cloud account and a Google Cloud project with the following APIs enabled:

* Google Speech-to-Text API
* Google Text-to-Speech API

Then, you have to create a service account and download the JSON key file.

You also have to have a valid OpenAI API key.

Finally, you have to set the following environment variables:

```bash
GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/service-account.json"
OPENAI_KEY="your-openai-key"
OPENAI_MODEL="text-davinci-003" # or any other model you want to use
```

Then, you're ready to run the application:

```bash
GRPC_SERVER="localhost:50051"
OPENAI_INSTRUCTION="answer to this sentence like you are chatting with a friend"

poetry run python -m sumbody \
    --grpc-server=$GRPC_SERVER \
    --openai-instruction=$OPENAI_INSTRUCTION
```
