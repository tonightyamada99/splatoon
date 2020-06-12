# -*- coding: utf-8 -*-
"""
Created on Wed Jul 31 04:18:05 2019

@author: Yamada
"""

import cv2
import csv
import csvread
import os.path
import numpy as np


# 表示するウィンドウの設定
click_window = "Click Window"
click_window_size = (1920, 1080)
position_window = "Position Window"
reference_window = "Reference Window"
reference_window_size = (854, 480)

# 配信映像の切り出し座標
# capture_koshien_1
TL_koshien_1 = [(164, 126)]
BR_koshien_1 = [(1115, 661)]

# capture_koshien_2
TL_koshien_2 = [(410, 446)]
BR_koshien_2 = [(868, 704)]

# capture_koshien_3
TL_koshien_3 = [(399, 432)]
BR_koshien_3 = [(879, 704)]

    
def onMouse(event, x, y, flag, params):
    ''' 画像上をクリックしたときの処理 '''
    click_window, position_window, click_img, position_img, ptlist = params
    # マウスの位置を示すラインを描画
    if event == cv2.EVENT_MOUSEMOVE:
        img2 = np.copy(click_img)
        h, w = img2.shape[0], img2.shape[1]
        cv2.line(img2, (x, 0), (x, h - 1), (255, 0, 0))
        cv2.line(img2, (0, y), (w - 1, y), (255, 0, 0))
        cv2.imshow(click_window, img2)

        img2 = np.copy(position_img)
        h, w = img2.shape[0], img2.shape[1]
        cv2.line(img2, (round(x * 4/9), 0), (round(x * 4/9), h - 1), (255, 0, 0))
        cv2.line(img2, (0, round(y * 4/9)), (w - 1, round(y * 4/9)), (255, 0, 0))
        cv2.imshow(position_window, img2)
    # 左クリック→生存
    if event == cv2.EVENT_LBUTTONDOWN:
        ptlist.append([0, x, y])            
        cv2.circle(click_img, (x, y), 3, (0, 255, 0), 3)
        cv2.circle(position_img, (round(x * 4/9), round(y * 4/9)), 3, (0, 255, 0), 3)
        cv2.imshow(click_window, click_img)
        cv2.imshow(position_window, position_img)
    # 右クリック→倒された瞬間
    elif event == cv2.EVENT_RBUTTONDOWN:
        ptlist.append([1, x, y])     
        cv2.circle(click_img, (x, y), 3, (0, 0, 255), 3)
        cv2.circle(position_img, (round(x * 4/9), round(y * 4/9)), 3, (0, 0, 255), 3)
        cv2.imshow(click_window, click_img)
        cv2.imshow(position_window, position_img)
    # Shift + 右クリック→倒された後
    elif event == cv2.EVENT_RBUTTONUP and flag & cv2.EVENT_FLAG_SHIFTKEY:
        ptlist.append([2, x, y])     
        cv2.circle(click_img, (x, y), 3, (255, 0, 0), 3)
        cv2.circle(position_img, (round(x * 4/9), round(y * 4/9)), 3, (255, 0, 0), 3)
        cv2.imshow(click_window, click_img)
        cv2.imshow(position_window, position_img)
    # Shift + 左クリック→取得不可能
    elif event == cv2.EVENT_LBUTTONUP and flag & cv2.EVENT_FLAG_CTRLKEY:
        ptlist.append([9, 0, 0])     
        cv2.circle(click_img, (x, y), 3, (255, 255, 255), 3)
        cv2.circle(position_img, (round(x * 4/9), round(y * 4/9)), 3, (255, 255, 255), 3)
        cv2.imshow(click_window, click_img)
        cv2.imshow(position_window, position_img)        



