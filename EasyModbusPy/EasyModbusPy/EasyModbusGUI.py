import tkinter
from tkinter import *
from tkinter.ttk import *
import ModbusClient
from pickletools import string1

class EasyModbusGUI(tkinter.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        master.title("EasyModbusPython Client")
        self.pack()
        self.createWidgets()
        
        
    def createWidgets(self):
        self.pack(fill=tkinter.BOTH, expand=True)
                
        self.columnconfigure(1, weight=1)
        self.columnconfigure(3, pad=7)
        self.rowconfigure(3, weight=1)
        self.rowconfigure(5, pad=7)
        
        
        #Button Read Coils
        self.readCoils = tkinter.Button(self, text="Read Coils (FC1)", width=25, command=self.ReadCoils)
        self.readCoils.grid(row = 3, column = 0, padx = 20, pady = 6, columnspan=2)
        
        #Button Read Discrete Inputs
        self.readDiscreteInputs = tkinter.Button(self, text="Read Discrete Inputs (FC2)", width=25, command=self.ReadDiscreteInputs)
        self.readDiscreteInputs.grid(row = 4, column = 0, padx = 20, pady = 6, columnspan=2)
        
        #Button Read Holding Registers
        self.readHoldingRegisters = tkinter.Button(self, text="Read Holding Registers (FC3)", width=25, command=self.ReadHoldingRegisters)
        self.readHoldingRegisters.grid(row = 5, column = 0, padx = 20, pady = 6, columnspan=2)
 
        #Button Read Input Registers
        self.readInputRegisters = tkinter.Button(self, text="Read Input Registers (FC4)", width=25, command=self.ReadInputRegisters)
        self.readInputRegisters.grid(row = 6, column = 0, padx = 20, pady = 6, columnspan=2)       
        
        #label for IP Addresses
        label = tkinter.Label(self, text="IP-Address:")
        label.grid(row = 1, column = 0, sticky=tkinter.W)
        
        #Entry for IPAddress
        self.ipAddressEntry = tkinter.Entry(self, width=15)
        self.ipAddressEntry.insert(tkinter.END, "127.0.0.1")
        self.ipAddressEntry.grid(row = 2, column = 0, sticky=tkinter.W)
        
        #label for Display Port
        labelPort = tkinter.Label(self, text="Port:")
        labelPort.grid(row = 1, column = 1, sticky=tkinter.W)
        
        #Text Field for Port
        self.portEntry = tkinter.Entry(self, width=10)
        self.portEntry.insert(tkinter.END, "502")
        self.portEntry.grid(row = 2, column = 1, sticky=tkinter.W)

        #label for Display Starting Address
        labelStartingAddress = tkinter.Label(self, text="Starting Address:")
        labelStartingAddress.grid(row = 3, column = 3, sticky=tkinter.W)
        
        #Text Field for starting Address
        self.startingAddress = tkinter.Entry(self, width=10)
        self.startingAddress.insert(tkinter.END, "1")
        self.startingAddress.grid(row = 3, column = 4, sticky=tkinter.W)

        #label for Display Number of values
        labelStartingAddress = tkinter.Label(self, text="Number of values:")
        labelStartingAddress.grid(row = 4, column = 3, sticky=tkinter.W)
        
        #Text Field for number of Values
        self.quantity = tkinter.Entry(self, width=10)
        self.quantity.insert(tkinter.END, "1")
        self.quantity.grid(row = 4, column = 4, sticky=tkinter.W)

        #label for Response from server
        labelResponse = tkinter.Label(self, text="Response from Server")
        labelResponse.grid(row = 1, column = 5, sticky=tkinter.W, padx = 10)        
    
        #Text Field for response from server
        self.response = tkinter.StringVar
        self.responseTextField = tkinter.Text(self,  width=35, height = 10)
        scroll = Scrollbar(self, command=self.responseTextField.yview)
        self.responseTextField.configure(yscrollcommand=scroll.set)
        self.responseTextField.insert(tkinter.END, "")
        self.responseTextField.grid(row = 1, column = 5, rowspan=8, padx = 10) 
        scroll.grid(row = 2, column = 6, rowspan=5, sticky=N+S+E)
 
           
    def onReverse(self):
        self.name.set(self.name.get()[::-1])
      
    def ReadCoils(self):
        modbusClient = ModbusClient.ModbusClient(self.ipAddressEntry.get() ,int(self.portEntry.get()))
        if (not modbusClient.isConnected()):
            modbusClient.Connect()
        coils = modbusClient.ReadCoils(int(self.startingAddress.get()) - 1, int(self.quantity.get())) 
        self.responseTextField.delete('1.0', END)
        for coil in coils:
            if (coil == FALSE):
                response = "FALSE"
            else:
                response = "TRUE"
            
            self.responseTextField.insert(tkinter.END, response  + "\n")
        
        modbusClient.close() 
        
    def ReadDiscreteInputs(self):
        modbusClient = ModbusClient.ModbusClient(self.ipAddressEntry.get() ,int(self.portEntry.get()))
        if (not modbusClient.isConnected()):
            modbusClient.Connect()
        discrInputs = modbusClient.ReadDiscreteInputs(int(self.startingAddress.get()) - 1, int(self.quantity.get())) 
        self.responseTextField.delete('1.0', END)
        for inp in discrInputs:
            if (inp == FALSE):
                response = "FALSE"
            else:
                response = "TRUE"
            
            self.responseTextField.insert(tkinter.END, response  + "\n")
        
        modbusClient.close() 
   
    def ReadHoldingRegisters(self):
        modbusClient = ModbusClient.ModbusClient(self.ipAddressEntry.get() ,int(self.portEntry.get()))
        if (not modbusClient.isConnected()):
            modbusClient.Connect()
        holdingRegisters = modbusClient.ReadHoldingRegisters(int(self.startingAddress.get()) - 1, int(self.quantity.get())) 
        self.responseTextField.delete('1.0', END)
        for register in holdingRegisters:
 
            
            self.responseTextField.insert(tkinter.END, str(register)  + "\n")
        
        modbusClient.close()   
        
    def ReadInputRegisters(self):
        modbusClient = ModbusClient.ModbusClient(self.ipAddressEntry.get() ,int(self.portEntry.get()))
        if (not modbusClient.isConnected()):
            modbusClient.Connect()
        inputRegisters = modbusClient.ReadInputRegisters(int(self.startingAddress.get()) - 1, int(self.quantity.get())) 
        self.responseTextField.delete('1.0', END)
        for register in inputRegisters:
            
            self.responseTextField.insert(tkinter.END, str(register)  + "\n")
        
        modbusClient.close()   
      
      
root = tkinter.Tk()
app = EasyModbusGUI(root)
app.mainloop()