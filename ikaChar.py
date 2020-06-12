# -*- coding: utf-8 -*-

import cv2
import csv
import os.path
import numpy as np




# ocr_card.py
import os
from PIL import Image
import pyocr
import pyocr.builders

# 1.インストール済みのTesseractのパスを通す
path_tesseract = "C:\\Program Files\\Tesseract-OCR"
if path_tesseract not in os.environ["PATH"].split(os.pathsep):
    os.environ["PATH"] += os.pathsep + path_tesseract

# 2.OCRエンジンの取得
tools = pyocr.get_available_tools()
tool = tools[0]



TL_time_ratio = (0.475, 0.05)      # at FHD ( 912, 54)
BR_time_ratio = (0.525, 0.091666)  # at FHD (1008, 99)
                   



# TopLeft, BottomRight
TLBR_y = [(480, 40), (920, 100)] 
TLBR_b = [(1000, 40), (1440, 100)]

TLBR_list = [TLBR_y, TLBR_b]

# HSVの閾値
hsv_y_min = (90, 128, 128)
hsv_y_max = (100, 255, 255)

hsv_b_min = (165, 128, 128)
hsv_b_max = (175, 255, 255)

hsv_w_min = (0, 0, 224)
hsv_w_max = (179, 10, 255)

hsv_a_min = [hsv_y_min, hsv_b_min]
hsv_a_max = [hsv_y_max, hsv_b_max]


# 各プレイヤーのイカランプの位置
# ピンチ表示に対して調整が必要
TL_lamp = [(550, 42), (642, 42), (715, 42), (792, 42), (1044, 42), (1130, 42), (1227, 42), (1323, 42)] 
BR_lamp = [(596, 98), (692, 98), (789, 98), (875, 98), (1127, 98), (1204, 98), (1277, 98), (1369, 98)]


def cv2pil(image_cv):
    image_cv = cv2.cvtColor(image_cv, cv2.COLOR_BGR2RGB)
    image_pil = Image.fromarray(image_cv)
    image_pil = image_pil.convert('RGB')

    return image_pil

    
def jugChar(video_path, frame_start, frame_end):
    ''' イカランプの判別 '''      
    video_name, video_ext = os.path.splitext(os.path.basename(video_path))
    
    video = cv2.VideoCapture(video_path)
    W = video.get(cv2.CAP_PROP_FRAME_WIDTH)
    H = video.get(cv2.CAP_PROP_FRAME_HEIGHT)

    TL_time = (round(W * TL_time_ratio[0]), round(H * TL_time_ratio[1]))
    BR_time = (round(W * BR_time_ratio[0]), round(H * BR_time_ratio[1]))

    time_list = [] # record

    fcount = 0
    while(video.isOpened()):
        ret, frame = video.read()
    
        if not ret:
            break
      
        fcount = fcount + 1  
        
        if frame_start <= fcount < frame_end:
            img_trimmed = frame[TL_time[1] : BR_time[1], TL_time[0] : BR_time[0]]
        
            img_bgr = cv2.cvtColor(img_trimmed, cv2.COLOR_RGB2BGR)
            img_hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)        
            img_bin = cv2.inRange(img_hsv, hsv_w_min, hsv_w_max)
            
            img_org = cv2pil(img_bin)
        
            builder = pyocr.builders.TextBuilder()
            lang = 'eng'
            result = tool.image_to_string(img_org, lang=lang, builder=builder)
            
   
            time_list.append([result])
                
        elif fcount == frame_end:
            break
                                
    video.release

    # CSV出力
    with open(video_name + '_time.csv', 'w') as file:
        writer = csv.writer(file, lineterminator='\n')
        writer.writerows(time_list)
        

def jugLampImg(img_path): 
    ''' 画像で文字判別の練習 '''
    frame = cv2.imread(img_path)
    height_img, width_img, channels = frame.shape[:3]

    TL_time = (round(width_img * TL_time_ratio[0]), round(height_img * TL_time_ratio[1]))
    BR_time = (round(width_img * BR_time_ratio[0]), round(height_img * BR_time_ratio[1]))
    
    img_trimmed = frame[TL_time[1] : BR_time[1], TL_time[0] : BR_time[0]]

    img_bgr = cv2.cvtColor(img_trimmed, cv2.COLOR_RGB2BGR)
    img_hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)        
    img_bin = cv2.inRange(img_hsv, hsv_w_min, hsv_w_max)
    
    img_org = cv2pil(img_bin)

    # 4.ＯＣＲ実行
    builder = pyocr.builders.TextBuilder()
    lang = 'jpn+eng'
    result = tool.image_to_string(img_org, lang=lang, builder=builder)
    
    print(result)    

                    
    
def main():
    ''' メイン処理 ''' 
    # img_path = '.\\testimg_1.png'
    # jugLampImg(img_path)
    
    video_path = 'D:\\splatoon_movie\\capture\\overlook_turf\\overlook_turf_stage0.avi'
    frame_start = 484
    frame_end = 1000
    jugChar(video_path, frame_start, frame_end)
    
    
        
if __name__ == "__main__":
    main()