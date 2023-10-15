import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
import matplotlib.pyplot as plt
import plot_signals as signal_plot
from test_output import signal_samples_are_equal


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
        self.root.title('Display Signals')
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

        if self.signal_one_type == 0:
            plt.subplot(2, 2, 1)
            signal_plot.SignalsMethods.plot_normal_signal(self.indexes_one, self.values_one, 'Time',
                                                          'Amplitude',
                                                          signal_plot.SignalType.Continuous, True)
            plt.subplot(2, 2, 3)
            signal_plot.SignalsMethods.plot_normal_signal(self.indexes_one, self.values_one, 'Time', 'Amplitude',
                                                          signal_plot.SignalType.Discrete, True)
        else:
            plt.subplot(2, 2, 1)
            signal_plot.SignalsMethods.plot_normal_signal(self.indexes_one, self.values_one, 'Frequency', 'Phase Shift',
                                                          signal_plot.SignalType.Continuous, True)
            plt.subplot(2, 2, 3)
            signal_plot.SignalsMethods.plot_normal_signal(self.indexes_one, self.values_one, 'Frequency', 'Phase Shift',
                                                          signal_plot.SignalType.Discrete,
                                                          True)

        if self.signal_two:
            if self.signal_two_type == 0:
                plt.subplot(2, 2, 2)
                signal_plot.SignalsMethods.plot_normal_signal(self.indexes_two, self.values_two, 'Time', 'Amplitude',
                                                              signal_plot.SignalType.Continuous, False)
                plt.subplot(2, 2, 4)
                signal_plot.SignalsMethods.plot_normal_signal(self.indexes_two, self.values_two, 'Time', 'Amplitude',
                                                              signal_plot.SignalType.Discrete, False)
            else:
                plt.subplot(2, 2, 2)
                signal_plot.SignalsMethods.plot_normal_signal(self.indexes_two, self.values_two, 'Frequency',
                                                              'Phase Shift',
                                                              signal_plot.SignalType.Continuous, False)
                plt.subplot(2, 2, 4)
                signal_plot.SignalsMethods.plot_normal_signal(self.indexes_two, self.values_two, 'Frequency',
                                                              'Phase Shift',
                                                              signal_plot.SignalType.Discrete,
                                                              False)

        plt.tight_layout()
        plt.show()


