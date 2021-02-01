# -*- coding: utf-8 -*-

import csv
    

def csvread(csv_path):
    ''' カンマ区切りCSVファイルを読み込んでリストで返す ''' 
    try:
        with open(csv_path, 'r') as f:
            reader = csv.reader(f)
            csv_list = [ row for row in reader ]
    
        return_list = []
        # 各行について
        for row in csv_list:
            new_row = []
        
            # 行の各要素について
            for e in row:
                # float型に変換できるか
                try:
                    float(e)
                except:
                    # 変換できなかったら文字列
                    # str型で格納
                    new_row.append(e)
                    
                # 変換できたら数字
                else:
                    # 整数かどうか -> 文字列について小数点"."の有無で判別する
                    if e.isdigit():
                        # int型で格納
                        new_row.append(int(float(e)))
                    else:
                        # float型で格納
                        new_row.append(float(e))
            
            return_list.append(new_row)
            
            
        return return_list
    
    
    except FileNotFoundError:
        print('Error in csvread: Not Found CSV File')
        return None
    



def test():
    ''' 実行テスト '''
    csv_path = 'testCSV.csv'
    csv_list = csvread(csv_path)
    
    for row in csv_list:
        print(row)

        
if __name__ == "__main__":
    test()

    


            
        
