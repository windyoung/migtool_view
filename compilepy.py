# -*- coding: utf-8 -*-
'''
Author: windyoung
Date: 2020-12-09 00:41:15
LastEditTime: 2020-12-09 09:29:47
LastEditors: windyoung
Description: 
FilePath: \migtool_viewer\convjpg2ico.py

'''
# import pythonMagick


def base64ico():
    import base64
    open_icon = open("logo.ico", "rb")
    b64str = base64.b64encode(open_icon.read())
    open_icon.close()

# pyinstaller.exe - i ./logo.ico - F - w .\MigrationStepViewer.spec
# D: \apps\py_work\migtool_plugin\migtool_viewer

def compile2exe():
    import os
    change_root ="D:"
    cd_path = r"cd D:\apps\py_work\migtool_plugin\migtool_viewer"
    compile_py = "pyinstaller.exe -i ./logo.ico -F -w .\MigrationStepViewer.spec"
    os.system(change_root)
    os.system(cd_path)
    os.system(compile_py)

compile2exe()

