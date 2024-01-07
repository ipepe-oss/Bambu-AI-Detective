from datetime import datetime, timedelta
from pathlib import Path

import paho.mqtt.client as mqtt
import json, ssl, os, time

BAMBU_IP_ADDRESS = os.getenv("ALL_PRINTER_ADDRESS")
ACCESS_CODE = os.getenv("ALL_PRINTER_ACCESS_CODE")
SERIAL = os.getenv("ALL_PRINTER_SERIAL_NUMBER")


TURN_ON_LIGHT_WHEN_NOT_IDLE = os.getenv("CONTROLLER_TURN_ON_LIGHT_WHEN_NOT_IDLE", "true").lower() == "true"
TURN_OFF_LIGHT_WHEN_IDLE_AFTER_MINUTES = int(os.getenv("CONTROLLER_TURN_OFF_LIGHT_WHEN_IDLE_AFTER_MINUTES", "15"))
PAUSE_PRINTING_WHEN_AI_DETECTED_SCORE_ABOVE = float(os.getenv("CONTROLLER_PAUSE_PRINTING_WHEN_AI_DETECTED_SCORE_ABOVE", "0.3"))
REFRESH_RATE = int(os.getenv("ALL_REFRESH_RATE", "30"))


CMD_CHAMBER_LIGHT_ON = json.dumps({
    "system": {"sequence_id": "0", "command": "ledctrl", "led_node": "chamber_light", "led_mode": "on",
               "led_on_time": 500, "led_off_time": 500, "loop_times": 0, "interval_time": 0}})
CMD_CHAMBER_LIGHT_OFF = json.dumps({
    "system": {"sequence_id": "0", "command": "ledctrl", "led_node": "chamber_light", "led_mode": "off",
               "led_on_time": 500, "led_off_time": 500, "loop_times": 0, "interval_time": 0}})

CMD_PAUSE = json.dumps({"print": {"sequence_id": "0", "command": "pause"}})
CMD_RESUME = json.dumps({"print": {"sequence_id": "0", "command": "resume"}})
CMD_STOP = json.dumps({"print": {"sequence_id": "0", "command": "stop"}})

CMD_PUSH_ALL = json.dumps({"pushing": {"sequence_id": "0", "command": "pushall"}})

CMD_START_PUSH = json.dumps({ "pushing": {"sequence_id": "0", "command": "start"}})

def deep_merge(source, destination):
    for key, value in source.items():
        if isinstance(value, dict):
            node = destination.setdefault(key, {})
            merge(value, node)
        else:
            destination[key] = value
    return destination

def data_storage_read(file_key):
    file_path = Path(f"./data_storage/{file_key}")
    if file_path.exists():
        with file_path.open("r") as f:
            result = f.read()
            print(f"Reading {file_key} with {result}")
            return result
    else:
        return None

def data_storage_write(file_key, file_content):
    file_content = str(file_content)
    file_path = Path(f"./data_storage/{file_key}")
    if file_content is None:
        if file_path.exists():
            file_path.unlink()
        return
    else:
        if data_storage_read(file_key) == file_content:
            return
        print(f"Writing {file_key} with {file_content}")
        with file_path.open("w") as f:
            f.write(file_content)


def on_connect(client, userdata, flags, result_code):
    if result_code == 0:
        client.subscribe(f"device/{SERIAL}/report")
        client.publish(f"device/{SERIAL}/request", CMD_START_PUSH)
        client.publish(f"device/{SERIAL}/request", CMD_PUSH_ALL)