def clickposition(video_path, player_num, csvtype):
    ''' 座標をクリックで取得する '''
    video_name, video_ext = os.path.splitext(os.path.basename(video_path))
    video_dir = os.path.dirname(video_path)     
    
    # 動画の情報を読み込む
    layout_list = csvread.csvread(video_dir + '\\' + video_name + '\\' + video_name + '_layout.csv', 's')
    status_list = csvread.csvread(video_dir + '\\' + video_name + '\\' + video_name + '_status.csv', 's')
    
    rule = status_list[1][0]
    stage_num   = int(status_list[1][1])
    frame_start = int(status_list[1][5])
    frame_end   = int(status_list[1][6])

    # 動画を読み込む
    video = cv2.VideoCapture(video_path)
    fps = video.get(cv2.CAP_PROP_FPS)
    
    # 座標取得間隔を[秒]で指定
    interval = 1 
    fps_int = round(fps*interval) 

    # 俯瞰画像を読み込む    
    overlook_img_path = '.\\overlook_img\\overlook_' + str(stage_num) + '_' + rule + '.png'
    overlook_img = cv2.imread(overlook_img_path) 
    
    point_list = [['dead-or-alive', 'point_y', 'point_x']]
    
    frame_count = 0
    while(video.isOpened()):        
        ret, frame = video.read()
        
        if not ret:
            break
    
        frame_count += 1     
        
        if frame_start <= frame_count < frame_end:
            if (frame_count - frame_start) % fps_int == 0:
                cv2.namedWindow(click_window)
                cv2.namedWindow(position_window)
                cv2.namedWindow(reference_window)
                
                ptlist = []
                
                # レイアウトに応じて画像を切り取る
                if layout_list[frame_count][0] == '1':
                    trimmed_frame = frame[TL_koshien_1[0][1] : BR_koshien_1[0][1], TL_koshien_1[0][0] : BR_koshien_1[0][0]]
                elif layout_list[frame_count][0] == '2':
                    trimmed_frame = frame[TL_koshien_2[0][1] : BR_koshien_2[0][1], TL_koshien_2[0][0] : BR_koshien_2[0][0]]
                elif layout_list[frame_count][0] == '3':
                    trimmed_frame = frame[TL_koshien_3[0][1] : BR_koshien_3[0][1], TL_koshien_3[0][0] : BR_koshien_3[0][0]]
                else:
                    trimmed_frame = frame    
                    
                    
                click_img = cv2.resize(overlook_img, click_window_size) 
                frame_img = cv2.resize(frame, reference_window_size)  
                position_img = cv2.resize(trimmed_frame, reference_window_size) 

                # クリック処理                
                cv2.setMouseCallback(click_window, onMouse, [click_window, position_window, click_img, position_img, ptlist])
                
                cv2.imshow(click_window, click_img)
                cv2.imshow(position_window, position_img)
                cv2.imshow(reference_window, frame_img)

                # 座標クリックができたらキー入力で次の処理へ            
                k = cv2.waitKey()
                # ESCが入力されたら中断
                if k == 27:
                    break
            
                else:
                    pt_length = len(ptlist)
                        
                    # 1回もクリックしていない場合
                    if pt_length == 0:
                        point_list.append([99, 0, 0])     
                            
                    else:
                        cor_ptlist = [ptlist[pt_length - 1][0], ptlist[pt_length - 1][1]/click_window_size[0],  ptlist[pt_length - 1][2]/click_window_size[1]]           
                        point_list.append(cor_ptlist)
                        
        elif frame_count == frame_end:
            break

    video.release()
    cv2.destroyAllWindows()

    # 座標リストをCSVで保存
    if csvtype == 'n':
        type_csv = ''
    elif csvtype == 'c':
        type_csv = '_teisei'
    else:
        type_csv = '_ex'
        
    csv_path = video_dir + '\\' + video_name + '\\' + video_name + '_pointlist_player' + str(player_num) + '_int' + str(interval) +'s' + type_csv + '.csv'
        
    with open(csv_path, 'w') as file:
        writer = csv.writer(file, lineterminator='\n')
        writer.writerows(point_list)  
        
        
def main():
    ''' メイン処理 '''
    site = 'hokkaido'
    day = 'day1'
    match_status = 'SF-2-3'
    
    player_num = 8
    
    video_path = 'D:\splatoon_movie\K5' + '\\' + site + '_'+ day + '\\K5_' + site + '_' + day + '_' + match_status + '.mp4'
    clickposition(video_path, player_num, 'n')
    
    
if __name__ == "__main__":
    main()
