import matplotlib
matplotlib.use('TkAgg')
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import os.path
from tkinter import messagebox
from backend import Backend
import sqlite3


class DialogWindow(tk.Toplevel):
    '''
    this class creates the radiobuttons for the user to select their choice
    '''

    def __init__(self, master, backend):
        self.backend = backend
        tk.Toplevel.__init__(self, master)

        canvas = tk.Canvas(self, height=700, width=1000, background='#2C5881')
        canvas.pack()

        self.grab_set()
        self.focus_set()
        self.transient(master)

        self.frame = tk.Frame(self, background='#81F0F7', border=5)
        self.frame.place(relx=0.3, rely=0.1, relwidth=0.4, relheight=0.8)

        self.selection = tk.IntVar(master)
        self.selection.set(0)
        self.sorted_countries = backend

        amount = 0
        x = 0.05
        for i in range(6):
            amount += 3
            self.radioButton = tk.Radiobutton(self.frame, text="Data For Top "+str(amount)+" Countries", variable=self.selection, value=amount,
                                              background='#81F0F7',
                                              font=("Palatino Linotype", 15, 'bold'), indicatoron=False)
            self.radioButton.place(relx=0.2, rely=x, relwidth=0.6, relheight=.08)
            x += 0.09
            self.radioButton10 = tk.Radiobutton(self.frame, text='Data For Top 30 Countries', variable=self.selection, value=30,
                                                background='#81F0F7',
                                                font=("Palatino Linotype", 15, 'bold'), indicatoron=False)
            self.radioButton10.place(relx=0.2, rely=x, relwidth=0.6, relheight=.06)

        self.plotButton = tk.Button(self.frame, text='Okay',
                                    command=self.set_num,
                                    font=("Palatino Linotype", 15, 'bold'))
        self.plotButton.pack(side='bottom', fill='both')

    def set_num(self):
        self.num = self.selection.get()
        self.destroy()

    def get_num(self):
        return self.num




class PlotWindow(tk.Toplevel):
    '''
    this class plots the price trend or bar chart depending on the user choice
    '''

    def __init__(self, master, fct, *args):
        self.master = master
        super().__init__(master)
        fig = plt.figure(figsize=(8, 7))
        fct(*args)
        canvas = FigureCanvasTkAgg(fig, master=self)
        plt.tight_layout()
        canvas.get_tk_widget().grid()
        canvas.draw()


class MainWindow(tk.Tk):
    '''
    this class create main window from tk class and catches errors with the opening of the files
    '''

    def __init__(self, infilenames):
        self.backend = Backend()
        super().__init__()
        self.canvas = tk.Canvas(self, height=700, width=1200)
        self.canvas.pack()

        frame = tk.Frame(self.canvas, background='#2C5881', border=5)
        frame.place(relx=0, rely=0, relwidth=1, relheight=1)

        button = tk.Button(frame, text='Country: \n Emission Amount (1990, 2005, 2017)\n2017 Emission Percentage \n% Change in Emissions Between 1990 and 2017', background='#CBD7D5', border=4, command=self.displayDialog)
        button.place(relx=0, rely=0.6, relwidth=0.52, relheight=0.2)

        button.config(font=("Palatino Linotype", 20, 'bold'))

        button2 = tk.Button(frame, text='Top 10 Highest Co2 Emitting Countries \n In 2017 (Pie Chart)', background='#CBD7D5', border=4,
                            command=self.display_pie_chart)
        button2.place(relx=0.5, rely=0.6, relwidth=0.5, relheight=0.2)
        button2.config(font=("Palatino Linotype", 20, 'bold'))

        label = tk.Label(frame, text='2017 Co2 Emissions By Countries', background='white')
        label.place(relx=0.1, rely=0.1, relwidth=0.8, relheight=0.2)
        label.config(font=("Palatino Linotype", 40, 'bold'))

        for file in infilenames:
            if os.path.exists(file) == False or os.path.isfile(file) == False:
                tk.messagebox.showwarning("Error", "Cannot open this file\n(%s)" % file)

    def display_pie_chart(self):
        conn = sqlite3.connect("emissions.db")
        PlotWindow(self, self.backend.pie_chart_top_10_emissions)

    def displayDialog(self):
        dWin = DialogWindow(self, self.backend.sorted_countries)
        self.wait_window(dWin)
        choice = dWin.get_num()
        PlotWindow(self, self.backend.display_all_data, choice)




infileNames = ["emissions.db"]

mainWin = MainWindow(infileNames)
mainWin.mainloop()
