# -*- coding: utf-8 -*-

import csv
import glob
import os.path
import numpy as np

import csvread


# 試合開始からのフレーム数
length_start = 30
# 試合終了までのフレーム数
length_end = 6
# データ無しを示す文字列
str_none = 'nodata'
# データ無しの置換先 replace
rep_none = -2


def correct(video_path):
    ''' データを補正する '''
    # 動画の名前の取得
    video_name, video_ext = os.path.splitext(os.path.basename(video_path))
    video_dir = os.path.dirname(video_path)
    # 入力元
    info_path = video_dir + '\\' + video_name + '_info.csv'
    status_path = video_dir + '\\' + video_name + '_status.csv'
    data_path   = video_dir + '\\' + video_name + '_count.csv'
    # 出力先
    out_status_path = video_dir + '\\' + video_name + '_correct_status.csv'
    out_count_path  = video_dir + '\\' + video_name + '_correct_count.csv'

    if not os.path.exists(status_path) or not os.path.exists(data_path):
        print('動画のカウントファイルが見つかりません。')
    else:
        # 動画の情報を読み込む
        info_dict = csvread.readAsDict(info_path)
        rule = info_dict['rule']

        # カウントファイルを読み込む
        data_list = csvread.readAsList(data_path)
        data_array = np.array(data_list)

        # カウントの補正
        data_array = correctCount(data_array)
        # ペナルティカウントの補正
        data_array = correctPenaltyCount(data_array)
        # その他の補正
        data_array = correctOthers(data_array)
        # 試合終了直前の補正
        data_array = correctLast(data_array)
        # データ無しの補正
        data_array = np.where(data_array==str_none, rep_none, data_array)

        # CSV出力
        with open(out_count_path, 'w') as file:
            writer = csv.writer(file, lineterminator='\n')
            writer.writerows(data_array)


def searchListTop(list_top, target):
    ''' 検索語から始まる要素のインデックスを返す '''
    # インデックスリスト
    idx_list = []
    # 対象の型によって分岐
    length = len(list_top)
    if type(target) is str:
        idx_list = [i for i in range(length) if list_top[i].startswith(target)]
    elif type(target) is list:
        for t in target:
            idx_list += [i for i in range(length) if list_top[i].startswith(t)]

    return idx_list


def correctOthers(data_array):
    ''' 確保状況・塗り状況・オブジェクト位置・アサリ数を補正する '''
    # 対象列の名前
    target = ['control', 'ratio', 'location', 'clam']
    # 対象列の位置を取得
    idx_list = searchListTop(data_array[0], target)

    for index in idx_list:
        # 試合開始直後の補正 0で置き換える
        data_array[1:length_start+1, index] = np.zeros((1, length_start))

    return data_array


def correctCount(data_array):
    ''' カウントを補正する '''
    # 対象列の位置を取得
    idx_list = searchListTop(data_array[0], 'count')

    for index in idx_list:
        # 試合開始直後の補正 100で置き換える
        data_array[1:length_start+1, index] = np.ones((1, length_start)) * 100

        # 誤認識の補正
        for i in range(2, len(data_array)):
            # 現在と1つ前の値
            count_pre = data_array[i-1][index]
            count_now = data_array[i][index]
            if count_now != str_none and count_pre != str_none:
                # 差分を算出 diffrence
                dif = float(count_pre) - float(count_now)
                # カウントは1つ前と変わらないか1減るかのどちらか
                if dif != 0 and dif != 1:
                    # 現在の値を1つ前の値で置換
                    data_array[i][index] = count_pre

    return data_array


def correctPenaltyCount(data_array):
    ''' ペナルティカウントを補正する '''
    # 対象列の位置を取得
    idx_list = searchListTop(data_array[0], 'penalty')

    for index in idx_list:
        # 試合開始直後の補正 0で置き換える
        data_array[1:length_start+1, index] = np.zeros((1, length_start))

        # 誤認識の補正
        for i in range(2, len(data_array)):
            # 現在と1つ前の値
            count_pre = data_array[i-1][index]
            count_now = data_array[i][index]
            if count_now != str_none and count_pre != str_none:
                # 差分を算出 diffrence
                dif = float(count_pre) - float(count_now)
                # ペナルティカウントが1以上減ることはない
                # 増えた場合はペナルティが新たに追加された
                if dif > 1:
                    # 現在の値を1つ前の値で置換
                    data_array[i][index] = count_pre

    return data_array


def correctLast(data_array):
    ''' 試合終了直前を補正する '''
    # データがある行の位置を取得
    index_list = np.where(data_array[:, 1]!=str_none)[0]
    # データのある最終行のインデックス
    index_data = index_list[-1]
    # 最低限補正が必要となるインデックス
    index_end = len(data_array) - length_end
    # 比較してより長い方（インデックスが小さい方）で補正する
    index_last = index_data if index_data < index_end else index_end
    # 置換元
    last_array = data_array[index_last][1:]
    for i in range(index_last, len(data_array)):
         data_array[i][1:] = last_array

    return data_array


def main():
    ''' メイン処理 '''

    fnames = glob.glob('D:\\splatoon_movie\\capture\\video_sub_*.mp4' )

    for video_path in fnames:
        print(os.path.basename(video_path))
        correct(video_path)


if __name__ == "__main__":
    main()