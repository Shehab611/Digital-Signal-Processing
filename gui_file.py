import tkinter as tk
from tkinter import filedialog
import matplotlib.pyplot as plt
import plot_signals as signal_plot


class Task1dot1:

    def __init__(self):
        self.signal_one = None
        self.signal_two = None
        self.signal_one_type = None
        self.is_periodic_one = None
        self.num_samples_one = None
        self.indexes_one = None
        self.values_one = None
        self.signal_two_type = None
        self.is_periodic_two = None
        self.num_samples_two = None
        self.indexes_two = None
        self.values_two = None
        self.root = tk.Tk()
        self.root.title('First One')
        self.root.geometry('800x500')
        self.button_frame = tk.Frame(self.root)
        self.button_frame.columnconfigure(0, weight=1)
        self.button_frame.columnconfigure(1, weight=1)
        self.choose1_btn = tk.Button(self.button_frame, text='Choose First Signal', command=self.choose_signal_one)
        self.choose1_btn.grid(row=0, column=0, sticky=tk.W + tk.E, padx=10)
        self.choose2_btn = tk.Button(self.button_frame, text='Choose Second Signal', command=self.choose_signal_two)
        self.choose2_btn.grid(row=0, column=1, sticky=tk.W + tk.E, padx=10)
        self.display_btn = tk.Button(self.button_frame, text='Display Signal', command=self.display_signal)
        self.display_btn.grid(row=1, column=0, sticky=tk.W + tk.E, padx=10, pady=40)
        self.button_frame.pack(fill='x', pady=10)
        self.root.mainloop()

    def choose_signal_one(self):
        self.signal_one = filedialog.askopenfile(filetypes=[("txt", "*.txt")])
        # define the signal
        self.signal_one_type = int(self.signal_one.readline().strip())
        self.is_periodic_one = int(self.signal_one.readline().strip())
        self.num_samples_one = int(self.signal_one.readline().strip())
        samples_one = [list(map(float, line.strip().split())) for line in self.signal_one]
        self.indexes_one = [sample[0] for sample in samples_one]
        self.values_one = [sample[1] for sample in samples_one]

    def choose_signal_two(self):
        self.signal_two = filedialog.askopenfile(filetypes=[("txt", "*.txt")])
        # define the signal
        self.signal_two_type = int(self.signal_two.readline().strip())
        self.is_periodic_two = int(self.signal_two.readline().strip())
        self.num_samples_two = int(self.signal_two.readline().strip())
        samples_two = [list(map(float, line.strip().split())) for line in self.signal_two]
        self.indexes_two = [sample[0] for sample in samples_two]
        self.values_two = [sample[1] for sample in samples_two]

    def display_signal(self):
        # define Signal One

        if self.signal_one_type == 0:
            plt.subplot(4, 1, 1)
            signal_plot.SignalPlot.plot_normal_signal(self.indexes_one, self.values_one, 'Time', 'Amplitude',
                                                      signal_plot.SignalType.Continuous, True)
            plt.subplot(4, 1, 2)
            signal_plot.SignalPlot.plot_normal_signal(self.indexes_one, self.values_one, 'Time', 'Amplitude',
                                                      signal_plot.SignalType.Discrete, True)
        else:
            plt.subplot(4, 1, 1)
            signal_plot.SignalPlot.plot_normal_signal(self.indexes_one, self.values_one, 'Frequency', 'Phase Shift',
                                                      signal_plot.SignalType.Continuous, True)
            plt.subplot(4, 1, 2)
            signal_plot.SignalPlot.plot_normal_signal(self.indexes_one, self.values_one, 'Frequency', 'Phase Shift',
                                                      signal_plot.SignalType.Discrete,
                                                      True)

        if self.signal_two:
            if self.signal_two_type == 0:
                plt.subplot(4, 1, 3)
                signal_plot.SignalPlot.plot_normal_signal(self.indexes_two, self.values_two, 'Time', 'Amplitude',
                                                          signal_plot.SignalType.Continuous, False)
                plt.subplot(4, 1, 4)
                signal_plot.SignalPlot.plot_normal_signal(self.indexes_two, self.values_two, 'Time', 'Amplitude',
                                                          signal_plot.SignalType.Discrete, False)
            else:
                plt.subplot(4, 1, 3)
                signal_plot.SignalPlot.plot_normal_signal(self.indexes_two, self.values_two, 'Frequency', 'Phase Shift',
                                                          signal_plot.SignalType.Continuous, False)
                plt.subplot(4, 1, 4)
                signal_plot.SignalPlot.plot_normal_signal(self.indexes_two, self.values_two, 'Frequency', 'Phase Shift',
                                                          signal_plot.SignalType.Discrete,
                                                          False)

        plt.grid(True)
        plt.tight_layout()
        plt.show()
