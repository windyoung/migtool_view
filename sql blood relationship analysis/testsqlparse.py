# -*- coding: utf-8 -*-
'''
Author: windyoung
Date: 2020-10-13 05:25:20
LastEditTime: 2020-10-22 19:58:19
LastEditors: windyoung
Description: 
FilePath: \migtool_view\sql blood relationship analysis\testsqlparse.py

'''

import sqlparse
import sys
from sqlparse.sql import IdentifierList, Identifier, Where
from sqlparse.tokens import Keyword, DML


class Testsqlparse():
    def is_subselect(self, parsed):
        if not parsed.is_group:
            return False
        for item in parsed.tokens:
            if item.ttype is DML and item.value.upper() == 'SELECT':
                return True
        return False

    def extract_from_part(self, parsed):
        print("-->", self.__class__,
              sys._getframe().f_code.co_name, ",parsed:", parsed)
        from_seen = False
        for item in parsed.tokens:
            if from_seen:
                if self.is_subselect(item):
                    for x in self.extract_from_part(item):
                        yield x
                elif item.ttype is Keyword:
                    raise StopIteration
                else:
                    yield item
            elif item.ttype is Keyword and item.value.upper() == 'FROM':
                from_seen = True

    def extract_table_identifiers(self, token_stream):
        for item in token_stream:
            if isinstance(item, IdentifierList):
                for identifier in item.get_identifiers():
                    yield identifier.get_name()
            elif isinstance(item, Identifier):
                yield item.get_name()
            # It's a bug to check for Keyword here, but in the example
            # above some tables names are identified as keywords...
            elif item.ttype is Keyword:
                yield item.value

    def extract_tables(self, sql):
        stream = self.extract_from_part(sqlparse.parse(sql)[0])
        return list(self.extract_table_identifiers(stream))


if __name__ == '__main__':
    sql1 = """SELECT K.A, K.B
  FROM (SELECT H.B
          FROM (SELECT G.C
                  FROM (SELECT F.D FROM (SELECT E.E FROM A, B, C, D, E), F),
                       G),
               H),
       I,
       J,
       K
 ORDER BY 1, 2;

    """
    sql2 = '''
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
    x = Testsqlparse()
    a = ','.join(x.extract_tables(sql1))
    print(f"Tables: {a}")
