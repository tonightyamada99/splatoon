# -*- coding: utf-8 -*-

import csv
    

def readAsList(csv_path):
    ''' リスト形式で読み込む ''' 
    try:
        with open(csv_path, 'r') as f:
            reader = csv.reader(f)
            csv_list = [ row for row in reader ]
    
        return_list = []
        # 各行について
        for row in csv_list:
            new_row = []
        
            # 行の各要素について
            for tmp in row:
                # float型に変換できるか
                try:
                    float(tmp)
                except:
                    # 変換できなかったらstr型
                    e = tmp
                    
                # 変換できたら数字
                else:
                    # 整数かどうか -> 文字列について小数点"."の有無で判別する
                    if tmp.isdigit():
                        # int型
                        e = int(float(tmp))
                    else:
                        # float型
                        e = float(tmp)
                        
                # 行に格納
                new_row.append(e)
            
            # リストに格納
            return_list.append(new_row)
            
            
        return return_list
    
    
    except FileNotFoundError:
        print('Error in csvread: Not Found CSV File')
        return None
    


def readAsDict(csv_path):
    ''' 辞書形式で読み込む 1行目がキー(key) 2行目が値(value) ''' 
    
    try:
        with open(csv_path, 'r') as f:
            reader = csv.reader(f)
            csv_list = [ row for row in reader ]
    
        return_dict = {}
        for idx in range(len(csv_list[0])):
            # 1行目をキー(key)、2行目を値(value)とする
            key = csv_list[0][idx]
            tmp = csv_list[1][idx]
            
            # float型に変換できるか
            try:
                float(tmp)
            except:
                # 変換できなかったらstr型
                value = tmp
                
            # 変換できたら数字
            else:
                # 整数かどうか -> 文字列について小数点"."の有無で判別する
                if tmp.isdigit():
                    # int型
                    value = int(float(tmp))
                else:
                    # float型
                    value = float(tmp)
            
            # 辞書に格納
            return_dict[key] = value
            
            
        return return_dict
    
    
    except FileNotFoundError:
        print('Error in csvread: Not Found CSV File')
        return None
    
    

def test():
    ''' 実行テスト '''
    csv_path = 'testCSV.csv'
    csv_list = readAsList(csv_path)
    
    for row in csv_list:
        print(row)

    csv_dict = readAsDict(csv_path)
    print(csv_dict)
    
    
        
if __name__ == "__main__":
    test()

    


            
        
