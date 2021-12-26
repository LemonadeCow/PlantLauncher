import os, platform, subprocess, sys
import json
from pathlib import Path
from tkinter import *
import ttk

if __name__ == '__main__':
    main = Tk()
    main.title('Plant Launcher')
    main.geometry('500x500')

    rows = 0

    while rows < 50:
        main.rowconfigure(rows, weight=1)
        main.columnconfigure(rows, weight=1)
        rows += 1

    nb = ttk.Notebook(main)
    nb.grid(row=1, column=0, columnspan=50, rowspan=49, sticky='NESW')
    # place in row 1 column 0, span 50 columns, 49 rows

    page1 = ttk.Frame(nb)
    nb.add(page1, text='tab1')

    main.mainloop()