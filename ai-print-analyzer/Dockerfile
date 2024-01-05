FROM python:3.9-slim-buster

WORKDIR /app

RUN apt-get update && apt-get install -y ffmpeg wget unzip
RUN wget https://tsd-pub-static.s3.amazonaws.com/ml-models/model-weights-5a6b1be1fa.onnx
RUN pip install onnxruntime pillow numpy

COPY . .

CMD [ "python", "run.py" ]