class Task1dot2:
    def __init__(self):
        self.selected_option = 'sine'  # Set the default value to 'sine'
        self.amp = None
        self.phase_shift = None
        self.analog_freq = None
        self.sampling_freq = None
        self.x_axis, self.y_axis = None, None
        self.root = tk.Tk()
        self.root.title('Generate Signals')
        self.root.geometry('800x500')

        # Create a label
        label = tk.Label(self.root, text="Signal Generation:", font=('Arial', 16))
        label.grid(row=0, column=0, sticky=tk.W + tk.E)

        wave_type_label = tk.Label(self.root, text="Wave Type:", font=('Arial', 16))
        wave_type_label.grid(row=0, column=1, sticky=tk.W)
        self.wave_type_combo = ttk.Combobox(self.root, values=['sine', 'cosine'], font=('Arial', 16))
        self.wave_type_combo.current(0)
        self.wave_type_combo.grid(row=0, column=2, padx=5, sticky=tk.W + tk.E)

        amp_label = tk.Label(self.root, text="Amplitude:", font=('Arial', 16))
        amp_label.grid(row=1, column=0, sticky=tk.W)
        self.amp_txt_box = tk.Entry(self.root, font=('Arial', 16))
        self.amp_txt_box.grid(row=1, column=1, padx=5, sticky=tk.W + tk.E, )
        phase_shift_label = tk.Label(self.root, text="Phase Shift:", font=('Arial', 16))
        phase_shift_label.grid(row=2, column=0, sticky=tk.W)
        self.phase_shift_txt_box = tk.Entry(self.root, font=('Arial', 16))
        self.phase_shift_txt_box.grid(row=2, column=1, padx=5, sticky=tk.W + tk.E, pady=10)
        analog_freq_label = tk.Label(self.root, text="Analog Frequency:", font=('Arial', 16))
        analog_freq_label.grid(row=3, column=0, sticky=tk.W)
        self.analog_freq_txt_box = tk.Entry(self.root, font=('Arial', 16))
        self.analog_freq_txt_box.grid(row=3, column=1, padx=5, sticky=tk.W + tk.E, pady=10)
        sampling_freq_label = tk.Label(self.root, text="Sampling Frequency:", font=('Arial', 16))
        sampling_freq_label.grid(row=4, column=0, sticky=tk.W)
        self.sampling_freq_txt_box = tk.Entry(self.root, font=('Arial', 16))
        self.sampling_freq_txt_box.grid(row=4, column=1, padx=5, sticky=tk.W + tk.E, pady=10)
        generate_signal_btn = tk.Button(self.root, text='Generate Signal', font=('Arial', 14), command=self.plot_signal)
        generate_signal_btn.grid(row=5, column=1, padx=15, pady=15, )
        test_signal_btn = tk.Button(self.root, text='Test Signal', font=('Arial', 14), command=self.test_signal)
        test_signal_btn.grid(row=6, column=1, padx=15, pady=15, )
        self.root.mainloop()

    def get_signal_data(self):
        self.selected_option = self.wave_type_combo.get()
        self.amp = float(self.amp_txt_box.get())
        self.phase_shift = float(self.phase_shift_txt_box.get())
        self.analog_freq = float(self.analog_freq_txt_box.get())
        self.sampling_freq = float(self.sampling_freq_txt_box.get())

    def generate_signal(self):
        self.get_signal_data()
        self.x_axis, self.y_axis = signal_plot.SignalsMethods.generate_signal(self.amp, self.phase_shift,
                                                                              self.analog_freq,
                                                                              self.sampling_freq,
                                                                              self.selected_option)

    def plot_signal(self):
        self.generate_signal()
        plt.subplot(2, 1, 1)
        y_label = 'Amplitude'
        if self.sampling_freq == 0:
            x_label = ' Time '

        else:
            x_label = 'Samples'

        signal_plot.SignalsMethods.plot_normal_signal(self.x_axis, self.y_axis, x_label, y_label,
                                                      signal_plot.SignalType.Continuous, True)
        plt.subplot(2, 1, 2)
        signal_plot.SignalsMethods.plot_normal_signal(self.x_axis, self.y_axis, x_label, y_label,
                                                      signal_plot.SignalType.Discrete, True)

        plt.grid(True)
        plt.tight_layout()
        plt.show()

    def test_signal(self):
        self.generate_signal()

        if self.selected_option == 'sine':
            test_message = signal_samples_are_equal('SinOutput.txt', self.y_axis)
        else:
            test_message = signal_samples_are_equal('CosOutput.txt', self.y_axis)

        messagebox.showinfo(title='Test Case Result', message=test_message)


class Task1:
    def __init__(self):
        def open_task_one_dot_one():
            Task1dot1()

        def open_task_one_dot_two():
            Task1dot2()

        self.root = tk.Tk()
        self.root.title('Task One')
        self.root.geometry('800x500')
        self.button_frame = tk.Frame(self.root)
        self.button_frame.columnconfigure(0, weight=1)
        self.button_frame.columnconfigure(1, weight=1)
        self.task1dot1_btn = tk.Button(self.button_frame, text='Open Task 1.1', command=open_task_one_dot_one)
        self.task1dot1_btn.grid(row=0, column=0, sticky=tk.W + tk.E, padx=10)
        self.task1dot2_btn = tk.Button(self.button_frame, text='Open Task 1.2', command=open_task_one_dot_two)
        self.task1dot2_btn.grid(row=0, column=1, sticky=tk.W + tk.E, padx=10)
        self.button_frame.pack(fill='x', pady=10)
        self.root.mainloop()


class MainGui:

    def __init__(self):
        def open_task_one():
            Task1()

        self.root = tk.Tk()
        self.root.title('Choose Task')
        self.root.geometry('800x500')
        self.button_frame = tk.Frame(self.root)
        self.button_frame.columnconfigure(0, weight=1)
        self.button_frame.columnconfigure(1, weight=1)
        self.task1_btn = tk.Button(self.button_frame, text='Task 1', command=open_task_one)
        self.task1_btn.grid(row=0, column=0, sticky=tk.W + tk.E, padx=10)
        self.button_frame.pack(fill='x', pady=10)
        self.root.mainloop()
