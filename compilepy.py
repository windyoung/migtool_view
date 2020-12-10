# -*- coding: utf-8 -*-
'''
Author: windyoung
Date: 2020-12-09 00:41:15
LastEditTime: 2020-12-10 11:57:39
LastEditors: windyoung
Description: 
FilePath: \migtool_viewer\compilepy.py
 '''


from tkinter import ttk
def base64ico():
    import base64
    open_icon = open("logo.ico", "rb")
    b64str = base64.b64encode(open_icon.read())
    open_icon.close() 

def compile2exe():
    import os
    spec_="""# -*- mode: python ; coding: utf-8 -*-
# -*- mode: python ; coding: utf-8 -*-
block_cipher = None
a = Analysis(['MigrationStepViewer.py'],
             pathex=['D:\\apps\\py_work\\migtool_plugin\\migtool_viewer'],
             binaries=[('logo.ico','.')],
             datas=[],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='MigrationStepViewer',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=False,
          icon='logo.ico' )

"""
    change_root ="D:"
    cd_path = r"cd D:\apps\py_work\migtool_plugin\migtool_viewer"
    compile_py = r"pyinstaller.exe -i ./logo.ico -F -w .\MigrationStepViewer.spec --onefile"
    os.system(change_root)
    os.system(cd_path)
    os.system(compile_py)

def check_tkversion():
    import tkinter
    print("Checking tk version",tkinter.TkVersion)


def test_tkstylemap():
    import tkinter
    root = tkinter.Tk()
    style = ttk.Style(root)
    style.configure("Treeview", foreground="yellow",
                    background="grey", fieldbackground="green")
    tree = ttk.Treeview(root, columns=('Data'))
    tree.heading('#0', text='Item')
    tree.heading('#1', text='Data')
    tree.insert("", "end", text="Item_0", values=100, tags="A")
    tree.insert("", "end", text="Item_1", values=200, tags="B")
    tree.insert("", "end", text="Item_2", values=300, tags="C")
    tree.tag_configure("A", foreground="black")  # Py 3.7.3: no effect
    tree.tag_configure("B", foreground="red")
    tree.pack()

    def fixed_map(option):
        # Fix for setting text colour for Tkinter 8.6.9
        # From: https://core.tcl.tk/tk/info/509cafafae
        #
        # Returns the style map for 'option' with any styles starting with
        # ('!disabled', '!selected', ...) filtered out.

        # style.map() returns an empty list for missing options, so this
        # should be future-safe.
        return [elm for elm in style.map('Treeview', query_opt=option) if
            elm[:2] != ('!disabled', '!selected')]


    style = ttk.Style()
    style.map('Treeview', foreground=fixed_map('foreground'),
            background=fixed_map('background'))
    root.mainloop()


compile2exe()

# test_tkstylemap()

