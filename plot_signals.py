from tkinter import filedialog

import matplotlib.pyplot as plt
from enum import Enum
import numpy as np


class SignalsMethods:
    @staticmethod
    def plot_normal_signal(indexes, values, x_label, y_label, signal_type, signal_title):
        plt.title(signal_title)
        if signal_type == SignalType.Continuous:
            plt.plot(indexes, values, )
        else:
            plt.stem(indexes, values, )
        plt.xlabel(x_label)
        plt.ylabel(y_label)
        plt.grid(True)

    @staticmethod
    def generate_signal(amp, phase_shift, angular_freq, sampling_freq, signal_type):
        signal = None
        if sampling_freq == 0:
            t = np.arange(0, 10, 0.01)
            omega = 2 * np.pi * angular_freq
            if signal_type == 'sine':
                signal = amp * np.sin(omega * t + phase_shift)
            elif signal_type == 'cosine':
                signal = amp * np.cos(omega * t + phase_shift)
        else:
            t = np.arange(0, sampling_freq, 1)
            omega = 2 * np.pi * (angular_freq / sampling_freq)
            if signal_type == 'sine':
                signal = amp * np.sin(omega * t + phase_shift)
            elif signal_type == 'cosine':
                signal = amp * np.cos(omega * t + phase_shift)

        return t, signal

    @staticmethod
    def read_signal():
        signal = filedialog.askopenfile(filetypes=[("txt", "*.txt")])
        # define the signal
        signal_type = int(signal.readline().strip())
        is_periodic = int(signal.readline().strip())
        num_samples = int(signal.readline().strip())
        samples_one = [list(map(float, line.strip().split())) for line in signal]
        indexes = [sample[0] for sample in samples_one]
        values = [sample[1] for sample in samples_one]
        return signal_type, is_periodic, num_samples, indexes, values

    @staticmethod
    def arithmetic_operations_on_signal(operation, y1_values=None, y2_values=None, multiplier=None):
        signal_output = None
        if operation == ArithmeticSignalOperations.Addition:
            signal_output = [x + y for x, y in zip(y1_values, y2_values)]
        elif operation == ArithmeticSignalOperations.Subtraction:
            signal_output = [x - y for x, y in zip(y1_values, y2_values)]
        elif operation == ArithmeticSignalOperations.Multiplication:
            signal_output = [x * multiplier for x in y1_values]
        elif operation == ArithmeticSignalOperations.Squaring:
            signal_output = [x ** 2 for x in y1_values]
        elif operation == ArithmeticSignalOperations.Accumulation:
            accumulated_signal = []
            accumulated_sum = 0
            for point in y1_values:
                accumulated_sum += point
                accumulated_signal.append(accumulated_sum)
            signal_output = accumulated_signal
        elif operation == ArithmeticSignalOperations.Shifting:
            signal_output = [x + multiplier for x in y1_values]

        return signal_output


class SignalType(Enum):
    Continuous = 1
    Discrete = 2


class ArithmeticSignalOperations(Enum):
    Addition = 0
    Subtraction = 1
    Multiplication = 2
    Squaring = 3
    Shifting = 4
    Normalization = 5
    Accumulation = 6
