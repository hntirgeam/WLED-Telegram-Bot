import os
import random

import requests
from colorthief import ColorThief

WLED_URL = f"http://{os.getenv('WLED_URL')}/json"
BRIGHTNESS_STEP = 25
MAX_BRIGHTNESS = 255
MIN_BRIGHTNESS = 0


def send_post_request(json_data):
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    res = requests.post(WLED_URL, json=json_data, headers=headers)

    if res:
        return True
    return False


def send_get_request(field1, field2=None):
    res = requests.get(WLED_URL)
    res_json: dict = res.json()

    if field2:
        return res_json.get(field1).get(field2)
    return res_json.get(field1)


def turn_off_on():
    json_data = {"on": "t"}
    status = send_post_request(json_data)
    return status


def change_brightness(where: bool):
    current_brightness = int(send_get_request("state", "bri"))
    if where:
        if current_brightness + BRIGHTNESS_STEP < MAX_BRIGHTNESS:
            new_br = current_brightness + BRIGHTNESS_STEP
            json_data = {"bri": new_br}
            status = send_post_request(json_data)
            if status:
                return f"Current brightness is {new_br}"
            return False

        else:
            json_data = {"bri": MAX_BRIGHTNESS}
            status = send_post_request(json_data)
            if status:
                return f"Current brightness is {MAX_BRIGHTNESS}"
            return False

    else:
        if current_brightness - BRIGHTNESS_STEP > MIN_BRIGHTNESS:
            new_br = current_brightness - BRIGHTNESS_STEP
            json_data = {"bri": new_br}
            status = send_post_request(json_data)
            if status:
                return f"Current brightness is {new_br}"
            return False

        else:
            json_data = {"bri": MIN_BRIGHTNESS}
            status = send_post_request(json_data)
            if status:
                return f"Current brightness is {MIN_BRIGHTNESS}"
            return False


def set_random_mode():
    modes = send_get_request("effects")
    random_mode = random.randint(0, len(modes))
    json_data = {"seg": [{"fx": random_mode}]}
    status = send_post_request(json_data)
    if status:
        return modes[random_mode]
    return status


def set_static_mode():
    json_data = {"seg": [{"fx": 0}]}
    status = send_post_request(json_data)
    if status:
        return "Static"
    return status


def get_dominant_color_from_image(image):
    color_thief = ColorThief(image)
    return color_thief.get_color(quality=5)


def get_color_name(r, g, b):
    url = f"https://www.thecolorapi.com/id?rgb={r},{g},{b}"
    try:
        response = requests.get(url).json()["name"]
        name_color = response["value"]
        hex_color = response["closest_named_hex"]
        return f"{name_color}: [{hex_color}](https://www.color-hex.com/color/{hex_color[1:]})"
    except:
        return "no idea..."


def set_dominant_color(color):
    r, g, b = color
    json_data = {"seg": [{"col": [[r, g, b]]}]}
    status = send_post_request(json_data)
    if status:
        return get_color_name(r, g, b)
    return status
