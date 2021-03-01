# -*- coding: utf-8 -*-

import csv


# エラーメッセージ
text = {'notfound':'Error in csvread.py : Not Found CSV File'}


def convertType(input_str):
    ''' str型入力をstr, int, floatの中で適切な型で出力する '''
    # float型に変換できるか
    try:
        float(input_str)
    except:
        # 変換できなかったらstr型
        output = input_str
    # 変換できたら数字
    else:
        # 整数かどうか -> 文字列について小数点"."の有無で判別する
        if input_str.isdigit():
            # int型
            output = int(float(input_str))
        else:
            # float型
            output = float(input_str)

    return output


def readAsList(csv_path):
    ''' リスト形式で読み込む '''
    # ファイルを開けるか
    try:
        with open(csv_path, 'r') as f:
            reader = csv.reader(f)
            csv_list = [ row for row in reader ]
    # 開けなかったら
    except FileNotFoundError:
        print(text['notfound'])
    # 開けたら
    else:
        # 出力リスト
        return_list = []
        # 各行について
        for row in csv_list:
            new_row = []
            # 各要素について
            for e in row:
                # 型を変換
                e = convertType(e)
                # 行に格納
                new_row.append(e)

            # 出力リストに格納
            return_list.append(new_row)

        return return_list


def readAsDict(csv_path):
    ''' 辞書形式で読み込む 1行目がキー(key) 2行目が値(value) '''
    # ファイルを開けるか
    try:
        with open(csv_path, 'r') as f:
            reader = csv.reader(f)
            csv_list = [ row for row in reader ]
    # 開けなかったら
    except FileNotFoundError:
        print(text['notfound'])
    # 開けたら
    else:
        # 出力辞書
        return_dict = {}
        for idx in range(len(csv_list[0])):
            # 1行目をキー(key)、2行目を値(value)とする
            key   = csv_list[0][idx]
            value = csv_list[1][idx]
            # 型を変換
            value = convertType(value)
            # 出力辞書に格納
            return_dict[key] = value

        return return_dict