# -*- coding: utf-8 -*-

import cv2
import csv
import numpy as np



# TopLeft, BottomRight
TLBR_y = [(480, 40), (920, 100)] 
TLBR_b = [(1000, 40), (1440, 100)]

TLBR_list = [TLBR_y, TLBR_b]

# HSVの閾値
hsv_y_min = (90, 128, 128)
hsv_y_max = (100, 255, 255)

hsv_b_min = (165, 128, 128)
hsv_b_max = (175, 255, 255)

hsv_sp_min = (0, 0, 128)
hsv_sp_max = (179, 128, 255)

hsv_w_min = (0, 0, 224)
hsv_w_max = (179, 10, 255)

hsv_a_min = [hsv_y_min, hsv_b_min]
hsv_a_max = [hsv_y_max, hsv_b_max]


# 各プレイヤーのイカランプの位置
# ピンチ表示に対して調整が必要
TL_lamp = [(550, 42), (642, 42), (715, 42), (792, 42), (1044, 42), (1130, 42), (1227, 42), (1323, 42)] 
BR_lamp = [(596, 98), (692, 98), (789, 98), (875, 98), (1127, 98), (1204, 98), (1277, 98), (1369, 98)]


def onlyRec():
    '''' 録画するだけ '''
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter('.\\test.avi', fourcc, 60, (1920, 1080))
    
    capture = cv2.VideoCapture(0)
    print(capture.isOpened())
    capture.set(3, 1920)
    capture.set(4, 1080)
    
    count = 0
    while(True):
        ret, frame = capture.read()
        count += 1

        out.write(frame)
        
        if count % 30 == 0:
            cv2.imshow('frame', frame)
    
        # "q"キー または ctrl + C でキャプチャ停止
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    out.release()
    capture.release()
    cv2.destroyAllWindows()


def jugLamp():
    ''' イカランプの判別 + 録画 '''      
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter('.\\test.avi', fourcc, 60, (1920, 1080))
    
    capture = cv2.VideoCapture(0)
    print(capture.isOpened())
    capture.set(3, 1920)
    capture.set(4, 1080)
    

    doa_list = [] # Dead or Alive
    
    fcount = 0
    while(True):
        ret, frame = capture.read()
    
        if not ret:
            break
        
        out.write(frame)
      
        fcount += 1  
        
        if fcount % 30 == 0:
            cv2.imshow('frame', frame)
            
            # イカランプの状態リスト 0:dead  1:alive  2:sp
            lamp_list = [0, 0, 0, 0, 0, 0, 0, 0]
            # 面積を記録しておく
            surf_list = [0, 0, 0, 0, 0, 0, 0, 0]
            
            for i in (0, 1):
                # イカランプ部分をトリミング
                TL = TLBR_list[i][0]
                BR = TLBR_list[i][1]
                img_trimmed = frame[TL[1] : BR[1], TL[0] : BR[0]] 
                
                img_bgr = cv2.cvtColor(img_trimmed, cv2.COLOR_RGB2BGR)
                img_hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
                      
                # alive の判定
                img_bin = cv2.inRange(img_hsv, hsv_a_min[i], hsv_a_max[i])
                num_labels, label_image, stats, center = cv2.connectedComponentsWithStats(img_bin)
            
                num_labels = num_labels - 1
                stats = np.delete(stats, 0, 0)
                center = np.delete(center, 0, 0)
                       
                for index in range(num_labels):
                    s = stats[index][4]
                    mx = int(center[index][0]) + TL[0]
                    
                    for player_num in range(int(4*i), int(4*(i+1))):    
                        # まとまりがアイコン表示位置に入っているか             
                        if TL_lamp[player_num][0] < mx < BR_lamp[player_num][0]:
                            # 面積が前より大きければ大きいほうを採用
                            if surf_list[player_num] < s:                     
                                lamp_list[player_num] = 1
                                surf_list[player_num] = s
                            
                # sp の判定
                img_bin = cv2.inRange(img_hsv, hsv_sp_min, hsv_sp_max)
                num_labels, label_image, stats, center = cv2.connectedComponentsWithStats(img_bin)
            
                num_labels = num_labels - 1
                stats = np.delete(stats, 0, 0)
                center = np.delete(center, 0, 0)
                    
                for index in range(num_labels):
                    s = stats[index][4]
                    mx = int(center[index][0]) + TL[0]
                    
                    for player_num in range(int(4*i), int(4*(i+1))):                        
                        if TL_lamp[player_num][0] < mx < BR_lamp[player_num][0]:
                            if surf_list[player_num] < s:                     
                                lamp_list[player_num] = 2
                                surf_list[player_num] = s
                                
                                
            # 面積の閾値を設けて誤認識をdeadに戻す
            for player_num in range(8):
                if surf_list[player_num] < 800: # 閾値はFHD向けで調整が必要そう
                    lamp_list[player_num] = 0
                

            doa_list.append(lamp_list + surf_list)
                

        # "q"キー または ctrl + C でキャプチャ停止
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
                                
    out.release()
    capture.release()
    cv2.destroyAllWindows()

    # CSV出力
    with open('test_lamp.csv', 'w') as file:
        writer = csv.writer(file, lineterminator='\n')
        writer.writerows(doa_list)



                    
    
def main():
    ''' メイン処理 ''' 
    
    # onlyRec()
    
    # jugLamp()
    
    
        
if __name__ == "__main__":
    main()