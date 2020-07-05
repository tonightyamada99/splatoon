#!/usr/bin/env python

import cv2
import csv
import os.path
import numpy as np
import pandas as pd


def getColorRatio(frame, x, y, r):
        # フレームをHSVに変換
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask = np.zeros(hsv.shape, dtype=np.uint8)
        cv2.circle(mask, (x, y), r, (255, 255, 255), -1)
        hsv = hsv & mask
        # hsv = hsv[top : bottom, left : right]
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

        # リストを作って返す
        list = [yellow_ratio, blue_ratio, other_ratio]
        return arr


def getColorRatioNawabari(frame):
        # フレームをHSVに変換
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # 取得する色の範囲を指定する
        lower_yellow = np.array([20, 100, 140])
        upper_yellow = np.array([90, 255, 255])
               
        lower_blue = np.array([110, 100, 90])
        upper_blue = np.array([254, 255, 255])
               
        # HSV の範囲指定で2値化する。
        binary_yellow = cv2.inRange(hsv, lower_yellow, upper_yellow)
        binary_blue = cv2.inRange(hsv, lower_blue, upper_blue)

        # 各色の割合
        yellow_count = cv2.countNonZero(binary_yellow)
        blue_count = cv2.countNonZero(binary_blue) 

        # リストを作って返す
        list = [yellow_count, blue_count]
        return list

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



