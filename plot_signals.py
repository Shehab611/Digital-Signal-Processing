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

        # interval index
        interval_index = []
        xqn = []
        all_encodes = []

        for i in values:
            for interval in intervals:
                if interval[0] <= i <= interval[1]:
                    xqn.append(float(Decimal((Decimal(interval[0]) + Decimal(interval[1])) / 2)))
                    index = intervals.index(interval)
                    interval_index.append(index + 1)
                    frmt = "{0:0%sb}" % int(encoded_bits)
                    encoded = frmt.format(index)
                    all_encodes.append(encoded)
                    break

        # Get Error
        getcontext().prec = 3
        errorofn = []
        for i in range(len(xqn)):
            errorofn.append(float(Decimal(xqn[i]) - Decimal(values[i])))

        return interval_index, all_encodes, xqn, errorofn


class FourierTransform:

    @staticmethod
    def calculate_dft_and_idft(values, type_of_calc):
        output = []
        for k in range(len(values)):
            harmonic = FourierTransform.calculate_harmonic_or_element(k, values, type_of_calc)
            if type_of_calc == 'idft':
                output.append(int(harmonic.real))
            else:
                output.append(harmonic)

        return output

    @staticmethod
    def calculate_harmonic_or_element(k, values, type_of_calc):
        N = len(values)
        summ = 0
        for n in range(N):
            summ += FourierTransform.calculate_one_element(n, k, values, type_of_calc)
        if type_of_calc == 'idft':
            return summ * (1 / N)
        return summ

    @staticmethod
    def calculate_one_element(n, k, values, type_of_calc):
        if values[n] == 0:
            return 0
        rtn = values[n] * FourierTransform.calculate_exp(n, k, len(values), type_of_calc)
        if type_of_calc == 'idft':
            rtn = (rtn.real.__round__() + (rtn.imag.__round__() * 1j))
        return rtn

    @staticmethod
    def calculate_exp(n, k, N, type_of_calc):
        the_power = (1j * 2 * n * k) / N
        if the_power.imag == 0:
            return 1 + 0j
        sin_value = float(math.sin(math.pi * the_power.imag.__abs__()))
        cos_value = float(math.cos(math.pi * the_power.imag.__abs__()))
        if type_of_calc == 'dft':
            sin_value *= -1j
        else:
            cos_value = cos_value.__round__()
            sin_value *= 1j
        e = cos_value + sin_value

        return e

    @staticmethod
    def calculate_fundamentel_freq(sampling_freq, len_of_values):
        periodic_time_of_sample = 1 / sampling_freq
        down_term = len_of_values * periodic_time_of_sample
        up_term = 2 * math.pi
        return up_term / down_term

    @staticmethod
    def calculate_ampl(dft):
        ampl = []
        for i in range(len(dft)):
            the_powered_real_number = dft[i].real * dft[i].real
            the_powered_imag_number = dft[i].imag * dft[i].imag
            summ = the_powered_real_number + the_powered_imag_number
            ampl.append(math.sqrt(float(summ)))
        return ampl

    @staticmethod
    def calculate_phase_shift(dft):
        phases = []
        for i in range(len(dft)):
            # frac = dft[i].imag / dft[i].real
            # value_in_degree = math.degrees(math.atan(frac))
            phases.append(float(math.atan2(dft[i].imag, dft[i].real)))
        return phases

    @staticmethod
    def signal_representation(x, amp_y, theta_y):
        plt.subplot(2, 1, 1)
        SignalsMethods.plot_normal_signal(x, amp_y, 'Frequency',
                                          'Amplitude',
                                          SignalType.Discrete,
                                          'Frequency Domain with Amplitude')
        plt.subplot(2, 1, 2)
        SignalsMethods.plot_normal_signal(x, theta_y, 'Frequency',
                                          'Phase Shift',
                                          SignalType.Discrete,
                                          'Frequency Domain with Phase Shift')
        plt.tight_layout()
        plt.show()

    @staticmethod
    def plot_freq_domain(folding_freq, amp_y, theta_y):
        x = []
        for i in range(len(amp_y)):
            x.append(i * folding_freq)
        FourierTransform.signal_representation(x, amp_y, theta_y)

    @staticmethod
    def plot_time_domain(y):
        x = []
        for i in range(len(y)):
            x.append(i)

        SignalsMethods.plot_normal_signal(x, y, 'time', 'samples', SignalType.Discrete, 'Time Domain')
        plt.tight_layout()
        plt.show()

    @staticmethod
    def convert_from_polar_form(ampl, theta):
        outputs = []
        for i in range(len(ampl)):
            img = ampl[i] * math.sin(theta[i]) * 1j
            real = ampl[i] * math.cos(theta[i])
            complex_num = img + real
            outputs.append(complex_num)
        return outputs


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
