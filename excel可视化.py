import pandas as pd
import os
from Oscilloscope import Oscilloscope
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

#建立根窗口
base = Tk()
base.geometry('1400x800')
base.title('Excel数据可视化')

#显示excel文件路径的文本组件
text1 = StringVar()
text1.set('请选择excel文件')
label1 = Label(base,textvariable=text1)
Text_excel_path = Text(base, bd=2,width=30,height = 2)
excel_path = ''

#定义excel文件选择命令
def file_choose():
    global excel_path,Text_excel_path,base
    d = File_browser(os.getcwd()+'\\'+'excel')
    base.wait_window(d.top)
    excel_path =d.path
    Text_excel_path.delete('1.0', 'end')
    Text_excel_path.insert(END,excel_path )
    # mainloop()

#定义读取excel文件命令
excel_data = None
def read_excel():
    global excel_data
    if excel_path:
        try:
            # with open(excel_path) as excel_file:
            excel_data = pd.read_excel(excel_path,encoding='utf-8')
            # text1.set(excel_path)
            create_check_button()
        except:
            print(excel_path)
            text1.set('不是标准格式的excel文件，请重新选择或更改配置')
    else:
        text1.set('请选择excel文件')

def check_progress():
    text1.set('正在读取。。。')
    while True:
        if type(excel_data) != type(None):
            # print(len(excel_data))
            text1.set('读取完成，共%d条数据'%len(excel_data))
            break
        sleep(0.5)
    # 创建开始可视化按钮
    B_n = Button(base, text='可视化', command=visual_data).grid()


#信号复选框
def create_check_button():
    global signal_choose,signal_name_list
    signal_name_list = list(excel_data.columns)
    signal_choose = Checkbar(base, text = '请选择信号',picks = signal_name_list)
    signal_choose.grid(sticky=W)

#将高耗时操作线程化，防止界面卡死
# 创建进程
t_read_excel = threading.Thread(target=read_excel)
t_check_progress = threading.Thread(target=check_progress)

# 设置守护
t_read_excel.setDaemon(True)
t_check_progress.setDaemon(True)

#定义‘读取excel按钮’的按键命令（读取excel并监视进度）
def read_excel_p():
    t_check_progress.start()
    t_read_excel.start()

#浏览文件按钮
browse = Button(base,
                text='浏览',
                command=file_choose,
                activeforeground='white',
                activebackground='green')

#读取excel按钮
read_excel_button = Button(base,
                text='导入',
                command=read_excel_p,
                activeforeground='white',
                activebackground='green')

label1.grid(row=2,column=0,sticky=W)
Text_excel_path.grid(row=3,column=0,sticky=W)
browse.grid(row=3,column=1,sticky=W)
read_excel_button.grid(row=3,column=2,sticky=W)
v = locals()
# 定义可视化命令
def visual_data():
    # 获取可视化名单
    signal_choosed_list = [i[0] for i in list(zip(signal_name_list, list(signal_choose.state()))) if i[1] == 1]
    # 判断是否已经开始画图的参数
    global begin
    begin = 0
    if begin == 0:
        begin = 1
        # 实例化示波器
        for i,j in zip(signal_choosed_list,range(len(signal_choosed_list))):

            v['frame'+str(j+1)] = LabelFrame(height=600, width=700, bg='white', text=i, font=('黑体', 30))
            v['frame' + str(j + 1)].grid(row=4,column=j)
            series = excel_data[i].dropna()
            long = len(series)
            jump = long//2000
            if jump == 0:
                jump = 1
            series = pd.DataFrame(series).iloc[range(0,long,jump),0]
            short = len(series)
            v['o'+str(j+1)]  = Oscilloscope(xlim=(short//5, (series.index.max()-series.index.min())/short), y_lim=(series.min(), series.max()), color='red', frame=v['frame'+str(j+1)])
            # 导入数据
            v['o'+str(j+1)].input_list(xs_list=list(series.index), ys_list=list(series.values))
            # 定义线程
            v['t'+ str(j+1)]= threading.Thread(target=v['o'+str(j+1)].run)
            # 开始线程
            v['t'+ str(j+1)].start()
    else:
        pass



mainloop()