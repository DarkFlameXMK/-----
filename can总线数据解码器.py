# -*-coding: utf-8-*-

import pandas as pd
import os
from time import sleep
from tkinter import *
from tkinter import ttk
#导入封装的文件管理器
from file_browser import File_browser
import re
from tkinter import scrolledtext
from Checkbar import Checkbar
import threading
from choose_excel import Excel_browser
import decoder as dc

pd.options.mode.chained_assignment = None

#建立根窗口
base = Tk()
base.geometry('1000x500')
base.title('CAN报文解析器')

#建立选择配置文件的下拉菜单
text0 = StringVar()
text0.set('请选择配置文件')
label0 = Label(base,textvariable=text0)
file_list = os.listdir(os.getcwd())
cfg_file_list = []
for i in file_list:
    if re.match(r"^.*\.cfg$",i):
        cfg_file_list.append(i)
cfg_file_choose = ttk.Combobox(base)
cfg_file_choose['value'] = cfg_file_list
cfg_file_path = ''

#在下拉菜单中选中配置文件后，将文件路径赋值给cfg_file_path
def choose(event):
    global cfg_file_path
    cfg_file_path = cfg_file_choose.get()
cfg_file_choose.bind("<<ComboboxSelected>>",choose)

#定义从配置文件中提取参数的命令
skiprows = 0
usecols = []
id_col_name = ''
kargs_list = []
def get_kargs():
    if len(kargs_list) == 0:
        get_kargs_()
    else:
        text0.set('请勿重复点击！')

def get_kargs_():
    global skiprows,usecols,id_col_name
    if cfg_file_path:
        with open(cfg_file_path) as cfgfile:
            f1line = cfgfile.readlines()
        count=0
        b = []
        for i in f1line:
            if re.match(r"^跳过行数", i):
                skiprows = int(re.split(r'行数：', i)[-1].strip())
            if re.match(r"^读取的列的范围：", i):
                usecols = re.split(r'范围：', i)[-1].strip().split()
                usecols = list(map(int, usecols))
            if re.match(r"^信号标签所在", i):
                id_col_name = re.split(r'col_name：', i)[-1].strip()
            if re.match(r"^信号\d", i):
                b.append(count)
            count += 1
        ss = []
        for i in b:
            ss.append(f1line[i:i + 8])
        for i in ss:
            karg_dict = {}
            karg_dict.update(id_col_name=id_col_name)
            for j in i:
                if re.match(r'^.信号名称', j):
                    karg_dict.update(signal_name=re.split(r'名称：', j)[-1].strip())
                if re.match(r'^.信号标签', j):
                    karg_dict.update(id_value=re.split(r'标签：', j)[-1].strip())
                if re.match(r'^.信号格式', j):
                    karg_dict.update(form=re.split(r'格式：', j)[-1].strip())
                if re.match(r'^.*起始位', j):
                    karg_dict.update(start=int(re.split(r'始位：', j)[-1].strip()))
                if re.match(r'^.*宽度', j):
                    karg_dict.update(width=int(re.split(r'宽度：', j)[-1].strip()))
                if re.match(r'^.*信号位置', j):
                    try:
                        karg_dict.update(V_position=int(re.split(r'信号位置：', j)[-1].strip()))
                    except:
                        pass
                if re.match(r'^.倍率', j):
                    karg_dict.update(zoom=float(re.split(r'倍率：', j)[-1].strip()))
            if karg_dict:
                kargs_list.append(karg_dict)
        Kargs.delete('1.0', 'end')
        Kargs.insert(END, skiprows)
        Kargs.insert(END, '\n')
        Kargs.insert(END, usecols)
        Kargs.insert(END, '\n')
        for i in kargs_list:
            Kargs.insert(END,i)
            Kargs.insert(END, '\n')
        Kargs.config(state=DISABLED)
    else:
        Kargs.insert(END, '请选择配置文件')
    create_check_button()

def thread_it(func, *args):
    '''将函数打包进线程'''
    # 创建
    t = threading.Thread(target=func, args=args)
    # 守护 !!!
    t.setDaemon(True)
    # 启动
    t.start()

Kargs = scrolledtext.ScrolledText(base, bd=2, width=30, height=5)
get_kargs = Button(base,
                text='提取参数',
                command=get_kargs,
                activeforeground='white',
                activebackground='green')

