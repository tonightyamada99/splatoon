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
import CvOverlayImage
from PIL import Image, ImageDraw, ImageFilter, ImageFont


font_path = '‪C:\Windows\Fonts\FOT-RowdyStd-EB.otf'
color_heatmap = [(136, 32, 29), (183, 104, 0), (233, 160, 0), (150, 158, 0), (68, 153, 0),
                 (31, 195, 143), (0, 241, 255), (0, 152, 243), (18, 0, 230), (51, 27, 123)]

def pil2cv(image):
    ''' PIL型 -> OpenCV型 '''
    new_image = np.array(image, dtype=np.uint8)
    if new_image.ndim == 2:  # モノクロ
        pass
    elif new_image.shape[2] == 3:  # カラー
        new_image = new_image[:, :, ::-1]
    elif new_image.shape[2] == 4:  # 透過
        new_image = new_image[:, :, [2, 1, 0, 3]]
    return new_image

def img_add_msg(img, point, message):
    ''' 画像に文字を入れる　その1 '''
    font_path = '‪C:\Windows\Fonts\FOT-RowdyStd-EB.otf'          # Windowsのフォントファイルへのパス
    font_size = 20                             # フォントサイズ
    font = ImageFont.truetype(font_path, font_size)     # PILでフォントを定義
    img = Image.fromarray(img)                          # cv2(NumPy)型の画像をPIL型に変換
    draw = ImageDraw.Draw(img)                          # 描画用のDraw関数を用意
 
    # テキストを描画（位置、文章、フォント、文字色（BGR+α）を指定）
    draw.text(point, message, font=font, fill=(0, 0, 0, 0))
    img = np.array(img)                                 # PIL型の画像をcv2(NumPy)型に変換
    return img  

def img_add_text(img, point, message):
    ''' 画像に文字を入れる　その2 '''
    font_path = '‪C:\Windows\Fonts\FOT-RowdyStd-EB.otf'          # Windowsのフォントファイルへのパス
    font_size = 20                             # フォントサイズ
    font = ImageFont.truetype(font_path, font_size)     # PILでフォントを定義
    draw = ImageDraw.Draw(img)                          # 描画用のDraw関数を用意
 
    # テキストを描画（位置、文章、フォント、文字色（BGR+α）を指定）
    draw.text(point, message, font=font, fill=(0, 0, 0, 255))       
    return img  

def overlook(video_path, player_num, stage_num):
    ''' 俯瞰視点に座標を記録 '''
    video_name, video_ext = os.path.splitext(os.path.basename(video_path))
    video_dir = os.path.dirname(video_path)
    
    csv_path = video_dir + '\\' + video_name + '\\' + video_name + '_pointlist_player' + str(player_num) + '_int1s.csv'
    output_name = video_dir + '\\' + video_name + '\\' + video_name + '_position_overlook_player' + str(player_num) + '_int1s.png'
    
    if(os.path.exists(csv_path)):
        
        point_list =  csvread.csvread(csv_path, 's')            
        status_list = csvread.csvread(video_dir + '\\' + video_name + '\\' + video_name + '_status.csv', 's')
        
        rule = status_list[1][0]
        #    stage_num = int(status_list[1][1])
        
        ''' Draw Points on Overlook Image '''
        img_ol = cv2.imread('.\\overlook_img\\overlook_' + str(stage_num) + '_' + rule + '.png') 
        height_ol, width_ol, c = img_ol.shape


        for (doa, y, x) in point_list[1:len(point_list)]:
            y_ol = round(float(y) * width_ol)
            x_ol = round(float(x) * height_ol)
            
            if doa == '0':
                cv2.circle(img_ol, (y_ol, x_ol), 5, (255, 255, 0), -1)
            elif doa == '1':
                cv2.circle(img_ol, (y_ol, x_ol), 5, (255, 0, 255), -1)
            else:
                continue
            
        cv2.imwrite(output_name, img_ol)  


        
