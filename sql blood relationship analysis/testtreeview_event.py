'''
Author: windyoung
Date: 2020-10-10 23:22:30
LastEditTime: 2020-10-22 19:58:12
LastEditors: windyoung
Description: 
FilePath: \migtool_view\sql blood relationship analysis\testtreeview_event.py

'''
import tkinter
from tkinter import ttk  # 导入内部包

 
def test_treaview():
    li = ['王记','12','男']
    root = tkinter.Tk()
    root.title('测试')
    tree = ttk.Treeview(root,columns=['1','2','3'],show='headings')
    tree.column('1',width=100,anchor='center')
    tree.column('2',width=100,anchor='center')
    tree.column('3',width=100,anchor='center')
    tree.heading('1',text='姓名')
    tree.heading('2',text='学号')
    tree.heading('3',text='性别')
    tree.insert('','end',values=li)
    tree.grid()
    
    
    def treeviewClick(event):#单击
        print ('单击')
        for item in tree.selection():
            item_text = tree.item(item,"values")
            print(item_text)#输出所选行的第一列的值
    
    tree.bind('<ButtonRelease-1>', treeviewClick)#绑定单击离开事件===========
    
    root.mainloop()

def test_re():
    import re 
    this_text=r'''step detail infomation
    ------------------------------->
    item--> CMD:
    value--> source .bash_profile; 
    ${QMDB_HOME_PATH}/bin/mdbcimport -c ocs -t bal --file ${QMDB_HOME_PATH}/bal02.txt --server ${QMDB_HOST_IP_B}:${QMDB_PORT_ID} -F 'YYYY-MM-DD HH:MM:SS'  
    ------------------------------->
    item--> FINISH:
    value--> ]$ 
    ------------------------------->
    item--> IP:
    value--> ${QMDB_HOST_IP_B} 
    ------------------------------->
    item--> IS_SSH:
    value--> Y 
    ------------------------------->
    item--> PORT:
    value--> 22 
    ------------------------------->
    item--> PWD:
    value--> ${QMDB_HOST_PWD_B} 
    ------------------------------->
    item--> USER:
    value--> ${QMDB_HOST_USER_B} 
    ------------------------------->
    '''
    #par=r"\$\{([a-zA-Z0-9]|_)*\}"
    par=r"\$\{(\w+)?\}"
    param_list=re.findall(par,this_text )
    print(param_list)
test_re()