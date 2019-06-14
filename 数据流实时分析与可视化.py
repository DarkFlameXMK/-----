#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import time
class Data_stream():
    def __init__(self):
        self.data = pd.read_csv('428fqx7 4-28-2019 7-46-12 pm.csv', skiprows=126, usecols=range(21))
        self.stream = []
        self.is_stop = False
    def start_stream(self):
        for i in range(self.data.shape[0]):
            self.stream.append(pd.DataFrame(self.data.iloc[i,:]).T)
            time.sleep(0.0001)
            if self.is_stop==True:
                self.stream = []
                break


# In[ ]:


import numpy as np
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.animation import FuncAnimation
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter import *
get_ipython().run_line_magic('matplotlib', 'auto')

class Oscilloscope():
    '''
    可以将数据进行波形动态可视化的示波器
    xlim：包含两个元素的元祖，第一个是示波器x轴的显示宽度，第二个是x轴的移动步长
    ylim：包含两个元素的元祖，第一个是y轴上边界，第二个是y轴下边界
    color：字符串，用于设置曲线颜色
    frame：窗口中的frame控件，示波器的图像就输出在这个frame上
    '''
    def __init__(self,xlim=(70,0.03),y_lim=(-1.2,1.2),color='blue',frame=None):
        #x,y是每一帧所实际用到的数据集
        self.x = []
        self.y = []
        #xs,ys是总的数据集
        self.xs = []
        self.ys = []
        #实例化一张图片
        self.fig = Figure(figsize=(7,6),facecolor="white")
        #接收frame控件
        self.frame = frame
        #将图片输出到frame
        self.canvs = FigureCanvasTkAgg(self.fig, self.frame)
        self.canvs.get_tk_widget().pack()
        #向图片添加子图
        self.ax1 = self.fig.add_subplot(111)
        #导入示波器的坐标轴配置参数
        self.xlim_count = xlim[0]
        self.xlim_step = xlim[1]
        self.y_lim_bottom = y_lim[0]
        self.y_lim_top = y_lim[1]
        #接收颜色参数
        self.color = color
        #初始化一个数据为空的plot动作，后面会通过update方法输入数据
        self.p1, = self.ax1.plot(self.x, self.y, linestyle="-", color = self.color)
        #停止标识
        self.is_stop = False

    #输入总数据集（默认输入一个0到5的sin函数）
    def input_list(self,xs_list=np.arange(0, 5, 0.03),ys_list=np.sin(np.arange(0, 5, 0.03))):
        self.xs = xs_list
        self.ys = ys_list
        print('list input')

    #定义一个数据更新器，更新示波器每一帧所用到的数据
    def update(self,x,y):
        self.x.append(x)
        self.y.append(y)
        if len(self.x) > self.xlim_count:
            self.x.pop(0)
            self.ax1.set_xlim(min(self.x), max(self.x) + self.xlim_step)
        else:
            self.ax1.set_xlim(0, self.xlim_count*self.xlim_step)
        if len(self.y) > self.xlim_count:
            self.y.pop(0)
        self.ax1.set_ylim(self.y_lim_bottom, self.y_lim_top)
        self.p1.set_data(self.x, self.y)

        if self.xs and self.x[-1] == self.xs[-1]:
            
            self.x = []
            self.y = []
        self.canvs.draw()
        plt.pause(0.01)

    #定义示波器运行方法
    def run(self):
        '''
        运行示波器
        speed表示更新速度
        '''
#         #利用matplotlib中的FuncAnimation方法更新图像
#         ani = FuncAnimation(fig=self.fig, func=self.update, frames=len(self.xs), interval=1000/speed)
        for i in range(len(self.xs)):
            self.update(self.xs[i],self.ys[i])
            
#             self.frame.update_idletasks()
#             self.frame.update()
            
            if self.is_stop==True:
                break
        
        #更新frame控件显示的内容
        



# In[3]:


stream = Data_stream()


# In[4]:


import decoder as dc
import matplotlib.pyplot as plt
import threading
root = Tk()
root.title("实时数据示波器")
frame1 = LabelFrame(height = 600,width = 700,bg='white',text = '引擎转速',font = ('黑体',30))
frame1.pack(side='left', expand='yes', fill='both')
a = Oscilloscope(frame=frame1,xlim=(70,100),y_lim=(2500,3000))

a.is_stop = False
stream.is_stop = False
def stream_show():
    global data
    while stream.stream:
        time.sleep(0.001)
        data = stream.stream.pop()
        decoder = dc.Decoder(data = data,signal_name='引擎转速',id_col_name='PT',id_value='C9',form='Motorola',start=16,width=16)
        try:
            engspd = decoder.run()
            if engspd.values:
#                 print(engspd.index[0],engspd.values[0])
                a.update(engspd.index[0],engspd.values[0])
            else:
                pass
        except:
            pass
t0 = threading.Thread(target = stream.start_stream,name = '0')
t1 = threading.Thread(target = stream_show,name = '1')
t0.start()
time.sleep(0.1)
t1.start()
def stop_t(event):
    a.is_stop = True
    stream.is_stop = True
root.bind('<Destroy>', stop_t)
root.mainloop()   