def on_message(client, userdata, msg):
    print(msg.payload)
    doc = json.loads(msg.payload)
    # example doc: {"print":{"upload":{"status":"idle","progress":0,"message":""},"nozzle_temper":18.9375,"nozzle_target_temper":0,"bed_temper":15.6875,"bed_target_temper":0,"chamber_temper":5,"mc_print_stage":"1","heatbreak_fan_speed":"0","cooling_fan_speed":"0","big_fan1_speed":"0","big_fan2_speed":"0","mc_percent":100,"mc_remaining_time":0,"ams_status":0,"ams_rfid_status":0,"hw_switch_state":0,"spd_mag":100,"spd_lvl":2,"print_error":0,"lifecycle":"product","wifi_signal":"-43dBm","gcode_state":"IDLE","gcode_file_prepare_percent":"0","queue_number":0,"queue_total":0,"queue_est":0,"queue_sts":0,"project_id":"0","profile_id":"0","task_id":"0","subtask_id":"0","subtask_name":"","gcode_file":"","stg":[],"stg_cur":255,"print_type":"idle","home_flag":2113800,"mc_print_line_number":"447767","mc_print_sub_stage":0,"sdcard":true,"force_upgrade":false,"mess_production_state":"active","layer_num":492,"total_layer_num":0,"s_obj":[],"filam_bak":[],"fan_gear":0,"nozzle_diameter":"0.4","nozzle_type":"stainless_steel","upgrade_state":{"sequence_id":0,"progress":"100","status":"UPGRADE_SUCCESS","consistency_request":false,"dis_state":3,"err_code":0,"force_upgrade":false,"message":"0%, 0B/s","module":"ota","new_version_state":2,"cur_state_code":0,"new_ver_list":[]},"hms":[],"online":{"ahb":false,"rfid":false,"version":31644318},"ams":{"ams":[{"id":"0","humidity":"5","temp":"0.0","tray":[{"id":"0","remain":-1,"k":0.019999999552965164,"n":1,"tag_uid":"0000000000000000","tray_id_name":"","tray_info_idx":"GFL96","tray_type":"PLA","tray_sub_brands":"","tray_color":"F4D976FF","tray_weight":"0","tray_diameter":"0.00","tray_temp":"0","tray_time":"0","bed_temp_type":"0","bed_temp":"0","nozzle_temp_max":"240","nozzle_temp_min":"190","xcam_info":"000000000000000000000000","tray_uuid":"00000000000000000000000000000000"},{"id":"1","remain":-1,"k":0.019999999552965164,"n":1,"tag_uid":"E24BD67400000100","tray_id_name":"A00-D0","tray_info_idx":"GFA00","tray_type":"PLA","tray_sub_brands":"PLA Basic","tray_color":"8E9089FF","tray_weight":"1000","tray_diameter":"1.75","tray_temp":"55","tray_time":"8","bed_temp_type":"1","bed_temp":"35","nozzle_temp_max":"230","nozzle_temp_min":"190","xcam_info":"D007D007E803E8039A99193F","tray_uuid":"632C0CAADF93482786CA32CBD3C52490"},{"id":"2","remain":-1,"k":0.019999999552965164,"n":1,"tag_uid":"0000000000000000","tray_id_name":"","tray_info_idx":"GFL95","tray_type":"PLA","tray_sub_brands":"","tray_color":"FC2B2DFE","tray_weight":"0","tray_diameter":"0.00","tray_temp":"0","tray_time":"0","bed_temp_type":"0","bed_temp":"0","nozzle_temp_max":"240","nozzle_temp_min":"190","xcam_info":"000000000000000000000000","tray_uuid":"00000000000000000000000000000000"},{"id":"3","remain":-1,"k":0.019999999552965164,"n":1,"tag_uid":"0000000000000000","tray_id_name":"","tray_info_idx":"GFB98","tray_type":"ASA","tray_sub_brands":"","tray_color":"004B7CFF","tray_weight":"0","tray_diameter":"0.00","tray_temp":"0","tray_time":"0","bed_temp_type":"0","bed_temp":"0","nozzle_temp_max":"280","nozzle_temp_min":"240","xcam_info":"000000000000000000000000","tray_uuid":"00000000000000000000000000000000"}]}],"ams_exist_bits":"1","tray_exist_bits":"f","tray_is_bbl_bits":"f","tray_tar":"255","tray_now":"255","tray_pre":"255","tray_read_done_bits":"f","tray_reading_bits":"0","version":7,"insert_flag":true,"power_on_flag":false},"ipcam":{"ipcam_dev":"1","ipcam_record":"enable","timelapse":"disable","resolution":"","mode_bits":3},"vt_tray":{"id":"254","tag_uid":"0000000000000000","tray_id_name":"","tray_info_idx":"","tray_type":"","tray_sub_brands":"","tray_color":"00000000","tray_weight":"0","tray_diameter":"0.00","tray_temp":"0","tray_time":"0","bed_temp_type":"0","bed_temp":"0","nozzle_temp_max":"0","nozzle_temp_min":"0","xcam_info":"000000000000000000000000","tray_uuid":"00000000000000000000000000000000","remain":0,"k":0.019999999552965164,"n":1},"lights_report":[{"node":"chamber_light","mode":"off"}],"command":"push_status","msg":0,"sequence_id":"30966"}}
    current_status = data_storage_read("current_status") or "idle"

    if "print" in doc:
        if "gcode_state" in doc["print"]:
            if doc["print"]["gcode_state"] == "PRINTING" or doc["print"]["gcode_state"] == "RUNNING":
                data_storage_write("current_status", "printing")
            elif doc["print"]["gcode_state"] == "PAUSED":
                data_storage_write("current_status", "paused")
            elif doc["print"]["gcode_state"] == "STOPPED":
                data_storage_write("current_status", "stopped")
            else:
                data_storage_write("current_status", "idle")
        if "lights_report" in doc:
            if "chamber_light" in doc["lights_report"]:
                if doc["lights_report"]["chamber_light"]["mode"] == "on":
                    data_storage_write("chamber_light", "on")
                else:
                    data_storage_write("chamber_light", "off")


