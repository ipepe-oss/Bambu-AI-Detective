# frozen_string_literal: true

def capture_frame
  # 'ffmpeg -i "http://192.168.1.17:1984/api/stream.mjpeg?src=p1s" -vf "scale=416:416" -vframes:v 1 frame.png'
  system(
    'ffmpeg -i "http://streamer:1984/api/stream.mjpeg?src=p1s" -vf "scale=416:416" -vframes:v 1 frame.png'
  )
end