def transform(video_path, stage_num, player_num, rotate):
    ''' 俯瞰視点 → ナワバリマップの座標変換 '''
    video_name, video_ext = os.path.splitext(os.path.basename(video_path))
    video_dir = os.path.dirname(video_path)
    
    csv_path = video_dir + '\\' + video_name + '\\' + video_name + '_pointlist_player' + str(player_num) + '_int1s.csv'
    
    if(os.path.exists(csv_path)):
        
        point_list =  csvread.csvread(csv_path, 's')            
        status_list = csvread.csvread(video_dir + '\\' + video_name + '\\' + video_name + '_status.csv', 's')
        
        rule = status_list[1][0]
        #    stage_num = int(status_list[1][1])
        
        img_ol = cv2.imread('.\\overlook_img\\overlook_' + str(stage_num) + '_' + rule + '.png') 
        height_ol, width_ol, c = img_ol.shape
            
        ''' Map Drawing Status '''
        img_map = cv2.imread('.\\map\\map_' + str(stage_num) + '_' + rule + '_trans.png')
        #h, w, c = img_map.shape
        
        
        ''' Read Map and Overlook Status CSV '''
        stage_status_list = csvread.csvread('.\\overlook_img\\overlook_status.csv', 's')
        
        x_center = round(float(stage_status_list[stage_num + 1][1]) * height_ol)
        y_center = round(float(stage_status_list[stage_num + 1][2]) * width_ol)
        x_top    = round(float(stage_status_list[stage_num + 1][3]) * height_ol)
        x_bottom = round(float(stage_status_list[stage_num + 1][4]) * height_ol)
        y_tl     = round(float(stage_status_list[stage_num + 1][5]) * width_ol)
        y_tr     = round(float(stage_status_list[stage_num + 1][6]) * width_ol)
        y_bl     = round(float(stage_status_list[stage_num + 1][7]) * width_ol)
        y_br     = round(float(stage_status_list[stage_num + 1][8]) * width_ol)
        x_vp1    = round(float(stage_status_list[stage_num + 1][9]) * height_ol)
        x_vp2    = round(float(stage_status_list[stage_num + 1][10]) * height_ol)
        
        
        map_status_list = csvread.csvread('.\\map\\map_status.csv', 's')
        
        Y_center = float(map_status_list[stage_num + 1][1])
        X_center = float(map_status_list[stage_num + 1][2])
        Y_TL     = float(map_status_list[stage_num + 1][3])
        X_TL     = float(map_status_list[stage_num + 1][4])
        Y_TR     = float(map_status_list[stage_num + 1][5])
        X_TR     = float(map_status_list[stage_num + 1][6])
        Y_BL     = float(map_status_list[stage_num + 1][7])
        X_BL     = float(map_status_list[stage_num + 1][8])
        Y_BR     = float(map_status_list[stage_num + 1][9])
        X_BR     = float(map_status_list[stage_num + 1][10])
        degree   = float(map_status_list[stage_num + 1][11])
        
        
        ''' Correct Points List '''
        # 座標変換：問題の箇所
        def x_correct(x):
            x_corrected = (height_ol - x_vp1) / (x - x_vp1) * x
            return round(x_corrected)
        
        def y_correct(x, y):
            if y <= width_ol/2:
                A = (x_bottom - x) / (x_bottom - x_top) * (y_tl - y_bl) / (width_ol/2 - y_bl)
                y_corrected = (y - A*width_ol/2) / (1 - A)
            else:
                A = (x_bottom - x) / (x_bottom - x_top) * (y_tr - y_br) / (width_ol/2 - y_br)
                y_corrected = (y - A*width_ol/2) / (1 - A)
            return round(y_corrected)
        
        x_center_cor = x_correct(x_center)
        y_center_cor = y_correct(x_center, y_center)
        
        x_top_cor = x_correct(x_top)
        x_bottom_cor = x_bottom
        y_tr_cor = y_correct(x_top, y_tr)
        y_bl_cor = y_correct(x_bottom, y_bl)
        y_tl_cor = y_correct(x_top, y_tl)
        y_br_cor = y_correct(x_bottom, y_br)
        
        x_length = x_bottom - x_top
        y_length = y_br - y_bl
        
        X_length = math.sqrt((X_TL - X_BL)**2 + (Y_TL - Y_BL)**2)
        Y_length = math.sqrt((X_TL - X_TR)**2 + (Y_TL - Y_TR)**2)
        
        theta = math.pi / 180 * degree
        
        if rotate == 'y':
            if not stage_num == 22:            
                if player_num >= 5:
                    theta += math.pi
            
        map_point_list = [['dead-or-alive', 'point']]
        
        for i in range(1, len(point_list)):
            y_data = int(float(point_list[i][1]) * width_ol)
            x_data = int(float(point_list[i][2]) * height_ol)
            
            y_cor = y_correct(x_data, y_data)  
            x_cor = x_correct(x_data)  
            
            y_resize = (y_cor - y_center_cor) * Y_length/y_length    
            x_resize = (x_cor - x_center_cor) * X_length/x_length
            
            y_map = x_resize * math.sin(theta) + y_resize * math.cos(theta) + Y_center 
            x_map = x_resize * math.cos(theta) - y_resize * math.sin(theta) + X_center
            
            map_point_list.append([point_list[i][0], (round(y_map), round(x_map))])
            
        return map_point_list
    
    else:
    
        return 'nodata'  
    
    
