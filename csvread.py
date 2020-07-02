# -*- coding: utf-8 -*-


import csv

def csvread(csv_path, out_type):
    ''' CSVファイルを型を指定して読み込む '''
    f = open(csv_path, 'r')
    reader = csv.reader(f)
    csvdata = [ e for e in reader ]
    f.close()
    
    if out_type == 'string' or out_type == 'str' or out_type == 's':
        return csvdata
    
    elif out_type == 'float' or out_type == 'f':
        list_length = len(csvdata)
        csv_list = [[] for j in range(list_length)]
        for i in range(list_length):
            csv_list[i] = [float(s) for s in csvdata[i]]
            
        return csv_list

    elif out_type == 'integer' or out_type == 'int' or out_type == 'i':
        list_length = len(csvdata)
        csv_list = [[] for j in range(list_length)]
        for i in range(list_length):
            csv_list[i] = [int(float(s)) for s in csvdata[i]]
            
        return csv_list
    
    else:
        print('Enter "out_type" in "string", "float" or "integer".')
        return None