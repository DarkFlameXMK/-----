from tkinter import *
class Checkbar(LabelFrame):
    def __init__(self,parent=None,text = None,picks=[], side=LEFT, anchor=W):
        LabelFrame.__init__(self ,parent,text = text)
        self.vars = []
        for pick in picks:
            var = IntVar()
            chk = Checkbutton(self, text=pick, variable=var)
            chk.pack(side=side, anchor=anchor, expand=YES)
            self.vars.append(var)
    def state(self):
        return map((lambda var: var.get()), self.vars)