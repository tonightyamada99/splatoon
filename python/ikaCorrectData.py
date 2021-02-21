# -*- coding: utf-8 -*-

import csv
import glob
import os.path
import numpy as np

import csvread


# 試合開始からの時間
length_start = 30


def correctCount(count_list):
    ''' カウントを補正する '''
    # 試合開始直後の補正
    count_list[1:length_start+1] = [100 for i in range(length_start)]

    for i in range(2, len(count_list)):
        # 現在と1つ前の値
        count_pre = count_list[i-1]
        count_now = count_list[i]
        # データ無し -> -1に置換
        if count_now == 'nodata':
            cor_count = -1
        # データ有り & 前フレームがデータ無し -> そのまま記録
        elif count_pre == -1:
            cor_count = count_now
        # 両方データ有り -> 差分を算出
        else:
            dif = float(count_pre) - float(count_now)     # 差分 diffrence
            # カウントは前のフレームと変わらないか1減るかのどちらか
            if dif == 0 or dif == 1:
                cor_count = count_now
            else:
                cor_count = count_pre

        # リストを置換
        count_list[i] = cor_count

    return count_list


def correctPenaltyCount(count_list):
    ''' ペナルティカウントを補正する '''
    # 試合開始直後の補正
    count_list[1:length_start+1] = [0 for i in range(length_start)]

    # 誤認識とデータ無しの補正
    for i in range(2, len(count_list)):
        # 現在と1つ前の値
        count_pre = count_list[i-1]
        count_now = count_list[i]
        # データ無し -> -1に置換
        if count_now == 'nodata':
            cor_count = -1
        # データ有り & 1つ前がデータ無し -> そのまま記録
        elif count_pre == -1:
            cor_count = count_now
        # 両方データ有り -> 差分を算出
        else:
            dif = float(count_pre) - float(count_now)     # 差分 diffrence
            # カウントは前のフレームと変わらないか1減るか
            # 増えた場合は新たにペナルティが追加されたと判断
            if dif <= 1:
                cor_count = count_now
            # １以上減っている場合は前の値を記録
            else:
                cor_count = count_pre

        # リストを置換
        count_list[i] = cor_count

    return count_list


def correct(video_path):
    ''' カウントの修正 '''
    video_name, video_ext = os.path.splitext(os.path.basename(video_path))
    video_dir = os.path.dirname(video_path)
    # 入力パス
    info_path = video_dir + '\\' + video_name + '_info.csv'
    data_path = video_dir + '\\' + video_name + '_count.csv'
    # 出力パス
    out_path  = video_dir + '\\' + video_name + '_count_correct.csv'

    if not os.path.exists(info_path):
        print('動画のカウントファイルが見つかりません。')

    elif not os.path.exists(data_path):
        print('動画のカウントファイルが見つかりません。')

    else:
        # カウントファイルを読み込む
        data_list = csvread.readAsList(data_path)
        data_array = np.array(data_list)
        array_top = data_array[0]

        # 出力リスト
        fcount_array  = data_array[:, 0]
        correct_array = np.array([fcount_array]).T

        # カウントの補正
        # 対象列の位置を取得
        idx_list = [i for i in range(len(array_top)) \
                    if array_top[i].startswith('count')]
        for index in idx_list:
            # 対象列の抜粋
            cor_count_array = data_array[:, index]
            # 補正処理
            cor_count_array = correctCount(cor_count_array)
            # リストに追加
            add_array = np.array([cor_count_array]).T
            correct_array = np.append(correct_array, add_array, axis=1)

        # ペナルティカウントの補正
        idx_list = [i for i in range(len(array_top)) \
                    if array_top[i].startswith('penalty')]
        for index in idx_list:
            # 対象列の抜粋
            cor_count_array = data_array[:, index]
            # 補正処理
            cor_count_array = correctPenaltyCount(cor_count_array)
            # リストに追加
            add_array = np.array([cor_count_array]).T
            correct_array = np.append(correct_array, add_array, axis=1)

        # CSV出力
        with open(out_path, 'w') as file:
            writer = csv.writer(file, lineterminator='\n')
            writer.writerows(correct_array)


def main():
    ''' メイン処理 '''

    fnames = glob.glob('D:\\splatoon_movie\\capture\\video_sub_zones_1.avi' )

    for video_path in fnames:
        print('==================================================')
        print(os.path.basename(video_path))

        correct(video_path)


if __name__ == "__main__":
    main()