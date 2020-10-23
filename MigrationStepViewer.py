# -*- coding: utf-8 -*-
'''
@Author: windyoung
@Date: 2020-10-10 21:22:33
LastEditTime: 2020-10-23 10:08:42
LastEditors: windyoung
@Description:
FilePath: \migtool_view\MigrationStepViewer.py
@
'''
import yaml
import logging
import os
import re
import tkinter
from tkinter import StringVar, ttk
import tkinter.messagebox

import cx_Oracle


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
        # print(res)
        return res
        pass

    def init_db_con(self):
        self.db_con = cx_Oracle.connect(self.migsever_db_constr)
        self.db_cur = self.db_con.cursor()

    def check_project_id(self, project_id):
        sql = f''' SELECT COUNT(1) cnt
        FROM MGF_PROJECT A
        WHERE A.PROJECT_ID = :PROJECT_ID
        AND A.STATE = 'A' '''
        self.db_cur.execute(sql, {"PROJECT_ID": project_id})
        res = self.db_cur.fetchall()[0][0]
        # print(res)
        return res

    def get_mgf_catg_id(self, project_id, exec_order_id):
        sql = "SELECT a.step_catg_id FROM MGF_MIG_FLOW_CATG A  WHERE A.PROJECT_ID =  :PROJECT_ID  AND A.EXEC_ORDER_ID = :EXEC_ORDER_ID"
        self.db_cur.execute(
            sql, {"PROJECT_ID": project_id, "EXEC_ORDER_ID": exec_order_id})
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
        sql = "SELECT a.func_par_list FROM MGF_MIG_FLOW_STEP A WHERE A.STEP_ID = :STEP_ID"
        res = []
        self.db_cur.execute(sql, {"STEP_ID": step_id})
        # res = self.db_cur.fetchall()
        for row in self.db_cur:
            res.append(row[0].read())
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
        # print(sql_par_ver_code_res)
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
        # print("get_param_cur_value res", res)
        for row in res:
            # COMMENTS 以# 开头 用 par_ver_code  ，否则 用 Global
            if row[7][0] == "#" and row[0] == par_ver_code:
                result.append(self.format_param_cur_value(row))
            elif row[0] == "Global":
                result.append(self.format_param_cur_value(row))
        # print("get_param_cur_value result", result)
        return result


