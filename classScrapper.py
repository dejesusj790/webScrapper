from tkinter.font import BOLD
from numpy import place
import requests
import lxml.html as lh
import pandas as pd
import tkinter as tk
import customtkinter as ctk
import webbrowser as wb

# ============ Vital Links ============
URL = "https://banner.newpaltz.edu/pls/PROD/bwckzschd.p_dsp_results?p_term=202209&p_subj=BIO&p_crses=&p_title=&p_credits=&p_days=&p_time_span=&p_levl=&p_instr_pidm=&p_attr=&p_instructional_method=" #This URL needs to be changed based on semester
bannerURL= "https://my.newpaltz.edu"

# ============ Scrapping Web ============
page = requests.get(URL) #This will get the HTML code of the page
doc = lh.fromstring(page.content)
tr_elements = doc.xpath("//tr") #tr is new table row, so this will break up table into it's rows
# print([len(T) for T in tr_elements[:12]]) #This will check if the rows have the same width (1 in the beginning is the header "Undergraduate Courses")
col = []
i = 0
for t in tr_elements[1]: #This will get the headers (CRN, Course, etc.)
    i += 1
    name = t.text_content()
    col.append((name,[]))
for j in range(2,len(tr_elements)):
    T = tr_elements[j]    #T is going to the row
    if(len(T) != 12): #This will stop if all the col (Crn, Course, etc.) aren't present, there should be 12 cols in a single row
        continue
    i = 0 #Index of the col, starting at 0 aka the beginning
    for t in T.iterchildren():  #Looping through the element in the row
        data = t.text_content()
        col[i][1].append(data)
        i += 1
Dict = {title:column for (title,column) in col} #Setting up the header and data for pd table (aka dataframe (df))
df = pd.DataFrame(Dict)   #Creating dataframe with the headers and data
# print(df.head())    #Sample of the first 5 rows of the dataframe

# ============ Functions ============
def section_count(course):
    count = 0
    for x in range(0,len(df)):
        if df.loc[x,"CRN"] == course or df.loc[x,"Title"] == course or df.loc[x,"Course"] == course:
            count += 1
    # print(course," = ",count) #Checking if the count matches
    return count

def avail_seats(course): #Will tell you if immediately if a class has a spot open or not
    # course_loc = 0
    course_count = section_count(course)
    count = 0
    # ============ Result Window ============
    resultWindow = ctk.CTkToplevel(master= mainWindow, height= "380", width= "475")
    resultWindow.title("Result")
    frame = ctk.CTkFrame(master = resultWindow, height= 250, width= 400)
    frame.pack(expand= True)
    frame.place(relx= .5, rely= .10, anchor = tk.N)
    label = ctk.CTkLabel(master = frame, wraplength= 375, justify= "left")
    label.pack(expand= True)
    label.place(relx= .5, rely= .09, anchor = tk.N)

    # ============ Result Buttons ============
    open = ctk.CTkButton(master = resultWindow, text = "Open Site", width = 100, command = lambda: wb.open(bannerURL))
    close = ctk.CTkButton(master = resultWindow, text = "Close", width = 100, command = lambda: resultWindow.destroy())
    closeBool = False

    # ============ Setting up Message ============
    finalMessage = ""
    for x in range(0,len(df)):
        if df.loc[x,"CRN"] == course or df.loc[x,"Title"] == course or df.loc[x,"Course"] == course:
            course_loc = x
            seats = df.loc[course_loc,"Avail"]
            if seats != "F":
                message = df.loc[course_loc,"Course"]+" "+df.loc[course_loc,"Title"]+" (CRN: "+df.loc[x,"CRN"]+") has "+seats+" open slot(s)!"+"\n"
                finalMessage += message
                open.place(relx = .15, rely = .85, anchor = tk.W)
                close.configure(fg_color= "#3d3d3d") #This is the gray color
                close.place(relx = .85, rely = .85, anchor = tk.E)
                closeBool = True
                pass
            else:
                message = df.loc[course_loc,"Course"]+" "+df.loc[course_loc,"Title"]+" (CRN: "+df.loc[x,"CRN"]+") is full, there are no open slots."+"\n"
                finalMessage += message
                if(closeBool != True):
                    close.place(relx = .5, rely = .9, anchor = tk.CENTER)
                pass
            count += 1
            if(course_count == count):
                label.configure(text= ''.join(finalMessage))
                return
    finalMessage = "Could not find that class, please review input or URL"
    label.configure(text= finalMessage)
    close.place(relx = .5, rely = .9, anchor = tk.CENTER)       

# ============ Setting up Main Window ============
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("green")

mainWindow = ctk.CTk() # make a tk window
mainWindow.geometry("500x300")
mainWindow.title("Class Finder")
# ============ Entry ============
entry = ctk.CTkEntry(master = mainWindow, placeholder_text = "Class Name")
entry.place(relx = .5, rely = .30, anchor = tk.N)

# ============ Main Window Label ============
Instructions = "Please enter either: CRN, Title, or Course Abbrv"
InstructionLabel = ctk.CTkLabel(master = mainWindow, text = Instructions, text_font = BOLD).place(relx = .5, rely = .15, anchor= tk.N)

# ============ Search Button ============
search = ctk.CTkButton(master = mainWindow, text = "Search", command = lambda: avail_seats(entry.get()), hover = True).place(relx = .5, rely = .55, anchor = tk.CENTER)

# ============ Start ============
mainWindow.mainloop()