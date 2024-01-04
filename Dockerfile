FROM gcc:12 AS builder
WORKDIR /work
COPY src/BambuP1Streamer.cpp /work/BambuP1Streamer.cpp
COPY src/BambuTunnel.h /work/BambuTunnel.h
RUN gcc BambuP1Streamer.cpp -o BambuP1Streamer

RUN wget https://public-cdn.bambulab.com/upgrade/studio/plugins/01.04.00.15/linux_01.04.00.15.zip
RUN unzip linux_01.04.00.15.zip

RUN wget https://github.com/AlexxIT/go2rtc/releases/download/v1.6.2/go2rtc_linux_amd64
RUN chmod a+x go2rtc_linux_amd64

FROM debian:12

RUN mkdir -p /app
WORKDIR /app
COPY --from=builder /work/BambuP1Streamer /app/BambuP1Streamer
COPY --from=builder /work/go2rtc_linux_amd64 /app/go2rtc_linux_amd64
COPY --from=builder /work/libBambuSource.so /app/libBambuSource.so
RUN chmod a+x go2rtc_linux_amd64 libBambuSource.so BambuP1Streamer
COPY go2rtc.yaml /app

CMD [ "./go2rtc_linux_amd64" ]
