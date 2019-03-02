#!/usr/bin/env python

import sys

if sys.version_info[0] < 3:                 #The Module "Tkinter" is named "tkinter" in Python 3.
    from Tkinter import *
    import tkMessageBox as messagebox       #We import tkMessageBos as messagebox, because thats the name in Python 3

else:
    from tkinter import *
    from builtins import int
    from future.moves import tkinter
    import tkinter.messagebox as messagebox
from easymodbus.modbusClient import *

class EasyModbusGUI(Frame):
    def __init__(self, master=None):
        Frame.__init__(self)
        master.title("EasyModbusPython Client")
        self.pack()
        self.createWidgets()
        
        
    def createWidgets(self):
        self.pack(fill=BOTH, expand=True)
                
        self.columnconfigure(1, weight=1)
        self.columnconfigure(3, pad=7)
        self.rowconfigure(3, weight=1)
        self.rowconfigure(5, pad=7)
        
        #label Read operations
        readOperationsLabel = Label(self, text="Read Operations", font = 15)
        readOperationsLabel.config(font=15)
        readOperationsLabel.grid(row = 0, column = 0)
        
        #Button Read Coils
        self.readCoils = Button(self, text="Read Coils (FC1)", width=25, command=self.__ReadCoils)
        self.readCoils.grid(row = 4, column = 0, padx = 20, pady = 6, columnspan=2)
        
        #Button Read Discrete Inputs
        self.readDiscreteInputs = Button(self, text="Read Discrete Inputs (FC2)", width=25, command=self.__ReadDiscreteInputs)
        self.readDiscreteInputs.grid(row = 5, column = 0, padx = 20, pady = 6, columnspan=2)
        
        #Button Read Holding Registers
        self.readHoldingRegisters = Button(self, text="Read Holding Registers (FC3)", width=25, command=self.__ReadHoldingRegisters)
        self.readHoldingRegisters.grid(row = 6, column = 0, padx = 20, pady = 6, columnspan=2)
 
        #Button Read Input Registers
        self.readInputRegisters = Button(self, text="Read Input Registers (FC4)", width=25, command=self.__ReadInputRegisters)
        self.readInputRegisters.grid(row = 7, column = 0, padx = 20, pady = 6, columnspan=2)       
        
        #label for IP Addresses
        label = Label(self, text="IP-Address:")
        label.grid(row = 2, column = 0, sticky=W)
        
        #Entry for IPAddress
        self.ipAddressEntry = Entry(self, width=15)
        self.ipAddressEntry.insert(END, "127.0.0.1")
        self.ipAddressEntry.grid(row = 3, column = 0, sticky=W)
        
        #label for Display Port
        labelPort = Label(self, text="Port:")
        labelPort.grid(row = 2, column = 1, sticky=W)
        
        #Text Field for Port
        self.portEntry = Entry(self, width=10)
        self.portEntry.insert(END, "502")
        self.portEntry.grid(row = 3, column = 1, sticky=W)

        #label for Display Starting Address
        labelStartingAddress = Label(self, text="Starting Address:")
        labelStartingAddress.grid(row = 4, column = 3, sticky=W)
        
        #Text Field for starting Address
        self.startingAddress = Entry(self, width=10)
        self.startingAddress.insert(END, "1")
        self.startingAddress.grid(row = 4, column = 4, sticky=W)

        #label for Display Number of values
        labelStartingAddress = Label(self, text="Number of values:")
        labelStartingAddress.grid(row = 5, column = 3, sticky=W)
        
        #Text Field for number of Values
        self.quantity = Entry(self, width=10)
        self.quantity.insert(END, "1")
        self.quantity.grid(row = 5, column = 4, sticky=W)

        #label for Response from server
        labelResponse = Label(self, text="Response from Server")
        labelResponse.grid(row = 2, column = 5, sticky=W, padx = 10)        
    
        #Text Field for response from server
        self.response = StringVar
        self.responseTextField = Text(self,  width=35, height = 10)
        scroll = Scrollbar(self, command=self.responseTextField.yview)
        self.responseTextField.configure(yscrollcommand=scroll.set)
        self.responseTextField.insert(END, "")
        self.responseTextField.grid(row = 2, column = 5, rowspan=8, padx = 10) 
        scroll.grid(row = 3, column = 6, rowspan=5, sticky=N+S+E)
        
        #Empty row between Read and Write operations
        self.rowconfigure(15, minsize=20)
        
        #label Write operations
        readOperationsLabel = Label(self, text="Write Operations", font = 15)
        readOperationsLabel.config(font=15)
        readOperationsLabel.grid(row = 20, column = 0)
        
        #Label select datatye to write
        datatype = Label(self, text="Select datatype to write")
        datatype.grid(row = 25, column = 0,  sticky=W)       

        #Combobox to selct the type of variable to write 
        lst1 = ['Coils (bool)','Holding Registers (word)']
        self.variableDatatype = StringVar(self)
        self.variableDatatype.set('Coils (bool)')
        self.variableDatatype.trace('w',self.datatypeChanged)
        dropdown = OptionMenu(self,self.variableDatatype,*lst1)
        dropdown.grid(row = 25, column = 1,columnspan = 3,  sticky=W)

        #Label select value to write
        datatype = Label(self, text="Select value to write")
        datatype.grid(row = 26, column = 0, sticky=W)   #
        
        #Combobox to selct true or false in case "coils" has been selcted
        lst1 = ['FALSE', 'TRUE']
        self.variableData = StringVar(self)
        self.variableData.set('FALSE')
        self.dropdownData = OptionMenu(self,self.variableData,*lst1)
        self.dropdownData.grid(row = 26, column = 1, sticky=W)
        
        #TextField for the Register Values to write
        self.registerValueToWrite = Entry(self, width=10)
        self.registerValueToWrite.insert(END, "1")
        
        #label for Display startingAddress
        labelStartingAddress = Label(self, text="Starting Address:")
        labelStartingAddress.grid(row = 27, column = 0, sticky=W)
        
        #Text Field for starting Address
        self.startingAddressWrite = Entry(self, width=10)
        self.startingAddressWrite.insert(END, "1")
        self.startingAddressWrite.grid(row = 27, column = 1, sticky=W)
        
        #label for Request to Server
        labelResponse = Label(self, text="Request to Server")
        labelResponse.grid(row = 24, column = 5, sticky=W, padx = 10)     
        
        #Text Field containing data to write to server
        self.request = StringVar
        self.requestTextField = Text(self,  width=35, height = 10)
        scroll = Scrollbar(self, command=self.requestTextField.yview)
        self.requestTextField.configure(yscrollcommand=scroll.set)
        self.requestTextField.insert(END, "")
        self.requestTextField.grid(row = 25, column = 5, rowspan=8, padx = 10) 
        scroll.grid(row = 25, column = 6, rowspan=8, sticky=N+S+E)
        
        #Button Add Entry to request list
        self.addEntryToRequestList = Button(self, text="Add Value to \n request list", width=15, command=self.addValueToRequestList)
        self.addEntryToRequestList.grid(row = 26, column = 3,columnspan = 2)
        
        #Button Delete Entry from request list
        self.addEntryToRequestList = Button(self, text="Delete Value from \n request list", width=15, command=self.deleteValueToRequestList)
        self.addEntryToRequestList.grid(row = 28, column = 3,columnspan = 2)
                
        
        #Button Write values to server
        writeValuesToServerButton = Button(self, text="Write Requested Values to Server", width=25, command=self.__writeValuesToServer)
        writeValuesToServerButton.grid(row = 30, column = 0, padx = 20, pady = 6, columnspan=2)
        
    def addValueToRequestList(self):
        if (self.variableDatatype.get()  == 'Coils (bool)'):
            self.requestTextField.insert(END, self.variableData.get())  
            self.requestTextField.insert(END, "\n")
        else:
            self.requestTextField.insert(END, self.registerValueToWrite.get())  
            self.requestTextField.insert(END, "\n")          
        
        
    def datatypeChanged(self,a,b,c):
        self.requestTextField.delete('1.0', END)
        if (self.variableDatatype.get()  == 'Coils (bool)'):
            self.registerValueToWrite.grid_remove()
            self.dropdownData.grid(row = 26, column = 1, sticky=W)
        else:
            self.registerValueToWrite.grid(row = 26, column = 1, sticky=W)
            self.dropdownData.grid_remove()
           
    def onReverse(self):
        self.name.set(self.name.get()[::-1])
      
    def __ReadCoils(self):
        try:
            modbusClient = ModbusClient(self.ipAddressEntry.get(), int(self.portEntry.get()))
            if (not modbusClient.is_connected()):
                modbusClient.connect()
            coils = modbusClient.read_coils(int(self.startingAddress.get()) - 1, int(self.quantity.get()))
            self.responseTextField.delete('1.0', END)
            for coil in coils:
                if (coil == FALSE):
                    response = "FALSE"
                else:
                    response = "TRUE"
                
                self.responseTextField.insert(END, response  + "\n")
        except Exception as e:
            messagebox.showerror('Exception Reading coils from Server', str(e))
        finally:
            modbusClient.close()
        
    def __ReadDiscreteInputs(self):
        try:
            modbusClient = ModbusClient(self.ipAddressEntry.get(), int(self.portEntry.get()))
            if (not modbusClient.is_connected()):
                modbusClient.connect()
            discrInputs = modbusClient.read_discreteinputs(int(self.startingAddress.get()) - 1, int(self.quantity.get()))
            self.responseTextField.delete('1.0', END)
            for inp in discrInputs:
                if (inp == FALSE):
                    response = "FALSE"
                else:
                    response = "TRUE"
                
                self.responseTextField.insert(END, response  + "\n")
        except Exception as e:
            messagebox.showerror('Exception Reading discrete inputs from Server', str(e))
        finally:
            modbusClient.close() 
   
    def __ReadHoldingRegisters(self):
        try:
            modbusClient = ModbusClient(self.ipAddressEntry.get(), int(self.portEntry.get()))
            if (not modbusClient.is_connected()):
                modbusClient.connect()
            holdingRegisters = modbusClient.read_holdingregisters(int(self.startingAddress.get()) - 1, int(self.quantity.get()))
            self.responseTextField.delete('1.0', END)
            for register in holdingRegisters:
     
                
                self.responseTextField.insert(END, str(register)  + "\n")
        except Exception as e:
            messagebox.showerror('Exception Reading holding registers from Server', str(e))
        
        finally:
            modbusClient.close()   
        
    def __ReadInputRegisters(self):
        try:
            modbusClient = ModbusClient(self.ipAddressEntry.get(), int(self.portEntry.get()))
            if (not modbusClient.is_connected()):
                modbusClient.connect()
            inputRegisters = modbusClient.read_inputregisters(int(self.startingAddress.get()) - 1, int(self.quantity.get()))
            self.responseTextField.delete('1.0', END)
            for register in inputRegisters:
                
                self.responseTextField.insert(END, str(register)  + "\n")
            
            modbusClient.close()   
        except Exception as e:
            messagebox.showerror('Exception Reading input Registers from Server', str(e))
      
    def __writeValuesToServer(self):
        try:
            modbusClient = ModbusClient(self.ipAddressEntry.get(), int(self.portEntry.get()))
            if (not modbusClient.is_connected()):
                modbusClient.connect()
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
                    modbusClient.write_multiple_coils(int(self.startingAddressWrite.get()) - 1, valueToWrite)
                else:              
                    textFieltValues = str(self.requestTextField.get('1.0', END)[:-1])
                    if "TRUE" in textFieltValues:               #String comparison contains some ""Null" symbol
                        dataToSend = 1
                    else:
                        dataToSend = 0
                    modbusClient.write_single_coil(int(self.startingAddressWrite.get()) - 1, dataToSend)
            else:
                if (numberOfLines > 1):
                    valueToWrite = list()
                    for i in range(1, numberOfLines+1):
                        textFieltValues = int(self.requestTextField.get(str(i)+".0", str(i+1)+".0")[:-1])
                        valueToWrite.append(textFieltValues)
                    modbusClient.write_multiple_registers(int(self.startingAddressWrite.get()) - 1, valueToWrite)
                else:              
                    textFieltValues = int(self.requestTextField.get('1.0', END)[:-1])
                    modbusClient.write_single_register(int(self.startingAddressWrite.get()) - 1, textFieltValues)
        except Exception as e:
            messagebox.showerror('Exception writing values to Server', str(e))
        modbusClient.close()
        
    def deleteValueToRequestList(self):
        numberOfLines = (int(self.requestTextField.index('end').split('.')[0]) - 2)
        cursorPos = int(self.requestTextField.index(INSERT)[0])                     #Find the current Cursorposition e.g. 1.0 -> First line
        if (cursorPos-1 != numberOfLines):            #don't delete the last line, because the last line contains only a "newline"
            self.requestTextField.delete(str(cursorPos)+".0",str(cursorPos+1)+".0")     #Delete the whole line using e.g. delete("1.0","2.0) deletes the first line
      
root = Tk()
app = EasyModbusGUI(root)
app.mainloop()