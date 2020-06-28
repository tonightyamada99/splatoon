#!/usr/bin/env python
# coding: utf-8
# In[ ]:
# -*- coding: utf-8 -*-
import cv2
import csv
import os.path
import numpy as np
import pandas as pd

# 指定した位置(x,y)の半径rの範囲の円内の色割合を取得する関数
# def getColorRatio(base_frame, frame, x, y, r):
    # 初期画像との差分で比較する
        #hsv = cv2.absdiff(base_hsv, hsv)

def getColorRatio(frame, x, y, r):
    # フレームをHSVに変換
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask = np.zeros(hsv.shape, dtype=np.uint8)
        cv2.circle(mask, (x, y), r, (255, 255, 255), -1)
        hsv = hsv & mask
        #hsv = hsv[top : bottom, left : right]
        # 取得する色の範囲を指定する
        lower_yellow = np.array([20, 100, 140])
        upper_yellow = np.array([90, 255, 255])
               
        lower_blue = np.array([110, 100, 90])
        upper_blue = np.array([254, 255, 255])
               
        # HSV の範囲指定で2値化する。
        binary_yellow = cv2.inRange(hsv, lower_yellow, upper_yellow)
        binary_blue = cv2.inRange(hsv, lower_blue, upper_blue)
        # 全画素に占める割合
        yellow_ratio = cv2.countNonZero(binary_yellow) / (r * r * 3.14)
        blue_ratio = cv2.countNonZero(binary_blue) / (r * r * 3.14)
        other_ratio =  1 - yellow_ratio - blue_ratio

        # numpyで配列を作って返す
        arr = np.asarray([yellow_ratio, blue_ratio, other_ratio])
        return arr


def trackingColor(video_path, frame_start, frame_end):
   
        video_name, video_ext = os.path.splitext(os.path.basename(video_path))
        video = cv2.VideoCapture(video_path)
        W = video.get(cv2.CAP_PROP_FRAME_WIDTH)
        H = video.get(cv2.CAP_PROP_FRAME_HEIGHT)
        fps = video.get(cv2.CAP_PROP_FPS)
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        #out = cv2.VideoWriter(video_name + '_tracking_color.mp4', fourcc, fps, (int(W), int(H)))
        color_arr = []
        fcount = 0   
        while(video.isOpened()):
               ret, frame = video.read()
               if not ret:
                       break
               fcount = fcount + 1 
               if fcount == frame_start:
                       base_hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
               if frame_start <= fcount < frame_end:
                       # 色割合をリストに格納
                       color_ratio = getColorRatio(frame, 540, 960, 1920)
                       color_arr.append(color_ratio)
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
               elif fcount == frame_end:
                       break
        cv2.destroyAllWindows()                         
        video.release
        #out.release
        # CSV出力
        np.savetxt(video_name + '_tracking_color_ratio.csv', color_arr, delimiter=',')
def main():
        video_path = 'overlook_turf_stage0.mp4'
        trackingColor(video_path, 484, 5887)   
if __name__ == "__main__":
        main()



