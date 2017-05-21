import tkinter
from tkinter import *
from tkinter.ttk import *
import ModbusClient
from pickletools import string1
from turtledemo.__main__ import font_sizes
from builtins import int
from future.moves import tkinter
from test.test_tcl import TkinterTest

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
        
        #label Read operations
        readOperationsLabel = tkinter.Label(self, text="Read Operations", font = 15)
        readOperationsLabel.config(font=15)
        readOperationsLabel.grid(row = 0, column = 0)
        
        #Button Read Coils
        self.readCoils = tkinter.Button(self, text="Read Coils (FC1)", width=25, command=self.ReadCoils)
        self.readCoils.grid(row = 4, column = 0, padx = 20, pady = 6, columnspan=2)
        
        #Button Read Discrete Inputs
        self.readDiscreteInputs = tkinter.Button(self, text="Read Discrete Inputs (FC2)", width=25, command=self.ReadDiscreteInputs)
        self.readDiscreteInputs.grid(row = 5, column = 0, padx = 20, pady = 6, columnspan=2)
        
        #Button Read Holding Registers
        self.readHoldingRegisters = tkinter.Button(self, text="Read Holding Registers (FC3)", width=25, command=self.ReadHoldingRegisters)
        self.readHoldingRegisters.grid(row = 6, column = 0, padx = 20, pady = 6, columnspan=2)
 
        #Button Read Input Registers
        self.readInputRegisters = tkinter.Button(self, text="Read Input Registers (FC4)", width=25, command=self.ReadInputRegisters)
        self.readInputRegisters.grid(row = 7, column = 0, padx = 20, pady = 6, columnspan=2)       
        
        #label for IP Addresses
        label = tkinter.Label(self, text="IP-Address:")
        label.grid(row = 2, column = 0, sticky=tkinter.W)
        
        #Entry for IPAddress
        self.ipAddressEntry = tkinter.Entry(self, width=15)
        self.ipAddressEntry.insert(tkinter.END, "127.0.0.1")
        self.ipAddressEntry.grid(row = 3, column = 0, sticky=tkinter.W)
        
        #label for Display Port
        labelPort = tkinter.Label(self, text="Port:")
        labelPort.grid(row = 2, column = 1, sticky=tkinter.W)
        
        #Text Field for Port
        self.portEntry = tkinter.Entry(self, width=10)
        self.portEntry.insert(tkinter.END, "502")
        self.portEntry.grid(row = 3, column = 1, sticky=tkinter.W)

        #label for Display Starting Address
        labelStartingAddress = tkinter.Label(self, text="Starting Address:")
        labelStartingAddress.grid(row = 4, column = 3, sticky=tkinter.W)
        
        #Text Field for starting Address
        self.startingAddress = tkinter.Entry(self, width=10)
        self.startingAddress.insert(tkinter.END, "1")
        self.startingAddress.grid(row = 4, column = 4, sticky=tkinter.W)

        #label for Display Number of values
        labelStartingAddress = tkinter.Label(self, text="Number of values:")
        labelStartingAddress.grid(row = 5, column = 3, sticky=tkinter.W)
        
        #Text Field for number of Values
        self.quantity = tkinter.Entry(self, width=10)
        self.quantity.insert(tkinter.END, "1")
        self.quantity.grid(row = 5, column = 4, sticky=tkinter.W)

        #label for Response from server
        labelResponse = tkinter.Label(self, text="Response from Server")
        labelResponse.grid(row = 2, column = 5, sticky=tkinter.W, padx = 10)        
    
        #Text Field for response from server
        self.response = tkinter.StringVar
        self.responseTextField = tkinter.Text(self,  width=35, height = 10)
        scroll = Scrollbar(self, command=self.responseTextField.yview)
        self.responseTextField.configure(yscrollcommand=scroll.set)
        self.responseTextField.insert(tkinter.END, "")
        self.responseTextField.grid(row = 2, column = 5, rowspan=8, padx = 10) 
        scroll.grid(row = 3, column = 6, rowspan=5, sticky=N+S+E)
        
        #Empty row between Read and Write operations
        self.rowconfigure(15, minsize=20)
        
        #label Write operations
        readOperationsLabel = tkinter.Label(self, text="Write Operations", font = 15)
        readOperationsLabel.config(font=15)
        readOperationsLabel.grid(row = 20, column = 0)
        
        #Label select datatye to write
        datatype = tkinter.Label(self, text="Select datatype to write")
        datatype.grid(row = 25, column = 0,  sticky=tkinter.W)       

        #Combobox to selct the type of variable to write 
        lst1 = ['Coils (bool)','Holding Registers (bool)']
        self.variableDatatype = StringVar(self)
        self.variableDatatype.set('Coils (bool)')
        self.variableDatatype.trace('w',self.datatypeChanged)
        dropdown = tkinter.OptionMenu(self,self.variableDatatype,*lst1)
        dropdown.grid(row = 25, column = 1,columnspan = 3,  sticky=tkinter.W)

        #Label select value to write
        datatype = tkinter.Label(self, text="Select value to write")
        datatype.grid(row = 26, column = 0, sticky=tkinter.W)   #
        
        #Combobox to selct true or false in case "coils" has been selcted
        lst1 = ['FALSE', 'TRUE']
        self.variableData = StringVar(self)
        self.variableData.set('FALSE')
        self.dropdownData = tkinter.OptionMenu(self,self.variableData,*lst1)
        self.dropdownData.grid(row = 26, column = 1, sticky=tkinter.W)
        
        #TextField for the Register Values to write
        self.registerValueToWrite = tkinter.Entry(self, width=10)
        self.registerValueToWrite.insert(tkinter.END, "1")
        
        #label for Display startingAddress
        labelStartingAddress = tkinter.Label(self, text="Starting Address:")
        labelStartingAddress.grid(row = 27, column = 0, sticky=tkinter.W)
        
        #Text Field for starting Address
        self.startingAddressWrite = tkinter.Entry(self, width=10)
        self.startingAddressWrite.insert(tkinter.END, "1")
        self.startingAddressWrite.grid(row = 27, column = 1, sticky=tkinter.W)
        
        #label for Request to Server
        labelResponse = tkinter.Label(self, text="Request to Server")
        labelResponse.grid(row = 24, column = 5, sticky=tkinter.W, padx = 10)     
        
        #Text Field containing data to write to server
        self.request = tkinter.StringVar
        self.requestTextField = tkinter.Text(self,  width=35, height = 10)
        scroll = Scrollbar(self, command=self.requestTextField.yview)
        self.requestTextField.configure(yscrollcommand=scroll.set)
        self.requestTextField.insert(tkinter.END, "")
        self.requestTextField.grid(row = 25, column = 5, rowspan=8, padx = 10) 
        scroll.grid(row = 25, column = 6, rowspan=8, sticky=N+S+E)
        
        #Button Add Entry to request list
        self.addEntryToRequestList = tkinter.Button(self, text="Add Value to \n request list", width=15, command=self.addValueToRequestList)
        self.addEntryToRequestList.grid(row = 26, column = 3,columnspan = 2)
        
        #Button Delete Entry from request list
        self.addEntryToRequestList = tkinter.Button(self, text="Delete Value from \n request list", width=15, command=self.deleteValueToRequestList)
        self.addEntryToRequestList.grid(row = 28, column = 3,columnspan = 2)
                
        
        #Button Write values to server
        writeValuesToServerButton = tkinter.Button(self, text="Write Requested Values to Server", width=25, command=self.__writeValuesToServer)
        writeValuesToServerButton.grid(row = 30, column = 0, padx = 20, pady = 6, columnspan=2)
        
    def addValueToRequestList(self):
        if (self.variableDatatype.get()  == 'Coils (bool)'):
            self.requestTextField.insert(tkinter.END, self.variableData.get())  
            self.requestTextField.insert(tkinter.END, "\n")
        else:
            self.requestTextField.insert(tkinter.END, self.registerValueToWrite.get())  
            self.requestTextField.insert(tkinter.END, "\n")          
        
        
    def datatypeChanged(self,a,b,c):
        self.requestTextField.delete('1.0', END)
        if (self.variableDatatype.get()  == 'Coils (bool)'):
            self.registerValueToWrite.grid_remove()
            self.dropdownData.grid(row = 26, column = 1, sticky=tkinter.W)
        else:
            self.registerValueToWrite.grid(row = 26, column = 1, sticky=tkinter.W)
            self.dropdownData.grid_remove()
           
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
      
    def __writeValuesToServer(self):
        modbusClient = ModbusClient.ModbusClient(self.ipAddressEntry.get() ,int(self.portEntry.get()))
        if (not modbusClient.isConnected()):
            modbusClient.Connect()
        numberOfLines = (int(self.requestTextField.index('end').split('.')[0]) - 2)
        if (self.variableDatatype.get()  == 'Coils (bool)'):
            if (numberOfLines > 1):
                valueToWrite = list()
                for i in range(1, numberOfLines+1):
                    textFieltValues = str(self.requestTextField.get(str(i)+".0", str(i+1)+".0")[:-1])
                    if "TRUE" in textFieltValues:           #String comparison contains some ""Null" symbol
                        valueToWrite.append(1)
                    else:
                        valueToWrite.append(0)
                modbusClient.WriteMultipleCoils(int(self.startingAddressWrite.get()) - 1, valueToWrite)
            else:              
                textFieltValues = str(self.requestTextField.get('1.0', END)[:-1])
                if "TRUE" in textFieltValues:               #String comparison contains some ""Null" symbol
                    dataToSend = 1
                else:
                    dataToSend = 0
                modbusClient.WriteSingleCoil(int(self.startingAddressWrite.get()) - 1, dataToSend)
        else:
            if (numberOfLines > 1):
                valueToWrite = list()
                for i in range(1, numberOfLines+1):
                    textFieltValues = int(self.requestTextField.get(str(i)+".0", str(i+1)+".0")[:-1])
                    valueToWrite.append(textFieltValues)
                modbusClient.WriteMultipleRegisters(int(self.startingAddressWrite.get()) - 1, valueToWrite)
            else:              
                textFieltValues = int(self.requestTextField.get('1.0', END)[:-1])
                modbusClient.WriteSingleRegister(int(self.startingAddressWrite.get()) - 1, textFieltValues)
        modbusClient.close()
        
    def deleteValueToRequestList(self):
        numberOfLines = (int(self.requestTextField.index('end').split('.')[0]) - 2)
        cursorPos = int(self.requestTextField.index(INSERT)[0])                     #Find the current Cursorposition e.g. 1.0 -> First line
        if (cursorPos-1 != numberOfLines):            #don't delete the last line, because the last line contains only a "newline"
            self.requestTextField.delete(str(cursorPos)+".0",str(cursorPos+1)+".0")     #Delete the whole line using e.g. delete("1.0","2.0) deletes the first line
      
root = tkinter.Tk()
app = EasyModbusGUI(root)
app.mainloop()