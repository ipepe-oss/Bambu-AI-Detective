#!/usr/bin/python3

import struct
import sys
import os
import socket
import ssl

if len(sys.argv) != 4:
    print("Usage: {} <output_filename> <access_code> <hostname>".format(sys.argv[0]))
    sys.exit(1)

hostname, access_code, output_filename = sys.argv[1], sys.argv[2], sys.argv[3]

print("Connecting to {}:{}".format(hostname, 6000))

port = 6000

d = bytearray()
username = 'bblp'

d += struct.pack("IIL", 0x40, 0x3000, 0x0)
d += username.encode('ascii').ljust(32, b'\x00')
d += access_code.encode('ascii').ljust(32, b'\x00')

ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

jpeg_start = "ff d8 ff e0"
jpeg_end = "ff d9"

read_chunk_size = 1024

with socket.create_connection((hostname, port)) as sock:
    with ctx.wrap_socket(sock, server_hostname=hostname) as ssock:
        ssock.write(d)
        buf = bytearray()
        start = False
        while True:
            dr = ssock.recv(read_chunk_size)
            if not dr:
                break

            buf += dr

            if not start:
                i = buf.find(bytearray.fromhex(jpeg_start))
                if i >= 0:
                    start = True
                    buf = buf[i:]
                continue

            i = buf.find(bytearray.fromhex(jpeg_end))
            if i >= 0:
                img = buf[:i+len(jpeg_end)]
                with open(output_filename, 'wb') as f:
                    f.write(img)
                print("Image saved to", output_filename)
                break