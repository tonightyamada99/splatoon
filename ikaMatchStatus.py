# -*- coding: utf-8 -*-
"""
Created on Wed Apr  1 19:27:47 2020

@author: Yamada
"""
import cv2
import csv
import csvread
import os.path
import glob



# 時計の座標, FINISH!の座標
TL_time_ratio = [( 912/1920, 54/1080), (380/1920, 630/1080)]
BR_time_ratio = [(1008/1920, 99/1080), (690/1920, 720/1080)]

# 「ル」の字の座標, ルール名の座標
TL_rule_ratio = [(900/1920, 160/1080), ( 830/1920, 290/1080)] 
BR_rule_ratio = [(940/1920, 250/1080), (1100/1920, 500/1080)]

# ステージ名の座標
TL_stage_ratio = [(1500/1920,  972/1080)] 
BR_stage_ratio = [(1890/1920, 1053/1080)]


# ルール一覧
rule_list = ['turf', 'zones', 'tower', 'rain', 'clam']
# 一致率の閾値
threshold = 0.9

stage_list = csvread.csvread('stage.csv', 's')


def getStatus(video_path, out_path):
    ''' 動画の情報を調べる '''    

    # 取得状況の把握
    if (os.path.exists(out_path)):
        print('情報取得済み')
    else:
        video = cv2.VideoCapture(video_path)   
        H = video.get(cv2.CAP_PROP_FRAME_HEIGHT)
        W = video.get(cv2.CAP_PROP_FRAME_WIDTH)
        fps = video.get(cv2.CAP_PROP_FPS)
        frame_all = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
        
        # 動画の画面サイズに応じて切り取り範囲を設定
        TL_rule = []
        BR_rule = []
        for i in range(len(TL_rule_ratio)):
            TL = (round(W * TL_rule_ratio[i][0]), round(H * TL_rule_ratio[i][1]))
            BR = (round(W * BR_rule_ratio[i][0]), round(H * BR_rule_ratio[i][1])) 
            TL_rule.append(TL)
            BR_rule.append(BR)
    
        TL_time = []
        BR_time = []
        for i in range(len(TL_time_ratio)):
            TL = (round(W * TL_time_ratio[i][0]), round(H * TL_time_ratio[i][1]))
            BR = (round(W * BR_time_ratio[i][0]), round(H * BR_time_ratio[i][1])) 
            TL_time.append(TL)
            BR_time.append(BR)
    
        TL_stage = [(round(W * TL_stage_ratio[0][0]), round(H * TL_stage_ratio[0][1]))]
        BR_stage = [(round(W * BR_stage_ratio[0][0]), round(H * BR_stage_ratio[0][1]))]     
            
        # 「ル」の画像
        img_read = cv2.imread('.\\keyobject\\rule.png')
        img_rule = cv2.resize(img_read, dsize=None, fx=H/1080, fy=W/1920)
        
    
        # 試合終了判定画像
        img_read = cv2.imread('.\\keyobject\\time_fin.png')
        img_fin = cv2.resize(img_read, dsize=None, fx=H/1080, fy=W/1920)
            
        
        # ここから動画処理
        frame_rule  = 0
        rule = 'nodata'
        stage_num = 0
        frame_start = 0
        frame_end   = 0
        
        val_list = []
        fcount = 0
        while(video.isOpened()):
            ret, frame = video.read()
        
            if not ret:
                break
          
            fcount = fcount + 1  
            
            if frame_rule == 0:
                ''' ルール表示の判定 '''
                img_trm = frame[TL_rule[0][1] : BR_rule[0][1], TL_rule[0][0] : BR_rule[0][0]]
                jug = cv2.matchTemplate(img_trm, img_rule, cv2.TM_CCORR_NORMED)
                minVal, maxVal, minLoc, maxLoc = cv2.minMaxLoc(jug) 
                   
                if maxVal > threshold:     
                    frame_rule = fcount + round(fps*1)              
            
            elif fcount == frame_rule:
                ''' ルールの判定 '''
                img_trm = frame[TL_rule[1][1] : BR_rule[1][1], TL_rule[1][0] : BR_rule[1][0]]            
                
                val_rule = 0 
                for rule_name in rule_list:
                    img_read = cv2.imread('.\\keyobject\\rule_' + rule_name + '.png')
                    img_rname = cv2.resize(img_read, dsize=None, fx=H/1080, fy=W/1920) 
                    
                    jug = cv2.matchTemplate(img_trm, img_rname, cv2.TM_CCORR_NORMED)
                    minVal, maxVal, minLoc, maxLoc = cv2.minMaxLoc(jug) 
                    
                    if maxVal > val_rule:
                        rule = rule_name
                        val_rule = maxVal
                                  
                ''' ステージの判定 '''
                img_trm = frame[TL_stage[0][1] : BR_stage[0][1], TL_stage[0][0] : BR_stage[0][0]]  
                
                val_stage = 0 
                for i in range(0, 23):
                    img_read = cv2.imread('.\\keyobject\\stage_name_' + str(i) + '.png')
                    img_stage = cv2.resize(img_read, dsize=None, fx=H/1080, fy=W/1920)
                    
                    jug = cv2.matchTemplate(img_trm, img_stage, cv2.TM_CCORR_NORMED)
                    minVal, maxVal, minLoc, maxLoc = cv2.minMaxLoc(jug)
                    
                    if maxVal > val_stage:
                        stage_num = i
                        val_stage = maxVal       
                        
                ''' 試合開始判定画像を読み込む '''
                # ルールに応じて変える
                if rule == 'turf':
                    img_read = cv2.imread('.\\keyobject\\time_259.png')
                    img_time = cv2.resize(img_read, dsize=None, fx=H/1080, fy=W/1920)
                    
                else:
                    img_read = cv2.imread('.\\keyobject\\time_459.png')
                    img_time = cv2.resize(img_read, dsize=None, fx=H/1080, fy=W/1920) 
                       
        
            elif fcount > frame_rule:
                if frame_start == 0:               
                    ''' 試合開始の判定 '''
                    img_trm = frame[TL_time[0][1] : BR_time[0][1], TL_time[0][0] : BR_time[0][0]]
                    jug = cv2.matchTemplate(img_trm, img_time, cv2.TM_CCORR_NORMED)
                    minVal, maxVal, minLoc, maxLoc = cv2.minMaxLoc(jug) 
                       
                    if maxVal > threshold:     
                        frame_start = fcount - round(fps*1)  
    
                
                elif frame_end == 0:
                    ''' 試合終了の判定 '''
                    img_trm = frame[TL_time[1][1] : BR_time[1][1], TL_time[1][0] : BR_time[1][0]]
                    jug = cv2.matchTemplate(img_trm, img_fin, cv2.TM_CCORR_NORMED)
                    minVal, maxVal, minLoc, maxLoc = cv2.minMaxLoc(jug) 
                    
                    val_list.append([fcount, maxVal])
                       
                    if maxVal > threshold:     
                        frame_end = fcount    
    
                else:       
                    break
                                                      
        video.release

        if rule == 'zones':
            idx = stage_num + 1
            zones_num = stage_list[idx][2]
        else:
            zones_num = 0
        
        
        status_list = [['rule', 'stage_num', 'zones_num', 'fps', 'frame_all', 'frame_start', 'frame_end'],
                       [rule, stage_num, zones_num, fps, frame_all, frame_start, frame_end]] 
        
        # CSV出力
        with open(out_path, 'w') as file:
            writer = csv.writer(file, lineterminator='\n')
            writer.writerows(status_list)  
        
        print('完了')
        
    


def main():
    ''' メイン処理 '''   
    for i in range(2, 6):
        # ビデオディレクトリ取得 '*'はワイルドカード
        fnames = glob.glob('.\\DAY' + str(i) + '\\PL-DAY' + str(i) + '_*.avi' )
        
        for video_path in fnames:
            video_name, video_ext = os.path.splitext(os.path.basename(video_path))
            video_dir = os.path.dirname(video_path)    
          
            out_path = video_dir + '\\' + video_name + '_status.csv'
            
            print('=========================')
            print(video_name)

            getStatus(video_path, out_path)
            
            
        print('=========================')


    
if __name__ == "__main__":    
    main()
 