#显示CSV文件路径的文本组件
text1 = StringVar()
text1.set('请选择数据文件')
label1 = Label(base,textvariable=text1)
Text_csv_path = Text(base, bd=2,width=30,height = 2)
csv_path = ''

#定义CSV文件选择命令
def file_choose():
    global csv_path,Text_csv_path,base
    d = File_browser(os.curdir)
    base.wait_window(d.top)
    csv_path =d.path
    Text_csv_path.delete('1.0', 'end')
    Text_csv_path.insert(END,csv_path )
    # mainloop()

#定义读取csv文件命令
data = None
def read_csv():
    global data
    if csv_path:
        try:
            with open(csv_path) as csv_file:
                data = pd.read_csv(csv_file,skiprows=skiprows,usecols = range(usecols[0],usecols[1]))
            # text1.set(csv_path)
        except:
            print(csv_path)
            text1.set('不是标准格式的CSV文件，请重新选择或更改配置')
    else:
        text1.set('请选择CSV文件')
def check_progress():
    text1.set('正在读取。。。')
    while True:
        if type(data) != type(None):
            # print(len(data))
            text1.set('读取完成，共%d条数据'%len(data))
            break
        sleep(0.5)
    Button(signal_choose, text='解码并输出到excel', command=decode_to_excel_).pack()

#将高耗时操作线程化，防止界面卡死
# 创建进程
t_read_csv = threading.Thread(target=read_csv)
t_check_progress = threading.Thread(target=check_progress)

# 设置守护
t_read_csv.setDaemon(True)
t_check_progress.setDaemon(True)

#定义‘读取csv按钮’的按键命令（读取CSV并监视进度）
def read_csv_p():
    t_check_progress.start()
    t_read_csv.start()

#定义‘创建信号复选框’的命令
def create_check_button():
    global signal_choose
    signal_name_list = [i['signal_name'] for i in kargs_list]
    signal_choose = Checkbar(base, text = '请选择信号',picks = signal_name_list)
    signal_choose.grid(sticky=W)

#定义输出到excel命令
def decode_to_excel_():
    #1.获取并显示EXCEL文件的路径
    # global excel_path,Text_excel_path,base
    global decode_data
    decode_signal_list = []
    e = Excel_browser(os.getcwd()+'\\'+'excel')
    base.wait_window(e.top)
    excel_path =e.excel_path_
    Text_excel_path = scrolledtext.ScrolledText(base, bd=2, width=30, height=5)
    Text_excel_path.grid()
    # Text_excel_path.delete('1.0', 'end')
    Text_excel_path.insert(END,excel_path+'\n' )
    #2.开始解码
    signal_kargs_choosed_list = [i[0] for i in list(zip(kargs_list,list(signal_choose.state()))) if i[1]==1]
    for i,j in zip(signal_kargs_choosed_list,range(len(signal_kargs_choosed_list))):
        i['data']=data
        v = locals()
        v['signal_series'+str(j+1)]=decode(**i)
        decode_signal_list.append(v['signal_series'+str(j+1)])
    decode_data = pd.concat(decode_signal_list,axis=1)
    #3.存入excel
    decode_data.to_excel(excel_path,encoding='utf-8')


#定义单个信号解码命令
def decode(**kargs):
    decoder = dc.Decoder(**kargs)
    signal_series = decoder.run()
    return signal_series



#浏览文件按钮
browse = Button(base,
                text='浏览',
                command=file_choose,
                activeforeground='white',
                activebackground='green')
#读取csv按钮
read_csv_button = Button(base,
                text='导入',
                command=read_csv_p,
                activeforeground='white',
                activebackground='green')








label0.grid(row=0,column=0,sticky=W)
cfg_file_choose.grid(row=1,column=0,sticky=W)
Kargs.grid(row=0,column=1,sticky=W, columnspan=8, rowspan=2)
get_kargs.grid(row=1,column=10,sticky=W)
label1.grid(row=2,column=0,sticky=W)
Text_csv_path.grid(row=3,column=0,sticky=W)
browse.grid(row=3,column=1,sticky=W)
read_csv_button.grid(row=3,column=2,sticky=W)
mainloop()
