# -*- coding: utf-8 -*-
"""
Created on Thu May 14 15:19:56 2020

@author: Yamada
"""

import cv2
import numpy as np



def checkImgHSV(img_path): 
    ''' 画像のHSV閾値を調整 '''
    # トラックバーを作るため，まず最初にウィンドウを生成
    cv2.namedWindow("OpenCV Window")

    # トラックバーのコールバック関数は何もしない空の関数
    def nothing(x):
        pass

    # トラックバーの生成
    cv2.createTrackbar("H_min", "OpenCV Window", 0, 179, nothing)       # Hueの最大値は179
    cv2.createTrackbar("H_max", "OpenCV Window", 128, 179, nothing)
    cv2.createTrackbar("S_min", "OpenCV Window", 128, 255, nothing)
    cv2.createTrackbar("S_max", "OpenCV Window", 255, 255, nothing)
    cv2.createTrackbar("V_min", "OpenCV Window", 128, 255, nothing)
    cv2.createTrackbar("V_max", "OpenCV Window", 255, 255, nothing)

    #Ctrl+cが押されるまでループ
    try:
        while True:

            # (A)画像取得
            img_ori = cv2.imread(img_path)    # 映像を1フレーム取得
            if img_ori is None or img_ori.size == 0:    # 中身がおかしかったら無視
                continue 
            
            # (B)ここから画像処理
            image = cv2.cvtColor(img_ori, cv2.COLOR_RGB2BGR)      # OpenCV用のカラー並びに変換する
            bgr_image = cv2.resize(image, dsize=(960,540) ) # 画像サイズを半分に変更
            
            hsv_image = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2HSV)  # BGR画像 -> HSV画像


            # トラックバーの値を取る
            h_min = cv2.getTrackbarPos("H_min", "OpenCV Window")
            h_max = cv2.getTrackbarPos("H_max", "OpenCV Window")
            s_min = cv2.getTrackbarPos("S_min", "OpenCV Window")
            s_max = cv2.getTrackbarPos("S_max", "OpenCV Window")
            v_min = cv2.getTrackbarPos("V_min", "OpenCV Window")
            v_max = cv2.getTrackbarPos("V_max", "OpenCV Window")

            # inRange関数で範囲指定２値化
            bin_image = cv2.inRange(hsv_image, (h_min, s_min, v_min), (h_max, s_max, v_max)) # HSV画像なのでタプルもHSV並び

            # bitwise_andで元画像にマスクをかける -> マスクされた部分の色だけ残る
            masked_image = cv2.bitwise_and(hsv_image, hsv_image, mask=bin_image)
            
            # ラベリング結果書き出し用に画像を準備
            out_image = masked_image

            # 面積・重心計算付きのラベリング処理を行う
            num_labels, label_image, stats, center = cv2.connectedComponentsWithStats(bin_image)

            # 最大のラベルは画面全体を覆う黒なので不要．データを削除
            num_labels = num_labels - 1
            stats = np.delete(stats, 0, 0)
            center = np.delete(center, 0, 0)

            # 検出したラベルの数だけ繰り返す
            for index in range(num_labels):
                # ラベルのx,y,w,h,面積s,重心位置mx,myを取り出す
                x = stats[index][0]
                y = stats[index][1]
                w = stats[index][2]
                h = stats[index][3]
                s = stats[index][4]
                mx = int(center[index][0])
                my = int(center[index][1])
                #print("(x,y)=%d,%d (w,h)=%d,%d s=%d (mx,my)=%d,%d"%(x, y, w, h, s, mx, my) )
                
                if s > 800:
                    # ラベルを囲うバウンディングボックスを描画
                    cv2.rectangle(out_image, (x, y), (x+w, y+h), (255, 0, 255))
    
                    # 重心位置の座標と面積を表示
                    cv2.putText(out_image, "%d,%d"%(mx,my), (x-15, y+h+15), cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 0))
                    cv2.putText(out_image, "%d"%(s), (x, y+h+30), cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 0))

            # (X)ウィンドウに表示
            cv2.imshow('OpenCV Window', out_image)  # ウィンドウに表示するイメージを変えれば色々表示できる

            
            # キー入力で次の処理へ            
            k = cv2.waitKey()
            # ESCが入力されたら中断
            if k == 27:
                break


    except( KeyboardInterrupt, SystemExit):    # Ctrl+cが押されたら離脱
        cv2.destroyAllWindows()
        print( "SIGINTを検知" )

def main():
    img_path = 'name_all.png'
    checkImgHSV(img_path)
    


if __name__ == "__main__":
    main() 
