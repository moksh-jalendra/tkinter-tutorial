from tkinter import *

root = Tk()
root.geometry("300x200")

w = Label(root, text ='menu in tkinter ', font = "50") 
w.pack()

menubutton = Menubutton(root, text = "Menu")   
  
menubutton.menu = Menu(menubutton)  
menubutton["menu"]= menubutton.menu  

var1 = IntVar()
var2 = IntVar()
var3 = IntVar()

menubutton.menu.add_checkbutton(label = "option 1",
                                variable = var1)  
menubutton.menu.add_checkbutton(label = "option 2",
                                variable = var2)
menubutton.menu.add_checkbutton(label = "option 3 ",
                                variable = var3)
  
menubutton.pack()  
root.mainloop()