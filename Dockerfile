FROM python:3.9-slim-buster

RUN apt-get update && apt-get install -y wget
RUN cd /tmp && wget https://tsd-pub-static.s3.amazonaws.com/ml-models/model-weights-5a6b1be1fa.onnx

WORKDIR /app
COPY app/requirements.txt .
RUN python3 -m pip install -r requirements.txt

COPY app .
RUN mv /tmp/model-weights-5a6b1be1fa.onnx  /app/aidetector/model-weights-5a6b1be1fa.onnx

CMD [ "honcho", "start" ]