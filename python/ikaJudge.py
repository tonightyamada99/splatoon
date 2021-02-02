# -*- coding: utf-8 -*-

import cv2
import ikaImageProcessing as iip

                
# 要素の位置の座標
# 設定サイズ
TLBR_size = (1920, 1080)    # FHD
# 勝敗表示 win or lose
TL_wol = ( 40,  60)
BR_wol = (264, 132)
# ジャッジ
TL_jug = [(150, 850), (1320, 850)]
BR_jug = [(600, 950), (1770, 950)]
# ポイント
TL_pnt = [(140, 950), (1610, 950)]
BR_pnt = [(300, 1010), (1770, 1010)]

# 一致率の閾値 threshold
thd_val = 0.95

# 比較画像
# win
bin_win = cv2.imread('.\\pbm\\judge_win.pbm', -1)
# lose
bin_los = cv2.imread('.\\pbm\\judge_lose.pbm', -1)



def judgeJudge(frame):
    ''' ジャッジ画面の判定 '''     
    # 勝敗表示位置の切り抜き
    TL = TL_wol
    BR = BR_wol
    val_win = iip.matchRGB(bin_win, frame, TL, BR, 'wht')
    val_los = iip.matchRGB(bin_los, frame, TL, BR, 'wht')
        
    # 勝敗の一致率を比較
    if val_win > val_los:
        val = val_win
        wol = 'win'
        
    else:
        val = val_los
        wol = 'lose'
        
    # 一致率が閾値より大きければジャッジ画面
    if val > thd_val:     
        return True, wol    
    else:
        return False, None



def getJudge(frame, rule):
    ''' ジャッジ数字取得 '''
    # ナワバリバトル
    if rule == 'turf':
        # 「%」画像
        bin_per = cv2.imread('.\\pbm\\judge_percent.pbm', -1)     
        # 「p」画像
        bin_pnt = cv2.imread('.\\pbm\\judge_point_p.pbm', -1)     

        # 数字画像読み込み
        num_per = []
        num_pnt = []
        for num in range(10):
            # パーセント
            bin_num = cv2.imread('.\\pbm\\judge_count_' + str(num) + '.pbm', -1)              
            num_per.append(bin_num)
            # ポイント
            bin_num = cv2.imread('.\\pbm\\judge_point_' + str(num) + '.pbm', -1)  
            num_pnt.append(bin_num)
    
        # 出力リスト
        judge_list = [['percent_alfa', 'percent_bravo', 'point_alfa', 'point_bravo'],
                      [0, 0, 0, 0]]
        
        # アルファとブラボー
        for i in range(2):
            # パーセントの取得
            TL = TL_jug[i]
            BR = BR_jug[i]
            percent = 0.1 * iip.getNumber(frame, TL, BR, num_per, bin_per)         
            
            # ポイントの取得
            TL = TL_pnt[i]
            BR = BR_pnt[i]
            point = iip.getNumber(frame, TL, BR, num_pnt, bin_pnt) 
            
            # 結果を記録
            judge_list[1][i  ] = percent
            judge_list[1][i+2] = point
        
    
    # ガチマッチの場合
    else:
        # 「ノックアウト」画像
        bin_ko = cv2.imread('.\\pbm\\judge_ko.pbm', -1)     
        # 「カウント」画像
        bin_cnt = cv2.imread('.\\pbm\\judge_count.pbm', -1)  
        
        # 数字画像読み込み
        num_cnt = []
        for num in range(10):
            bin_num = cv2.imread('.\\pbm\\judge_count_' + str(num) + '.pbm', -1)              
            num_cnt.append(bin_num)
        
        # 出力リスト
        judge_list = [['count_alfa', 'count_bravo', 'point_alfa', 'point_bravo'],
                      [0, 0, 0, 0]]        
        
        # アルファとブラボー
        for i in range(2):
            # 「ノックアウト」との一致率を算出
            TL = TL_jug[i]
            BR = BR_jug[i]
            val_ko = iip.matchRGB(bin_ko, frame, TL, BR, 'wht')
            
            # 閾値以上ならばノックアウト
            if val_ko > thd_val:
                count = 'ko'
                point = 500
            else:
                # カウントの取得
                TL = TL_jug[i]
                BR = BR_jug[i]
                count = iip.getNumber(frame, TL, BR, num_cnt, bin_cnt)          
                
                if count >= 0:
                    point = count * 5
                else:
                    point = 0

            # 結果を記録
            judge_list[1][i  ] = count
            judge_list[1][i+2] = point                    
            
                
    return judge_list



def test():
    ''' 動作テスト ''' 
    img_path = 'capture_image\image_judge_14.png'
    frame = cv2.imread(img_path)   

    jug_jug, wol = judgeJudge(frame)
    print(jug_jug, wol)

    if jug_jug == True:
        judge_list = getJudge(frame, 'turf')
        
        for idx in range(len(judge_list[0])):
            print(judge_list[0][idx], judge_list[1][idx])
            
    # プレビュー
    scale = 0.5
    img_rsz = cv2.resize(frame, None, fx=scale, fy=scale)
         
    cv2.imshow('Preview', img_rsz)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
 

        
if __name__ == "__main__":    
    test()