def dot_hp(video_path, player_num, stage_num, map_point_list, output_name, texts):
    ''' マップに位置の点を描く HP用 '''
    video_name, video_ext = os.path.splitext(os.path.basename(video_path))
    video_dir = os.path.dirname(video_path)
   
    status_list = csvread.csvread(video_dir + '\\' + video_name + '\\' + video_name + '_status.csv', 's')
    rule = status_list[1][0]

    if map_point_list == 'nodata':
        img_dot = cv2.imread('.\\map\\map_' + str(stage_num) + '_' + rule + '_nodata.png')
        cv2.imwrite(output_name, img_dot)  
    
    else:     
        img_address = cv2.imread('address.png', cv2.IMREAD_UNCHANGED) 
        height_ad, width_ad, c = img_address.shape
        
        img_cross = cv2.imread('cross.png', cv2.IMREAD_UNCHANGED) 
        cross_size = (32, 32)
        img_cross_resize = cv2.resize(img_cross, cross_size)
        
        img_dot = cv2.imread('.\\map\\map_' + str(stage_num) + '_' + rule + '_white.png')     
        height_img, width_img, c = img_dot.shape
        for i in range(len(map_point_list)):    
            if map_point_list[i][0] == '0':
                cv2.circle(img_dot, map_point_list[i][1], 5, (255, 255, 0), -1)
            elif map_point_list[i][0] == '1':
                cv2.circle(img_dot, map_point_list[i][1], 5, (255, 0, 255), -1)
            else:
                continue
            
        for i in range(len(map_point_list)):
            if map_point_list[i][0] == '1':
                cross_point = (int(map_point_list[i][1][0] - cross_size[0]/2), int(map_point_list[i][1][1] - cross_size[1]/2))
                img_dot = CvOverlayImage.overlay(img_dot, img_cross_resize, cross_point)
             
        if stage_num == 0:
            img_dot = img_add_msg(img_dot, (500, 20), texts[0])
            img_dot = img_add_msg(img_dot, (500, 44), texts[1])    
            img_dot = img_add_msg(img_dot, (500, 80), texts[2])    
            img_dot = img_add_msg(img_dot, (500, 104), texts[3])    
            img_dot = img_add_msg(img_dot, (500, 128), texts[4])
            
        else:
            img_dot = img_add_msg(img_dot, (20, 20), texts[0])
            img_dot = img_add_msg(img_dot, (20, 44), texts[1])    
            img_dot = img_add_msg(img_dot, (20, 80), texts[2])    
            img_dot = img_add_msg(img_dot, (20, 104), texts[3])    
            img_dot = img_add_msg(img_dot, (20, 128), texts[4])
        
        
        if stage_num == 0: 
            img_dot = CvOverlayImage.overlay(img_dot, img_address, (width_img - width_ad, height_img - height_ad))
        else:
            img_dot = CvOverlayImage.overlay(img_dot, img_address, (0, height_img - height_ad))
            
        cv2.imwrite(output_name, img_dot)  
    
    
