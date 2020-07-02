# -*- coding: utf-8 -*-

import cv2
import csv
import time
import os.path
import numpy as np

# 2値化の閾値(0～255)
threshold = 220


# 表示するウィンドウの設定
window_name = "Trimming Name"
window_size = (1920, 1080)



def onMouse(event, x, y, flag, params):
    ''' 画像上をクリックしたときの処理 '''
    window_name, img_input, ptlist = params
    
    # if len(ptlist) == 0:        
    #     img_show = img_input
        
    # # マウスの位置を追って切り取り範囲を表示
    # if event == cv2.EVENT_MOUSEMOVE:
    #     img2 = np.copy(img_show)
    #     cv2.circle(img2, (x, y), 2, (255, 0, 255), -1)
    #     cv2.rectangle(img2, (x-100, y-40), (x+100, y-14), (255, 0, 255))
    #     cv2.imshow(window_name, img2)

    # 左クリック→ポイント確定
    if event == cv2.EVENT_LBUTTONDOWN:
        img2 = np.copy(img_input)
        cv2.circle(img2, (x, y), 2, (255, 0, 255), -1)
        cv2.rectangle(img2, (x-100, y-40), (x+100, y-14), (255, 255, 0))
        cv2.imshow(window_name, img2)
        ptlist.append((x, y))
        img_show = img2
        

       
def checkPoint(img_path): 
    ''' 名前部分の座標を確認 '''
    img_read = cv2.imread(img_path)
  
    cv2.namedWindow(window_name)
        
    ptlist = []  
    while True:
        # クリック処理 

        cv2.setMouseCallback(window_name, onMouse, [window_name, img_read, ptlist])
        
        cv2.imshow(window_name, img_read)
    
        # 座標クリックができたらキー入力で次の処理へ            
        k = cv2.waitKey()     
        if k == 27:
            cv2.destroyAllWindows()
            print(ptlist)
            break


def trimName(img_path, out_path, point, width_name): 
    ''' 名前部分の切り取り '''
    TL = (int(point[0] - width_name/2), point[1] - 44)
    BR = (int(point[0] + width_name/2), point[1] - 16)
    
    img_read = cv2.imread(img_path)

    img_name = img_read[TL[1]:BR[1], TL[0]:BR[0]]
    cv2.imwrite(out_path, img_name)


    # プレビュー画像を表示
    img_copy = img_read
    cv2.circle(img_copy, point, 2, (255, 0, 255), -1)
    cv2.rectangle(img_copy, TL, BR, (255, 0, 255))
    
    TL_prvw = (point[0] - 200, point[1] - 100)
    BR_prvw = (point[0] + 200, point[1] + 100) 
    
    img_trim = img_read[TL_prvw[1]:BR_prvw[1], TL_prvw[0]:BR_prvw[0]]
    
    scale = 2
    h, w = img_trim.shape[:2]
    img_prvw = cv2.resize(img_trim, (int(w*scale), int(h*scale)))
      
   
    cv2.imshow('playerImg', img_prvw)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


    
def main():
    ''' メイン処理 '''
    match = 'PL-DAY2_1-1'
    img_path = match + '_name_all.png'

    # これで大まかな座標を調べて
    # checkPoint(img_path)  
        
    # ここから微調整＆名前切り取り
    player_num = 8
    out_path = match + '_name_' + str(player_num) + '.png'    
    
    point = (1236, 682)
    width_name = 148
    trimName(img_path, out_path, point, width_name)
 
    
        
if __name__ == "__main__":
    main()