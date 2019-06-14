import pandas as pd
import numpy as np


class Decoder():
    '''解码器类
    data：总数据集
    signal_name：想要定义的信号的名字（例如车速，引擎转速等）
    id_col_name：原数据中信号id所在的列的列标签，默认为PT
    id_value：信号的id值，例如‘1BC’,‘1A1’等
    form：信号的格式，Intel或者Motorola，默认Motorola
    start：信号的起始位
    width：信号的宽度
    V_position：有效信号的位置，如果没有有效信号则默认输入None。
    '''

    # 接收参数
    def __init__(self, data=None, signal_name=None, id_col_name='PT', id_value=None, form='Motorola', start=None, width=None, V_position=None,zoom=1):
        self.data = data
        self.name = signal_name
        self.id_col_name = id_col_name
        self.id = id_value
        self.form = form
        self.stb = start
        self.wid = width
        self.V_position = V_position
        self.vpB = None
        self.zoom = zoom
    # 先定义一个16进制转二进制函数
    def x_to_b(self, num):
        num_d = int(num, 16)
        num_b = format(num_d, 'b')
        return num_b.rjust(8, '0')

    # 筛选行，分为两步：id筛选和信号有效筛选（V_position筛选）
    def select_rows(self):
        # id筛选
        self.data = self.data[self.data[self.id_col_name] == self.id]

        # 接下来进行V_position(信号是否有效)筛选：
        # 判断该信号是否存在有效信号
        if self.V_position != None:
            # 有效信号Byte位置
            self.vpB = self.V_position // 8 + 1
            # 有效信号bit位置
            vpb = 7 - self.V_position % 8
            # 对有效信号所在的Byte列进行二进制转码
            self.data.loc[:,'B%d' % self.vpB]=self.data['B%d' % self.vpB].map(self.x_to_b)
#             self.data.loc[:,'B%d' % self.vpB].map(self.x_to_b)
            # 筛选出有效信号
            self.data = self.data[self.data['B%d' % self.vpB].str[vpb] == '1']

    # 定义单列二进制转码函数
    def decode_col(self, Byte_num):
        if Byte_num == self.vpB:
            pass
        else:
             self.data.loc[:,'B%d' % Byte_num]=self.data['B%d' % Byte_num].map(self.x_to_b)


    # 定义总体二进制转码函数
    def decode_total(self):
        # 判断哪几个Byte需要解码
        # count:剩余的需要确定位置的信号bit位数
        count = self.wid
        # Bp_list：所有需要解码的Byte的序号的列表
        self.Bp_list = []
        # 起始位所在的ByteBp1
        Bp1 = self.stb // 8 + 1
        self.Bp_list.append(Bp1)
        # 剩余信号bit位数
        count -= 8 - self.stb % 8
        # 将剩余信号所在的Byte的序号加入Bp_list中
        while True:
            if count > 0 and self.form == 'Motorola':
                count -= 8
                self.Bp_list.append(Bp1 - 1)
            if count > 0 and self.form == 'Intel':
                count -= 8
                self.Bp_list.append(Bp1 + 1)
            if count <= 0:
                break
        # 对信号所在的所有Byte列进行解码
        for i in self.Bp_list:
            self.decode_col(i)

    # 信号字段拼接
    def form_str(self):
        # 定义一个值全是空字符串的列来容纳拼接的信号字段
#         self.data['signal_str'] = ''
        self.data.loc[:,'signal_str'] = ''
        # count:剩余的需要确定位置的信号bit位数
        count = self.wid

        # 定义一个非负数函数
        def not_negative(num):
            if num < 0:
                return 0
            else:
                return num

        # 信号在每个Byte中的起始位
        start = not_negative(8 - self.stb % 8 - self.wid)
        # 信号在每个Byte中的终结位
        end = 8 - self.stb % 8
        # 在每个Byte中进行字符串的提取与拼接
        for i in self.Bp_list:
#             self.data['signal_str'] = self.data['B%d' % i].str[start:end] + self.data['signal_str']
            self.data['signal_str'] = self.data['B%d' % i].str[start:end] + self.data['signal_str']
            count -= end - start
            end = 8
            start = not_negative(8 - count)

    # 转为10进制并进行提取
    def to_value(self):
        self.signal_value = self.data['signal_str'].map(lambda x: int(x, 2))

        self.signal_value *= self.zoom
        self.signal_value.name = self.name

    # run方法
    def run(self):
        self.select_rows()
        self.decode_total()
        self.form_str()
        self.to_value()
        return self.signal_value
