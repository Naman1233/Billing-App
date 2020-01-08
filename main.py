from tkinter import Frame, SUNKEN, Entry, Label, LEFT, END, Tk, Button, mainloop, FLAT, Scrollbar, BOTH, RIGHT, Listbox, Y, Canvas, VERTICAL
from functools import partial
import pdfkit
import json
from os import system
from datetime import datetime
from PIL import Image, ImageTk
import fitz
from jinja2 import Environment, FileSystemLoader
INDUSTRY_LOGO = r"IndustryLogo.ico"


class DateEntry(Frame):
    def __init__(self, master, frame_look={}, **look):
        args = dict(relief=SUNKEN, border=1)
        args.update(frame_look)
        Frame.__init__(self, master, **args)

        args = {'relief': FLAT}
        args.update(look)
        today = datetime.today()
        self.entry_1 = Entry(self, width=2, **args)
        self.label_1 = Label(self, text='/', **args)
        self.entry_2 = Entry(self, width=2, **args)
        self.label_2 = Label(self, text='/', **args)
        self.entry_3 = Entry(self, width=4, **args)
        self.entry_1.insert(END, today.day)
        self.entry_2.insert(END, today.month)
        self.entry_3.insert(END, today.year)

        self.entry_1.pack(side=LEFT)
        self.label_1.pack(side=LEFT)
        self.entry_2.pack(side=LEFT)
        self.label_2.pack(side=LEFT)
        self.entry_3.pack(side=LEFT)

        self.entries = [self.entry_1, self.entry_2, self.entry_3]

        self.entry_1.bind('<KeyRelease>', lambda e: self._check(0, 2))
        self.entry_2.bind('<KeyRelease>', lambda e: self._check(1, 2))
        self.entry_3.bind('<KeyRelease>', lambda e: self._check(2, 4))

    def _backspace(self, entry):
        cont = entry.get()
        entry.delete(0, END)
        entry.insert(0, cont[:-1])

    def _check(self, index, size):
        entry = self.entries[index]
        next_index = index + 1
        next_entry = self.entries[next_index] if next_index < len(self.entries) else None
        data = entry.get()

        if len(data) > size or not data.isdigit():
            self._backspace(entry)
        if len(data) >= size and next_entry:
            next_entry.focus()

    def get(self):
        return [e.get() for e in self.entries]


Bill = []
total = 0
columns=["Name", "Price", "Qty", "Amount"]
BillFrame = None
window = None
TAX_NAME = "CGST + SGST"
TAX = 2.56 # in %
Details = "Hi, aaaaaaaaaaaskfljwe;lk\nakldfjklaef\a;kldflka"


def AddEntry(Name, Price, Qty, window):
    global Bill, total
    try:
        [Name.get(), float(Price.get()), int(Qty.get())]
    except:
        return
    amount = float(Price.get())*int(Qty.get())
    Bill.append([Name.get(), float(Price.get()), int(Qty.get()), amount])
    total += amount
    show_bill(window)


def removeEntry(i):
    global Bill, window, total
    total -= Bill[i][3]
    Bill.pop(i)
    show_bill(window)  


def clear_bill():
    global Bill, window, total
    Bill = []
    total = 0
    show_bill(window)


