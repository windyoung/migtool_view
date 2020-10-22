# -*- coding:UTF-8 -*-
import sqlparse
'''
Author: Zhu Jian
Date: 2020-10-13 06:57:15
LastEditTime: 2020-10-13 12:39:46
LastEditors: Zhu Jian
Description: 
FilePath: \migtool_view\test1.py

'''

sql = "select id,name_,age from dual;select id,'18;19',age from actor;"
sql = "    select K.a,K.b from (select H.b from (select G.c from (select F.d from     (select E.e from A, B, C, D, E), F), G), H), I, J, K order by 1,2;"
sql = '''INSERT /*+append parallel(t,8)*/
INTO MIG_MID_SIM_NBR
  SELECT SIM_NBR_ID_SEQ.NEXTVAL,
         SIM_NBR_ID,
         B.SIM_CARD_ID_NEW,
         C.ACC_NBR_ID_NEW,
         'A' STATE,
         A.STATE_DATE,
         A.STATE_DATE,
         1 STAFF_ID,
         '' FIRST_FLAG,
         '0' SP_ID,
    FROM MIG_S_SIM_NBR A, MIG_MID_SIM_CARD B, MIG_MID_ACC_NBR C
   WHERE A.SIM_CARD_ID = B.SIM_CARD_ID
     AND A.ACC_NBR_ID = C.ACC_NBR_ID
'''
# 1.分割SQL
stmts = sqlparse.split(sql)
for stmt in stmts:
    # 2.format格式化
    print(sqlparse.format(stmt, reindent=True, keyword_case="upper"))
    # 3.解析SQL
    stmt_parsed = sqlparse.parse(stmt)
    print(stmt_parsed[0].tokens)
