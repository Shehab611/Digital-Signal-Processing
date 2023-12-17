import gui_file as gui
from plot_signals import PracticalTaskOne, SignalsMethods
import tkinter as tk
from tkinter import filedialog
from scipy.signal import firwin, freqz
from test_output import Compare_Signals_fir

#gui.MainGui()


def open_file_dialog():
    root = tk.Tk()
    root.withdraw()  # Hide the main window

    file_path = filedialog.askopenfilename()
    return file_path


# # print(-0.0009139992863517461 * -54.0)
# # 0.04935596146299429
#t = PracticalTaskOne.calculated_filtered_signal(open_file_dialog(),open_file_dialog())
# t = PracticalTaskOne.calculate_filter(open_file_dialog())
t = PracticalTaskOne.resampling(open_file_dialog(), open_file_dialog(), 0, 3)
# print(len(t[0]))
# print(len(t[1]))
print(len(t[0]),len(t[1]))
Compare_Signals_fir(open_file_dialog(), t[0], t[1])
