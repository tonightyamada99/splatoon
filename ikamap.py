# -*- coding: utf-8 -*-
"""
Created on Sun Feb 16 02:35:40 2020

@author: Yamada
"""

import cv2
import os
import csv
import math
import csvread
import numpy as np


# 一致率の閾値
threshold = 0.4

# 何フレームごとに処理を行ったか
frame_skip = 30
  

def drawPointOverlook(point_list, stage_num, rule, method):
    ''' 俯瞰視点の画像に座標点を描画 '''
    # 俯瞰視点画像読み込み
    img_ol = cv2.imread('.\\img_overlook\\img_overlook_' + str(stage_num) + '_' + rule + '.png') 
    height, width = img_ol.shape[:2]

    if method == 'point' or method == 'p': 
        # 点で描画
        for (doa, x, y) in point_list:
            x_ol = round(x * width)
            y_ol = round(y * height)

            if doa == 9:
                # やられた瞬間
                cv2.circle(img_ol, (x_ol, y_ol), 2, (255, 0, 255), -1)
            elif doa == 1:
                # 生存
                cv2.circle(img_ol, (x_ol, y_ol), 2, (255, 255, 0), -1)
            elif doa == 2:
                # スペシャル
                cv2.circle(img_ol, (x_ol, y_ol), 2, (0, 255, 255), -1)

    elif method == 'line' or method == 'l':
        # 線で描画
        x_pre = round(point_list[0][1] * width)
        y_pre = round(point_list[0][2] * height)
        point_pre = (x_pre, y_pre)
        
        for i in range(1, len(point_list)):
            doa = point_list[i][0]
            x_now = round(point_list[i][1] * width)
            y_now = round(point_list[i][2] * height)
            point_now = (x_now, y_now)
        
            if doa == 9:
                cv2.line(img_ol, point_pre, point_now, (255, 0, 255), 2)
            elif doa == 1:
                cv2.line(img_ol, point_pre, point_now, (255, 255, 0), 2)
            elif doa == 2:
                cv2.line(img_ol, point_pre, point_now, (0, 255, 255), 2)
                
            point_pre = point_now
            
    else:
        print('Enter "Method" in "line" or "point"')
                
            
    return img_ol 


def correctPointList(point_list, point_respawn):
    ''' 捕捉できなかったフレームの座標を線形補間 '''
    # 最初の方はどう考えてもalive
    frame_alive = int(60 / frame_skip * 2)
    for i in range(frame_alive):
        point_list[i][0] = 1 
    
    # 線形補間前の下準備
    tmp_point_list = []
    for i in range(len(point_list)):
        doa_pre = point_list[i-1][0]
        doa     = point_list[i][0]
        x       = point_list[i][1]
        y       = point_list[i][2]
        maxVal  = point_list[i][3]
    
        if doa == 0:
            if doa_pre != 0:
                # やられた瞬間(1or2 -> 0)を"9"と記録
                doa = 9     
            else:
                # やられている間の座標はリスポーン地点
                x = point_respawn[0]     
                y = point_respawn[1]
                
        tmp_point =  [doa, x, y, maxVal]
        tmp_point_list.append(tmp_point) 
        

    # ここから線形補間の処理
    cor_point_list = []  
           
    #１個目の座標
    doa   = tmp_point_list[0][0]
    x_pre = tmp_point_list[0][1]
    y_pre = tmp_point_list[0][2]
    cor_point_list.append([doa, x_pre, y_pre])
    
    # 一致率が閾値以下のときには記録をスキップして、次に閾値を上回ったらすべて補間する。
    # 記録をスキップした総数 = 記録する座標の個数（最低でも1）
    skip_count = 0
    # スキップ中のイカランプの状態
    tmp_doa_list = []  
    
    for i in range(1, len(point_list)):
        # 現在の座標など
        doa     = tmp_point_list[i][0] 
        x_now   = tmp_point_list[i][1]
        y_now   = tmp_point_list[i][2]
        maxVal  = tmp_point_list[i][3]

        # スキップカウントをすすめる
        skip_count += 1 
        tmp_doa_list.append(doa)
        
        if doa != 0:           
            if maxVal > threshold:  
                # 一致率が閾値が高い場合は記録を行う
                # 閾値より低い場合は座標の記録をスキップ
                for j in range(skip_count):    
                    # 前の座標と現在の座標で線形補間
                    cor_doa = tmp_doa_list[j]
                    # 2点を結ぶ直線を比率で分割する点
                    cor_x = (x_pre * (skip_count - (j+1)) + x_now * (j+1)) / skip_count
                    cor_y = (y_pre * (skip_count - (j+1)) + y_now * (j+1)) / skip_count
                    # 補間した座標を記録する
                    cor_point = [cor_doa, cor_x, cor_y]
                    cor_point_list.append(cor_point)
    
                # １個前の座標を置き換える
                x_pre = x_now
                y_pre = y_now   
                # カウントリセット
                skip_count = 0
                tmp_doa_list = []            
    
    
    return cor_point_list
        
        
def main():
    ''' メイン処理 '''
    # 対象の試合
    match = 'PL-DAY2_1-1'
    stage_num = 4
    rule = 'clam'
    # リスポーン地点の座標（ステージごとに記録しておいて呼び出す形にしたい）
    respawn = [(0.1515625, 0.1925925), (0.875, 0.75)]  # あまび FHDで(291, 208) (1680, 810)
    # 対象プレイヤー
    player_list = [i for i in range(1, 9)]
    

    # CSV読み込み
    csv_path = match + '_test.csv'
    all_list =  csvread.csvread(csv_path, 's')
    
    for player_num in player_list:
        # 最初の位置はリスポーン地点
        if player_num <= 4:
            point_respawn = respawn[0]
        elif player_num >= 5:
            point_respawn = respawn[1]
            
        point_list = [[1, point_respawn[0], point_respawn[1], 1]]
        
        # CSVから対象プレイヤー部分を抜粋
        for i in range(2, len(all_list)):            
            doa     = int(all_list[i][(player_num-1) * 4])
            point_x = float(all_list[i][(player_num-1) * 4 + 1])
            point_y = float(all_list[i][(player_num-1) * 4 + 2])
            maxVal  = float(all_list[i][(player_num-1) * 4 + 3])
            
            point_list.append([doa, point_x, point_y, maxVal])
            
        # 座標修正
        cor_point_list = correctPointList(point_list, point_respawn)
        
        # 画像に座標を描画
        method = 'line'
        output_path = match + '_position_overlook_player' + str(player_num) + '_' + method + '.png'
        img_drawn = drawPointOverlook(cor_point_list, stage_num, rule, method)
        cv2.imwrite(output_path, img_drawn)  
        
    
    
if __name__ == "__main__":
    main()
              