def show_bill(window):
    global BillFrame, Bill, total
    BillFrame.grid_forget()
    BillFrame.destroy()
    BillFrame = Frame(window)
    w_label = 15
    start = 5
    if len(Bill) != 0:
        canvas = Canvas(BillFrame, height=200, width=610)
        scrollbar = Scrollbar(BillFrame, orient="vertical", command=canvas.yview)
        scrollable_frame = Frame(canvas)
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(yscrollcommand=scrollbar.set,
                scrollregion=canvas.bbox("all")
            )
        )
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.grid(row=2, column=0, sticky='news', columnspan=7, pady=(0, 5))
        scrollbar.grid(row=2, column=7, sticky='ns')
        canvas.configure(yscrollcommand=scrollbar.set)
        Label(BillFrame, text="Bill:", width=w_label, height=3).grid(row=0, column=1)
        Label(BillFrame, text="Index", width=w_label//2, borderwidth=2, relief="ridge").grid(row=1, column=0, padx=(0, 0))
        Label(BillFrame, text="Name", width=w_label, borderwidth=2, relief="ridge").grid(row=1, column=1, padx=(0, 0))
        Label(BillFrame, text="Price", width=w_label, borderwidth=2, relief="ridge").grid(row=1, column=2, padx=(0, 0))
        Label(BillFrame, text="Qty", width=w_label, borderwidth=2, relief="ridge").grid(row=1, column=3, padx=(0, 0))
        Label(BillFrame, text="Amount", width=w_label, borderwidth=2, relief="ridge").grid(row=1, column=4, padx=(0, 0))
        for i in range(len(Bill) - 1, -1, -1):
            Label(scrollable_frame, text=str(i+1), width=w_label//2, borderwidth=2, relief="ridge").grid(row=start + 1 + len(Bill) - i, column=0, padx=(2, 0), pady=(2, 2))
            Label(scrollable_frame, text=Bill[i][0], width=w_label, borderwidth=2, relief="ridge", wraplength=100).grid(row=start + 1 + len(Bill) - i, column=1, padx=(8, 0), pady=(2, 2))
            Label(scrollable_frame, text=str(Bill[i][1]), width=w_label, borderwidth=2, relief="ridge", anchor='e').grid(row=start + 1 + len(Bill) - i, column=2, padx=(9, 0), pady=(2, 2))
            Label(scrollable_frame, text=str(Bill[i][2]), width=w_label, borderwidth=2, relief="ridge", anchor='e').grid(row=start + 1 + len(Bill) - i, column=3, padx=(8, 0), pady=(2, 2))
            Label(scrollable_frame, text="{0:.2f}".format(Bill[i][3]), width=w_label, borderwidth=2, relief="ridge", anchor="e").grid(row=start + 1 + len(Bill) - i, column=4, padx=(10, 0), pady=(2, 2))
            Button(scrollable_frame, text="Remove: " + str(i+1), command=partial(removeEntry, i), width=w_label//2+2).grid(row=start + 1 + len(Bill) - i, column=5, padx=(0, 0), pady=(0, 1))
        Label(BillFrame, text="Gross total:", width=w_label, anchor="e", borderwidth=2, relief="ridge").grid(row=len(Bill) + start + 3, column=3)
        Label(BillFrame, text="{0:.2f}".format(total), width=w_label, borderwidth=2, relief="ridge", anchor="e").grid(row=len(Bill) + start + 3, column=4)
        Label(BillFrame, text=TAX_NAME + ":", width=w_label, anchor="e", borderwidth=2, relief="ridge").grid(row=len(Bill) + start + 4, column=3)
        Label(BillFrame, text="{0:.2f}".format(round(total*TAX/100, 2)), width=w_label, borderwidth=2, relief="ridge", anchor="e").grid(row=len(Bill) + start + 4, column=4)
        Label(BillFrame, text="(" + str(TAX) + "%)", width=w_label//2, anchor="w", borderwidth=2, relief="ridge").grid(row=len(Bill) + start + 4, column=5)
        Label(BillFrame, text="Net total:", width=w_label, anchor="e", borderwidth=2, relief="ridge").grid(row=len(Bill) + start + 5, column=3)
        Label(BillFrame, text="{0:.2f}".format(round((total*(100+TAX))/100, 2)), width=w_label, borderwidth=2, relief="ridge", anchor="e").grid(row=len(Bill) + start + 5, column=4)
    BillFrame.grid(row=start, column=0, sticky='news', columnspan=15)



def convert_to_pdf(Name, Date):
    try:
        Name.get()
        Date.get()
    except:
        return
    Customer_name = Name.get()
    Date_day, Date_month, Date_year = Date.get()
    data = None
    with open("details.json", 'r') as f:
        data = json.load(f)
    
    global Bill, total
    Gross_total = total
    taxable_amount = round((Gross_total*TAX)/100, 2)
    Net_total = round((Gross_total*(100+TAX))/100, 2)
    Bill_html = "<table align=center>"
    Bill_html += "<tr><td colspan=3 height=100>"+ data["Details"] +"</td><td colspan=2></td></tr>"
    Bill_html += "<tr><td>Name:</td><td colspan=2>"+ str(Customer_name) +"</td><td>Date:</td><td>" + str(Date_day) + "/" +str(Date_month) +"/"+str(Date_year) + "</td></tr>"
    Bill_html += "<tr><td class=\"index\">Index</td><td class=\"name\">Name</td><td class=\"price\">Price</td><td class=\"qty\">Qty</td><td class=\"amount\">Amount</td></tr>"
    for i in range(len(Bill)):
        entry = Bill[i]
        Bill_html += "<tr><td class=\"index\">"+ str(i+1) +"</td><td class=\"name\">"+ entry[0] +"</td><td align=\"right\" class=\"price\">"+ "{0:.2f}".format(entry[1]) +"</td><td align=\"right\" class=\"qty\">"+ str(entry[2]) +"</td><td align=\"right\" class=\"amount\">" +"{0:.2f}".format(entry[3]) +"</td></tr>"
    file_name = "Bill"+data["Counts"]+".pdf"
    env = Environment(loader=FileSystemLoader('.'))
    Bill_html += "<tr class=\"gross-total\"><td colspan=4>Gross Total</td><td align=\"right\">" + "{0:.2f}".format(Gross_total) +"</td></tr>"
    Bill_html += "<tr class=\"taxable-amount\"><td colspan=4>Taxable Amount\n( "+data["TAX_NAME"] +": " + data["TAX"] +"%)</td><td align=\"right\">" + "{0:.2f}".format(taxable_amount) +"</td></tr>"
    Bill_html += "<tr class=\"net-total\"><td colspan=4>Net Total</td><td align=\"right\">"+ "{0:.2f}".format(Net_total) +"</td></tr>"
    Bill_html += "</table>"
    template = env.get_template("Bill_Preview.html")
    template_vars = {
                        "Bill": Bill_html, 
                    }
    html_out = template.render(template_vars)
    pdfkit.from_string(html_out, file_name)
    data["Counts"] = str(int(data["Counts"]) + 1)
    with open("details.json", "w") as f:
        json.dump(data, f)
    doc = fitz.open(file_name)
    rect = fitz.Rect(358, 15, 428, 118) 
    for page in doc:
        page._cleanContents()
        page.insertImage(rect, filename="IndustryLogo.jpg", overlay=True)
    doc.saveIncr()
    system(file_name)


def setting_window():
    setting_window = Tk()
    setting_window.geometry("490x80")
    setting_window.title("Settings")
    setting_window.resizable(0, 0)
    setting_window.iconbitmap(INDUSTRY_LOGO)
    global TAX, TAX_NAME, Details
    Label(setting_window, text="Details: ", width=10, anchor='e').grid(row=1, column=1)
    Label(setting_window, text="TAX_NAME: ", width=10, anchor='e').grid(row=3, column=1)
    Label(setting_window, text="TAX: ", width=10, anchor='e').grid(row=5, column=1)
    Label(setting_window, text=Details, width=50, anchor="w").grid(row=1, column=2)
    Label(setting_window, text=TAX_NAME, width=50, anchor="w").grid(row=3, column=2)
    Label(setting_window, text=str(TAX), width=50, anchor="w").grid(row=5, column=2)
    Button(setting_window, text="Change", width=7, command=lambda: change_details("Details", setting_window)).grid(row=1, column=3)
    Button(setting_window, text="Change", width=7, command=lambda: change_details("TAX_NAME", setting_window)).grid(row=3, column=3)
    Button(setting_window, text="Change", width=7, command=lambda: change_details("TAX", setting_window)).grid(row=5, column=3)
    mainloop() 


def change_details(string, setting_window):
    setting_window.destroy()
    change_window = Tk()
    change_window.geometry("450x50")
    change_window.resizable(0, 0)
    change_window.iconbitmap(INDUSTRY_LOGO)
    change_window.title("Change "  + string)
    Label(change_window, text="New "+ string + ": ", width=20).grid(row=0, column=0, columnspan=2)
    change = Entry(change_window, width=50)
    change.grid(row=0, column=2)
    Button(change_window, text="Change", command=lambda: change_final(string, change, change_window)).grid(row=1, column=1)
    mainloop()


def change_final(string, change, change_window):
    temp = None
    if string == "Details" or string == "TAX_NAME":
        try:
            temp = change.get()
        except:
            return
    elif string == "TAX":
        try:
            temp = float(change.get())
        except:
            return
    data = None
    with open("details.json", 'r') as f:
        data = json.load(f)
    data[string] = temp
    with open("details.json", 'w') as f:
        json.dump(data, f)
    global window
    if string == "Details":
        global Details, Details_label
        Details = temp
        Details_label.config(text=Details)
    elif string == "TAX":
        global TAX
        TAX = temp
    else:
        global TAX_NAME
        TAX_NAME = temp
    change_window.destroy()
    global Bill
    show_bill(window)



with open("details.json", 'r') as f:
    data = json.load(f)
    TAX_NAME = data["TAX_NAME"]
    TAX = float(data["TAX"])
    Details = data["Details"]
window = Tk()
window.geometry("820x800")
window.title("Billing App")
window.resizable(0, 1)
window.iconbitmap(INDUSTRY_LOGO)
load = Image.open(INDUSTRY_LOGO)
render = ImageTk.PhotoImage(load)
Label(window, image=render, height=100, width=200).grid(row=0, column=1)
BillFrame = Frame(window, height=200, width=803)
Name = Entry(window, width=40)
Label(window, text="Name: ", width=6, anchor='e').grid(row=3, column=0)
Label(window, text=" Price: ", width=5, anchor='e').grid(row=3, column=2)
Label(window, text=" Qty: ", width=5, anchor='e').grid(row=3, column=4)
Name.grid(row=3, column=1)
Price = Entry(window, width=24)
Price.grid(row=3, column=3)
Qty = Entry(window, width=20)
Qty.grid(row=3, column=5)
Details_label = Label(window, text=Details, height=5, wraplength=350, anchor="w")
Details_label.grid(row=0, column=2, columnspan=5)
Label(window, text="Customer Name: ", anchor='e', height=3).grid(row=1, column=0, columnspan=3)
Label(window, text="Product Details: ", anchor='w').grid(row=2, column=0, columnspan=3)
Customer_Name = Entry(window, width=24)
Customer_Name.insert(END, "Anonymous")
Customer_Name.grid(row=1, column=3)
Label(window, text="Date: ", width=5, anchor='e').grid(row=1, column=4)
date = DateEntry(window)
date.grid(row=1, column=5)
Button(window, text='Add', width=22, command=lambda :AddEntry(Name, Price, Qty, window)).grid(row=3, column=7)
Button(window, text="show bill", command=lambda: convert_to_pdf(Customer_Name, date)).grid(row=4, column=1)
Button(window, text="settings", command=setting_window).grid(row=4, column=2)
Button(window, text="Clear", command=clear_bill).grid(row=4, column=3)
mainloop()
