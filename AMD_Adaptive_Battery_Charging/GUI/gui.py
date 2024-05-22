from tkinter import *
import tkinter as tk
import sys
import os

home = os.path.join(os.path.expanduser('~'), 'AMD_Adaptive_Battery_Charging')
sys.path.insert(0, os.path.join(home, 'SCRIPTS'))
from pipe import *

class NotificationApp(tk.Tk):
    def __init__(self, _min, current, _max, interval, end):
        super().__init__()
        self.wm_title("ACRLF User Input")
        self.geometry("600x300")

        self.text = tk.Label(self, text="ACRLF USER INPUT\n\nChoose the time (in minutes) you want the ACRLF Agent to charge your laptop:")
        self.text.place(x=80,y=20)
        
        self.slider = tk.Scale(self, from_=_min, to=_max, tickinterval=interval, length=300, orient="horizontal")
        self.slider.set(current)
        self.slider.place(x=140, y=80)
        self.slider.bind("<ButtonRelease-1>", self.get_value)

        self.after(end * 1000 * 60, self.destroy)
        self.mainloop() # self.wait_window()
    
    def get_value(self, event):
        self.value = self.slider.get()

        if self.value is not None:
            server(1, self.value)
            self.destroy()    


if __name__ == '__main__':
    app = NotificationApp(60, 120, 180, 15, 1)
    
    

    