import math

import numpy as np

import gui_file as gui
from plot_signals import TaskSeven

gui.MainGui()
indicates = [0,1,2,3,4,5,6,7,8]
signal1 = [2,1,0,0,3]
signal2 = [3,2,1,1,5]
signal_analysis1 = [1,2,3,1,2,6,8,2,4]
signal_analysis2 = [2,6.1,8,2.02,4,1,2.2,3,1.06]
#c = TaskSeven.calculate_time_analysis(signal_analysis1,signal_analysis2,indicates,100)
#c = TaskSeven.calculate_normalized_cross_correlation(signal1,signal2)
c = TaskSeven.get_correlation_of_test()
print(c)
