# #  lec 2 

# from tkinter import * 

# root = Tk()
# root.geometry('500x300')


# va1 = IntVar()

# va2 = IntVar()

# #   Checkbutto  

# """ but = Checkbutton(root,text='yes' , variable=va1)
# but.pack()
 
# but = Chec kbutton(root,text='no' , variable= va2)
# but.pack()"""

#  # radio button 
 
 
# """

# but = Radiobutton(root , text='you are under 18 ' , variable= va1,value= 1).pack()
# but = Radiobutton(root,text='you are above 18' ,variable= va1 , value=0 ).pack()
 
# """


# # scrollbar 

# # sbar =  Scrollbar(root)
# # sbar.pack(side=RIGHT , fill=Y)
 



# ##  list value 

# l = Listbox(root)
# l.insert(1,'shinobu') 
# l.insert(2,'kokshibu')
# l.insert(3,'inosuke')
# l.insert(4,"zenetsu")
# l.insert(5,'shinobu') 
# l.insert(6,'kokshibu')
# l.insert(7,'inosuke')
# l.insert(8,"zenetsu")
# l.insert(9,'shinobu') 
# l.insert(10,'kokshibu')
# l.insert(11,'inosuke')
# l.insert(12,"zenetsu")
# l.insert(13,'shinobu') 
# l.insert(14,'kokshibu')
# l.insert(15,'inosuke')
# l.insert(16,"zenetsu")

# # sbar.config(command= l .yview)


# l.pack()


# # 




# root.mainloop()



### showing image in lable 

import tkinter

root = tkinter.Tk()
root.geometry('300x400')

img = tkinter.PhotoImage(file='sample.png')


labl = tkinter.Button(root , image= img )
labl.image = img
labl.pack()
root.mainloop()