def get_ai_max_score():
    if os.path.exists("/app/web/last_score_data.json"):
        with open("/app/web/last_score_data.json", "r") as f:
            score_data = json.load(f)
            if "timestamp" in score_data:
                if datetime.now() - datetime.fromtimestamp(float(score_data["timestamp"])) > timedelta(minutes=REFRESH_RATE):
                    return None
            if "max_score" in score_data:
                max_score = float(score_data["max_score"])
                return max_score

def my_loop():
    current_status = data_storage_read("current_status")
    chamber_light = data_storage_read("chamber_light")
    ai_max_score = get_ai_max_score()

    if PAUSE_PRINTING_WHEN_AI_DETECTED_SCORE_ABOVE > 0 and PAUSE_PRINTING_WHEN_AI_DETECTED_SCORE_ABOVE <= 1:
        if current_status == "printing":
            data_storage_write("last_printing_timestamp", datetime.now().timestamp())
            if ai_max_score is not None:
                if float(ai_max_score) > 0.4:
                    client.publish(f"device/{SERIAL}/request", CMD_PAUSE)
                    data_storage_write("current_status", "paused")
                    data_storage_write("ai_max_score", None)
    if TURN_ON_LIGHT_WHEN_NOT_IDLE:
        if current_status != "idle":
            if chamber_light == "off" or chamber_light is None:
                client.publish(f"device/{SERIAL}/request", CMD_CHAMBER_LIGHT_ON)
                data_storage_write("chamber_light", "on")
    if TURN_OFF_LIGHT_WHEN_IDLE_AFTER_MINUTES > 1:
        if chamber_light == "on" and current_status == "idle":
            if data_storage_read("last_printing_timestamp") is not None:
                if datetime.now() - datetime.fromtimestamp(float(data_storage_read("last_printing_timestamp"))) > timedelta(minutes=TURN_OFF_LIGHT_WHEN_IDLE_AFTER_MINUTES):
                    data_storage_write("last_printing_timestamp", None)
                    client.publish(f"device/{SERIAL}/request", CMD_CHAMBER_LIGHT_OFF)
            else:
               data_storage_write("last_printing_timestamp", datetime.now().timestamp())


client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.check_hostname = False
client.username_pw_set('bblp', ACCESS_CODE)
client.tls_set(tls_version=ssl.PROTOCOL_TLS, cert_reqs=ssl.CERT_NONE)
client.tls_insecure_set(True)
client.connect(BAMBU_IP_ADDRESS, 8883, 60)

last_execution_timestamp = datetime.now().timestamp()

while True:
    if datetime.now().timestamp() - last_execution_timestamp > REFRESH_RATE:
        last_execution_timestamp = datetime.now().timestamp()
        my_loop()
    client.loop()
