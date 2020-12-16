# -*- coding: utf-8 -*-

'''
@Author: windyoung
@Date: 2020-10-10 21:22:33
LastEditTime: 2020-12-15 22:55:26
LastEditors: windyoung
@Description:
FilePath: \migtool_plugin\migtool_viewer\MigrationStepViewer_oracle.py
'''

import logging
import os
import re
import sys
import tkinter
import tkinter.messagebox
from tkinter import Scrollbar, StringVar, ttk,filedialog

import cx_Oracle
import yaml
import records


class stepviewData():
    def __init__(self, migsever_db_constr):
        self.migsever_db_constr = migsever_db_constr
        self.init_db_con()
        pass

    def get_all_steps_for_exporter(self, project_id):
        sql = f''' SELECT COUNT(1) cnt
        FROM MGF_PROJECT A
        WHERE A.PROJECT_ID = :PROJECT_ID
        AND A.STATE = 'A' '''
        self.db_cur.execute(sql, {"PROJECT_ID": project_id})
        res = self.db_cur.fetchall()[0][0]
        return res

    def init_db_con(self):
        # oracle 
        self.db_con = cx_Oracle.connect(self.migsever_db_constr)
        self.db_cur = self.db_con.cursor()
 

    def init_db_con_ora(self,migsever_db_constr):
        # oracle 
        self.db_con = cx_Oracle.connect(migsever_db_constr)
        self.db_cur = self.db_con.cursor()
 
        
    def check_project_id(self, project_id):
        sql = f''' SELECT COUNT(1) cnt
        FROM MGF_PROJECT A
        WHERE A.PROJECT_ID = :PROJECT_ID
        AND A.STATE = 'A' '''
        self.db_cur.execute(sql, {"PROJECT_ID": project_id})
        res = self.db_cur.fetchall()[0][0]
        return res

    def get_project_info(self, project_id):
        sql = f''' SELECT A.PROJECT_ID||'|'||A.PROJECT_NAME  p_info
        FROM MGF_PROJECT A
        WHERE A.PROJECT_ID = :PROJECT_ID
        AND A.STATE = 'A' '''
        self.db_cur.execute(sql, {"PROJECT_ID": project_id})
        res = self.db_cur.fetchall()[0][0]
        return res

    def get_mgf_catg_id(self, project_id, exec_order_id):
        sql = "SELECT a.step_catg_id FROM MGF_MIG_FLOW_CATG A  WHERE A.PROJECT_ID =  :PROJECT_ID  AND A.EXEC_ORDER_ID = :EXEC_ORDER_ID"
        self.db_cur.execute(sql, {"PROJECT_ID": project_id, "EXEC_ORDER_ID": exec_order_id})
        res = self.db_cur.fetchall()[0][0]
        return res

    def get_all_steps_by_catgid(self, step_catg_id):
        sql = '''SELECT A.EXEC_ORDER_ID, A.STEP_ID, A.STEP_NAME, A.FUNCTION_CODE, A.STATE
        FROM MGF_MIG_FLOW_STEP A
        WHERE A.STEP_CATG_ID = :STEP_CATG_ID 
        ORDER BY  A.EXEC_ORDER_ID ASC        
        '''
        self.db_cur.execute(sql, {"STEP_CATG_ID": step_catg_id})
        res = self.db_cur.fetchall()
        return res

    def get_step_detail_by_stepid(self, step_id):
        sql = "SELECT A.FUNC_PAR_LIST, A.STEP_NAME ,A.STATE ,A.FUNCTION_CODE,A.BACKGROUND,A.FLOW,A.DEPEND_FLOW FROM MGF_MIG_FLOW_STEP A WHERE A.STEP_ID = :STEP_ID"
        res = []
        self.db_cur.execute(sql, {"STEP_ID": step_id})
        for row in self.db_cur:
            res.append([row[0].read(), row[1], row[2],
                        row[3], row[4], row[5], row[6]])
        return res

    def format_param_cur_value(self, rec):
        # A.PAR_VER_CODE ,A.PAR_CODE, A.GET_TYPE, A.CON_ID, A.SQL, A.CONSTANT,A.CURRENT_VALUE,A.COMMENTS
        # 0                 1           2           3       4       5           6               7
        # ,CONSTANT,COMMAND,SQL
        if rec[2] == "CONSTANT":
            return[rec[1], rec[2], rec[6]]
        elif rec[2] == "COMMAND":
            return[rec[1], rec[2], f"cur value:{rec[6]} <-\n command:{rec[4]}"]
        elif rec[2] == "SQL":
            return[rec[1], rec[2], f"cur value:{rec[6]} <-\n db: {rec[3]},sql:{rec[4]}"]

    def get_param_cur_value(self, project_id, par_code):
        result = []
        sql_par_ver_code = "SELECT a.par_ver_code FROM MGF_PROJECT A WHERE A.PROJECT_ID = :PROJECT_ID "
        self.db_cur.execute(sql_par_ver_code, {"PROJECT_ID": project_id})
        sql_par_ver_code_res = self.db_cur.fetchall()
        if len(sql_par_ver_code_res) == 1:
            par_ver_code = sql_par_ver_code_res[0][0]
        else:
            par_ver_code = "Global"
        sql = '''SELECT A.PAR_VER_CODE ,A.PAR_CODE, A.GET_TYPE, A.CON_ID, A.SQL, A.CONSTANT,A.CURRENT_VALUE,A.COMMENTS
        FROM MGF_PARAMETER A
        WHERE A.PAR_CODE = :PAR_CODE
        AND A.PROJECT_ID = :PROJECT_ID
        '''
        self.db_cur.execute(
            sql, {"PROJECT_ID": project_id, "PAR_CODE": par_code})
        res = self.db_cur.fetchall()
        for row in res:
            # COMMENTS 以# 开头 用 par_ver_code  ，否则 用 Global
            if row[7][0] == "#" and row[0] == par_ver_code:
                result.append(self.format_param_cur_value(row))
            elif row[0] == "Global":
                result.append(self.format_param_cur_value(row))
        return result

    def search_step_detail(self, catg_id, keyword):
        if keyword == "":
            return 0
        s_CATG_ID = catg_id
        s_KEYWORD = f"{keyword}".upper()
        param_list = {"STEP_CATG_ID": s_CATG_ID, "s_KEYWORD": s_KEYWORD}
        print(param_list)
        sql = """SELECT A.STEP_ID   FROM MGF_MIG_FLOW_STEP A WHERE (REGEXP_LIKE(UPPER(A.STEP_NAME), :s_KEYWORD ) 
                  OR REGEXP_LIKE(UPPER(A.FUNC_PAR_LIST), :s_KEYWORD )) AND A.STEP_CATG_ID = :STEP_CATG_ID   """
        self.db_cur.execute(sql, param_list)
        res_ = self.db_cur.fetchall()
        res = []
        for row in res_:
            res.append(str(row[0]))
        return res


