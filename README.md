# Bambu P1 Camera Streamer + AI Spaghetti Detective
This is a dockerized version of the Bambu P1 Camera Streamer + AI to detect spaghetti.

This is based on work of:
 * https://github.com/antirez/failed-3d-prints-bot - basis for the AI detection code
 * https://github.com/hisptoot/BambuP1PSource2Raw - basis for the camera preview download
 * https://bjh21.me.uk/bedstead/ - font for image overlay
 * https://github.com/AlexxIT/go2rtc - streaming in the browser
 * https://github.com/TheSpaghettiDetective/obico-server/ - neural network model
 * https://github.com/MikeSiekkinen/BambuLabOBSOverlay - basis for MQTT integration

## License
This project is a derivative from https://github.com/hisptoot/BambuSource2Raw so it uses same license as the original project. See [LICENSE](LICENSE) for more details.

## RUN - Getting started
1. Clone this repo
2. Plug in the right values for the environment variables into `.env`
3. Run `docker-compose up -d --build`
4. Visit http://localhost:8080 to see the web dashboard with current ai detection status.

### Example `.env`
All environment variables are prefixed with their respective service name. If variable is prefixed with `ALL_` it is used by all services.
```
ALL_REFRESH_RATE=10
ALL_PRINTER_ADDRESS=192.168.1.111
ALL_PRINTER_ACCESS_CODE=12345678
ALL_PRINTER_SERIAL_NUMBER=01P00A0A0000000
CONTROLLER_TURN_ON_LIGHT_WHEN_NOT_IDLE=true
CONTROLLER_TURN_OFF_LIGHT_WHEN_IDLE_AFTER_MINUTES=15
CONTROLLER_PAUSE_PRINTING_WHEN_AI_DETECTED_SCORE_ABOVE=0.3
NOTIFIER_MAX_SCORE_10_NOTIFICATION_ADDRESS=https://hooks.slack.com/services/A/B/C
NOTIFIER_MAX_SCORE_30_NOTIFICATION_ADDRESS=https://hooks.slack.com/services/A/B/C
NOTIFIER_NOTIFICATION_RESET_PERIOD_MINUTES=60
```

### docker-compose.yml

```yaml
version: '3.7'
services:
  app:
    build: ./
    restart: unless-stopped
    env_file:
      - .env
    ports:
      - "1984:1984"
      - "8080:8080"
    logging:
      driver: json-file
      options:
        max-size: 50m
```

## Web Dashboard

Visit http://localhost:8080 to see the web dashboard with current ai detection status.
![Web Dashboard](docs/images/web-dashboard.png)

## Changelog

| Date       | Version     | Description                                                                             |
|------------|-------------|-----------------------------------------------------------------------------------------|
| 2024-01-06 | v1.0.0-beta | Initial version                                                                         |
| 2024-01-06 | v1.0.1-beta | Removed dependency on go2rtc and Bambulab prioprietary libraries                        |
| 2024-01-06 | v2.0.0-beta | Added support for pausing the print using MQTT and cropping the image for AI processing |


## Upcoming features (in the importance order)
1. [ ] Add support for multiple printers (for print farmers)
2. [ ] Add printer dashboard inspired by https://www.wolfwithsword.com/bambulab-home-assistant-dashboard/

## Architecture
1. As a basis we are using python image. 
2. In this python image container we are running https://github.com/nickstenning/honcho (python port of foreman) to run multiple processes in one container.
3. The first process is the streamer. It is based on https://github.com/hisptoot/BambuP1PSource2Raw
4. The second process is the web dashboard. It is a simple index.html page that pulls json and image from AI detector
5. The third process is the AI detector. It is based on https://github.com/antirez/failed-3d-prints-bot
6. The fourth process is the notifier. It is based on https://github.com/caronc/apprise
7. The fifth process is the controller. It is responsible for controlling the printer based on the AI detection score. It is also responsible for turning on/off the light and pausing the print when the AI detection score is above the threshold.
8. Everything is dockerized and can be run with docker-compose

## Notifier
Notifier is based on https://github.com/caronc/apprise and sends notifications to various services. Notifier service is reading dynamically from environment variables and can be configured to send notifications to multiple services. It will look for variables that fit this pattern: `NOTIFIER_MAX_SCORE_*_NOTIFICATION_ADDRESS` where `*` is the max score from `aidetector` that will trigger the notification. For example `NOTIFIER_MAX_SCORE_10_NOTIFICATION_ADDRESS` will send notification to the address specified in the variable when the max score is 10 percent (0.1 float). For environment value insert apprise address that is supported. [Supported addresses list is available here](https://github.com/caronc/apprise?tab=readme-ov-file#supported-notifications)


## Streamer
Only tested on a P1S. I would expect it to work for a p1p camera. I would not expect this to work on an X1/X1C - the codecs are different and I don't believe that local network streaming is enabled.


