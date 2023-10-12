import tkinter as tk
from tkinter import filedialog
import matplotlib.pyplot as plt
import plot_signals as signal_plot


class Task1dot1:

    def __init__(self):
        self.signal_one = None
        self.signal_two = None
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

    def choose_signal_two(self):
        self.signal_two = filedialog.askopenfile(filetypes=[("txt", "*.txt")])

    def display_signal(self):
        # define Signal One
        signal_type = int(self.signal_one.readline().strip())
        is_periodic = int(self.signal_one.readline().strip())
        num_samples = int(self.signal_one.readline().strip())
        samples = [list(map(float, line.strip().split())) for line in self.signal_one]
        indexes = [sample[0] for sample in samples]
        values = [sample[1] for sample in samples]

        if signal_type == 0:
            plt.subplot(2, 1, 1)
            signal_plot.SignalPlot.plot_normal_signal(indexes, values, 'Time', 'Amplitude',
                                                      signal_plot.SignalType.Continuous, True)
            plt.subplot(2, 1, 2)
            signal_plot.SignalPlot.plot_normal_signal(indexes, values, 'Time', 'Amplitude',
                                                      signal_plot.SignalType.Discrete, True)
        else:
            plt.subplot(2, 1, 1)
            signal_plot.SignalPlot.plot_normal_signal(indexes, values, 'Frequency', 'Phase Shift',
                                                      signal_plot.SignalType.Continuous, True)
            plt.subplot(2, 1, 2)
            signal_plot.SignalPlot.plot_normal_signal(indexes, values, 'Frequency', 'Phase Shift',
                                                      signal_plot.SignalType.Discrete,
                                                      True)

        plt.grid(True)
        plt.tight_layout()
        plt.show()
