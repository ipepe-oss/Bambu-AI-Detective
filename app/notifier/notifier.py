import apprise, os, json, time

print("Starting...")

notification_addresses = {}

print("Notification addresses:")
for key, value in os.environ.items():
    if key.startswith("NOTIFIER_MAX_SCORE_") and key.endswith("_NOTIFICATION_ADDRESS"):
        integer_part = key[len("NOTIFIER_MAX_SCORE_"):-len("_NOTIFICATION_ADDRESS")]
        if integer_part.isdigit() and 1 <= int(integer_part) <= 100:
            print(f"{key}: {value}")
            notification_addresses[integer_part] = apprise.Apprise()
            notification_addresses[integer_part].add(value)

print("Notification addresses loaded.")

refresh_rate = int(os.getenv("ALL_REFRESH_RATE", "30"))
reset_period_minutes = int(os.getenv("NOTIFIER_NOTIFICATION_RESET_PERIOD_MINUTES", "60"))

while True:
    print("Notifier loop checking for new data...")
    if os.path.exists("/app/web/last_score_data.json"):
        print("Found last_score_data.json")
        with open("/app/web/last_score_data.json", "r") as f:
            score_data = json.load(f)
            max_score = float(score_data["max_score"])

            print("Max score:", max_score)

            for notification_address_threshold in notification_addresses.keys():
                print(f"Checking notification_address_threshold {notification_address_threshold}")
                print(f"Max score: {max_score}")
                if max_score*100 >= int(notification_address_threshold):
                    if not os.path.exists(f"/app/notifier/last_notification_{notification_address_threshold}_timestamp.txt"):
                        last_notification_timestamp = 0
                    else:
                        last_notification_timestamp = os.path.getmtime(f"/app/notifier/last_notification_{notification_address_threshold}_timestamp.txt")
                    print(f"Last notification timestamp: {last_notification_timestamp}")
                    if time.time() - last_notification_timestamp > reset_period_minutes*60:
                        print(f"Max score {max_score} is greater than or equal to threshold {notification_address_threshold}")
                        notification_addresses[notification_address_threshold].notify(
                            title=f"Bambulab+AI Detector: Max score: {max_score} is greater than or equal to threshold {notification_address_threshold}",
                            body=f"Bambulab+AI Detector: Max score: {max_score} is greater than or equal to threshold {notification_address_threshold}",
                            attach="/app/web/last_image.png"
                        )
                        if not os.path.exists("/app/web/last_image.png"):
                            print("Warning: last_image.png not found.")
                        with open(f"/app/notifier/last_notification_{notification_address_threshold}_timestamp.txt", "w") as f:
                            f.write(str(time.time()))
                    else:
                        print(f"Max score {max_score} is greater than or equal to threshold {notification_address_threshold}, but the reset period has not elapsed.")
                else:
                    print(f"Max score {max_score} is less than threshold {notification_address_threshold}")
    else:
        print("last_score_data.json not found.")
    time.sleep(refresh_rate)