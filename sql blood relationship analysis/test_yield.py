
'''
Author: Zhu Jian
Date: 2020-10-14 00:58:13
LastEditTime: 2020-10-14 15:30:44
LastEditors: Zhu Jian
Description: 
FilePath: \migtool_view\test_yield.py

'''
def test1(a):
    for i  in range(1,a):
        print("test1",i)


def test2(a):
    for i in range(1, a):
        yield i

test1(5)
a=test2(3)
print("test2",a)
print("test2",tuple(a))
