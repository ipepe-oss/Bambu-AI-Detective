FROM gcc:12 AS builder
WORKDIR /build
COPY streamer/src/BambuP1Streamer.cpp /build/BambuP1Streamer.cpp
COPY streamer/src/BambuTunnel.h /build/BambuTunnel.h
RUN gcc BambuP1Streamer.cpp -o BambuP1Streamer

RUN wget https://public-cdn.bambulab.com/upgrade/studio/plugins/01.04.00.15/linux_01.04.00.15.zip
RUN unzip linux_01.04.00.15.zip

RUN wget https://github.com/AlexxIT/go2rtc/releases/download/v1.6.2/go2rtc_linux_amd64
RUN chmod a+x go2rtc_linux_amd64

RUN wget https://tsd-pub-static.s3.amazonaws.com/ml-models/model-weights-5a6b1be1fa.onnx

FROM python:3.9-slim-buster

WORKDIR /app

RUN apt-get update && apt-get install -y ffmpeg

COPY . .

RUN cd /app/aidetector && pip install onnxruntime pillow numpy honcho

COPY --from=builder /build/model-weights-5a6b1be1fa.onnx /app/aidetector/model-weights-5a6b1be1fa.onnx
COPY --from=builder /build/BambuP1Streamer /app/streamer/BambuP1Streamer
COPY --from=builder /build/go2rtc_linux_amd64 /app/streamer/go2rtc_linux_amd64
COPY --from=builder /build/libBambuSource.so /app/streamer/libBambuSource.so
COPY --from=builder /build/libbambu_networking.so /app/streamer/libbambu_networking.so
RUN cd /app/streamer/ && chmod a+x go2rtc_linux_amd64 libBambuSource.so BambuP1Streamer
COPY streamer/go2rtc.yaml /app/streamer/go2rtc.yaml

EXPOSE 1984

CMD [ "honcho", "start" ]