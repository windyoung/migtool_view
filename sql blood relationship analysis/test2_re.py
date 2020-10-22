import ply.lex as lex
import re
'''
Author: windyoung
Date: 2020-10-13 09:55:56
LastEditTime: 2020-10-22 19:59:02
LastEditors: windyoung
Description: 
FilePath: \migtool_view\sql blood relationship analysis\test2_re.py

'''

def tables_in_query(sql_str):

    # remove the /* */ comments
    q = re.sub(r"/\*[^*]*\*+(?:[^*/][^*]*\*+)*/", "", sql_str)

    # remove whole line -- and # comments
    lines = [line for line in q.splitlines() if not re.match("^\s*(--|#)", line)]

    # remove trailing -- and # comments
    q = " ".join([re.split("--|#", line)[0] for line in lines])

    # split on blanks, parens and semicolons
    tokens = re.split(r"[\s)(;]+", q)

    # scan the tokens. if we see a FROM or JOIN, we set the get_next
    # flag, and grab the next one (unless it's SELECT).

    tables = set()
    get_next = False
    for tok in tokens:
        if get_next:
            if tok.lower() not in ["", "select"]:
                tables.add(tok)
            get_next = False
        get_next = tok.lower() in ["from", "join"]

    dictTables = dict()
    for table in tables:
        fields = []
        for token in tokens:
            if token.startswith(table):
                if token != table:
                    fields.append(token)
        if len(list(set(fields))) >= 1:
            dictTables[table] = list(set(fields))
    return dictTables

def extract_table_name_from_sql(sql_str):

    # remove the /* */ comments
    q = re.sub(r"/\*[^*]*\*+(?:[^*/][^*]*\*+)*/", "", sql_str)

    # remove whole line -- and # comments
    lines = [line for line in q.splitlines(
    ) if not re.match(r"^\s*(--|#)", line)]

    # remove trailing -- and # comments
    q = " ".join([re.split("--|#", line)[0] for line in lines])

    # split on blanks, parens and semicolons
    tokens = re.split(r"[\s)(;]+", q)

    # scan the tokens. if we see a FROM or JOIN, we set the get_next
    # flag, and grab the next one (unless it's SELECT).

    result = set()
    get_next = False
    for token in tokens:
        if get_next:
            if token.lower() not in ["", "select"]:
                result.add(token)
            get_next = False
        get_next = token.lower() in ["from", "join"]

    return result


sql21 = "create table s123 SELECT a.time_updated_server/1000,content,nick,name FROM      " \
    "table1 a JOIN   " \
    "table2 b ON a.sender_id = b.user_id JOIN table3 c ON a.channel_id = c.channel_id JOIN table4 d ON c.store_id = d.store_id WHERE sender_id NOT IN(SELECT user_id FROM table5 WHERE store_id IN ('agent_store:1', 'ask:1')) AND to_timestamp(a.time_updated_server/1000)::date >= '2014-05-01' GROUP BY 1,2,3,4 HAVING sum(1) > 500 ORDER BY 1 ASC"
sql22 = "    select K.a,K.b from (select H.b from (select G.c from (select F.d from   \n  (select E.e from A, B, C, D, E), F), G), H), I, J, K order by 1,2;"

sql23 = """SELECT a.time_updated_server/1000,
content,
nick,
name
FROM table1 a
JOIN table2 b ON a.sender_id = b.user_id
JOIN table3 c ON a.channel_id = c.channel_id
JOIN table4 d ON c.store_id = d.store_id
WHERE sender_id NOT IN
(SELECT user_id
FROM table5
WHERE store_id IN ('agent_store:1', 'ask:1'))
AND to_timestamp(a.time_updated_server/1000)::date >= '2014-05-01'
GROUP BY 1,2,3,4
HAVING sum(1) > 500
ORDER BY 1 ASC
"""
sql24 = sql = '''INSERT /*+append parallel(t,8)*/
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
print(extract_table_name_from_sql(sql24))

print(tables_in_query(sql24))
