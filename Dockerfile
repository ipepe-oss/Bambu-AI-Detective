FROM gcc:12 AS builder
WORKDIR /build
COPY src/BambuP1Streamer.cpp /build/BambuP1Streamer.cpp
COPY src/BambuTunnel.h /build/BambuTunnel.h
RUN gcc BambuP1Streamer.cpp -o BambuP1Streamer

RUN wget https://public-cdn.bambulab.com/upgrade/studio/plugins/01.04.00.15/linux_01.04.00.15.zip
RUN unzip linux_01.04.00.15.zip

RUN wget https://github.com/AlexxIT/go2rtc/releases/download/v1.6.2/go2rtc_linux_amd64
RUN chmod a+x go2rtc_linux_amd64

FROM debian:12

RUN mkdir -p /app
WORKDIR /app
COPY --from=builder /build/BambuP1Streamer /app/BambuP1Streamer
COPY --from=builder /build/go2rtc_linux_amd64 /app/go2rtc_linux_amd64
COPY --from=builder /build/libBambuSource.so /app/libBambuSource.so
COPY --from=builder /build/libbambu_networking.so /app/libbambu_networking.so
RUN chmod a+x go2rtc_linux_amd64 libBambuSource.so BambuP1Streamer
COPY go2rtc.yaml /app

CMD [ "./go2rtc_linux_amd64" ]
