# -*- coding: utf-8 -*-

import cv2
import sys
import csv
import glob
import os.path
import numpy as np
from PIL import Image, ImageDraw, ImageFont

import csvread
import ikaLamp
import ikaRule
import ikaStage
import ikaStartEnd


# 視点指定のウィンドウ関連
name_window = 'Select Viewpoint and Player Number'
name_track_1 = 'Viewpoint'
name_track_2 = 'User Num'
width_window = 960

text_how =  'Viewpoint -> 0:俯瞰 1:主観 を選択\n'
text_how += 'User Num  -> イカランプ位置を左から1～4で指定\n'
text_how += '指定完了したらESCで終了'

# フォント
font_path = 'C:\\Users\\Yamada\\AppData\\Local\\Microsoft\\Windows\\Fonts\\Cica-Regular.ttf'

# 処理状況メーターの長さ
length_meter = 20



def selectViewpoint(frame): 
    ''' フレーム表示して視点と位置を指定 '''    
    # 最初にウィンドウを生成
    cv2.namedWindow(name_window)
    
    # フレーム画像リサイズ
    H, W = frame.shape[:2]
    scale = width_window / W 
    resize_frame = cv2.resize(frame, None, fx=scale, fy=scale)
    
    # 説明文画像
    height_window = round(width_window / 10)
    image = Image.new('RGB', (width_window, height_window), (224, 224, 224))
    
    # 文字描画
    size = round(height_window / 3 * 0.8)
    font = ImageFont.truetype(font_path, size=size)
    draw = ImageDraw.Draw(image)
    draw.text((20, 10), text_how, fill=(32, 32, 32), font=font)

    # PIL -> OpenCV
    img_how = np.array(image, dtype=np.uint8)
    img_how = cv2.cvtColor(img_how, cv2.COLOR_RGB2BGR)
    
    
    # 画像表示
    img_prv = cv2.vconcat([img_how, resize_frame])
    cv2.imshow(name_window, img_prv) 

    # トラックバーのコールバック関数は何もしない空の関数
    def nothing(x):
        pass
    
    # トラックバーを生成
    cv2.createTrackbar(name_track_1, name_window, 0, 1, nothing)
    cv2.createTrackbar(name_track_2, name_window, 1, 4, nothing)

    # ESCが押されるまでループ
    while True:                   
        k = cv2.waitKey()
        
        if k == 27:
            # トラックバーの値を取得
            vp_num   = cv2.getTrackbarPos(name_track_1, name_window)
            user_num = cv2.getTrackbarPos(name_track_2, name_window)
            
            if vp_num == 0:
                viewpoint = 'obj' # 俯瞰:objective
                user_num = 0
            elif vp_num == 1:
                viewpoint = 'sub' # 主観:subjective
                
            # 終了
            cv2.destroyAllWindows()                
            break
                    
        
    return viewpoint, user_num
        


def getStatus(video_path):
    ''' 試合動画の情報を取得する '''
    # 出力先・名前の設定    
    video_name, video_ext = os.path.splitext(os.path.basename(video_path))
    video_dir = os.path.dirname(video_path)    
  
    out_path = video_dir + '\\' + video_name + '_status.csv'


    # 取得状況の把握
    if (os.path.exists(out_path)):
        print('情報取得済み')
        status_list = csvread.readAsList(out_path)
        
    else:
        # 動画読み込み
        video = cv2.VideoCapture(video_path)   
        fps = video.get(cv2.CAP_PROP_FPS)
        frame_all = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
        
        # 取得する変数たち
        frame_rule  = 0
        rule        = 'nodata'
        stage_num   = 0
        frame_start = 0
        frame_end   = 0
        viewpoint   = 'nodata'
        user_num    = 0
        
        
        # ここから動画処理
        fcount = 0
        while(video.isOpened()):
            # フレーム取得
            ret, frame = video.read()
        
            # フレーム取得できなかったら終了
            if not ret:
                break
          
            # フレームカウント
            fcount += 1  
            

            # 進行状況をコマンドラインに表示
            ratio = fcount / frame_all
            
            meter_count = round(length_meter*ratio)
            meter = '#' * meter_count
            meter += ' ' * (length_meter - meter_count)
        
            sys.stdout.flush()     
            sys.stdout.write('\rMatch Status  [' + meter + '] ' + str(round(ratio*100, 2)) + '% ')
            
        
            if frame_rule == 0:
                # ルール表示の判定
                jug_frame = ikaRule.judgeRule(frame)
                
                if jug_frame == True:     
                    # 「ル」が表示されてから1秒後
                    # エフェクトによってルール名などが表示されていないため
                    frame_rule = fcount + round(fps*1)              
            
            
            elif fcount == frame_rule:
                # ルール取得
                rule = ikaRule.getRule(frame)
                
                # ステージ取得
                stage_num = ikaStage.getStage(frame)
                
                
            elif frame_start == 0:  
                # 試合開始の判定
                if rule == 'turf':
                    jug_start = ikaStartEnd.judgeStartTurf(frame)
                else:
                    jug_start = ikaStartEnd.judgeStartGachi(frame)
                
                if jug_start == True:
                    # 試合開始は1秒前
                    # 試合開始ピッタリは時計表示がなくて認識できない
                    frame_start = fcount - round(fps*1)  
                    
                    # チームカラーの取得
                    team_color = ikaLamp.getTeamColor(frame)
                    
                    # 視点の取得
                    # viewpoint, user_num = 'obj', 0
                    viewpoint, user_num = selectViewpoint(frame)
    
    
            elif frame_end == 0:
                # 試合終了の判定
                jug_end = ikaStartEnd.judgeEnd(frame)
                
                if jug_end == True:    
                    frame_end = fcount    
    
            else:       
                break

            
        video.release
        # ここまで動画処理   
        
        sys.stdout.flush()     
        sys.stdout.write('\rMatch Status  [' + '#' * length_meter + '] 100.00% ')        

        # 記録用リスト        
        status_list = [['fps', 'frame_all', 'frame_start', 'frame_end', 'viewpoint', 'rule', 'stage_num', 'team_color_alfa', 'team_color_bravo', 'user_num'],
                       [fps, frame_all, frame_start, frame_end, viewpoint, rule, stage_num] + team_color + [user_num]] 
        
        # CSV出力
        with open(out_path, 'w') as file:
            writer = csv.writer(file, lineterminator='\n')
            writer.writerows(status_list)  
        
        
    return status_list



def main():
    ''' メイン処理 '''   
    # ビデオディレクトリ取得 *はワイルドカード
    fnames = glob.glob('.\\capture_movie\\movie*.avi' )
    
    for video_path in fnames:
        
        print('==================================================')
        print(os.path.basename(video_path))

        status_list = getStatus(video_path)
        
        print('--------------------------------------------------')
        for idx in range(len(status_list[0])):
            print(status_list[0][idx], status_list[1][idx])
                    
        
    print('==================================================')


    
if __name__ == "__main__":    
    main()
 