class stepviewGui(tkinter.Frame):
    def __init__(self):
        os.putenv("NLS_LANG", "SIMPLIFIED CHINESE_CHINA.ZHS16GBK")
        self.migsever_db_constr = ""
        self.project_id = ""
        self.draw_GUI()

    def set_oracle_path(self):
        # print(os.environ)
        all_path=os.environ['PATH']
        ora_path=filedialog.askdirectory(title="choose database client path")
        newpath = f"{all_path};{ora_path}"
        os.putenv("PATH", newpath)

    def rd_cfg(self):
        if os.path.exists("./migstepviewer_oracle.cfg"):
            with open("./migstepviewer_oracle.cfg", 'r', encoding="utf-8") as fp:
                a = yaml.safe_load(fp)
            print(a)
            self.migsever_db_constr = a['db_con']
            self.project_id = a['projectid']
            # 先删后插
            self.ent_db_con_str.delete(0, 'end')
            self.ent_db_con_str.insert('end', self.migsever_db_constr)
            self.ent_project_idstr["state"] = "normal"
            self.ent_project_idstr.delete(0, 'end')
            self.ent_project_idstr.insert('end', self.project_id)

    def test_db(self):
        try:
            self.db_inst = stepviewData(self.migsever_db_constr)
            self.db_inst.db_cur.execute(
                "SELECT * FROM MGF_PROJECT A WHERE ROWNUM < 3 ")
            print(self.db_inst.db_cur.fetchall())
        except Exception as e:
            print("ERROR IN ORACLE : {}".format(str(e)))
            self.btn_project_id_lock["state"] = "disabled"
            self.ent_project_idstr["state"] = 'readonly'
            return str(e)
        return True

    def clean_treeview_text(self):
        items = self.tree_allsteps.get_children()
        [self.tree_allsteps.delete(item) for item in items]
        items = self.tree_onestep.get_children()
        [self.tree_onestep.delete(item) for item in items]
        self.text_stepdetail.delete(1.0, tkinter.END)
        pass

    def filling_allsteps_data_in_treeview(self, data):
        # 插入数据
        for i in data:
            # 如果状态为 DISABLE ， 修改背景色
            if i[4] == 'DISABLE':
                self.tree_allsteps.tag_configure(
                    'disabledstep', background="black", foreground="white")
                # 定义disable的 值的格式
                self.tree_allsteps.insert(
                    '', 'end', values=i, tags=('disabledstep',))
            else:
                self.tree_allsteps.insert('', 'end', values=i, )

    def show_onestep(self, event):
        "从选中获取stepid 在 stepdetail里 展示内容"
        # 设置了单选，这里处理选中的一行
        item = self.tree_allsteps.selection()
        item_text = self.tree_allsteps.item(item, "values")
        # 输出所选行的第一列的值
        if item_text == "":
            return False
        step_id = item_text[1]
        res_ = self.db_inst.get_step_detail_by_stepid(step_id)
        # A.FUNC_PAR_LIST, A.STEP_NAME ,A.STATE ,A.FUNCTION_CODE,A.BACKGROUND,A.FLOW,A.DEPEND_FLOW
        stepdetails = res_[0][0]
        stepname = res_[0][1]
        state = res_[0][2]
        funccode = res_[0][3]
        background = res_[0][4]
        flow = res_[0][5]
        depflow = res_[0][6]
        if len(res_) == 1:
            stepdetail = yaml.full_load(stepdetails)
            # 展示 内容到 text
            # 先清除原内容
            self.text_stepdetail.delete(1.0, tkinter.END)
            items = self.tree_onestep.get_children()
            [self.tree_onestep.delete(item) for item in items]
            # 插入 具体信息
            # 如果状态为 DISABLE ， 修改背景色
            if state == 'DISABLE':
                self.text_stepdetail.insert(
                    "end", f"DISABLED STEP, step id[ {step_id} ], name [ {stepname} ] \n", 'disabledstep')
            else:
                self.text_stepdetail.insert(
                    "end", f"step id[ {step_id} ], name [ {stepname} ] \n")
            self.text_stepdetail.insert(
                "end", f"FUNCTION_CODE[{funccode}],BACKGROUND[{background}],FLOW[{flow}],DEPEND_FLOW[{depflow}]  \n")
            self.text_stepdetail.insert(
                "end", ">>>>>>>>>>>>>>>>>>>detail infomation>>>>>>>>>>>>>>>>>>>>>>>>>>\n", 'tag1')
            for key in stepdetail:
                key_ = str(key).upper()
                values_ = stepdetail[key]
                # print("values_", values_)
                if key_ == 'TABLE_NAME_LIST':
                    values_ = "\n{}".format(str(values_).replace(',', '\n'))
                elif key_ == 'RES_LIST':
                    # print("values_ reformt ", type(values_), len(values_))
                    values_ = "\n{}".format("\n".join(values_))
                elif key_ == 'TABLE_LIST':
                    # print("values_ reformt ",type(values_),len(values_))
                    values_ = "\n{}".format("\n".join(values_))
                elif key_ == 'TRIGGER_LIST':
                    # print("values_ reformt ",type(values_),len(values_))
                    values_ = "\n{}".format("\n".join(values_))
                self.text_stepdetail.insert(
                    "end", f"item--> {key_}:\nvalue--> {values_} \n")
                self.text_stepdetail.insert(
                    "end", "<------------------------------->\n", 'tag2')
            self.text_stepdetail.insert(
                "end", ">>>>>>>>>>>>>>>>>>> params infomation>>>>>>>>>>>>>>>>>>>>>>>>>>\n", 'tag1')
            # 处理参数
            # 获取TEXT的文本
            this_text = self.text_stepdetail.get('0.0', 'end')
            par = r"\$\{(\w+)?\}"
            param_list = re.findall(par, this_text)
            params_res = []
            for i in param_list:
                a = self.db_inst.get_param_cur_value(self.project_id, i)
                if len(a) == 0:
                    continue
                params_res.append(a[0])
            for i in params_res:
                self.tree_onestep.insert('', 'end', values=i)
            return True
        else:
            print("ERROR IN get step detail ")
            tkinter.messagebox.showerror(
                'ERROR', f"can not get step detail \ncheck step id {step_id}  ", parent=self.root)
            self.root.focus_force()
            return False

    def show_params(self, event):
        for item in self.tree_onestep.selection():
            item_text = self.tree_onestep.item(item, "values")
            self.text_stepdetail.insert(
                "end", f"param [{item_text[0]}] : {item_text[2]} \n")
            self.text_stepdetail.insert(
                "end", "------------------------------->\n", 'tag2')

    def search_catg(self,):
        catg_id = self.catg_id
        project_id = self.project_id
        keyword = self.strV_search_keyword.get()
        if keyword == "":
            return 0
        res = self.db_inst.search_step_detail(catg_id, keyword)
        if res == 0:
            return 0
        items = self.tree_allsteps.get_children()
        for item in items:
            item_text = self.tree_allsteps.item(item, "values")
            if item_text[1] not in res:
                self.tree_allsteps.delete(item)
        items = self.tree_onestep.get_children()
        [self.tree_onestep.delete(item) for item in items]
        self.text_stepdetail.delete(1.0, tkinter.END)

    def btn_connect_db(self):
        "点击 connect 按钮：1，清空其他地方的展示；2，锁定 数据库连接串 self.migsever_db_constr  ;3，检查数据库是否可以连接 ;4,解锁项目id"
        # 1，清空其他地方的展示
        # self.strV_project_id.set("")
        self.btn_search['state'] = "disabled"
        # 2，锁定 数据库连接串
        # 2.1 拼接 数据库连接串
        self.migsever_db_constr = self.ent_db_con_str.get()
        print("migsever_db_constr",self.migsever_db_constr)
        # 3，检查数据库是否可以连接
        res=self.test_db()
        if res == True:
            self.ent_db_con_str["bg"] = "green"
            # 4,解锁项目id
            # self.ent_project_idstr["state"] ='readonly'
            self.ent_project_idstr["state"] = 'normal'
            self.btn_project_id_lock["state"] = 'normal'
            self.btn_project_id_lock["bg"] = "green"
            # 5, 锁定选择框
            for i in self.allbtn_catg:
                self.allbtn_catg[i]["state"] = 'disabled'
                self.allbtn_catg[i]["bg"] = self.dft_bg
            # 6，清空输入
            self.clean_treeview_text()
        else:
            self.ent_db_con_str["bg"] = "red"
            tkinter.messagebox.showerror(
                'ERROR', f'db test connect error\n{res}', parent=self.root)
            self.root.focus_force()

    def btn_check_project(self):
        "点击 OK 按钮：1，检查   project_id的输入  ；2，检查项目状态 ;3, 绑定  project_id的输入 "
        # 1，检查   project_id的输入
        try:
            project_id_ = str(self.ent_project_idstr.get())
            project_id_ = int(project_id_.split("|")[0])
        except Exception as e:
            project_id_ = ""
        # 2，检查项目状态
        res = self.db_inst.check_project_id(project_id_)
        if res == 1:
            # self.ent_project_idstr["bg"] = "green"
            # self.ent_project_idstr["fg"] = "white"
            # 锁定 输入框状态
            self.ent_project_idstr["state"] = 'disabled'
            self.btn_project_id_lock["state"] = 'disabled'
            self.btn_project_id_lock["bg"] = "green"
            # 解锁 选择框按钮
            for i in self.allbtn_catg:
                self.allbtn_catg[i]["state"] = 'normal'
                self.allbtn_catg[i]["bg"] = 'green'
            # 3, 绑定  project_id的输入
            self.project_id = project_id_
            # 4, 数据库连接写入配置文件
            with open("./migstepviewer_oracle.cfg", 'w', encoding="utf-8") as fp:
                yaml.safe_dump({"db_con": self.ent_db_con_str.get().strip(
                ), "projectid": self.project_id}, fp)
            # 5, 展示project 名字
            namestr = self.db_inst.get_project_info(self.project_id)
            # print(namestr)
            self.strV_project_id.set(namestr)
            # self.ent_project_idstr.setvar(namestr)
        else:
            self.ent_project_idstr["bg"] = "red"
            self.btn_project_id_lock["bg"] = "red"
            tkinter.messagebox.showerror(
                'ERROR', f'project id check error\ncheck project id {project_id_} count\nresult {res}', parent=self.root)
            self.root.focus_force()

    def btn_click_catg_btn(self, exec_order_id):
        "点击category按钮：1，清空下方的展示；2，获取 step_catg_id，没有steps的情况弹窗   3 返回 step_catg_id 4,更新展示全部的step "
        print("exec_order_id", exec_order_id)
        project_id = self.project_id
        # 修改btn的状态
        for i in self.allbtn_catg:
            self.allbtn_catg[i]["state"] = 'normal'
            self.allbtn_catg[i]["bg"] = 'green'
        btn_cate = self.allbtn_catg[exec_order_id]
        btn_cate['bg'] = "deepskyblue"
        self.tree_allsteps["selectmode"] = 'browse'
        self.tree_onestep["selectmode"] = "extended"
        # 1，清空下方的展示
        self.clean_treeview_text()
        # 2 获取 step_catg_id，没有steps的情况弹窗
        try:
            catg_id = self.db_inst.get_mgf_catg_id(project_id, exec_order_id)
            self.catg_id = catg_id
        except Exception as e:
            print("ERROR IN get catg_id : {}".format(str(e)))
            tkinter.messagebox.showerror(
                'ERROR', f"can not get catg_id \ncheck project_id {project_id} ,exec_order_id {exec_order_id}", parent=self.root)
            catg_id = 0
        # 4,更新展示全部的step
        allsteps = self.db_inst.get_all_steps_by_catgid(catg_id)
        self.filling_allsteps_data_in_treeview(allsteps)
        # 5 重置输入框
        self.strV_search_keyword.set("")
        self.btn_search['state'] = 'normal'

    def show_ver(self,event):
    # Submit requirements and bugs to 'zhu.jian@iwhalecloud.com'
        ver_text = '''v0.1 工具基本功能完成
v0.1.1增加配置记忆
2020-10-13 v0.1.2修复按键延后响应,增加版本提示
2020-11-09 v0.1.3增加项目名称显示
2020-11-09 v0.1.4增加滚动条和搜索, 增加中文语言字符设置
2020-12-08 v0.1.5增加分隔符颜色区分和stepname显示,增加value的格式化
2020-12-10 v0.1.6修复step状态显示，增加step详情信息,修改版本提示方式,TRIGGER_LIST展示格式
2020-12-15 v0.1.7增加数据库连接报错提示，增加指定64位oracle客户端环境变量
'''
        tkinter.messagebox.showinfo(
            title=f'版本说明{self.ver},{self.ver_date}', icon=None, message=ver_text, parent=self.root, type="ok")
        self.root.focus_force()

    def resource_path(self, file_):
        basepath_ = getattr(sys, '_MEIPASS', os.path.dirname(
            os.path.abspath(__file__)))
        return os.path.join(basepath_, file_)

    def show_dbconstr_help(self, event):
        with open(self.resource_path('./db_conn_str_format.txt'), 'r', encoding='utf-8')as fp:
            help_srt = str(fp.read())
        tkinter.messagebox.showinfo(
            title=f'connection string format help v{self.ver},{self.ver_date}', icon=None, message=help_srt, parent=self.root, type="ok")
        self.root.focus_force()

    def draw_GUI(self):
        # 版本号，时间
        self.ver = "0.1.7"
        self.ver_date = "2020-12-15"
        # 绘制主窗口
        self.root = tkinter.Tk()
        self.root.title(f"Migration Steps Viewer oracle v{self.ver}")
        self.root.geometry("1210x900+60+30")
        self.root.resizable(1, 1)
        self.root.iconbitmap(self.resource_path('./logo.ico'))
        # 参数绑定
        self.dft_bg = self.root.cget('background')
        self.strV_db_con_str = StringVar()
        self.strV_project_id = StringVar()
        self.strV_step_text = StringVar()
        self.strV_search_keyword = StringVar()
        # 页面布局
        # 输入数据库连接串（可以，连接）
        # 连接时1，清空其他地方的展示；2，锁定 数据库连接串 ; 3，检查数据库是否可以连接
        self.lblframe_input = tkinter.LabelFrame(
            self.root, text="input infomation", padx=5, pady=5)
        self.lblframe_input.pack(side='top', expand=False, fill='x')
        self.lbl_db_con_str = tkinter.Label(
            self.lblframe_input, text="Database Constr:")
        self.lbl_db_con_str.pack(side='left')
        self.ent_db_con_str = tkinter.Entry(
            self.lblframe_input, width=45, textvariable=self.strV_db_con_str)
        self.strV_db_con_str.set(
            "mig_pool/smart@10.45.82.28:1521/orcl input mig database connection string here")
        self.ent_db_con_str.pack(side='left')
        self.btn_con_db = tkinter.Button(
            self.lblframe_input, text="Test&Connect", command=self.btn_connect_db)
        self.btn_con_db.pack(side='left')
        # 选择项目 （可以 确认）
        # 确认时1，锁定 项目id；2，检查项目状态
        self.lbl_project_id = tkinter.Label(
            self.lblframe_input, text="Project id:")
        self.lbl_project_id.pack(side='left')
        self.ent_project_idstr = tkinter.Entry(
            self.lblframe_input, width=30, textvariable=self.strV_project_id)
        self.strV_project_id.set("input project id here")
        self.ent_project_idstr.pack(side='left')
        self.btn_project_id_lock = tkinter.Button(
            self.lblframe_input, text="OK", state='disabled', command=self.btn_check_project)
        self.btn_project_id_lock.pack(side='left')
        self.btn_setenv = tkinter.Button(
            self.lblframe_input, text="SET DB ENV", state='active', command=self.set_oracle_path)
        self.btn_setenv.pack(side='right')
        self.lbl_ver_info = tkinter.Label(
            self.lblframe_input, text=f"   VER: {self.ver}, {self.ver_date}",)
        self.lbl_ver_info.pack(side='right')
        self.lbl_ver_info.bind("<Button-1>",self.show_ver)
        # 读取配置文件
        self.rd_cfg()
        # 7个按钮展示不同的catg
        self.lblframe_catg = tkinter.LabelFrame(
            self.root, text="choose step category", padx=5, pady=5)
        self.lblframe_catg.pack(side='top', expand=False, fill='x')
        # 点击时 1，清空下方的展示；2，没有steps的情况->提示 ， 3,更新展示全部的step
        self.btn_cate1 = tkinter.Button(
            self.lblframe_catg, text="CATG 1: Input", bg="lightgrey", state='disabled', command=lambda: self.btn_click_catg_btn(1))
        self.btn_cate1.pack(side='left')
        self.btn_cate2 = tkinter.Button(
            self.lblframe_catg, text="CATG 2: ReviewData", bg="darkgray", state='disabled', command=lambda: self.btn_click_catg_btn(2))
        self.btn_cate2.pack(side='left')
        self.btn_cate3 = tkinter.Button(
            self.lblframe_catg, text="CATG 3: Transfer", bg="lightgrey", state='disabled', command=lambda: self.btn_click_catg_btn(3))
        self.btn_cate3.pack(side='left')
        self.btn_cate4 = tkinter.Button(
            self.lblframe_catg, text="CATG 4: KPI", bg="darkgray", state='disabled', command=lambda: self.btn_click_catg_btn(4))
        self.btn_cate4.pack(side='left')
        self.btn_cate5 = tkinter.Button(
            self.lblframe_catg, text="CATG 5: Loads", bg="lightgrey", state='disabled', command=lambda: self.btn_click_catg_btn(5))
        self.btn_cate5.pack(side='left')
        self.btn_cate6 = tkinter.Button(
            self.lblframe_catg, text="CATG 6: Test", bg="darkgray", state='disabled', command=lambda: self.btn_click_catg_btn(6))
        self.btn_cate6.pack(side='left')
        self.btn_cate7 = tkinter.Button(
            self.lblframe_catg, text="CATG 7: Rollback", bg="lightgrey", state='disabled', command=lambda: self.btn_click_catg_btn(7))
        self.btn_cate7.pack(side='left')
        self.allbtn_catg = {1: self.btn_cate1,
                            2: self.btn_cate2,
                            3: self.btn_cate3,
                            4: self.btn_cate4,
                            5: self.btn_cate5,
                            6: self.btn_cate6,
                            7: self.btn_cate7, }
        self.btn_search = tkinter.Button(
            self.lblframe_catg, text="search", command=self.search_catg)
        self.btn_search.pack(side='right')
        self.ent_search = tkinter.Entry(
            self.lblframe_catg, width=30, textvariable=self.strV_search_keyword)
        self.ent_search.pack(side='right')
        self.btn_search['state'] = "disabled"
        # 结果展示
        self.lblframe_step = tkinter.LabelFrame(
            self.root, text="step infomation", padx=5, pady=5)
        self.lblframe_step.pack(side='top', expand=True, fill='both')
        # # 一个Treeview展示 step的 执行顺序，stepid，名字，类型，状态（根据状态展示）
        # 左键选中一行 在 单个step的 中展示信息
        # 增加滚动条
        self.sbar_step = Scrollbar(
            self.lblframe_step, orient='vertical', width=15, borderwidth=0)
        self.sbar_step.pack(side='left', fill='y')
        self.tree_allsteps = ttk.Treeview(self.lblframe_step, columns=[
                                          "exec_order_id", "step_id", "step_name", "function_code", "state"], selectmode='browse', show='headings', height=35)
        self.tree_allsteps.column('exec_order_id', width=5, anchor='w')
        self.tree_allsteps.column('step_id', width=20, anchor='w')
        self.tree_allsteps.column('step_name', width=260, anchor='w')
        self.tree_allsteps.column('function_code', width=60, anchor='w')
        self.tree_allsteps.column('state', width=25, anchor='w')
        self.tree_allsteps.heading('exec_order_id', text='exec_order_id')
        self.tree_allsteps.heading('step_id', text='step_id')
        self.tree_allsteps.heading('step_name', text='step_name')
        self.tree_allsteps.heading('function_code', text='function_code')
        self.tree_allsteps.heading('state', text='state')
        # 测试数据
        tree1 = (("1", "1", "1", "1", 'finish'),
                 ("2", "1", "1", "1", 'finish'),
                 ("3", "1", "1", "1", 'finish'))
        self.tree_allsteps.insert(
            '', 'end', values=("0", "1", "1", "1", 'finish'))
        for i in tree1:
            self.tree_allsteps.insert('', 'end', values=i)
        # 配置位置和大小
        self.tree_allsteps.pack(side='left', fill='both', expand=True)
        # 滚动条
        self.tree_allsteps.config(yscrollcommand=self.sbar_step.set)
        self.sbar_step.config(command=self.tree_allsteps.yview)

        # 绑定事件
        # 绑定点击 事件：单击离开 ==========
        self.tree_allsteps.bind("<ButtonRelease-1>", self.show_onestep)
        # 绑定点击 事件：回车键 ===========
        self.tree_allsteps.bind("<Return>", self.show_onestep)
        # 绑定点击 事件：方向上下键 =========== 会有延迟响应的问题
        # self.tree_allsteps.bind("<Up>", self.show_onestep)
        # self.tree_allsteps.bind("<Down>", self.show_onestep)
        # 绑定点击 事件：选中Treeview ==========
        self.tree_allsteps.bind("<<TreeviewSelect>>", self.show_onestep)
        self.tree_allsteps["selectmode"] = "none"
        # 使用frame区分
        self.frm_onestep = tkinter.Frame(self.lblframe_step)
        self.frm_onestep.pack(side='left', fill='both', expand=True)
        # #  或者用ScrolledText 展示 step 内容
        self.text_stepdetail = tkinter.Text(
            self.frm_onestep, width=30, height=40)
        # 配置位置和大小
        self.text_stepdetail.pack(
            side='top', anchor='n', fill='both', expand=False)
        # # 一个Treeview/WORD 展示step或者param 内容 ，一个列表展示 参数值(先不做)
        self.tree_onestep = ttk.Treeview(self.frm_onestep, columns=[
                                         "step item", "type", "value"], show='headings', selectmode='extended', height=5)
        self.tree_onestep.column('step item',  width=50, anchor='w')
        self.tree_onestep.column('type',  width=35, anchor='w')
        self.tree_onestep.column('value',   width=200, anchor='w')
        self.tree_onestep.heading('step item', text='item',)
        self.tree_onestep.heading('type',  text='param type')
        self.tree_onestep.heading('value',  text='current value')
        # 配置位置和大小
        self.tree_onestep.pack(side='top', anchor='s',
                               fill='both', expand=True)
        # 修改内容显示的格式， 申明一个tag,在a位置使用
        self.text_stepdetail.tag_add('tag1', 'end')
        self.text_stepdetail.tag_add('tag2', 'end')
        self.text_stepdetail.tag_add('disabledstep', 'end')
        # 设置tag即插入文字的大小,颜色等
        self.text_stepdetail.tag_config('tag1', foreground='blue')
        self.text_stepdetail.tag_config('tag2', foreground='skyblue')
        self.text_stepdetail.tag_config(
            'disabledstep', foreground='white', background='black')

        # 点击选中值
        # self.tree_onestep.bind("<ButtonRelease-1>", self.show_params)
        self.tree_onestep.bind("<<TreeviewSelect>>", self.show_params)

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
        self.root.mainloop()


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(funcName)s - %(levelname)s - %(message)s')
    app = stepviewGui()
