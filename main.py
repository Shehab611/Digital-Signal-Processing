import gui_file as gui
from plot_signals import PracticalTaskOne, SignalsMethods, PracticalTaskTwo, TaskSeven
import tkinter as tk
from tkinter import filedialog
from test_output import Compare_Signals_fir


#gui.MainGui()


def open_file_dialog():
    root = tk.Tk()
    root.withdraw()  # Hide the main window

    file_path = filedialog.askopenfilename()
    return file_path

x = PracticalTaskTwo()
dcta = PracticalTaskTwo.calculate_average_files(x.folder_one_path, 10, 50, 150, 300)
# dctb = PracticalTaskTwo.calculate_average_files(x.folder_two_path, 10, 50, 150, 300)
# dcttest = PracticalTaskTwo.calculate_average_files(x.folder_test_path, 10, 50, 150, 300)
# correlation1 = TaskSeven.calculate_cross_correlation(dcta, dcttest)
# correlation2 = TaskSeven.calculate_cross_correlation(dctb, dcttest)
# maxx = correlation1[0]
# maxx1 = correlation2[0]
#
# if maxx > maxx1:
#     print('Test Signal 1 belongs to class B ', 'Test Signal 2 belongs to class A ')
# else:
#     print('Test Signal 2 belongs to class B ', 'Test Signal 1 belongs to class A')
# # print(-0.0009139992863517461 * -54.0)
# # 0.04935596146299429
# _,_,_,x,y=SignalsMethods.read_signal_from_file(open_file_dialog())
# t = PracticalTaskOne.apply_filter_on_signal(open_file_dialog(),x,y)
# t = PracticalTaskOne.calculate_filter(open_file_dialog())
# _,_,_,x,y=SignalsMethods.read_signal_from_file(open_file_dialog())
# t = PracticalTaskOne.resampling(x,y, 2, 3)
# print(len(t[0]))
# print(len(t[1]))
# print(len(t[0]),len(t[1]))
# Compare_Signals_fir(open_file_dialog(), t[0], t[1])
