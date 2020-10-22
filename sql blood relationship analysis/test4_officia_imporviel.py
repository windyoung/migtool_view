'''
Author: Zhu Jian
Date: 2020-10-13 12:53:09
LastEditTime: 2020-10-13 13:27:40
LastEditors: Zhu Jian
Description:  官方样例改进join
FilePath: \migtool_view\test4.py

'''
import sqlparse
from sqlparse.sql import IdentifierList, Identifier
from sqlparse.tokens import Keyword, DML

# 支持的join方式
ALL_JOIN_TYPE = ('LEFT JOIN', 'RIGHT JOIN', 'INNER JOIN', 'FULL JOIN',
                 'LEFT OUTER JOIN', 'FULL OUTER JOIN')


def is_subselect(parsed):
    """
    是否子查询
    :param parsed:
    :return:
    """
    if not parsed.is_group:
        return False
    for item in parsed.tokens:
        if item.ttype is DML and item.value.upper() == 'SELECT':
            return True
    return False


def extract_from_part(parsed):
    """
    提取from之后模块
    :param parsed:
    :return:
    """
    from_seen = False
    for item in parsed.tokens:
        if from_seen:
            if is_subselect(item):
                for x in extract_from_part(item):
                    yield x
            elif item.ttype is Keyword:
                from_seen = False
                continue
            else:
                yield item
        elif item.ttype is Keyword and item.value.upper() == 'FROM':
            from_seen = True


def extract_join_part(parsed):
    """
    提交join之后模块
    :param parsed:
    :return:
    """
    flag = False
    for item in parsed.tokens:
        if flag:
            if item.ttype is Keyword:
                flag = False
                continue
            else:
                yield item
        if item.ttype is Keyword and item.value.upper() in ALL_JOIN_TYPE:
            flag = True


def extract_table_identifiers(token_stream):
    for item in token_stream:
        if isinstance(item, IdentifierList):
            for identifier in item.get_identifiers():
                yield identifier.get_name()
        elif isinstance(item, Identifier):
            yield item.get_name()
        elif item.ttype is Keyword:
            yield item.value


def extract_tables(sql):
    """
    提取sql中的表名（select语句）
    :param sql:
    :return:
    """
    x=sqlparse.parse(sql)[0]
    print(x,x.tokens)
    from_stream = extract_from_part(x)
    join_stream = extract_join_part(x)
    return list(extract_table_identifiers(from_stream)) + list(
        extract_table_identifiers(join_stream))


sql1 = "select id,name_,age ,';'from dual ; select id,'18;19',age from actor;"
sql2 = "    select K.a,K.b from (select H.b from (select G.c from (select F.d from    \n (select E.e from A, B, C, D, E) Q , F), G), H), I, J, K order by 1,2;"
sql3 = '''select used_res_id_seq.nextval,
       a.used_res_id,
       b.prod_id_new prod_id,
       a.res_type,
       c.res_id_new,
       a.created_date,
       a.state,
       a.state_date,
       '0' sp_id,
  from mig_s_used_res a,
       mig_mid_prod b,
       (select 'B' res_type, sim_card_id res_id, sim_card_id_new res_id_new
          from mig_mid_sim_card
        union all
        select 'A' res_type, acc_nbr_id res_id, acc_nbr_id_new res_id_new
          from mig_mid_acc_nbr) c
 where a.indep_prod_id = b.prod_id
   and a.res_type = c.res_type
   and a.res_id = c.res_id ;
'''
sql4 = '''SELECT *
  FROM (SELECT SIM_NBR_ID_SEQ.NEXTVAL,
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
           AND A.ACC_NBR_ID = C.ACC_NBR_ID);
'''
print(extract_tables(sql1 ))
