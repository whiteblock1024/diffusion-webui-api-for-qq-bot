import json
import requests
import os
import base64
import urllib.request
import cv2
import numpy as np
import time

from sympy import N

# sd_webui url
sd_webui_port = 7860
sd_webui_url = f"http://127.0.0.1:{sd_webui_port}/api/predict/"

# path
self_path = os.path.dirname(os.path.realpath(__file__)).replace("\\", "/")
t2i_release_path = f'{self_path}/release/ai_draw_acg_t2i.png'
i2i_release_path = f'{self_path}/release/ai_draw_acg_i2i.png'
i2i_source_path = f'{self_path}/source/source_i2i.png'
i2i_mask_path = f'{self_path}/source/mask_i2i.png'

# mask process
def mask_process():

    mask = cv2.imread(i2i_mask_path)

    black_pixels = np.where(
        (mask[:, :, 0] == 0) &
        (mask[:, :, 1] == 0) &
        (mask[:, :, 2] == 0)
    )

    other_pixels = np.where(
        (mask[:, :, 0] != 0) |
        (mask[:, :, 1] != 0) |
        (mask[:, :, 2] != 0)
    )

    mask[black_pixels] = [255, 255, 255]
    mask[other_pixels] = [0, 0, 0]
    cv2.imwrite(i2i_mask_path, mask)

# text to image
def ai_draw_t2i(input_str: str = 'girl,masterpiece'):

    # default args
    steps = 40
    cfg = 7
    method = "Euler a"
    width = 512
    height = 512
    str_p = 256

    # args process
    args_list = input_str.split()
    if '--steps' in args_list:
        p = args_list.index('--steps')
        steps = int(args_list[p+1])
        if steps > 70:
            steps = 70
        if p < str_p:
            str_p = p
    if '--cfg' in args_list:
        p = args_list.index('--cfg')
        cfg = int(args_list[p+1])
        if p < str_p:
            str_p = p
    if '--method' in args_list:
        p = args_list.index('--method')
        method = "".join(args_list[p+1]).replace('-', ' ')
        if p < str_p:
            str_p = p
    if '--width' in args_list:
        p = args_list.index('--width')
        width = int(args_list[p+1])
        if p < str_p:
            str_p = p
    if '--height' in args_list:
        p = args_list.index('--height')
        height = int(args_list[p+1])
        if p < str_p:
            str_p = p

    if (str_p < 256):
        input_str = ""
        for i in range(0, str_p):
            input_str += " " + "".join(args_list[i])

    # http request
    data = json.dumps({
        "fn_index": 12,
        "data": [
            input_str,
            "",
            "None",
            "None",
            steps,
            method,
            False,
            False,
            1,
            1,
            cfg,
            -1,
            -1,
            0,
            0,
            0,
            False,
            height,
            width,
            False,
            False,
            0.7,
            "None",
            False,
            False,
            None,
            "",
            "Seed",
            "",
            "Steps",
            "",
            True,
            False,
            None
        ],
        "session_hash": "jwtz4inq1ol"
    })
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request(
        "POST", sd_webui_url, headers=headers, data=data)

    # base64 decode
    img_base64 = json.loads(response.text)["data"][0][0][22:]
    img_data = base64.b64decode(img_base64)

    # file io
    with open(t2i_release_path, 'wb') as f:
        f.write(img_data)


# image to image
def ai_draw_i2i(input_str: str = 'girl,masterpiece', source_url: str = 'None', mask_url: str = 'None', redraw: str = 0):

    # default args
    steps = 30
    cfg = 7
    method = "Euler a"
    width = 512
    height = 512
    str_p = 256
    mask =  None

    # args process
    args_list = input_str.split()
    if '--steps' in args_list:
        p = args_list.index('--steps')
        steps = int(args_list[p+1])
        if steps > 70:
            steps = 70
        if p < str_p:
            str_p = p
    if '--cfg' in args_list:
        p = args_list.index('--cfg')
        cfg = int(args_list[p+1])
        if p < str_p:
            str_p = p
    if '--method' in args_list:
        p = args_list.index('--method')
        method = "".join(args_list[p+1]).replace('-', ' ')
        if p < str_p:
            str_p = p
    if '--width' in args_list:
        p = args_list.index('--width')
        width = int(args_list[p+1])
        if p < str_p:
            str_p = p
    if '--height' in args_list:
        p = args_list.index('--height')
        height = int(args_list[p+1])
        if p < str_p:
            str_p = p

    if (str_p < 256):
        input_str = ""
        for i in range(0, str_p):
            input_str += " " + "".join(args_list[i])

    # download source image
    urllib.request.urlretrieve(source_url, filename=i2i_source_path)

    # base64 encode
    with open(i2i_source_path, 'rb') as f:
        source_img_data = f.read()
    source_img_base64 = "data:image/png;base64," + \
        str(base64.b64encode(source_img_data), "utf-8")

    # mask process
    if redraw:
        urllib.request.urlretrieve(mask_url, filename=i2i_mask_path)

        mask_process()

        with open(i2i_mask_path, 'rb') as f:
            mask_img_data = f.read()
        mask_img_base64 = "data:image/png;base64," + \
            str(base64.b64encode(mask_img_data), "utf-8")

        mask = {
            "image": source_img_base64,
            "mask": mask_img_base64
        }

    # http request
    data = json.dumps({
        "fn_index": 31,
        "data": [
            redraw,
            input_str,
            "",
            "None",
            "None",
            source_img_base64,
            mask,
            None,
            None,
            "Draw mask",
            steps,
            method,
            4,
            "original",
            False,
            False,
            1,
            1,
            cfg,
            0.75,
            -1,
            -1,
            0,
            0,
            0,
            False,
            height,
            width,
            "Just resize",
            False,
            32,
            "Inpaint masked",
            "",
            "",
            "None",
            "",
            "",
            1,
            50,
            0,
            False,
            4,
            1,
            "<p style=\"margin-bottom:0.75em\">Recommended settings: Sampling Steps: 80-100, Sampler: Euler a, Denoising strength: 0.8</p>",
            128,
            8,
            [
                "left",
                "right",
                "up",
                "down"
            ],
            1,
            0.05,
            128,
            4,
            "fill",
            [
                "left",
                "right",
                "up",
                "down"
            ],
            False,
            False,
            None,
            "",
            "<p style=\"margin-bottom:0.75em\">Will upscale the image to twice the dimensions; use width and height sliders to set tile size</p>",
            64,
            "None",
            "Seed",
            "",
            "Steps",
            "",
            True,
            False,
            None,
            "",
            ""
        ],
        "session_hash": "7x5krn9gilx"
    })
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request(
        "POST", sd_webui_url, headers=headers, data=data)

    # base64 decode
    img_base64 = json.loads(response.text)["data"][0][0][22:]
    img_data = base64.b64decode(img_base64)

    # file io
    with open(i2i_release_path, 'wb') as f:
        f.write(img_data)
