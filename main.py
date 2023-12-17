import gui_file as gui
from plot_signals import PracticalTaskOne
import tkinter as tk
from tkinter import filedialog
from scipy.signal import firwin, freqz
from test_output import Compare_Signals_fir


# gui.MainGui()
def open_file_dialog():
    root = tk.Tk()
    root.withdraw()  # Hide the main window

    file_path = filedialog.askopenfilename()
    return file_path

print(-0.0009139992863517461 * -54.0)
#0.04935596146299429
t = PracticalTaskOne.calculated_filtered_signal(open_file_dialog(),open_file_dialog())
# t = PracticalTaskOne.up_sampling(open_file_dialog(),open_file_dialog(),3)
print(t[0])
print(t[1])
Compare_Signals_fir(open_file_dialog(), t[0], t[1])
