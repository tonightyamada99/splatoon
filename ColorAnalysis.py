#!/usr/bin/env python
# coding: utf-8

# In[ ]:


# -*- coding: utf-8 -*-

import cv2
import csv
import os.path
import numpy as np
import pandas as pd

def trackingName(video_path, frame_start, frame_end):
    
    video_name, video_ext = os.path.splitext(os.path.basename(video_path))
    
    video = cv2.VideoCapture(video_path)
    W = video.get(cv2.CAP_PROP_FRAME_WIDTH)
    H = video.get(cv2.CAP_PROP_FRAME_HEIGHT)
    fps = video.get(cv2.CAP_PROP_FPS)
    
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(video_name + '_tracking_color.mp4', fourcc, fps, (int(W), int(H)))


    yellow_list = []
    blue_list = []
    other_list = []
    
    fcount = 0    
    while(video.isOpened()):
        ret, frame = video.read()
    
        if not ret:
            break
      
        fcount = fcount + 1  
        
        if frame_start <= fcount < frame_end:

            # フレームをHSVに変換
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            
            #初期画像との差分で比較する
            #hsv = cv2.absdiff(base_hsv, hsv)

            # 取得する色の範囲を指定する
            lower_yellow = np.array([20, 100, 140])
            upper_yellow = np.array([90, 255, 255])
            
            lower_blue = np.array([110, 100, 90])
            upper_blue = np.array([255, 255, 255])
            
            # HSV の範囲指定で2値化する。
            binary_yellow = cv2.inRange(hsv, lower_yellow, upper_yellow)
            binary_blue = cv2.inRange(hsv, lower_blue, upper_blue)

            # 全画素に占める割合
            yellow_ratio = cv2.countNonZero(binary_yellow) / binary_yellow.size
            blue_ratio = cv2.countNonZero(binary_blue) / binary_yellow.size
            other_ratio =  binary_yellow.size - cv2.countNonZero(binary_yellow) - cv2.countNonZero(binary_blue) / binary_yellow.size
            
            # 色割合をリストに格納
            yellow_list.append(yellow_ratio)
            blue_list.append(blue_ratio)
            other_list.append(other_ratio)

            
            '''
            # 指定した色に基づいたマスク画像の生成
            #img_mask = cv2.inRange(hsv, lower_yellow, upper_yellow)
            img_mask = cv2.inRange(hsv, lower_blue, upper_blue)

            # フレーム画像とマスク画像の共通の領域を抽出する。
            img_color = cv2.bitwise_and(frame, frame, mask=img_mask)

            cv2.imshow("SHOW COLOR IMAGE", img_color)
            
            out.write(img_color)
            '''

            # qを押したら終了
            k = cv2.waitKey(1)
            if k == ord('q'):
                break

            '''
            gray_cv = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
            ret, gray_frame = cv2.threshold(gray_cv, threshold, 255, cv2.THRESH_BINARY)
            
            jug = cv2.matchTemplate(gray_frame, gray_tmp, cv2.TM_CCOEFF)
            minVal, maxVal, minLoc, maxLoc = cv2.minMaxLoc(jug)   
            
            TL = maxLoc
            BR = (TL[0] + w, TL[1] + h)
            cv2.rectangle(out_frame, TL, BR, (255, 0, 255), 2)
            
            out.write(out_frame)
            
            center = ((TL[0] + BR[0]) / 2, (TL[1] + BR[1]) / 2)
            position_list.append(center)
            '''
                
        elif fcount == frame_end:
            break
    cv2.destroyAllWindows()                          
    video.release
    out.release
    
    
    # CSV出力
    
    '''
    with open(video_name + '_tracking_color_ratio.csv', 'w') as file:
        writer = csv.writer(file, lineterminator='\n')
        writer.writeline(yellow_list)    
        writer.writeline(blue_list)  
        writer.writeline(blue_list)  
    '''
    
    df = pd.DataFrame({'yellow': yellow_list,
                       'blue': blue_list,
                       'other': other_list})
    df.to_csv(video_name + '_tracking_color_ratio.csv')
    
                    
    
def main():
    video_path = 'overlook_turf_stage0.mp4'
    trackingName(video_path, 484, 5887)    
    
        
if __name__ == "__main__":
    main()


# In[ ]:


get_ipython().run_line_magic('run', '-i imgHSV.py')


# In[ ]:




