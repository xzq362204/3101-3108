# -*- coding: utf-8 -*-
import os
import qrcode
import subprocess
from os import listdir
from PIL import Image
from cros.factory.test import session
#import Image, ImageFont, ImageDraw

static_path = '/usr/local/factory/sh/cutoff'

def Remove_png():
    png_exist = False
    for file in os.listdir('%s' % static_path):
      if file.endswith('png'):
        png_exist = True
    if png_exist:
      status,output = subprocess.getstatusoutput('rm %s/*.png' % static_path)
      if status != 0:
        raise Exception("Remove the pictures fail")

def GetMLB():
    # get MLB
    status_1,output = subprocess.getstatusoutput('vpd -l 2>/dev/null | grep  -w "mlb_serial_number"')
    if status_1 == 0:
      mlb = output.replace('"', "").split("=")[1].strip()
      if mlb:
        return mlb 
    raise Exception("Get mlb failled")

def make_qr_png():
    mlb = GetMLB()
    qr_contents='%s'% mlb
    qr_contents = qr_contents
    qr = qrcode.QRCode(version=1, error_correction=qrcode.ERROR_CORRECT_L, box_size=18)
    qr.add_data(qr_contents)
    qr.make(fit=True)                                             
    orig_img = qr.make_image()
    new_img = orig_img.resize((400, 400))
    filename = os.path.basename(os.path.realpath(__file__)).split('.')[0]
    if not os.path.exists(static_path):
        os.makedirs(static_path)
    new_img.save("%s/qr.png" % static_path)
    new_img.show()


def GetFlow():
    status_3,output = subprocess.getstatusoutput('factory device-data 2>/dev/null | grep  -w "obe"')
    session.console.info("status_3=%s output=%s"% (status_3, output))
    if status_3 == 0:
      flow = output.replace('"',"").split(":")[1].strip()
      session.console.info("flow=%s "% (flow))
      if flow:
        return flow 
    raise Exception("Get flow failled")


def make_flow_png(): # Using the picture of existing
    session.console.info("make_flow_png begin")
    text = GetFlow()
    session.console.info("GetFlow")
    subprocess.getoutput('chmod 644 %s/qr/*.png ' % static_path)
    if text == 'Y':
        subprocess.getoutput('cp %s/qr/obe1.png %s' % (static_path, static_path))
    elif text == 'N':
        subprocess.getoutput('cp %s/qr/pack.png %s' % (static_path, static_path))
    else:
        raise Exception("Get value is null")

def qr_flow():
    # Get .png
    img_list = sorted(
      [(static_path + '/' + name) for name in os.listdir(static_path) if name.endswith('.png')])
    img_list_target = img_list[1:]
    img_list_target.append(img_list[0])

    size_x, size_y = Image.open(img_list_target[0]).size

    creat_new_img = Image.new('RGB', (size_x * len(img_list_target), size_y))

    for i in range(1, len(img_list_target) + 1):
      from_img = Image.open(img_list_target[i - 1]).resize((size_y, size_x), Image.ANTIALIAS)
      creat_new_img.paste(from_img, (size_x * (i - 1), 0))

    return creat_new_img.save('%s/qr_flow.png' % static_path)
 
if __name__ == '__main__':
    session.console.info("enter __main__")
    Remove_png()
    session.console.info("Remove_png")
    make_qr_png()
    session.console.info("make_qr_png")
    make_flow_png()
    session.console.info("make_flow_png")
    qr_flow()
