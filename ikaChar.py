# -*- coding: utf-8 -*-

import cv2
import csv
import os
import os.path
from PIL import Image
import pyocr
import pyocr.builders


TL_time_ratio = (0.475, 0.05)      # at FHD ( 912, 54)
BR_time_ratio = (0.525, 0.091666)  # at FHD (1008, 99)                   

TL_count_ratio = [(804/1920, 154/1080), (1026/1920, 154/1080)]  # at FHD 1920*1080
BR_count_ratio = [(894/1920, 210/1080), (1116/1920, 210/1080)]


# HSVの閾値
# 黄
hsv_y_min = (90, 0, 128)
hsv_y_max = (100, 255, 255)
# 青
hsv_b_min = (165, 128, 128)
hsv_b_max = (175, 255, 255)
# 白
hsv_w_min = (0, 0, 0)
hsv_w_max = (179, 128, 255)
# 黄と青と白
hsv_all_min = [hsv_y_min, hsv_b_min, hsv_w_min]
hsv_all_max = [hsv_y_max, hsv_b_max, hsv_w_max]


# GRAYの閾値
threshold_list = [80, 160, 224] #224


# 以下OCR関連
# インストール済みのTesseractのパスを通す
path_tesseract = "C:\\Program Files\\Tesseract-OCR"
if path_tesseract not in os.environ["PATH"].split(os.pathsep):
    os.environ["PATH"] += os.pathsep + path_tesseract

# OCRエンジンの取得
tools = pyocr.get_available_tools()
tool = tools[0]

# OCR設定
builder = pyocr.builders.DigitBuilder(tesseract_layout=4)   # layoutは調整が必要かも  
lang = 'eng+jpn'



def cv2pil(image):
    ''' OpenCV型 -> PIL型 '''
    new_image = image.copy()
    if new_image.ndim == 2:  # モノクロ
        pass
    elif new_image.shape[2] == 3:  # カラー
        new_image = cv2.cvtColor(new_image, cv2.COLOR_BGR2RGB)
    elif new_image.shape[2] == 4:  # 透過
        new_image = cv2.cvtColor(new_image, cv2.COLOR_BGRA2RGBA)
        
    new_image = Image.fromarray(new_image)
    
    return new_image


def zonesCount(frame, method):
    H, W = frame.shape[:2]

    char_list = []
    for i in [0, 1]:
        TL_count = (round(W * TL_count_ratio[i][0]), round(H * TL_count_ratio[i][1]))
        BR_count = (round(W * BR_count_ratio[i][0]), round(H * BR_count_ratio[i][1]))
        
        img_trimmed = frame[TL_count[1] : BR_count[1], TL_count[0] : BR_count[0]]
        
        if method == 'HSV':
            # RGB -> BGR -> HSV
            img_bgr = cv2.cvtColor(img_trimmed, cv2.COLOR_RGB2BGR)
            img_hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
            
            for j in range(len(hsv_all_min)):
                # HSV閾値で2値化
                img_bin = cv2.inRange(img_hsv, hsv_all_min[j], hsv_all_max[j])     
                # OpenCV型 -> PIL型
                img_tgt = cv2pil(img_bin)
                # img_tgt.show()
                # OCRで文字認識
                result = tool.image_to_string(img_tgt, lang=lang, builder=builder)   
                char_list.append(result)  
                
        elif method == 'GRAY':
            # グレースケール
            img_gray = cv2.cvtColor(img_trimmed, cv2.COLOR_RGB2GRAY)
            
            for j in range(len(threshold_list)):
                # グレースケール
                ret, img_bin = cv2.threshold(img_gray, threshold_list[j], 255, cv2.THRESH_BINARY_INV)
                # OpenCV型 -> PIL型
                img_tgt = cv2pil(img_bin)
                # img_tgt.show()
                # OCRで文字認識
                result = tool.image_to_string(img_tgt, lang=lang, builder=builder)   
                char_list.append(result)      
            
        else:
            print('Enter "method" in HSV or GRAY')
            break
    
    return char_list




def recogChar(video_path, frame_start, frame_end):
    ''' 動画で文字認識 '''      
    video_name, video_ext = os.path.splitext(os.path.basename(video_path))
    
    video = cv2.VideoCapture(video_path)

    count_list = [['fcount', 'yellow80', 'yellow160', 'yellow224', 'blue80', 'blue160', 'blue224']] # record

    fcount = 0
    while(video.isOpened()):
        ret, frame = video.read()
    
        if not ret:
            break
      
        fcount = fcount + 1  
        
        if frame_start <= fcount < frame_end:
            if (fcount - frame_start) % 15 == 0:
                # この中に行いたい処理を書く
                count = zonesCount(frame, 'GRAY')
       
                count_list.append([fcount] + count)
                
        elif fcount == frame_end:
            break
                                
    video.release
    
    # CSV出力
    with open(video_name + '_count.csv', 'w') as file:
        writer = csv.writer(file, lineterminator='\n')
        writer.writerows(count_list)
        
        
def binalization(image):
    ''' 2値化のチェック '''
    for i in range(16):
        threshold = int(i*16)
    
        img_gry = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        ret, img_bin = cv2.threshold(img_gry, threshold, 255, cv2.THRESH_BINARY_INV)
        
        cv2.imshow('threshold = ' + str(threshold), img_bin)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    
    
def main():
    ''' メイン処理 ''' 
    img_path = 'image.png'
    frame = cv2.imread(img_path)
    
    # for method in ['HSV', 'GRAY']:
    #     count = zonesCount(frame, method) 
    #     print(count)
    
    # binalization(frame) 
    
    
    video_path = 'video.mp4'
    frame_start = 1
    frame_end = 9999
    recogChar(video_path, frame_start, frame_end)
    
    
        
if __name__ == "__main__":
    main()