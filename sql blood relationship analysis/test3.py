# coding=utf-8

'''
Author: Zhu Jian
Date: 2020-10-13 12:36:21
LastEditTime: 2020-10-13 13:28:08
LastEditors: Zhu Jian
Description: 
FilePath: \migtool_view\test3.py

'''
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import sqlparse
from sqlparse.sql import Identifier, IdentifierList
from sqlparse.tokens import Keyword, Name

RESULT_OPERATIONS = {'UNION', 'INTERSECT', 'EXCEPT', 'SELECT'}
ON_KEYWORD = 'ON'
PRECEDES_TABLE_NAME = {'FROM', 'JOIN', 'DESC', 'DESCRIBE', 'WITH'}


class BaseExtractor(object):
    def __init__(self, sql_statement):
        self.sql = sqlparse.format(
            sql_statement, reindent=True, keyword_case='upper')
        self._table_names = set()
        self._alias_names = set()
        self._limit = None
        self._parsed = sqlparse.parse(self.stripped())
        for statement in self._parsed:
            self.__extract_from_token(statement)
            self._limit = self._extract_limit_from_query(statement)
        self._table_names = self._table_names - self._alias_names

    @property
    def tables(self):
        return self._table_names

    @property
    def limit(self):
        return self._limit

    def is_select(self):
        return self._parsed[0].get_type() == 'SELECT'

    def is_explain(self):
        return self.stripped().upper().startswith('EXPLAIN')

    def is_readonly(self):
        return self.is_select() or self.is_explain()

    def stripped(self):
        return self.sql.strip(' \t\n;')

    def get_statements(self):
        statements = []
        for statement in self._parsed:
            if statement:
                sql = str(statement).strip(' \n;\t')
                if sql:
                    statements.append(sql)
        return statements

    @staticmethod
    def __precedes_table_name(token_value):
        for keyword in PRECEDES_TABLE_NAME:
            if keyword in token_value:
                return True
        return False

    @staticmethod
    def get_full_name(identifier):
        if len(identifier.tokens) > 1 and identifier.tokens[1].value == '.':
            return '{}.{}'.format(identifier.tokens[0].value,
                                  identifier.tokens[2].value)
        return identifier.get_real_name()

    @staticmethod
    def __is_result_operation(keyword):
        for operation in RESULT_OPERATIONS:
            if operation in keyword.upper():
                return True
        return False

    @staticmethod
    def __is_identifier(token):
        return isinstance(token, (IdentifierList, Identifier))

    def __process_identifier(self, identifier):
        if '(' not in '{}'.format(identifier):
            self._table_names.add(self.get_full_name(identifier))
            return

        # store aliases
        if hasattr(identifier, 'get_alias'):
            self._alias_names.add(identifier.get_alias())
        if hasattr(identifier, 'tokens'):
            # some aliases are not parsed properly
            if identifier.tokens[0].ttype == Name:
                self._alias_names.add(identifier.tokens[0].value)
        self.__extract_from_token(identifier)

    def as_create_table(self, table_name, overwrite=False):
        exec_sql = ''
        sql = self.stripped()
        if overwrite:
            exec_sql = 'DROP TABLE IF EXISTS {};\n'.format(table_name)
        exec_sql += 'CREATE TABLE {} AS \n{}'.format(table_name, sql)
        return exec_sql

    def __extract_from_token(self, token):
        if not hasattr(token, 'tokens'):
            return

        table_name_preceding_token = False

        for item in token.tokens:
            if item.is_group and not self.__is_identifier(item):
                self.__extract_from_token(item)

            if item.ttype in Keyword:
                if self.__precedes_table_name(item.value.upper()):
                    table_name_preceding_token = True
                    continue

            if not table_name_preceding_token:
                continue

            if item.ttype in Keyword or item.value == ',':
                if (self.__is_result_operation(item.value) or
                        item.value.upper() == ON_KEYWORD):
                    table_name_preceding_token = False
                    continue
                # FROM clause is over
                break

            if isinstance(item, Identifier):
                self.__process_identifier(item)

            if isinstance(item, IdentifierList):
                for token in item.tokens:
                    if self.__is_identifier(token):
                        self.__process_identifier(token)

    def _get_limit_from_token(self, token):
        if token.ttype == sqlparse.tokens.Literal.Number.Integer:
            return int(token.value)
        elif token.is_group:
            return int(token.get_token_at_offset(1).value)

    def _extract_limit_from_query(self, statement):
        limit_token = None
        for pos, item in enumerate(statement.tokens):
            if item.ttype in Keyword and item.value.lower() == 'limit':
                limit_token = statement.tokens[pos + 2]
                return self._get_limit_from_token(limit_token)

    def get_query_with_new_limit(self, new_limit):
        if not self._limit:
            return self.sql + ' LIMIT ' + str(new_limit)
        limit_pos = None
        tokens = self._parsed[0].tokens
        # Add all items to before_str until there is a limit
        for pos, item in enumerate(tokens):
            if item.ttype in Keyword and item.value.lower() == 'limit':
                limit_pos = pos
                break
        limit = tokens[limit_pos + 2]
        if limit.ttype == sqlparse.tokens.Literal.Number.Integer:
            tokens[limit_pos + 2].value = new_limit
        elif limit.is_group:
            tokens[limit_pos + 2].value = (
                '{}, {}'.format(next(limit.get_identifiers()), new_limit)
            )

        str_res = ''
        for i in tokens:
            str_res += str(i.value)
        return str_res


class SqlExtractor(BaseExtractor):
    """提取sql语句"""

    @staticmethod
    def get_full_name(identifier, including_dbs=False):
        if len(identifier.tokens) > 1 and identifier.tokens[1].value == '.':
            a = identifier.tokens[0].value
            b = identifier.tokens[2].value
            db_table = (a, b)
            full_tree = '{}.{}'.format(a, b)
            if len(identifier.tokens) == 3:
                return full_tree
            else:
                i = identifier.tokens[3].value
                c = identifier.tokens[4].value
                if i == ' ':
                    return full_tree
                full_tree = '{}.{}.{}'.format(a, b, c)
                return full_tree
        return None, None


if __name__ == '__main__':
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
    sql= '''select used_res_id_seq.nextval,
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
        and a.res_id = c.res_id 
'''
    sql2 = "    select K.a,K.b from (select H.b from (select G.c from (select F.d from    \n (select E.e from A, B, C, D, E)   , F), G), H), I, J, K order by 1,2;"
    sql_extractor = SqlExtractor(sql2)

    print(sql_extractor.sql)
    print(sql_extractor.tables)
