# import tkinter 

# root = tkinter.Tk()
# root.geometry('900x400')


# #  frame    


# f = tkinter.Frame(root, bg ='red' , bd=2)
# f.pack(side='top' , fill='x', padx=10 ,pady= 10 )

# b = tkinter.Button( f , text='click heare').pack(pady=5)




# root.mainloop()





###nhide and show difreaint pages





# import tkinter as tk

# def show_page(page_to_show, page_to_hide):
#     # Hide the current frame
#     page_to_hide.pack_forget()
#     # Show the new frame
#     page_to_show.pack(fill="both", expand=True)

# root = tk.Tk()
# root.title("Page Switcher 2026")
# root.geometry("400x300")

# # --- Page 1 ---
# page1 = tk.Frame(root, bg="lightgreen")
# tk.Label(page1, text="Welcome to Page 1", font=("Arial", 18), bg="lightgreen").pack(pady=20)
# # Button to switch to Page 2
# tk.Button(page1, text="Go to Page 2", command=lambda: show_page(page2, page1)).pack()

# # --- Page 2 ---
# page2 = tk.Frame(root, bg="lightcoral")
# tk.Label(page2, text="Welcome to Page 2", font=("Arial", 18), bg="lightcoral").pack(pady=20)
# # Button to switch back to Page 1
# tk.Button(page2, text="Back to Page 1", command=lambda: show_page(page1, page2)).pack()

# # Start with Page 1 visible
# page1.pack(fill="both", expand=True)

# root.mainloop()




# import tkinter as tk

# # 1. Create the main application window
# root = tk.Tk()
# root.title("Tkinter Frame Example 2026")
# root.geometry("400x300")

# # 2. Create a 'Top Frame' for a header or input area
# # Relief adds a visual border style (sunken, raised, etc.)
# top_frame = tk.Frame(root, bg="lightblue", bd=2, relief="sunken")
# top_frame.pack(side="top", fill="x", padx=10, pady=10)

# # Add widgets to the top_frame
# tk.Label(top_frame, text="This is inside the TOP frame", bg="lightblue").pack(pady=5)
# tk.Entry(top_frame).pack(pady=5)

# # 3. Create a 'Bottom Frame' for buttons or control area
# bottom_frame = tk.Frame(root, bg="lightgrey", bd=2, relief="groove")
# bottom_frame.pack(side="bottom", fill="both", expand=True, padx=10, pady=10)

# # Use a separate grid layout inside the bottom_frame
# # Frames allow you to use different layout managers independently
# tk.Button(bottom_frame, text="Action 1").grid(row=0, column=0, padx=20, pady=20)
# tk.Button(bottom_frame, text="Action 2").grid(row=0, column=1, padx=20, pady=20)

# # 4. Start the application loop
# root.mainloop()




###################### paint   app
# from tkinter import *


# root = Tk()

# # Create Title
# root.title(  "Paint App ")

# # specify size
# root.geometry("500x350")

# # define function when  
# # mouse double click is enabled
# def paint( event ):
   
#     # Co-ordinates.
#     x1, y1, x2, y2 = ( event.x - 3 ),( event.y - 3 ), ( event.x + 3 ),( event.y + 3 ) 
    
#     # Colour
#     Colour = "#000fff000" 
    
#     # specify type of display
#     w.create_arc(x1 ,y1,x2,y2 )


# # create canvas widget.
# w = Canvas(root, width = 400, height = 250) 

# # call function when double 
# # click is enabled.
# w.bind( "<B1-Motion>", paint )

# # create label.
# l = Label( root, text = "Double Click and Drag to draw." )
# l.pack()
# w.pack()

# mainloop()