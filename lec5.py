import tkinter 
root = tkinter.Tk()
a= tkinter.Variable()
a.set('')
def fun():
    b=text.get("1.0","end")
    a.set(b)
butn=tkinter.Button(root,textvariable=a ,command=fun ).pack()

text =tkinter.Text(root, height=10 , width=40 )
text.pack()
root.mainloop()