def line_hp(video_path, player_num, stage_num, map_point_list, output_name, texts):
    ''' マップに移動推移の線を描く  HP用 '''
    video_name, video_ext = os.path.splitext(os.path.basename(video_path))
    video_dir = os.path.dirname(video_path)
   
    status_list = csvread.csvread(video_dir + '\\' + video_name + '\\' + video_name + '_status.csv', 's')
    rule = status_list[1][0]

    if map_point_list == 'nodata':
        img_line = Image.open('.\\map\\map_' + str(stage_num) + '_' + rule + '_nodata.png')
        img_line.save(output_name)  
    
    else:
        ''' Draw Line '''        
        img_line = Image.open('.\\map\\map_' + str(stage_num) + '_' + rule + '_white.png')
        width_img, height_img = img_line.size        
        draw = ImageDraw.Draw(img_line)
     
        point_prev = map_point_list[1][1]
        for i in range(len(map_point_list)):   
            
            color_line = (int(255 * i/len(map_point_list)), int(255 - 255 * i/len(map_point_list)), 255)
            
            if map_point_list[i][0] == '0' or map_point_list[i][0] == '1':
                draw.line((point_prev, map_point_list[i][1]), fill=color_line, width=4)
                point_prev = map_point_list[i][1]
                
            elif map_point_list[i][0] == '2':
                if i < len(map_point_list) - 1:
                    point_prev = map_point_list[i+1][1] 

            elif map_point_list[i][0] == '9':
                if i < len(map_point_list) - 1:
                    continue


        ''' Draw Death Point '''
        cross_size = (32, 32)        
        img_cross = Image.open('cross.png')
        img_cross = img_cross.resize(cross_size)
        img_cross = img_cross.convert('RGBA')
    
        for i in range(len(map_point_list)):
            if map_point_list[i][0] == '1':
                cross_point_y = int(map_point_list[i][1][0] - cross_size[0]/2)
                cross_point_x = int(map_point_list[i][1][1] - cross_size[1]/2)  
                
                for y in range(cross_size[0]):
                    for x in range(cross_size[1]):
                        r, g, b, a = img_cross.getpixel((y, x))
                           
                        if a == 0:
                            continue
                        else:
                            if (y + cross_point_y) < width_img and (x + cross_point_x) < height_img:                           
                                img_line.putpixel((y + cross_point_y, x + cross_point_x), (r, g, b, 255))

        ''' Draw Scale '''    
        img_scale = Image.open('scale_line.png')
        img_scale = img_scale.convert('RGBA')
        width_sc, height_sc = img_scale.size  
    
        if stage_num == 0:
            for x in range(height_sc):
                for y in range(width_sc):
                    r, g, b, a = img_scale.getpixel((y, x))
                       
                    if a == 0:
                        continue
                    else:
                        img_line.putpixel((y, height_img - height_sc + x), (r, g, b, 255)) 
           
        else:
            for x in range(height_sc):
                for y in range(width_sc):
                    r, g, b, a = img_scale.getpixel((y, x))
                       
                    if a == 0:
                        continue
                    else:
                        img_line.putpixel((width_img - width_sc + y, height_img - height_sc + x), (r, g, b, 255)) 
                                          
        ''' Draw Address '''    
        img_address = Image.open('address.png')
        img_address = img_address.convert('RGBA')
        width_ad, height_ad = img_address.size  
    
        if stage_num == 0:
            for x in range(height_ad):
                for y in range(width_ad):
                    r, g, b, a = img_address.getpixel((y, x))
                       
                    if a == 0:
                        continue
                    else:
                        img_line.putpixel((width_img - width_ad + y, height_img - height_ad + x), (r, g, b, 255)) 
            
        else:
            for x in range(height_ad):
                for y in range(width_ad):
                    r, g, b, a = img_address.getpixel((y, x))
                       
                    if a == 0:
                        continue
                    else:
                        img_line.putpixel((y, height_img - height_ad + x), (r, g, b, 255)) 

        
        if stage_num == 0:
            img_line = img_add_text(img_line, (500, 20), texts[0])
            img_line = img_add_text(img_line, (500, 44), texts[1])    
            img_line = img_add_text(img_line, (500, 80), texts[2])    
            img_line = img_add_text(img_line, (500, 104), texts[3])    
            img_line = img_add_text(img_line, (500, 128), texts[4])
            
        else:
            img_line = img_add_text(img_line, (20, 20), texts[0])
            img_line = img_add_text(img_line, (20, 44), texts[1])    
            img_line = img_add_text(img_line, (20, 80), texts[2])    
            img_line = img_add_text(img_line, (20, 104), texts[3])    
            img_line = img_add_text(img_line, (20, 128), texts[4])
                        
        img_line.save(output_name)
        
        
        
