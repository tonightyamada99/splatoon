# -*- coding: utf-8 -*-

import cv2
import ikaImageProcessing as iip

                
# 要素の位置の座標
# 設定サイズ
TLBR_size = (1920, 1080)    # FHD
# win表示
TL_win = (1082, 126) 
BR_win = (1202, 168)
# 塗りポイント（ナワバリのみ）
L_pnt = 1560
R_pnt = 1700 
T_pnt = [184, 268, 352, 436, 698, 782, 866,  950]
B_pnt = [234, 318, 402, 486, 750, 834, 918, 1002]
# たおした数
L_kil = 1720
R_kil = 1770
T_kil = [206, 290, 374, 456, 730, 812, 896,  978]
B_kil = [236, 320, 404, 486, 760, 842, 926, 1008]
# スペシャルウエポン使用回数
L_spw = 1782
R_spw = 1832
T_spw = [204, 286, 370, 454, 732, 814, 898,  982]
B_spw = [234, 318, 400, 484, 762, 844, 928, 1012]

# 一致率の閾値 threshold
thd_val = 0.95

# 比較画像 win
bin_win = cv2.imread('.\\pbm\\result_win.pbm', -1)



def judgeResult(frame):
    ''' リザルト画面の判定 '''     
    # winとの一致率を算出 ※基準色は黒
    val = iip.getMatchValue(bin_win, frame, TL_win, BR_win, 'blk') 
    # 一致率が閾値より大きければリザルト画面
    judge = True if val > thd_val else False     
    
    return judge



def getResult(frame, rule):
    ''' リザルト数字取得 '''
    # 出力リスト
    list_top = ['pt_'   + str(i) for i in range(1, 9)] \
             + ['kill_' + str(i) for i in range(1, 9)] \
             + ['sp_'   + str(i) for i in range(1, 9)]
    result_list = [list_top, [0 for i in range(24)]]    

    # ナワバリバトルは塗りポイントも取得
    if rule == 'turf':    
        # 単位「p」画像
        bin_ptw = cv2.imread('.\\pbm\\result_point_win_p.pbm', -1) 
        bin_ptl = cv2.imread('.\\pbm\\result_point_lose_p.pbm', -1) 
        
        # 数字画像読み込み
        num_ptw = []
        num_ptl = []
        for num in range(10):
            # 勝利側
            bin_num = cv2.imread('.\\pbm\\result_point_win_' + str(num) + '.pbm', -1)              
            num_ptw.append(bin_num)
            # 敗北側
            bin_num = cv2.imread('.\\pbm\\result_point_lose_' + str(num) + '.pbm', -1)  
            num_ptl.append(bin_num)
    
        # 8プレイヤー分
        for i in range(8):
            # 対象座標            
            TL = [L_pnt, T_pnt[i]]
            BR = [R_pnt, B_pnt[i]]
            
            # 勝利側
            if i < 4:
                num_pnt = iip.getNumber(frame, TL, BR, num_ptw, bin_ptw) 
                # 勝利ボーナス1000ptを差し引く
                num_pnt -= 1000
                
            # 敗北側
            else:
                num_pnt = iip.getNumber(frame, TL, BR, num_ptl, bin_ptl) 
                
            # リストに記録
            result_list[1][i] = num_pnt
                   
                
    # たおした数とスペシャル回数
    # 数字画像読み込み 数字は共用
    num_ksw = []
    num_ksl = []
    for num in range(10):
        # 勝利側
        bin_num = cv2.imread('.\\pbm\\result_killsp_win_' + str(num) + '.pbm', -1)              
        num_ksw.append(bin_num)
        # 敗北側
        bin_num = cv2.imread('.\\pbm\\result_killsp_lose_' + str(num) + '.pbm', -1)  
        num_ksl.append(bin_num)
        
    # 8プレイヤー分
    for i in range(8):
        # たおした数          
        TL_kil = [L_kil, T_kil[i]]
        BR_kil = [R_kil, B_kil[i]]
        # スペシャル回数
        TL_spw = [L_spw, T_spw[i]]
        BR_spw = [R_spw, B_spw[i]]
                
        # 勝利側
        if i < 4:
            num_kil = iip.getNumber(frame, TL_kil, BR_kil, num_ksw)
            num_spw = iip.getNumber(frame, TL_spw, BR_spw, num_ksw)
            
        # 敗北側
        else:
            num_kil = iip.getNumber(frame, TL_kil, BR_kil, num_ksl)
            num_spw = iip.getNumber(frame, TL_spw, BR_spw, num_ksl)
            
        # リストに記録
        result_list[1][i+8 ] = num_kil
        result_list[1][i+16] = num_spw
        
         
    return result_list



def test():
    ''' 動作テスト ''' 
    img_path = 'capture_image\\image_result_4.png'
    frame = cv2.imread(img_path)     

    jug_rsl = judgeResult(frame)
    print(jug_rsl)
    
    result_list = getResult(frame, 'turf')
    for i in range(len(result_list[0])):
        print(result_list[0][i], result_list[1][i])   
        
    # プレビュー
    scale = 0.5
    img_rsz = cv2.resize(frame, None, fx=scale, fy=scale)
         
    cv2.imshow('Preview', img_rsz)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
           
    

if __name__ == "__main__":    
    test()
    