# -*- coding: utf-8 -*-

import cv2


# 2値化の閾値(0～255)
threshold = 220


def name(frame, gray_name):
    ''' 位置を「名前」で捕捉する '''
    h, w = gray_name.shape
    
    gray_cv = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
    ret, gray_frame = cv2.threshold(gray_cv, threshold, 255, cv2.THRESH_BINARY)
    
    jug = cv2.matchTemplate(gray_frame, gray_name, cv2.TM_CCOEFF_NORMED)
    minVal, maxVal, minLoc, maxLoc = cv2.minMaxLoc(jug)   
    
    TL = maxLoc
    BR = (TL[0] + w, TL[1] + h)
    point_x = int((TL[0] + BR[0]) / 2)
    point_y = int((TL[1] + 44)) # 名前の上端からイカの位置までの距離（FHDでの値）
    
    return point_x, point_y, maxVal
    
            
def testThreshold(img_path, threshold):
    ''' 閾値を調べる '''
    img_read= cv2.imread(img_path)

    img_gray = cv2.cvtColor(img_read, cv2.COLOR_RGB2GRAY)
    ret, img_thresh = cv2.threshold(img_gray, threshold, 255, cv2.THRESH_BINARY)
    
    cv2.imshow('Gray Img', img_thresh)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
                    
    
def main():
    ''' メイン処理 '''        
    img_path = 'image_2.png'
    frame = cv2.imread(img_path)
    
    player_list = [i for i in range(1, 9)]
    
    
    gray_all = [[]]  # index 0 はダミー
    for player_num in range(1,9):
        img_tmp = cv2.imread('PL-DAY2_1-1_name_' + str(player_num) + '.png', 0)
        ret, gray_tmp = cv2.threshold(img_tmp, threshold, 255, cv2.THRESH_BINARY)
        gray_all.append(gray_tmp)
        
    for player_num in player_list:
        gray_name = gray_all[player_num]
        point_x, point_y, maxVal = name(frame, gray_name)
        print(point_x , point_y, maxVal)
    
        
if __name__ == "__main__":
    main()
    