def heatmap_hp(video_path, player_num, stage_num, map_point_list, heatmap_fps, output_name, texts):
    ''' マップに位置のヒートマップを描く HP用  '''
    hist_size = 64
    max_sec = 30 # sec
    hist_max = heatmap_fps * max_sec   
    

    video_name, video_ext = os.path.splitext(os.path.basename(video_path))
    video_dir = os.path.dirname(video_path)
   
    status_list = csvread.csvread(video_dir + '\\' + video_name + '\\' + video_name + '_status.csv', 's')
    rule = status_list[1][0]

    if map_point_list == 'nodata':
        img_nodata = cv2.imread('.\\map\\map_' + str(stage_num) + '_' + rule + '_nodata.png')
        cv2.imwrite(output_name, img_nodata)  
    
    else: 
        img_map = cv2.imread('.\\map\\map_' + str(stage_num) + '_' + rule + '_white.png')
        h, w, c = img_map.shape
        
        csv_dir = video_dir + '\\' + video_name + '\\' + video_name + '_hist_player' + str(player_num) + '_int1s_fps' + str(heatmap_fps) + '_r' + str(hist_size) + '.csv'
    
        if(os.path.exists(csv_dir)):
            hist_list = csvread.csvread(csv_dir, 'i')
            
        else:
            map_hist_doa = []
            map_hist_y = []
            map_hist_x = []
            
            skip_count = 1
            y_pre = map_point_list[1][1][0]
            x_pre = map_point_list[1][1][1]
            
            for i in range(2, len(map_point_list)):
                
                doa = map_point_list[i][0]
                
                if doa == '0':
                    y_now = map_point_list[i][1][0]
                    x_now = map_point_list[i][1][1]
                
                    skiped_fps = heatmap_fps * skip_count
                    for j in range(skiped_fps):
                        y = (skiped_fps - j) / skiped_fps * y_pre + j / skiped_fps * y_now
                        x = (skiped_fps - j) / skiped_fps * x_pre + j / skiped_fps * x_now 
                        
                        map_hist_y.append(y)
                        map_hist_x.append(x)        
                        map_hist_doa.append(doa)   
    
                    y_pre = map_point_list[i][1][0]
                    x_pre = map_point_list[i][1][1]
                                                
                    skip_count = 1
                    
                if doa == '0':
                    y_now = map_point_list[i][1][0]
                    x_now = map_point_list[i][1][1]
                    
                elif doa == '9':
                    skip_count += 1
                    
            
            hist_list = np.zeros((h, w), np.uint16)
            for i in range(w):
                for j in range(h):
                    hist_count = 0
                    
                    for k in range(len(map_hist_doa)): 
                        if map_hist_doa[k] == '0':
                            len_points = math.sqrt((map_hist_y[k] - i)**2 + (map_hist_x[k] - j)**2)
                            if len_points <= hist_size:
                                hist_count += 1
                            
                    hist_list[j][i] = hist_count
                    
                
            with open(csv_dir, 'w') as file:
                writer = csv.writer(file, lineterminator='\n')
                writer.writerows(hist_list)

        
        ''' Make hist tmp '''        
        img_hist = np.ones((h, w, 3), np.uint8) * 255
        for i in range(w):
            for j in range(h):
                if hist_list[j][i] == 0:
                    continue
                
                color_idx = round(hist_list[j][i] / hist_max * 10)
                if color_idx > 9:
                    color_idx = 9
                    
                img_hist[j][i] = color_heatmap[int(color_idx)]
            
        cv2.imwrite('.\\hist_tmp.png', img_hist)     
        
        
        ''' Draw Heat Color '''
        img = Image.open('.\\map\\map_' + str(stage_num) + '_' + rule + '_white.png')
        img_back = img.convert('RGBA')
        img_hist = Image.open('.\\hist_tmp.png')
        
        trans = Image.new('RGBA', img_hist.size, (0, 0, 0, 0))
        width = img_hist.size[0]
        height = img_hist.size[1]
        for x in range(width):
            for y in range(height):
                r, g, b = img_hist.getpixel((x, y))
        
                if r == 255 and g == 255 and b == 255:
                    trans.putpixel((x, y), (255, 255, 255, 0))
                else:
                    trans.putpixel((x, y), (r, g, b, 192))
        
        result = Image.alpha_composite(img_back, trans)
    
    
        ''' White out of Map '''
        img = Image.open('.\\map\\map_' + str(stage_num) + '_' + rule + '_trans.png')
        img_trans = img.convert('RGBA')
    
        for x in range(width):
            for y in range(height):
                r, g, b, a = img_trans.getpixel((x, y))
        
                if r == 255 and g == 255 and b == 255:
                    result.putpixel((x, y), (255, 255, 255, 255))    
        
        
        ''' Draw Death Point '''
        cross_size = (32, 32)
        img_cross = Image.open('cross.png')
        img_cross = img_cross.resize(cross_size)
        img_cross = img_cross.convert('RGBA')
    
        for i in range(len(map_point_list)):
            if map_point_list[i][0] == '1':
                cross_point_x = int(map_point_list[i][1][0] - cross_size[0]/2)
                cross_point_y = int(map_point_list[i][1][1] - cross_size[1]/2)  
                
                for x in range(cross_size[0]):
                    for y in range(cross_size[1]):
                        r, g, b, a = img_cross.getpixel((x, y))
                           
                        if a == 0:
                            continue
                        else:
                            result.putpixel((x + cross_point_x, y + cross_point_y), (r, g, b, 255))

        ''' Draw Scale '''    
        img_scale = Image.open('scale_heat.png')
        img_scale = img_scale.convert('RGBA')
        width_sc, height_sc = img_scale.size  
    
        if stage_num == 0:
            for x in range(height_sc):
                for y in range(width_sc):
                    r, g, b, a = img_scale.getpixel((y, x))
                       
                    if a == 0:
                        continue
                    else:
                        result.putpixel((y, h - height_sc + x), (r, g, b, 255)) 
           
        else:
            for x in range(height_sc):
                for y in range(width_sc):
                    r, g, b, a = img_scale.getpixel((y, x))
                       
                    if a == 0:
                        continue
                    else:
                        result.putpixel((w - width_sc + y, h - height_sc + x), (r, g, b, 255)) 
                        
    
        ''' Draw Address '''    
        img_address = Image.open('address.png')
        img_address = img_address.convert('RGBA')
        width_ad, height_ad = img_address.size  
    
        if stage_num == 0:
            for x in range(height_ad):
                for y in range(width_ad):
                    r, g, b, a = img_address.getpixel((y, x))
                       
                    if a == 0:
                        continue
                    else:
                        result.putpixel((w - width_ad + y, h - height_ad + x), (r, g, b, 255)) 
            
        else:
            for x in range(height_ad):
                for y in range(width_ad):
                    r, g, b, a = img_address.getpixel((y, x))
                       
                    if a == 0:
                        continue
                    else:
                        result.putpixel((y, h - height_ad + x), (r, g, b, 255)) 
       
        if stage_num == 0:
            result = img_add_text(result, (500, 20), texts[0])
            result = img_add_text(result, (500, 44), texts[1])    
            result = img_add_text(result, (500, 80), texts[2])    
            result = img_add_text(result, (500, 104), texts[3])    
            result = img_add_text(result, (500, 128), texts[4])
            
        else:
            result = img_add_text(result, (20, 20), texts[0])
            result = img_add_text(result, (20, 44), texts[1])    
            result = img_add_text(result, (20, 80), texts[2])    
            result = img_add_text(result, (20, 104), texts[3])    
            result = img_add_text(result, (20, 128), texts[4])
        
        result.save(output_name)