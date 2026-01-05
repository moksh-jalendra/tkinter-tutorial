import tkinter

root=tkinter.Tk()

root.geometry('300x200')

"""a= tkinter.TkVersion
print(a)

#  now we start with gui 

root = tkinter.Tk(screenName='first gui' )
root.geometry('600x400')

# lable 

l = tkinter.Label(root,text='hi ')
l.place(x = 50, y=30)

# button 

b = tkinter.Button(root,text=' click me ')
b.place(x=50 , y=50)


# entry 
a = tkinter.Variable()

a.set('hi')
e = tkinter.Entry(root, textvariable=a)
e.pack()"""

def hello():
    name=b.get()
    a.set('hi welcome devloper  '+ name )
    

a = tkinter.Variable()
a.set(' enter your name ')

b = tkinter.Variable()
b.set('')

lab = tkinter.Label(root, textvariable=a )
lab.place(x=80, y=10)

ent = tkinter.Entry(root ,textvariable=b)
ent.place(x=80,y=50)

but = tkinter.Button(text='click heare' , command= hello)
but.place(x=80 , y= 120)


root.mainloop()




