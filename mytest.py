'''
Author: Zhu Jian
Date: 2020-10-13 13:25:25
LastEditTime: 2020-10-21 16:10:21
LastEditors: Zhu Jian
Description: 
FilePath: \migtool_view\mytest.py

'''

from sqlparse.tokens import Keyword, DML, Whitespace, Newline
from sqlparse.sql import IdentifierList, Identifier
from sqlparse import tokens
import sqlparse
sql1 = "select id,name_,age ,';'from dual ; select id,'18;19',age from actor;"
sql2 = """SELECT K.A, 
        K.B
        FROM (SELECT H.B
        FROM (SELECT G.C
        FROM (SELECT F.D FROM N (SELECT E.E FROM A, B, C, D, E) Q, F),
        G),
        H),
        I,
        J,
        K
        WHERE (K.A = 1 AND K.B = 2)
        OR (K.A, K.B) IN (SELECT J.J, J.K FROM J)
        ORDER BY 1, 2;
"""
sql4 = '''select used_res_id_seq.nextval,
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
sql3 = '''SELECT *  /*+ parallel(16,AA)*/
    --
    FROM (SELECT SIM_NBR_ID_SEQ.NEXTVAL,
    SIM_NBR_ID,
    BB.SIM_CARD_ID_NEW,
    CC.ACC_NBR_ID_NEW,
    'A' STATE,
    AA.STATE_DATE,
    AA.STATE_DATE,
    1 STAFF_ID,  
    -- 
    /**/
    '' FIRST_FLAG,
    '0' SP_ID,
    FROM CC.MIG_S_SIM_NBR AA, MIG.MIG_MID_SIM_CARD BB, MIG_MID_ACC_NBR CC
    WHERE AA.SIM_CARD_ID = BA.SIM_CARD_ID
    AND AA.ACC_NBR_ID = CC.ACC_NBR_ID
    and 2>1);
'''
sql5 = """
    insert /*+append parallel(8) nologging*/
    into mig_mid_used_res
    (USED_RES_ID,
    PROD_ID,
    RES_TYPE,
    RES_ID,
    CREATED_DATE,
    STATE,
    STATE_DATE,
    SP_ID)
    select a.used_res_sim used_res_id,
    subs_id prod_id,
    'B' res_type,
    a.sim_card_id res_id_new,
    a.fecha_alta created_date,
    decode(a.es_new, 1, 'A', 'X') state,
    nvl(a.fecha_baja, a.fecha_alta) state_date,
    0 sp_id
    from mig_tmp_std_post_sim_nbr a  where sim_card_id is not null 
"""


class get_sql_tables():
    def is_subs_select(self, parsed):
        if not parsed.is_group:
            return False
        for item in parsed.tokens:
            if item.ttype is DML and item.value.upper() == 'SELECT':
                return True
        return False

    def e_extract_from_part(self, parsed):
        from_seen = False
        for item in parsed.tokens:
            if from_seen:
                if self.is_subs_select(item):
                    yield from self.e_extract_from_part(item)
                elif item.ttype is Keyword:
                    return
                else:
                    yield item
            elif item.ttype is Keyword and item.value.upper() == 'FROM':
                from_seen = True

    def e_extract_table_identifiers(self, token_stream):
        print(token_stream)
        for item in token_stream:
            print('->', item, type(item), item.ttype)
            if isinstance(item, IdentifierList):
                for identifier in item.get_identifiers():
                    yield identifier.get_name()
            elif isinstance(item, Identifier):
                print("-->", item)
                # yield item.get_name()
                yield item.value
            # It's a bug to check for Keyword here, but in the example
            # above some tables names are identified as keywords...
            elif item.ttype is Keyword:
                yield item.value

    def e_extract_tables(self, sql):
        stream = self.e_extract_from_part(sqlparse.parse(sql)[0])
        return list(self.e_extract_table_identifiers(stream))

    def format_sql(self, sqllist):
        f_sql = []
        for sql in sqllist:
            a = sqlparse.split(sql)
            for b in a:
                c = sqlparse.format(b, reindent=True, keyword_case="upper")
                f_sql.append(c)
        return f_sql

    def analyze_sql(self, sql):
        a_parse = sqlparse.parse(sql)
        for b_token in a_parse[0].tokens:
            print("token ttype:", b_token.ttype, "value:", b_token.value)

    def analyze_sqls(self, sqllist):
        f_sqllist = self.format_sql(sqllist)
        for one_f_sql in f_sqllist:
            if one_f_sql == "" or one_f_sql is None:
                continue
            print("sql  --> ", one_f_sql)
            self.analyze_sql(one_f_sql)
        return f_sqllist

a = get_sql_tables()
b = a.analyze_sqls([sql2])
