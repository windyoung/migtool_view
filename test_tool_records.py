# -*- coding: utf-8 -*-
'''
Author: windyoung
Date: 2020-12-15 16:52:28
LastEditTime: 2020-12-16 00:35:34
LastEditors: windyoung
Description: 
FilePath: \migtool_plugin\migtool_viewer\test_tool_records.py

'''
from MigrationStepViewer import stepviewData
con_str_ora = 'oracle://mig_pool:smart@10.45.82.28:1521/orcl'
con_str_mysql = 'mysql+pymysql://mig_cc:mig_cc2020@10.159.0.132:3307/mig_tool'
con_str2 = 'mig_pool/smart@10.45.82.28:1521/orcl'

key1=3
key2 = 'pwd_tt'
a = stepviewData(con_str_ora)
# a1 = stepviewData(con_str_mysql)
# a.init_db_con_ora(con_str2)
b = a.get_param_cur_value(key1, key2)
# b1 = a1.get_param_cur_value(key1, key2)
print(f"oracle {b}\n mysql ")
