# -*- coding: utf-8 -*-

import cv2
import csv
import os.path
import numpy as np

# 2値化の閾値(0～255)
threshold = 220

def trackingName(video_path, frame_start, frame_end, player_num):
    ''' 位置を「名前」で捕捉する '''      
    video_name, video_ext = os.path.splitext(os.path.basename(video_path))
    
    video = cv2.VideoCapture(video_path)
    W = video.get(cv2.CAP_PROP_FRAME_WIDTH)
    H = video.get(cv2.CAP_PROP_FRAME_HEIGHT)
    fps = video.get(cv2.CAP_PROP_FPS)
    
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(video_name + '_tracking_player' + str(player_num) + '.avi', fourcc, fps, (int(W), int(H)))
    
    img_tmp = cv2.imread('name_player' + str(player_num) + '.png', 0)
    h, w = img_tmp.shape
    ret, gray_tmp = cv2.threshold(img_tmp, threshold, 255, cv2.THRESH_BINARY)

    position_list = []
    
    fcount = 0    
    while(video.isOpened()):
        ret, frame = video.read()
    
        if not ret:
            break
      
        fcount = fcount + 1  
        
        if frame_start <= fcount < frame_end:
            
            out_frame = frame
            
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
                
        elif fcount == frame_end:
            break
                                
    video.release
    out.release
    
    # CSV出力
    with open(video_name + '_tracking_player' + str(player_num) + '.csv', 'w') as file:
        writer = csv.writer(file, lineterminator='\n')
        writer.writerows(position_list)    
    
def trimmingName(img_path, TL, BR, player_num): 
    ''' 名前部分の切り取り '''
    img_read= cv2.imread(img_path)

    img_name = img_read[TL[1]:BR[1], TL[0]:BR[0]]
    cv2.imwrite('name_player' + str(player_num) + '.png', img_name)
    
    img_out = img_read
    cv2.rectangle(img_out, TL, BR, (255, 0, 255))
   
    cv2.imshow('playerImg', img_out)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def testThreshold(img_path, threshold):
    ''' 閾値を設定 '''
    img_read= cv2.imread(img_path)

    img_gray = cv2.cvtColor(img_read, cv2.COLOR_RGB2GRAY)
    ret, img_thresh = cv2.threshold(img_gray, threshold, 255, cv2.THRESH_BINARY)
    
    cv2.imshow('Gray Img', img_thresh)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
                    
    
def main():
    ''' メイン処理 '''
    img_path = 'name_all.png'
    TL = (840, 588)
    BR = (890, 612)
    player_num = 2
    # trimmingName(img_path, TL, BR, player_num)
    
    # testThreshold(img_path, threshold)

    video_path = 'overlook_turf_stage0.avi'
    trackingName(video_path, 484, 5887, 2)    
    
        
if __name__ == "__main__":
    main()