import tkinter




class EasyModbusGUI(tkinter.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.pack()
        self.createWidgets()
        
    def createWidgets(self):
        #self.nameEntry = tkinter.Entry(self)
        #self.nameEntry.pack()
        self.name = tkinter.StringVar
        self.name = "bhjk"
        self.nameEntry["textvariable"] = self.name
        self.ok = tkinter.Button(self)
        self.ok["text"] = "Ok"
        self.ok["command"] = self.quit()
        self.ok.pack(side="right")
        self.rev=tkinter.Button(self)
        self.rev["text"] = "Umdrehen"
        self.rev["command"] = self.onReverse
        self.rev.pack(side="right")
        
    def onReverse(self):
        self.name.set(self.name.get()[::-1])
      
root = tkinter.Tk()
app = EasyModbusGUI(root)
app.mainloop()
        
        