class stepviewGui(tkinter.Frame):
    def __init__(self):
        self.migsever_db_constr = ""
        self.project_id = ""
        self.draw_GUI()

    def rd_cfg(self):
        if os.path.exists("./migstepviewer.cfg"):
            with open("./migstepviewer.cfg", 'r', encoding="utf-8") as fp:
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
            return False
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
            self.tree_allsteps.insert('', 'end', values=i, tags=('color',))
        # 如果状态为 DISABLE ， 修改背景色
        items = self.tree_allsteps.get_children()
        for item in items:
            item_text = self.tree_allsteps.item(item, "values")
            if item_text[4] == 'DISABLE':
                # self.tree_allsteps.item(item,background="black",foreground="white")
                # self.tree_allsteps.grid_rowconfigure(self.tree_allsteps.index(item) ,background="black",foreground="white")
                self.tree_allsteps.tag_configure(
                    'color', background="black", foreground="white")

    def show_onestep(self, event):
        "从选中获取stepid 在 stepdetail里 展示内容"
        # 设置了单选，这里处理选中的一行
        item = self.tree_allsteps.selection()
        item_text = self.tree_allsteps.item(item, "values")
        print(item, item_text, type(item_text))  # 输出所选行的第一列的值
        if item_text == "":
            return False
        step_id = item_text[1]
        stepdetails = self.db_inst.get_step_detail_by_stepid(step_id)
        if len(stepdetails) == 1:
            stepdetail = yaml.load(stepdetails[0])
            # print(stepdetail)
            # 展示 内容到 text
            # 先清除原内容
            self.text_stepdetail.delete(1.0, tkinter.END)
            items = self.tree_onestep.get_children()
            [self.tree_onestep.delete(item) for item in items]
            # 插入 具体信息
            self.text_stepdetail.insert(
                "end", f"step [{step_id}] detail infomation\n------------------------------->\n")
            for key in stepdetail:
                self.text_stepdetail.insert("end",
                                            f"item--> {str(key).upper()}:\nvalue--> {str(stepdetail[key])} \n------------------------------->\n")
            self.text_stepdetail.insert(
                "end", "\n>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>\n")
            # 处理参数
            # 获取TEXT的文本
            this_text = self.text_stepdetail.get('0.0', 'end')
            # par=r"\$\{([a-zA-Z0-9]|_)+\}"
            par = r"\$\{(\w+)?\}"
            # print(this_text)
            param_list = re.findall(par, this_text)
            # print(param_list)
            params_res = []
            for i in param_list:
                a = self.db_inst.get_param_cur_value(self.project_id, i)
                if len(a) == 0:
                    continue
                params_res.append(a[0])
            # print(params_res)
            for i in params_res:
                self.tree_onestep.insert('', 'end', values=i)
            return True
        else:
            print("ERROR IN get step detail ")
            tkinter.messagebox.showerror(
                'ERROR', f"can not get step detail \ncheck step id {step_id} ", parent=self.root)
            self.root.focus_force()
            return False

    def show_params(self, event):
        for item in self.tree_onestep.selection():
            item_text = self.tree_onestep.item(item, "values")
            # print(item,item_text)
            self.text_stepdetail.insert(
                "end", f"param [{item_text[0]}] : {item_text[2]} \n------------------------------->\n")

    def btn_connect_db(self):
        "点击 connect 按钮：1，清空其他地方的展示；2，锁定 数据库连接串 self.migsever_db_constr  ;3，检查数据库是否可以连接 ;4,解锁项目id"
        # 1，清空其他地方的展示
        # self.strV_project_id.set("")
        # 2，锁定 数据库连接串
        self.migsever_db_constr = self.ent_db_con_str.get()
        print(self.migsever_db_constr)
        # 3，检查数据库是否可以连接
        if self.test_db() == True:
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
                'ERROR', 'db test connect error', parent=self.root)
            self.root.focus_force()

    def btn_check_project(self):
        "点击 OK 按钮：1，检查   project_id的输入  ；2，检查项目状态 ;3, 绑定  project_id的输入 "
        # 1，检查   project_id的输入
        try:
            project_id_ = int(self.ent_project_idstr.get())
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
        else:
            self.ent_project_idstr["bg"] = "red"
            self.btn_project_id_lock["bg"] = "red"
            tkinter.messagebox.showerror(
                'ERROR', 'project id check error', parent=self.root)
            self.root.focus_force()
        #4, 数据库连接写入配置文件
        with open("./migstepviewer.cfg", 'w', encoding="utf-8") as fp:
            yaml.safe_dump({"db_con": self.ent_db_con_str.get().strip(
            ), "projectid": self.ent_project_idstr.get().strip()}, fp)

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
            # project_id, exec_order_id = 10,10
            catg_id = self.db_inst.get_mgf_catg_id(project_id, exec_order_id)
            print("catg_id", catg_id)
        except Exception as e:
            print("ERROR IN get catg_id : {}".format(str(e)))
            tkinter.messagebox.showerror(
                'ERROR', f"can not get catg_id \ncheck project_id {project_id} ,exec_order_id {exec_order_id}", parent=self.root)
            catg_id = 0
        # 4,更新展示全部的step
        allsteps = self.db_inst.get_all_steps_by_catgid(catg_id)
        # print(allsteps)
        self.filling_allsteps_data_in_treeview(allsteps)

    def show_ver(self):
        tkinter.messagebox.showinfo(
            title=f'版本说明{self.ver}', icon=None, message="v0.1 工具基本功能完成\nv0.1.1 增加配置记忆\nv0.1.2 修复按键延后相应,增加版本提示", parent=self.root, type="ok")
        self.root.focus_force()

    def draw_GUI(self):
        """
        """
        # 版本号，时间
        self.ver = "0.1.2"

        # 绘制主窗口
        self.root = tkinter.Tk()
        self.root.title(f"Migration Steps Viewer v{self.ver}")
        self.root.geometry("1210x900+10+10")
        self.root.resizable(1, 1)
        self.show_ver()

        # 参数绑定
        self.dft_bg = self.root.cget('background')
        self.strV_db_con_str = StringVar()
        self.strV_project_id = StringVar()
        self.strV_step_text = StringVar()
        # 页面布局
        # 输入数据库连接串（可以，连接）
        # 连接时1，清空其他地方的展示；2，锁定 数据库连接串 ; 3，检查数据库是否可以连接
        self.lblframe_input = tkinter.LabelFrame(
            self.root, text="input infomation", padx=5, pady=5)
        self.lblframe_input.pack(side='top', expand=True, fill='both')
        self.lbl_db_con_str = tkinter.Label(
            self.lblframe_input, text="Database Constr:")
        self.lbl_db_con_str.pack(side='left')
        self.ent_db_con_str = tkinter.Entry(
            self.lblframe_input, width=45, textvariable=self.strV_db_con_str)
        self.strV_db_con_str.set(
            "mig_pool/smart@10.45.82.28:1521/orcl input mig database connection string here")
        # self.strV_db_con_str.set("zj_mig/smart@10.45.82.28:1521/orcl")
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
            self.lblframe_input, width=21, textvariable=self.strV_project_id)
        self.strV_project_id.set("input project id here")
        self.ent_project_idstr.pack(side='left')
        self.btn_project_id_lock = tkinter.Button(
            self.lblframe_input, text="OK", state='disabled', command=self.btn_check_project)
        self.btn_project_id_lock.pack(side='left')
        self.lbl_ver_info = tkinter.Label(
            self.lblframe_input, text=f"   VER: {self.ver}, 2020-10-23")
        self.lbl_ver_info.pack(side='right')
        # 读取配置文件
        self.rd_cfg()
        # 7个按钮展示不同的catg
        self.lblframe_catg = tkinter.LabelFrame(
            self.root, text="choose step category", padx=5, pady=5)
        # self.lblframe_catg.place(x=5, y=65, width=1200)
        self.lblframe_catg.pack(side='top', expand=True, fill='both')

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

        # 结果展示
        self.lblframe_step = tkinter.LabelFrame(
            self.root, text="step infomation", padx=5, pady=5)
        # self.lblframe_step.place(x=5, y=125, width=1200)
        self.lblframe_step.pack(side='top', expand=True, fill='both')
        # # 一个Treeview展示 step的 执行顺序，stepid，名字，类型，状态（根据状态展示）
        # 左键选中一行 在 单个step的 中展示信息

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
            self.frm_onestep, width=80, height=40)
        # 配置位置和大小
        self.text_stepdetail.pack(
            side='top', anchor='n', fill='both', expand=True)

        # # 一个Treeview/WORD 展示step或者param 内容 ，一个列表展示 参数值(先不做)
        self.tree_onestep = ttk.Treeview(self.frm_onestep, columns=[
                                         "step item", "type", "value"], show='headings', selectmode='extended', height=8)
        self.tree_onestep.column('step item',  width=50, anchor='w')
        self.tree_onestep.column('type',  width=35, anchor='w')
        self.tree_onestep.column('value',   width=200, anchor='w')

        self.tree_onestep.heading('step item', text='item',)
        self.tree_onestep.heading('type',  text='get type')
        self.tree_onestep.heading('value',  text='current value')
        # 配置位置和大小
        self.tree_onestep.pack(side='top', anchor='s',
                               fill='both', expand=True)
        # 点击选中值
        self.tree_onestep.bind("<ButtonRelease-1>", self.show_params)
        self.tree_onestep.bind("<<TreeviewSelect>>", self.show_params)

        self.root.mainloop()


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(funcName)s - %(levelname)s - %(message)s')
    app = stepviewGui()
