import math
from decimal import Decimal, getcontext
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
        samples = [list(map(float, line.strip().split())) for line in signal]
        indexes = [sample[0] for sample in samples]
        values = [sample[1] for sample in samples]
        return signal_type, is_periodic, num_samples, indexes, values

    @staticmethod
    def arithmetic_operations_on_signal(operation, y1_values=None, y2_values=None, multiplier=None, normalize=None):
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
        else:
            min_value = min(y1_values)
            max_value = max(y1_values)
            if normalize == '-1':
                signal_output = [2 * ((x - min_value) / (max_value - min_value)) - 1 for x in y1_values]
            else:
                signal_output = [(x - min_value) / (max_value - min_value) for x in y1_values]
        return signal_output

    @staticmethod
    def quantize_signal(type_of_signal, values, number_of_levels_or_bits):
        # Get Max & Min Ampl
        getcontext().prec = 4
        max_ampl = Decimal(max(values))
        min_ampl = Decimal(min(values))
        diff_in_ampl = max_ampl - min_ampl

        # calculate resolution
        if type_of_signal == "Bits":
            encoded_bits = number_of_levels_or_bits
            resolution = diff_in_ampl / Decimal(pow(2, number_of_levels_or_bits))
        else:
            encoded_bits = math.log2(number_of_levels_or_bits)
            resolution = diff_in_ampl / Decimal(number_of_levels_or_bits)
        getcontext().prec = 4

        # calculate intervals
        intervals = []
        value = min_ampl
        while value < max_ampl:
            intervals.append([float(value), float(value + resolution)])
            value += resolution
        # encoding signal
        binary_values = [bin(i)[2:].zfill(int(encoded_bits)) for i in range(2 ** int(encoded_bits))]
        int_values = [int(b, 2) + 1 for b in binary_values]
        encoded_values = dict(zip(int_values, binary_values))

        # interval index
        interval_index = []
        xqn = []
        all_encodes = []

        for i in range(len(values)):

            for index, interval in enumerate(intervals):
                if interval[0] <= values[i] <= interval[1]:
                    interval_index.append(index + 1)
                    xqn.append(float(Decimal((Decimal(interval[0]) + Decimal(interval[1])) / 2)))
                    all_encodes.append(encoded_values[index + 1])
                    break

        # Get Error
        getcontext().prec = 3
        errorofn = [float(Decimal(er) - Decimal(xn)) for er, xn in zip(xqn, values)]
        return interval_index, all_encodes, xqn, errorofn


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
