import math
from decimal import Decimal, getcontext
from tkinter import ttk, filedialog
import os
from enum import Enum
import numpy as np
from DerivativeSignal import DerivativeSignal
import tkinter as tk
from tkinter import messagebox
import matplotlib.pyplot as plt
import plot_signals as signal_plot
from test_output import signal_samples_are_equal, QuantizationTest1, QuantizationTest2, Shift_Fold_Signal, ConvTest, \
    Compare_Signals_fir
import pandas as pd


class SignalsMethods:
    @staticmethod
    def save_file(indicates, values, file_name):
        with open(file_name, 'w') as file:
            file.write('0 \n')
            file.write('0 \n')
            file.write(f'{len(indicates)}\n')
            for i in range(len(indicates)):
                file.write(f'{indicates[i]} {values[i]}\n')

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
    def read_signal_from_file(file_name):
        signal = open(file_name)
        # define the signal
        signal_type = int(signal.readline().strip())
        is_periodic = int(signal.readline().strip())
        num_samples = int(signal.readline().strip())
        samples = [list(map(float, line.strip().split())) for line in signal]
        indexes = [sample[0] for sample in samples]
        values = [sample[1] for sample in samples]
        return signal_type, is_periodic, num_samples, indexes, values

    @staticmethod
    def read_signal_from_file_without_indicates(file_name):
        signal = open(file_name)
        # define the signal
        signal_type = float(signal.readline().strip())
        is_periodic = float(signal.readline().strip())
        num_samples = float(signal.readline().strip())
        samples = [list(map(float, line.strip().split())) for line in signal]
        values = [sample[0] for sample in samples]
        return signal_type, is_periodic, num_samples, values

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
                output.append(harmonic.real.__round__(3))
            else:
                output.append(harmonic)
        return output

    @staticmethod
    def calculate_harmonic_or_element(k, values, type_of_calc):
        len_of_values = len(values)
        summ = 0
        for n in range(len_of_values):
            summ += FourierTransform.calculate_one_element(n, k, values, type_of_calc)
        if type_of_calc == 'idft':
            return summ * (1 / len_of_values)
        return summ

    @staticmethod
    def calculate_one_element(n, k, values, type_of_calc):
        if values[n] == 0:
            return 0
        rtn = values[n] * FourierTransform.calculate_exp(n, k, len(values), type_of_calc)
        if type_of_calc == 'idft':
            rtn = (rtn.real + (rtn.imag * 1j))
        return rtn

    @staticmethod
    def calculate_exp(n, k, len_of_values, type_of_calc):
        the_power = (1j * 2 * n * k) / len_of_values
        if the_power.imag == 0:
            return 1 + 0j
        sin_value = float(math.sin(math.pi * the_power.imag.__abs__()))
        cos_value = float(math.cos(math.pi * the_power.imag.__abs__()))
        if type_of_calc == 'dft':
            sin_value *= -1j
        else:
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
    def plot_freq_domain(fundamentel_freq, amp_y, theta_y):
        x = []
        for i in range(len(amp_y)):
            x.append(i * fundamentel_freq)
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


class DCTTransform:
    @staticmethod
    def calculate_angle(values_len, n, k):
        element_one = math.pi / (4 * values_len)
        element_two = (2 * n) - 1
        element_three = (2 * k) - 1
        result = element_one * element_two * element_three
        return math.cos(result)

    @staticmethod
    def calculate_one_element(signal_values, n, k):
        angle = DCTTransform.calculate_angle(len(signal_values), n, k)
        return signal_values[n] * angle

    @staticmethod
    def calculate_sum(signal_values, k):
        summ = 0
        for n in range(len(signal_values)):
            summ += DCTTransform.calculate_one_element(signal_values, n, k)
        return summ

    @staticmethod
    def dct_transform(signal_values):
        y_values = []
        values_len = len(signal_values)
        value_under_root = 2 / values_len
        for k in range(values_len):
            result = math.sqrt(value_under_root) * DCTTransform.calculate_sum(signal_values, k)
            y_values.append(result)
        return y_values

    @staticmethod
    def calculate_mean_of_signal(signal_values):
        summ = 0
        len_of_values = len(signal_values)
        for i in range(len_of_values):
            summ += signal_values[i]
        return summ / len_of_values

    @staticmethod
    def remove_dc_component(signal_values):
        len_of_values = len(signal_values)
        removed_values = []
        mean_value = DCTTransform.calculate_mean_of_signal(signal_values)
        for i in range(len_of_values):
            result = signal_values[i] - mean_value
            removed_values.append(round(result, 3))
        return removed_values


class TaskSix:
    @staticmethod
    def derivative_signal():
        return DerivativeSignal()

    @staticmethod
    def shifting_signal(signal, k, folding):
        shifted_signal = []
        for i in range(len(signal)):
            if folding:
                shifted_signal.append(signal[i] + k)
            else:
                shifted_signal.append(signal[i] - k)
        return shifted_signal

    @staticmethod
    def folding_signal(signal):
        signal.reverse()
        return signal

    @staticmethod
    def smoothing_signal(signal, window_size):
        smoothed_signal = []
        for i in range(len(signal) - 1):
            summ = 0
            for j in range(i, window_size):
                summ += signal[j]
            smoothed_signal.append(summ / window_size)
        return smoothed_signal

    @staticmethod
    def remove_dc(signal):
        new_signal = FourierTransform.calculate_dft_and_idft(signal, 'dft')
        new_signal[0] = 0
        new_signal = FourierTransform.calculate_dft_and_idft(new_signal, 'idft')
        return new_signal

    @staticmethod
    def convolve(indexes_1, signal_1, indexes_2, signal_2):
        # Length of the output signal
        min_ind = int(indexes_1[0] + indexes_2[0])
        max_ind = int(indexes_1[-1] + indexes_2[-1])
        result_length = max_ind - min_ind + 1
        result = [0] * result_length
        indices = [i for i in range(min_ind, max_ind + 1)]
        for i in range(len(indexes_1)):
            for j in range(len(indexes_2)):
                index = int(indexes_1[i] + indexes_2[j])
                result[index - min_ind] += signal_1[i] * signal_2[j]
        return indices, result


class TaskSeven:
    @staticmethod
    def calculate_cross_correlation_element(signal1, signal2):
        summ = 0
        for i in range(len(signal2)):
            summ += signal1[i] * signal2[i]
        return summ

    @staticmethod
    def shift_signal(signal):
        tmp_value = signal[0]
        signal = signal[1:]
        signal.append(tmp_value)
        return signal

    @staticmethod
    def calculate_cross_correlation(signal1, signal2):
        correlation = []
        for i in range(len(signal2)):
            value = TaskSeven.calculate_cross_correlation_element(signal1, signal2) / len(signal2)
            signal2 = TaskSeven.shift_signal(signal2)
            correlation.append(value)
        return correlation

    @staticmethod
    def calculate_normalized_cross_correlation(signal1, signal2, indicates):
        down_term_first_element = TaskSeven.calculate_cross_correlation_element(signal1, signal1, )
        down_term_second_element = TaskSeven.calculate_cross_correlation_element(signal2, signal2)
        down_term = math.sqrt((down_term_first_element * down_term_second_element)) / len(signal1)
        corr = TaskSeven.calculate_cross_correlation(signal1, signal2)
        normalized_cross_correlation_signal = [x / down_term for x in corr]
        return normalized_cross_correlation_signal, indicates

    @staticmethod
    def calculate_time_analysis(fs):
        _, _, _, indicates, signal1 = SignalsMethods.read_signal_from_file('time_analysis_files/TD_input signal1.txt')
        _, _, _, indicates, signal2 = SignalsMethods.read_signal_from_file('time_analysis_files/TD_input signal2.txt')
        calc_correlation = TaskSeven.calculate_cross_correlation(signal1, signal2)
        abs_value = [abs(x) for x in calc_correlation]
        max_value = max(abs_value)
        the_lag = indicates[abs_value.index(max_value)]
        ts = 1 / fs
        return the_lag * ts

    @staticmethod
    def get_signal_of_class(folder_path):
        means_list = []
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)

            if os.path.isfile(file_path) and filename.endswith('.txt'):
                # Read numbers from the text file
                with open(file_path, 'r') as file:
                    lines = file.readlines()

                # Convert lines to integers
                numbers = [int(line.strip()) for line in lines]

                # Calculate mean and append to means_list
                mean_value = sum(numbers) / len(numbers)
                means_list.append(mean_value)
        return means_list

    @staticmethod
    def get_correlation_of_test():
        with open('test_signals/Test1.txt', 'r') as file:
            lines1 = file.readlines()

        with open('test_signals/Test2.txt', 'r') as file:
            lines2 = file.readlines()

        # test signal
        signal_test_1 = [int(line.strip()) for line in lines1]
        signal_test_2 = [int(line.strip()) for line in lines2]

        # class signals
        signal_class_1 = TaskSeven.get_signal_of_class('class_1_files')
        signal_class_2 = TaskSeven.get_signal_of_class('class_2_files')
        signal_class = signal_class_1 + signal_class_2

        correlation1 = TaskSeven.calculate_cross_correlation(signal_test_1, signal_class)
        correlation2 = TaskSeven.calculate_cross_correlation(signal_test_2, signal_class)

        maxx = correlation1[0]
        maxx1 = correlation2[0]

        if maxx > maxx1:
            return 'Test Signal 1 belongs to class 2 (UP)', 'Test Signal 2 belongs to class 1 (Down)'
        else:
            return 'Test Signal 2 belongs to class 2 (UP)', 'Test Signal 1 belongs to class 1 (Down)'


class TaskEight:
    @staticmethod
    def fast_correlation(signal1, signal2):
        signal1 = FourierTransform.calculate_dft_and_idft(signal1, 'dft')
        signal2 = FourierTransform.calculate_dft_and_idft(signal2, 'dft')
        signal1 = [complex_num.conjugate() for complex_num in signal1]
        result = [x * y for x, y in zip(signal1, signal2)]
        result = FourierTransform.calculate_dft_and_idft(result, 'idft')
        result = [x / len(signal1) for x in result]
        return result

    @staticmethod
    def fast_convolution(signal1, signal2):
        signal1 = FourierTransform.calculate_dft_and_idft(signal1, 'dft')
        signal2 = FourierTransform.calculate_dft_and_idft(signal2, 'dft')
        result = [x * y for x, y in zip(signal1, signal2)]
        result = FourierTransform.calculate_dft_and_idft(result, 'idft')
        return result


class PracticalTaskOne:

    @staticmethod
    def get_the_next_odd_number(num=0.0):
        ceil_num = num.__ceil__()
        if ceil_num % 2 == 0:
            return ceil_num + 1
        elif ceil_num % 1 == 0:
            return ceil_num

    @staticmethod
    def read_filter_specifications(file_path):
        parameters = {}
        with open(file_path, 'r') as file:
            for line in file:
                key, value = line.strip().split(' = ')
                parameters[key] = value
        f2 = None
        filter_type = parameters['FilterType']
        fs = int(parameters['FS'])
        stop_band = int(parameters['StopBandAttenuation'])
        transition_band = int(parameters['TransitionBand'])
        if filter_type.__contains__('Band'):
            f1 = int(parameters['F1'])
            f2 = int(parameters['F2'])
        else:
            f1 = int(parameters['FC'])
        return filter_type, fs, stop_band, transition_band, f1, f2

    @staticmethod
    def get_window_type(stop_band):
        bands_to_windows = {
            21: 'rectangular',
            44: 'hanning',
            53: 'hamming',
            74: 'blackman'
        }
        for band, window_name in sorted(bands_to_windows.items()):
            if band >= stop_band:
                return window_name

    @staticmethod
    def calculate_total_elements(type_of_window, fs, transition_band):
        normalized_transition_band = transition_band / fs
        if type_of_window == 'rectangular':
            return PracticalTaskOne.get_the_next_odd_number(0.9 / normalized_transition_band)
        elif type_of_window == 'hanning':
            return PracticalTaskOne.get_the_next_odd_number(3.1 / normalized_transition_band)
        elif type_of_window == 'hamming':
            return PracticalTaskOne.get_the_next_odd_number(3.3 / normalized_transition_band)
        return PracticalTaskOne.get_the_next_odd_number(5.5 / normalized_transition_band)

    @staticmethod
    def calculate_new_fc(f1, transition_band, filter_type, f2=None):
        if filter_type == 'Low pass':
            return (f1 + (transition_band / 2)), None
        elif filter_type == 'High pass':
            return (f1 - (transition_band / 2)), None
        elif filter_type == 'Band pass':
            return (f1 - (transition_band / 2)), (f2 + (transition_band / 2))
        else:
            return (f1 + (transition_band / 2)), (f2 - (transition_band / 2))

    @staticmethod
    def window_items_list(window_type, total_elements, ):
        windows_list = []
        for element_index in range((total_elements / 2).__ceil__()):
            if window_type == 'hanning':
                windows_list.append(0.5 + (0.5 * math.cos((2 * math.pi * element_index) / total_elements)))
            elif window_type == 'hamming':
                windows_list.append(0.54 + (0.46 * math.cos((2 * math.pi * element_index) / total_elements)))
            elif window_type == 'blackman':
                first_element = 0.5 * math.cos((2 * math.pi * element_index) / (total_elements - 1))
                second_element = 0.08 * math.cos((4 * math.pi * element_index) / (total_elements - 1))
                windows_list.append(0.42 + second_element + first_element)
        return windows_list

    @staticmethod
    def filter_items_list(filter_type, total_elements, new_fc):
        f1 = new_fc[0]
        f2 = new_fc[1]
        filtered_list = []
        for element_index in range((total_elements / 2).__ceil__()):
            if filter_type == 'Low pass':
                if element_index == 0:
                    filtered_list.append(2 * f1)
                else:
                    x = element_index * 2 * math.pi * f1
                    filtered_list.append(2 * f1 * (math.sin(x) / x))
            elif filter_type == 'High pass':
                if element_index == 0:
                    filtered_list.append(1 - (2 * f1))
                else:
                    x = element_index * 2 * math.pi * f1
                    filtered_list.append(-2 * f1 * (math.sin(x) / x))
            elif filter_type == 'Band pass':
                if element_index == 0:
                    filtered_list.append(2 * round(f2 - f1, 2))
                else:
                    x1 = element_index * 2 * math.pi * f1
                    x2 = element_index * 2 * math.pi * f2
                    filtered_list.append((2 * f2 * (math.sin(x2) / x2)) - (2 * f1 * (math.sin(x1) / x1)))
            else:
                if element_index == 0:
                    filtered_list.append(1 - (2 * (f2 - f1)))
                else:
                    x1 = element_index * 2 * math.pi * f1
                    x2 = element_index * 2 * math.pi * f2
                    filtered_list.append(((2 * f2 * (math.sin(x2) / x2)) - (2 * f1 * (math.sin(x1) / x1))) * -1)
        return filtered_list

    @staticmethod
    def make_the_filter(file_path, ):
        filter_type, fs, stop_band, transition_band, f1, f2 = PracticalTaskOne.read_filter_specifications(file_path)
        window_type = PracticalTaskOne.get_window_type(stop_band)
        total_elements = PracticalTaskOne.calculate_total_elements(window_type, fs, transition_band)
        new_fc = PracticalTaskOne.calculate_new_fc(f1, transition_band, filter_type, f2)
        new_fc = tuple(elem / fs if elem is not None else None for elem in new_fc)
        indicates = PracticalTaskOne.make_the_filtered_indicates(total_elements)
        window_list = PracticalTaskOne.window_items_list(window_type, total_elements)
        filtered_list = PracticalTaskOne.filter_items_list(filter_type, total_elements, new_fc)
        filtered_list = PracticalTaskOne.make_the_filter_list(window_list, filtered_list)
        return indicates, filtered_list

    @staticmethod
    def apply_filter_on_signal(filter_spec_path, indexes_2, signal_2):
        indicates, filtered_list = PracticalTaskOne.make_the_filter(filter_spec_path)
        return TaskSix.convolve(indicates, filtered_list, indexes_2, signal_2, )

    @staticmethod
    def make_the_filtered_indicates(total_elements):
        indicates = []
        for i in range(-(total_elements // 2), (total_elements // 2) + 1):
            indicates.append(i)
        return sorted(set(indicates))

    @staticmethod
    def make_the_filter_list(window_list, filtered_list):
        multiplied_values = [x * y for x, y in zip(window_list, filtered_list)]
        combined_values = multiplied_values[::-1] + multiplied_values
        combined_values.pop(len(combined_values) // 2)
        return combined_values

    @staticmethod
    def resampling(signal_indicates, signal_list, factor_m, factor_l):
        filter_spec_path = ('C:/Users/sheha/Downloads/Practical Task/Practical task 1/Sampling test cases/Testcase '
                            '1/Filter Specifications.txt')
        filter_indicates, filter_list = PracticalTaskOne.make_the_filter(filter_spec_path)

        if factor_m == 0 and factor_l != 0:
            signal_indicates, signal_list = PracticalTaskOne.sampling_up(signal_indicates, signal_list, factor_l)
            m, n = TaskSix.convolve(filter_indicates, filter_list, signal_indicates, signal_list, )
            for i in range(2):
                n.pop()
                m.pop()
            return m, n

        elif factor_l == 0 and factor_m != 0:
            x, y = PracticalTaskOne.apply_filter_on_signal(filter_spec_path, signal_indicates, signal_list)
            return PracticalTaskOne.sampling_down(x, y, factor_m)

        elif factor_l != 0 and factor_m != 0:
            t, p = PracticalTaskOne.sampling_up(signal_indicates, signal_list, factor_l)
            x, y = TaskSix.convolve(filter_indicates, filter_list, t, p, )
            m, n = PracticalTaskOne.sampling_down(x, y, factor_m)
            n.pop()
            m.pop()
            return m, n
        return None, None

    @staticmethod
    def sampling_up(indicates, signal, factor_l):
        up_sampled_signal = []
        up_sampled_signal_indicates = []
        for i in range(len(indicates)):
            up_sampled_signal.append(signal[i])
            for _ in range(int(factor_l) - 1):
                up_sampled_signal.append(0)

        for i in range(len(up_sampled_signal)):
            up_sampled_signal_indicates.append(i)

        return up_sampled_signal_indicates, up_sampled_signal

    @staticmethod
    def sampling_down(indicates, signal, factor_m):
        down_sampled_signal = []
        down_sampled_signal_indicates = []

        for i in range(0, len(signal), factor_m):
            down_sampled_signal.append(signal[i])

        for i in range(len(down_sampled_signal)):
            down_sampled_signal_indicates.append(indicates[i])

        return down_sampled_signal_indicates, down_sampled_signal


class PracticalTaskTwo:
    folder_one_path = 'C:/Users/sheha/Downloads/Practical Task/Practical task 2/A'
    folder_two_path = 'C:/Users/sheha/Downloads/Practical Task/Practical task 2/B'
    folder_test_path = 'C:/Users/sheha/Downloads/Practical Task/Practical task 2/Test Folder'

    @staticmethod
    def apply_filter(minF, maxF, fs, signal):
        signal_indicates = [i for i in range(len(signal))]
        stop_band = 50
        transition_band = 500
        f1 = minF
        f2 = maxF
        if minF > 0 and maxF < fs / 2:
            filter_type = 'Band pass'
        else:
            filter_type = 'Band Stop'

        window_type = PracticalTaskOne.get_window_type(stop_band)
        total_elements = PracticalTaskOne.calculate_total_elements(window_type, fs, transition_band)
        new_fc = PracticalTaskOne.calculate_new_fc(f1, transition_band, filter_type, f2)
        new_fc = tuple(elem / fs if elem is not None else None for elem in new_fc)
        indicates = PracticalTaskOne.make_the_filtered_indicates(total_elements)
        window_list = PracticalTaskOne.window_items_list(window_type, total_elements)
        filtered_list = PracticalTaskOne.filter_items_list(filter_type, total_elements, new_fc)
        filtered_list = PracticalTaskOne.make_the_filter_list(window_list, filtered_list)
        return TaskSix.convolve(indicates, filtered_list, signal_indicates, signal, )

    @staticmethod
    def resampling_the_signal(newFs, maxF, Fs, signal_indicates, signal_list):
        if newFs >= 2 * maxF:
            # up sampling
            if newFs > Fs:
                return PracticalTaskOne.resampling(signal_indicates, signal_list, 0, (newFs / Fs))
            # down sampling
            elif newFs < Fs:
                return PracticalTaskOne.resampling(signal_indicates, signal_list, (Fs / newFs), 0)
            return signal_indicates, signal_list
        return None, None

    @staticmethod
    def find_peaks(signal):
        peaks = []
        for i in range(1, len(signal) - 1):
            if signal[i] > signal[i - 1] and signal[i] > signal[i + 1]:
                peaks.append(i)
        return peaks

    @staticmethod
    def compute_preserve_coff(signal):
        after_corr = TaskSeven.calculate_cross_correlation(signal, signal)
        signal = after_corr
        signal = signal[len(signal) // 2:]
        peaks = PracticalTaskTwo.find_peaks(signal)
        return peaks, after_corr

    @staticmethod
    def calculate_file_dct(file_path, minF, maxF, fs, newFs):
        _, _, _, signal = SignalsMethods.read_signal_from_file_without_indicates(file_path)
        signal_indicates = [i for i in range(len(signal))]
        _, signal = PracticalTaskTwo.apply_filter(minF, maxF, fs, signal)
        c, v = PracticalTaskTwo.resampling_the_signal(newFs, maxF, fs, signal_indicates, signal)
        if v is not None:
            signal = v
        signal = DCTTransform.remove_dc_component(signal)
        signal = SignalsMethods.arithmetic_operations_on_signal(
            operation=ArithmeticSignalOperations.Normalization,
            y1_values=signal, normalize='-1')
        signal, after_corr = PracticalTaskTwo.compute_preserve_coff(signal)
        return DCTTransform.dct_transform(signal), after_corr, signal

    @staticmethod
    def calculate_average_files(folder_path, minF, maxF, fs, newFs):
        dcts = []
        after_corr = []
        after_pres = []
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            if os.path.isfile(file_path) and filename.endswith('.txt'):
                x, y, z = PracticalTaskTwo.calculate_file_dct(file_path, minF, maxF, fs, newFs)
                dcts.append(sum(x) / len(x))
                after_corr.append(y)
                after_pres.append(z)
        return dcts, after_corr, after_pres


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


class Task1dot1:

    def __init__(self):
        self.signal_one_type = None
        self.indexes_one = None
        self.values_one = None
        self.signal_two_type = None
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
        self.signal_one_type, is_periodic_one, num_samples_one, self.indexes_one, self.values_one = (
            signal_plot.SignalsMethods.read_signal())

    def choose_signal_two(self):
        self.signal_two_type, is_periodic_two, num_samples_two, self.indexes_two, self.values_two = (
            signal_plot.SignalsMethods.read_signal())

    def display_signal(self):

        if self.signal_one_type == 0:
            plt.subplot(2, 2, 1)
            signal_plot.SignalsMethods.plot_normal_signal(self.indexes_one, self.values_one, 'Time',
                                                          'Amplitude',
                                                          signal_plot.SignalType.Continuous,
                                                          signal_title='First Continuous Signal')
            plt.subplot(2, 2, 3)
            signal_plot.SignalsMethods.plot_normal_signal(self.indexes_one, self.values_one, 'Time', 'Amplitude',
                                                          signal_plot.SignalType.Discrete,
                                                          'First Discrete Signal')
        else:
            plt.subplot(2, 2, 1)
            signal_plot.SignalsMethods.plot_normal_signal(self.indexes_one, self.values_one, 'Frequency', 'Phase Shift',
                                                          signal_plot.SignalType.Continuous,
                                                          'First Continuous Signal')
            plt.subplot(2, 2, 3)
            signal_plot.SignalsMethods.plot_normal_signal(self.indexes_one, self.values_one, 'Frequency', 'Phase Shift',
                                                          signal_plot.SignalType.Discrete,
                                                          'First Discrete Signal')

        if self.signal_two_type is not None:
            if self.signal_two_type == 0:
                plt.subplot(2, 2, 2)
                signal_plot.SignalsMethods.plot_normal_signal(self.indexes_two, self.values_two, 'Time', 'Amplitude',
                                                              signal_plot.SignalType.Continuous,
                                                              'Second Continuous Signal')
                plt.subplot(2, 2, 4)
                signal_plot.SignalsMethods.plot_normal_signal(self.indexes_two, self.values_two, 'Time', 'Amplitude',
                                                              signal_plot.SignalType.Discrete,
                                                              'Second Discrete Signal')
            else:
                plt.subplot(2, 2, 2)
                signal_plot.SignalsMethods.plot_normal_signal(self.indexes_two, self.values_two, 'Frequency',
                                                              'Phase Shift',
                                                              signal_plot.SignalType.Continuous,
                                                              'Second Continuous Signal')
                plt.subplot(2, 2, 4)
                signal_plot.SignalsMethods.plot_normal_signal(self.indexes_two, self.values_two, 'Frequency',
                                                              'Phase Shift',
                                                              signal_plot.SignalType.Discrete,

                                                              'Second Discrete Signal')

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
                                                      signal_plot.SignalType.Continuous,
                                                      'Continuous Signal')
        plt.subplot(2, 1, 2)
        signal_plot.SignalsMethods.plot_normal_signal(self.x_axis, self.y_axis, x_label, y_label,
                                                      signal_plot.SignalType.Discrete,
                                                      'Discrete Signal')

        plt.grid(True)
        plt.tight_layout()
        plt.show()

    def test_signal(self):
        self.generate_signal()

        if self.selected_option == 'sine':
            test_message = signal_samples_are_equal('test_outputs/SinOutput.txt', self.y_axis)
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


class Task2:
    def choose_signal_one(self):
        signal_one_type, is_periodic_one, num_samples_one, self.indexes_one, self.values_one = (
            signal_plot.SignalsMethods.read_signal())

    def choose_signal_two(self):
        signal_two_type, is_periodic_two, num_samples_two, self.indexes_two, self.values_two = (
            signal_plot.SignalsMethods.read_signal())

    def add_subtract_signal_representation(self, op):
        plt.subplot(2, 2, 1)
        signal_plot.SignalsMethods.plot_normal_signal(self.indexes_one, self.values_one, 'Time',
                                                      'Amplitude',
                                                      signal_plot.SignalType.Continuous,
                                                      'Signal One')
        plt.subplot(2, 2, 2)
        signal_plot.SignalsMethods.plot_normal_signal(self.indexes_two, self.values_two, 'Time',
                                                      'Amplitude',
                                                      signal_plot.SignalType.Continuous,
                                                      'Signal Two')
        plt.subplot(2, 1, 2)
        if op == '+':
            title = 'Addition'
        else:
            title = 'Subtraction'
        signal_plot.SignalsMethods.plot_normal_signal(self.indexes_two, self.signal_one_output, 'Time',
                                                      'Amplitude',
                                                      signal_plot.SignalType.Continuous,
                                                      f'{title} Signal')

        plt.grid(True)
        plt.tight_layout()
        plt.show()

    def add_signals(self):
        self.signal_one_output = signal_plot.SignalsMethods.arithmetic_operations_on_signal(
            operation=signal_plot.ArithmeticSignalOperations.Addition,
            y1_values=self.values_one, y2_values=self.values_two)
        self.add_subtract_signal_representation('+')

    def subtract_signals(self):
        self.signal_one_output = signal_plot.SignalsMethods.arithmetic_operations_on_signal(
            operation=signal_plot.ArithmeticSignalOperations.Subtraction,
            y1_values=self.values_one, y2_values=self.values_two)
        self.add_subtract_signal_representation('-')

    def signal_representation(self, op):
        plt.subplot(2, 1, 1)
        signal_plot.SignalsMethods.plot_normal_signal(self.indexes_one, self.values_one, 'Time',
                                                      'Amplitude',
                                                      signal_plot.SignalType.Continuous,
                                                      'Signal')
        plt.subplot(2, 1, 2)
        if op == '*':
            title = 'Multiply'
        elif op == '^':
            title = 'Squaring'
        elif op == 'a':
            title = 'Accumulating'
        elif op == 'n':
            title = 'Normalized'
        else:
            title = 'Shifting'
            self.indexes_one = self.signal_one_output
            self.signal_one_output = self.values_one
        signal_plot.SignalsMethods.plot_normal_signal(self.indexes_one, self.signal_one_output, 'Time',
                                                      'Amplitude',
                                                      signal_plot.SignalType.Continuous,
                                                      f'{title} Signal')

        plt.grid(True)
        plt.tight_layout()
        plt.show()

    def square_signal(self):
        self.signal_one_output = signal_plot.SignalsMethods.arithmetic_operations_on_signal(
            operation=signal_plot.ArithmeticSignalOperations.Squaring,
            y1_values=self.values_one)

        self.signal_representation('^')

    def accumulate_signal(self):
        self.signal_one_output = signal_plot.SignalsMethods.arithmetic_operations_on_signal(
            operation=signal_plot.ArithmeticSignalOperations.Accumulation,
            y1_values=self.values_one)
        self.signal_representation('a')

    def multiply_signal(self):
        self.signal_one_output = signal_plot.SignalsMethods.arithmetic_operations_on_signal(
            operation=signal_plot.ArithmeticSignalOperations.Multiplication,
            y1_values=self.values_one, multiplier=int(self.shift_mult_txt_box.get()))
        self.signal_representation('*')

    def normalize_from_zero_signal(self):
        self.signal_one_output = signal_plot.SignalsMethods.arithmetic_operations_on_signal(
            operation=signal_plot.ArithmeticSignalOperations.Normalization,
            y1_values=self.values_one, normalize='0')
        self.signal_representation('n')

    def normalize_signal(self):
        self.signal_one_output = signal_plot.SignalsMethods.arithmetic_operations_on_signal(
            operation=signal_plot.ArithmeticSignalOperations.Normalization,
            y1_values=self.values_one, normalize='-1')
        self.signal_representation('n')

    def shifting_signal(self):
        self.signal_one_output = signal_plot.SignalsMethods.arithmetic_operations_on_signal(
            operation=signal_plot.ArithmeticSignalOperations.Shifting,
            y1_values=self.indexes_one, multiplier=int(self.shift_mult_txt_box.get()))
        self.signal_representation('')

    def __init__(self):
        self.signal_one_output = None
        self.is_periodic_one = None
        self.num_samples_one = None
        self.indexes_one = None
        self.values_one = None
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
        self.add_signal_btn = tk.Button(self.button_frame, text='Add Two Signals', command=self.add_signals)
        self.add_signal_btn.grid(row=1, column=0, sticky=tk.W + tk.E, padx=10, pady=40)
        self.subtract_signal_btn = tk.Button(self.button_frame, text='Subtract Two Signals',
                                             command=self.subtract_signals)
        self.subtract_signal_btn.grid(row=1, column=1, sticky=tk.W + tk.E, padx=10, pady=40)
        self.square_signal_btn = tk.Button(self.button_frame, text='Square Signal One', command=self.square_signal)
        self.square_signal_btn.grid(row=2, column=0, sticky=tk.W + tk.E, padx=10, pady=10)
        self.accumulate_signal_btn = tk.Button(self.button_frame, text='Accumulate Signal One',
                                               command=self.accumulate_signal)
        self.accumulate_signal_btn.grid(row=2, column=1, sticky=tk.W + tk.E, padx=10, pady=10)
        self.shift_mult_lbl = tk.Label(self.button_frame, text="Shifting & Multiply:", font=('Arial', 16))
        self.shift_mult_lbl.grid(row=3, column=0, sticky=tk.W)
        self.shift_mult_txt_box = tk.Entry(self.button_frame, font=('Arial', 16))
        self.shift_mult_txt_box.grid(row=3, column=1, padx=5, sticky=tk.W + tk.E, pady=10)
        self.multiply_signal_btn = tk.Button(self.button_frame, text='Multiply Signal One',
                                             command=self.multiply_signal)
        self.multiply_signal_btn.grid(row=4, column=0, sticky=tk.W + tk.E, padx=10, pady=10)
        self.multiply_signal_btn = tk.Button(self.button_frame, text='Shifting Signal One',
                                             command=self.shifting_signal)
        self.multiply_signal_btn.grid(row=4, column=1, sticky=tk.W + tk.E, padx=10, pady=10)
        self.normalize_from_zero_signal_btn = tk.Button(self.button_frame, text='Normalize Signal One from 0 to 1',
                                                        command=self.normalize_from_zero_signal)
        self.normalize_from_zero_signal_btn.grid(row=5, column=0, sticky=tk.W + tk.E, padx=10, pady=10)
        self.normalize_signal_btn = tk.Button(self.button_frame, text='Normalize Signal One from -1 to 1',
                                              command=self.normalize_signal)
        self.normalize_signal_btn.grid(row=5, column=1, sticky=tk.W + tk.E, padx=10, pady=10)
        self.button_frame.pack(fill='x', pady=10)
        self.root.mainloop()


class Task3:
    def signal_representation(self):
        plt.subplot(2, 1, 1)
        signal_plot.SignalsMethods.plot_normal_signal(self.indexes, self.values, 'Samples',
                                                      'Amplitude',
                                                      signal_plot.SignalType.Continuous,
                                                      'Signal Before Quantization')
        plt.subplot(2, 1, 2)
        signal_plot.SignalsMethods.plot_normal_signal(self.indexes, self.xqn, 'Samples',
                                                      'Amplitude',
                                                      signal_plot.SignalType.Continuous,
                                                      'Signal After Quantization')
        plt.tight_layout()
        plt.show()

    def choose_signal_one(self):
        signal_type, is_periodic_one, num_samples_one, self.indexes, self.values = (
            signal_plot.SignalsMethods.read_signal())

    def get_data(self):
        self.levels_or_bits = self.levels_or_bits_combo.get()
        self.number_of_levels_or_bits = int(self.levels_or_bits_txt_box.get())

    def quantize_signal(self):
        self.get_data()
        self.interval_index, self.encoded_values, self.xqn, self.errorofn = signal_plot.SignalsMethods.quantize_signal(
            self.levels_or_bits, self.values,
            self.number_of_levels_or_bits)
        data = {"Interval Index": self.interval_index,
                "Encoded Values": self.encoded_values,
                "Quantized Values": self.xqn,
                "Error Values": self.errorofn}

        # Convert the dictionary to a pandas DataFrame
        df = pd.DataFrame(data)
        for index, row in df.iterrows():
            self.tree.insert("", tk.END, text=str(index), values=(
                row["Interval Index"], row["Encoded Values"], row["Quantized Values"], row['Error Values']))

    #  self.signal_representation()

    def test_quantized_signal_one(self):
        self.quantize_signal()

        test_message = QuantizationTest1("test_outputs/Quan1_Out.txt", self.encoded_values, self.xqn)
        messagebox.showinfo(title='Test Case Result', message=test_message)

    def test_quantized_signal_two(self):
        self.quantize_signal()
        test_message = QuantizationTest2("test_outputs/Quan2_Out.txt", self.interval_index, self.encoded_values,
                                         self.xqn,
                                         self.errorofn)
        messagebox.showinfo(title='Test Case Result', message=test_message)

    def __init__(self):
        self.values = None
        self.indexes = None
        self.number_of_levels_or_bits = None
        self.levels_or_bits = None
        self.interval_index, self.encoded_values, self.xqn, self.errorofn = None, None, None, None
        self.selected_option = 'Bits'
        self.root = tk.Tk()
        self.root.title('Choose Task')
        self.root.geometry('800x500')
        self.button_frame = tk.Frame(self.root)
        self.button_frame.columnconfigure(0, weight=1)
        self.button_frame.columnconfigure(1, weight=1)
        label = tk.Label(self.button_frame, text="Number of Bits or Levels", font=('Arial', 16))
        label.grid(row=0, column=0, sticky=tk.W)
        self.levels_or_bits_combo = ttk.Combobox(self.button_frame, values=['Bits', 'Levels'], font=('Arial', 16))
        self.levels_or_bits_combo.current(0)
        self.levels_or_bits_combo.grid(row=0, column=1, padx=5, sticky=tk.W + tk.E)
        label = tk.Label(self.button_frame, text="Enter Number of Bits or Levels", font=('Arial', 16))
        label.grid(row=1, column=0, sticky=tk.W, pady=18)
        self.levels_or_bits_txt_box = tk.Entry(self.button_frame, font=('Arial', 16))
        self.levels_or_bits_txt_box.grid(row=1, column=1, padx=5, sticky=tk.W + tk.E, pady=18)
        self.choose1_btn = tk.Button(self.button_frame, text='Choose The Signal', command=self.choose_signal_one)
        self.choose1_btn.grid(row=2, column=0, sticky=tk.W + tk.E, padx=10, pady=18)
        self.choose1_btn = tk.Button(self.button_frame, text='Quantize The Signal', command=self.quantize_signal)
        self.choose1_btn.grid(row=2, column=1, sticky=tk.W + tk.E, padx=15, pady=18)
        self.choose1_btn = tk.Button(self.button_frame, text='Test Quantized Signal One',
                                     command=self.test_quantized_signal_one)
        self.choose1_btn.grid(row=3, column=0, sticky=tk.W + tk.E, padx=10, pady=18)
        self.choose1_btn = tk.Button(self.button_frame, text='Test Quantized Signal Two',
                                     command=self.test_quantized_signal_two)
        self.choose1_btn.grid(row=3, column=1, sticky=tk.W + tk.E, padx=15, pady=18)
        self.tree = ttk.Treeview(self.button_frame)
        self.tree["columns"] = ("Interval Index", "Encoded Values", "Quantized Values", "Error Values")

        # Format the columns
        self.tree.column("#0", width=110, stretch=tk.NO, anchor="center")
        self.tree.column("Interval Index", width=100, anchor="center")
        self.tree.column("Encoded Values", width=100, anchor="center")
        self.tree.column("Quantized Values", width=100, anchor="center")
        self.tree.column("Error Values", width=100, anchor="center")

        # Add headings for the columns
        self.tree.heading("#0", text="Number of sample", anchor=tk.CENTER)
        self.tree.heading("Interval Index", text="Interval Index", anchor=tk.CENTER)
        self.tree.heading("Encoded Values", text="Encoded Values", anchor=tk.CENTER)
        self.tree.heading("Quantized Values", text="Quantized Values", anchor=tk.CENTER)
        self.tree.heading("Error Values", text="Error Values", anchor=tk.CENTER)
        self.tree.grid(row=4, sticky=tk.W + tk.E, pady=18, padx=8)
        self.button_frame.pack(fill='x', pady=15)

        self.root.mainloop()


def save_file_in_polar(ampl, phase):
    with open('polar_form.txt', 'w') as file:
        file.write('0 \n')
        file.write('1 \n')
        file.write(f'{len(ampl)}\n')
        for i in range(len(ampl)):
            file.write(f'{ampl[i]} {phase[i]}\n')


def save_file(data, file_name):
    with open(file_name, 'w') as file:
        file.write('0 \n')
        file.write('0 \n')
        file.write(f'{len(data)}\n')
        for i in range(len(data)):
            file.write(f'{i} {data[i]}\n')


def read_dft_test_signal():
    signal = open('test_outputs/Output_Signal_DFT_A,Phase.txt')
    # define the signal
    signal_type = int(signal.readline().strip())
    is_periodic = int(signal.readline().strip())
    num_samples = int(signal.readline().strip())
    samples = [list(map(float, line.strip().split())) for line in signal]
    indexes = [sample[0] for sample in samples]
    values = [sample[1] for sample in samples]
    return signal_type, is_periodic, num_samples, indexes, values


def reconstruct():
    signal = open("data.txt")
    int(signal.readline().strip())
    int(signal.readline().strip())
    num_samples = int(signal.readline().strip())
    values = []
    for i in range(int(num_samples)):
        values.append(complex(signal.readline().strip().split()[1]))

    x = signal_plot.FourierTransform.calculate_dft_and_idft(values, 'idft')
    signal_plot.FourierTransform.plot_time_domain(x)


class Task4:

    def read_signal(self):
        signal_one_type, self.signal_type, num_samples_one, self.signal_ampl, self.signal_phase = (
            signal_plot.SignalsMethods.read_signal())

    def calculate(self):
        if self.signal_type == 0:
            self.sampling_freq_value = float(self.sampling_freq.get())
            type_of_calc = 'dft'
            values = self.signal_phase
            fundamentel_freq = signal_plot.FourierTransform.calculate_fundamentel_freq(self.sampling_freq_value,
                                                                                       len(values))
            data = signal_plot.FourierTransform.calculate_dft_and_idft(values, type_of_calc)

            x = signal_plot.FourierTransform.calculate_ampl(data)
            y = signal_plot.FourierTransform.calculate_phase_shift(data)
            save_file(data, 'data.txt')
            save_file_in_polar(x, y)
            self.edit_ampl = self.edit_ampll.get()
            self.edit_theta = self.edit_phase.get()
            if self.edit_ampl and self.edit_theta:
                for i in range(len(x)):
                    x[i] *= int(self.edit_ampl)
                for i in range(len(y)):
                    y[i] *= int(self.edit_theta)
            elif self.edit_theta:
                for i in range(len(y)):
                    y[i] *= int(self.edit_theta)
            elif self.edit_ampl:
                for i in range(len(x)):
                    x[i] *= int(self.edit_ampl)

            signal_plot.FourierTransform.plot_freq_domain(fundamentel_freq, x, y)
        else:
            type_of_calc = 'idft'
            values = signal_plot.FourierTransform.convert_from_polar_form(self.signal_ampl, self.signal_phase)
            print(values)
            data = signal_plot.FourierTransform.calculate_dft_and_idft(values, type_of_calc)
            signal_plot.FourierTransform.plot_time_domain(data)

    def __init__(self):
        self.signal_type = None
        self.signal_ampl = None
        self.signal_phase = None
        self.sampling_freq_value = None
        self.edit_ampl = None
        self.edit_theta = None
        self.root = tk.Tk()
        self.root.title('Choose Task')
        self.root.geometry('800x500')
        self.button_frame = tk.Frame(self.root)
        self.button_frame.columnconfigure(0, weight=1)
        self.button_frame.columnconfigure(1, weight=1)
        label = tk.Label(self.button_frame, text="Enter Sampling Frequency", font=('Arial', 16))
        label.grid(row=0, column=0, sticky=tk.W)
        self.sampling_freq = tk.Entry(self.button_frame, font=('Arial', 16))
        self.sampling_freq.grid(row=0, column=1, padx=5, sticky=tk.W + tk.E, pady=18)
        self.choose1_btn = tk.Button(self.button_frame, text='Choose Signal', command=self.read_signal)
        self.choose1_btn.grid(row=1, column=0, sticky=tk.W + tk.E, padx=10)
        self.choose2_btn = tk.Button(self.button_frame, text='Calculate', command=self.calculate)
        self.choose2_btn.grid(row=1, column=1, sticky=tk.W + tk.E, padx=10)
        self.add_signal_btn = tk.Button(self.button_frame, text='Reconstruct Signal By IDFT', command=reconstruct)
        self.add_signal_btn.grid(row=2, column=0, sticky=tk.W + tk.E, padx=10, pady=40)
        label = tk.Label(self.button_frame, text="Enter Amplitude ", font=('Arial', 16))
        label.grid(row=3, column=0, sticky=tk.W)
        self.edit_ampll = tk.Entry(self.button_frame, font=('Arial', 16))
        self.edit_ampll.grid(row=3, column=1, padx=5, sticky=tk.W + tk.E, pady=18)
        label = tk.Label(self.button_frame, text="Enter Phase Shift ", font=('Arial', 16))
        label.grid(row=4, column=0, sticky=tk.W)
        self.edit_phase = tk.Entry(self.button_frame, font=('Arial', 16))
        self.edit_phase.grid(row=4, column=1, padx=5, sticky=tk.W + tk.E, pady=18)
        self.button_frame.pack(fill='x', pady=15)

        self.root.mainloop()


class Task5:
    def signal_representation(self, y):
        plt.subplot(2, 1, 1)
        signal_plot.SignalsMethods.plot_normal_signal(self.indexes, self.signal_values, 'x',
                                                      'y',
                                                      signal_plot.SignalType.Continuous,
                                                      'Signal Before DCT')
        plt.subplot(2, 1, 2)
        signal_plot.SignalsMethods.plot_normal_signal(self.indexes, y, 'x',
                                                      'y',
                                                      signal_plot.SignalType.Continuous,
                                                      'Signal After DCT')
        plt.tight_layout()
        plt.show()

    def read_signal(self):
        _, _, _, self.indexes, self.signal_values = (
            signal_plot.SignalsMethods.read_signal())

    def calculate_dct(self):
        y = signal_plot.DCTTransform.dct_transform(self.signal_values)
        self.signal_representation(y)
        x = int(self.coefficients.get())
        save_file(y[:x], 'dct_coefficients.txt')
        test_result = signal_samples_are_equal('test_outputs/DCT_output.txt', y)
        messagebox.showinfo(title='Test Case Result', message=test_result)

    def remove_dc(self):
        y = signal_plot.DCTTransform.remove_dc_component(self.signal_values)
        test_result = signal_samples_are_equal('test_outputs/DC_component_output.txt', y)
        messagebox.showinfo(title='Test Case Result', message=test_result)

    def __init__(self):
        self.signal_values = None
        self.indexes = None
        self.coefficients_value = None
        self.root = tk.Tk()
        self.root.title('Choose Task')
        self.root.geometry('800x500')
        self.button_frame = tk.Frame(self.root)
        self.button_frame.columnconfigure(0, weight=1)
        self.button_frame.columnconfigure(1, weight=1)
        label = tk.Label(self.button_frame, text="Enter First Coefficients to be Saved ", font=('Arial', 16))
        label.grid(row=0, column=0, sticky=tk.W)
        self.coefficients = tk.Entry(self.button_frame, font=('Arial', 16))
        self.coefficients.grid(row=0, column=1, padx=5, sticky=tk.W + tk.E, pady=18)
        self.choose1_btn = tk.Button(self.button_frame, text='Choose Signal', command=self.read_signal)
        self.choose1_btn.grid(row=1, column=0, sticky=tk.W + tk.E, padx=10)
        self.choose2_btn = tk.Button(self.button_frame, text='Calculate DCT', command=self.calculate_dct)
        self.choose2_btn.grid(row=1, column=1, sticky=tk.W + tk.E, padx=10)
        self.add_signal_btn = tk.Button(self.button_frame, text='Remove DC Component', command=self.remove_dc)
        self.add_signal_btn.grid(row=2, column=0, sticky=tk.W + tk.E, padx=10, pady=40)
        self.button_frame.pack(fill='x', pady=15)

        self.root.mainloop()


class Task6:
    def signal_representation(self, y):
        plt.subplot(2, 1, 1)
        signal_plot.SignalsMethods.plot_normal_signal(self.indexes, self.signal_values, 'x',
                                                      'y',
                                                      signal_plot.SignalType.Continuous,
                                                      'Signal Before DCT')
        plt.subplot(2, 1, 2)
        signal_plot.SignalsMethods.plot_normal_signal(self.indexes, y, 'x',
                                                      'y',
                                                      signal_plot.SignalType.Continuous,
                                                      'Signal After DCT')
        plt.tight_layout()
        plt.show()

    def read_signal(self):
        _, _, _, self.indexes, self.signal_values = (
            signal_plot.SignalsMethods.read_signal())

    def calculate_smoothing(self):
        k = int(self.window_size.get())
        signal_plot.TaskSix.smoothing_signal(self.signal_values, k)

    @staticmethod
    def calculate_sharpening():
        tt = signal_plot.TaskSix.derivative_signal()
        messagebox.showinfo(title='Test Case Result', message=tt)

    def calculate_shifting(self):
        steps = int(self.shifting_steps.get())
        signal_plot.TaskSix.shifting_signal(self.indexes, steps, False)

    def folding_signal(self):
        x = signal_plot.TaskSix.folding_signal(self.signal_values)
        self.signal_representation(x)
        msg = Shift_Fold_Signal('test_outputs/Output_fold.txt', self.indexes, x)
        messagebox.showinfo(title='Test Case Result', message=msg)

    def shift_folding_byn500(self):
        x = signal_plot.TaskSix.folding_signal(self.signal_values)
        y = signal_plot.TaskSix.shifting_signal(self.indexes, -500, True)
        self.signal_representation(y)
        msg = Shift_Fold_Signal('test_outputs/Output_ShiftFoldedby-500.txt', y, x)
        messagebox.showinfo(title='Test Case Result', message=msg)

    def shift_folding_by500(self):
        x = signal_plot.TaskSix.folding_signal(self.signal_values)
        y = signal_plot.TaskSix.shifting_signal(self.indexes, 500, True)
        self.signal_representation(y)
        msg = Shift_Fold_Signal('test_outputs/Output_ShifFoldedby500.txt', y, x)
        messagebox.showinfo(title='Test Case Result', message=msg)

    def remove_dc_component(self):
        tt = signal_plot.TaskSix.remove_dc(self.signal_values)
        self.signal_representation(tt)
        test_result = signal_samples_are_equal('test_outputs/DC_component_output.txt', tt)
        messagebox.showinfo(title='Test Case Result', message=test_result)

    @staticmethod
    def calculate_convolve():
        _, _, _, indexes_1, signal_1 = signal_plot.SignalsMethods.read_signal_from_file('inputs/Input_conv_Sig1.txt')
        _, _, _, indexes_2, signal_2 = signal_plot.SignalsMethods.read_signal_from_file('inputs/Input_conv_Sig2.txt')
        x, y = signal_plot.TaskSix.convolve(indexes_1, signal_1, indexes_2, signal_2)
        msg = ConvTest(x, y)
        messagebox.showinfo(title='Test Case Result', message=msg)

    def __init__(self):
        self.signal_values = None
        self.indexes = None
        self.root = tk.Tk()
        self.root.title('Choose Task')
        self.root.geometry('800x500')
        self.button_frame = tk.Frame(self.root)
        self.button_frame.columnconfigure(0, weight=1)
        self.button_frame.columnconfigure(1, weight=1)
        label = tk.Label(self.button_frame, text="Enter Window Size ", font=('Arial', 16))
        label.grid(row=0, column=0, sticky=tk.W)
        self.window_size = tk.Entry(self.button_frame, font=('Arial', 16))
        self.window_size.grid(row=0, column=1, padx=5, sticky=tk.W + tk.E, pady=18)
        self.choose1_btn = tk.Button(self.button_frame, text='Choose Signal', command=self.read_signal)
        self.choose1_btn.grid(row=1, column=0, sticky=tk.W + tk.E, padx=10)
        self.choose2_btn = tk.Button(self.button_frame, text='Calculate Smoothing', command=self.calculate_smoothing)
        self.choose2_btn.grid(row=1, column=1, sticky=tk.W + tk.E, padx=10)
        self.add_signal_btn = tk.Button(self.button_frame, text='Calculate Sharping', command=self.calculate_sharpening)
        self.add_signal_btn.grid(row=2, column=0, sticky=tk.W + tk.E, padx=10, pady=40)
        label = tk.Label(self.button_frame, text="Enter shifting steps ", font=('Arial', 16))
        label.grid(row=3, column=0, sticky=tk.W)
        self.shifting_steps = tk.Entry(self.button_frame, font=('Arial', 16))
        self.shifting_steps.grid(row=3, column=1, padx=5, sticky=tk.W + tk.E, pady=18)
        self.choose1_btn = tk.Button(self.button_frame, text='Calculate Shifting', command=self.calculate_shifting)
        self.choose1_btn.grid(row=4, column=0, sticky=tk.W + tk.E, padx=10, pady=18)
        self.choose1_btn = tk.Button(self.button_frame, text='Folding Signal', command=self.folding_signal)
        self.choose1_btn.grid(row=4, column=1, sticky=tk.W + tk.E, padx=10, pady=18)
        self.choose1_btn = tk.Button(self.button_frame, text='Shift Folding by 500', command=self.shift_folding_by500)
        self.choose1_btn.grid(row=5, column=0, sticky=tk.W + tk.E, padx=10, pady=18)
        self.choose1_btn = tk.Button(self.button_frame, text='Shift Folding by -500', command=self.shift_folding_byn500)
        self.choose1_btn.grid(row=5, column=1, sticky=tk.W + tk.E, padx=10, pady=18)
        self.choose1_btn = tk.Button(self.button_frame, text='Remove Dc Component', command=self.remove_dc_component)
        self.choose1_btn.grid(row=6, column=0, sticky=tk.W + tk.E, padx=10, pady=18)
        self.choose1_btn = tk.Button(self.button_frame, text='Calculate Convolve', command=self.calculate_convolve)
        self.choose1_btn.grid(row=6, column=1, sticky=tk.W + tk.E, padx=10, pady=18)
        self.button_frame.pack(fill='x', pady=15)

        self.root.mainloop()


class Task7:
    @staticmethod
    def calculate_correlation():
        _, _, _, indicates, signal1 = signal_plot.SignalsMethods.read_signal_from_file(
            'correalation_inputs,outputs/Corr_input signal1.txt')
        _, _, _, indicates, signal2 = signal_plot.SignalsMethods.read_signal_from_file(
            'correalation_inputs,outputs/Corr_input signal2.txt')
        correlation, indicates = signal_plot.TaskSeven.calculate_normalized_cross_correlation(signal1, signal2,
                                                                                              indicates)
        test_result = Compare_Signals_fir('correalation_inputs,outputs/CorrOutput.txt', indicates, correlation)
        messagebox.showinfo(title='Test Case Result', message=test_result)

    @staticmethod
    def time_analysis():
        value = signal_plot.TaskSeven.calculate_time_analysis(100)
        messagebox.showinfo(title='Time Analysis value', message=value)

    @staticmethod
    def template_matching():
        value = signal_plot.TaskSeven.get_correlation_of_test()
        new_value = f'{value[0]} \n {value[1]}'
        messagebox.showinfo(title='Template Matching', message=new_value)

    def __init__(self):
        self.root = tk.Tk()
        self.root.title('Choose Task')
        self.root.geometry('800x500')
        self.button_frame = tk.Frame(self.root)
        self.button_frame.columnconfigure(0, weight=1)
        self.button_frame.columnconfigure(1, weight=1)
        self.task1_btn = tk.Button(self.button_frame, text='Correlation', command=self.calculate_correlation)
        self.task1_btn.grid(row=0, column=0, sticky=tk.W + tk.E, padx=10)
        self.task1_btn = tk.Button(self.button_frame, text='Time Analysis', command=self.time_analysis)
        self.task1_btn.grid(row=0, column=1, sticky=tk.W + tk.E, padx=10)
        self.task1_btn = tk.Button(self.button_frame, text='Template Matching', command=self.template_matching)
        self.task1_btn.grid(row=1, column=0, sticky=tk.W + tk.E, padx=10, pady=10)
        self.button_frame.pack(fill='x', pady=15)
        self.root.mainloop()


class Task8:
    @staticmethod
    def fast_correlation():
        signal1 = [1, 0, 0, 1]
        signal2 = [0.5, 1, 1, 0.5]
        correlation = signal_plot.TaskEight.fast_correlation(signal1, signal2)
        print(correlation)

    @staticmethod
    def fast_convolution():
        signal1 = []
        signal2 = []
        convolution = signal_plot.TaskEight.fast_convolution(signal1, signal2)
        print(convolution)

    def __init__(self):
        self.root = tk.Tk()
        self.root.title('Choose Task')
        self.root.geometry('800x500')
        self.button_frame = tk.Frame(self.root)
        self.button_frame.columnconfigure(0, weight=1)
        self.button_frame.columnconfigure(1, weight=1)
        self.task1_btn = tk.Button(self.button_frame, text='Fast Correlation', command=self.fast_correlation)
        self.task1_btn.grid(row=0, column=0, sticky=tk.W + tk.E, padx=10)
        self.task1_btn = tk.Button(self.button_frame, text='Fast Convolution', command=self.fast_convolution)
        self.task1_btn.grid(row=0, column=1, sticky=tk.W + tk.E, padx=10)
        self.button_frame.pack(fill='x', pady=10)
        self.root.mainloop()


class PracticalTask1:
    def signal_representation(self, y):
        plt.subplot(2, 1, 1)
        signal_plot.SignalsMethods.plot_normal_signal(self.signal_inputs, self.signal_values, 'x',
                                                      'y',
                                                      signal_plot.SignalType.Continuous,
                                                      'Signal Before Filtering')
        plt.subplot(2, 1, 2)
        signal_plot.SignalsMethods.plot_normal_signal(self.filtered_signal_indicates, y, 'x',
                                                      'y',
                                                      signal_plot.SignalType.Continuous,
                                                      'Signal After Filtering')
        plt.tight_layout()
        plt.show()

    def resampling_representation(self, x, y):
        plt.subplot(2, 1, 1)
        signal_plot.SignalsMethods.plot_normal_signal(self.signal_inputs, self.signal_values, 'x',
                                                      'y',
                                                      signal_plot.SignalType.Continuous,
                                                      'Signal Before Resampling')
        plt.subplot(2, 1, 2)
        signal_plot.SignalsMethods.plot_normal_signal(x, y, 'x',
                                                      'y',
                                                      signal_plot.SignalType.Continuous,
                                                      'Signal After Resampling')
        plt.tight_layout()
        plt.show()

    def choose_signal(self):
        _, _, _, self.signal_inputs, self.signal_values = signal_plot.SignalsMethods.read_signal()

    def choose_filter(self):
        self.file_path = filedialog.askopenfilename()
        self.filter_type, self.fs, self.stop_band, self.transition_band, self.f1, self.f2 = (
            signal_plot.PracticalTaskOne
            .read_filter_specifications(
                self.file_path))
        data = {"Filter Type": self.filter_type,
                "Sampling Frequency": self.fs,
                "Stop Band": self.stop_band,
                "Transition Band": self.transition_band,
                "F1 (FC in low & high)": self.f1,
                "F2": self.f2,
                }
        # Convert the dictionary to a pandas DataFrame
        df = pd.DataFrame(data, index=[0])
        for index, row in df.iterrows():
            self.tree.insert("", tk.END, text=str(index), values=(
                row["Filter Type"], row["Sampling Frequency"], row["Stop Band"], row['Transition Band'],
                row['F1 (FC in low & high)'], row['F2']
            ))

    def aplay_filter_to_signal(self):
        self.x, self.y = signal_plot.PracticalTaskOne.make_the_filter(self.file_path)
        self.filtered_signal_indicates, self.filtered_signal_values = signal_plot.TaskSix.convolve(
            self.x,
            self.y,
            self.signal_inputs,
            self.signal_values)

    def plot_signal(self):
        self.signal_representation(self.filtered_signal_values)

    def test_applied_filter(self):
        file_path = filedialog.askopenfilename()
        msg = Compare_Signals_fir(file_path, self.filtered_signal_indicates, self.filtered_signal_values)
        messagebox.showinfo(title='Test Case Result', message=msg)

    def test_filter_type(self):
        file_path = filedialog.askopenfilename()
        msg = Compare_Signals_fir(file_path, self.x, self.y)
        messagebox.showinfo(title='Test Case Result', message=msg)

    def save_in_file(self):
        signal_plot.SignalsMethods.save_file(self.filtered_signal_indicates, self.filtered_signal_values,
                                             'coefficients.txt')

    def resampling(self):
        try:
            m_factor = int(self.factor_m_entry.get())
        except:
            m_factor = 0
        try:
            l_factor = int(self.factor_l_entry.get())
        except:
            l_factor = 0
        self.xx, self.yy = signal_plot.PracticalTaskOne.resampling(self.signal_inputs, self.signal_values, m_factor,
                                                                   l_factor)
        if self.xx is None and self.yy is None:
            msg = 'Error You can not resampling'
            messagebox.showinfo(title='Test Case Result', message=msg)
        else:
            self.resampling_representation(self.xx, self.yy)

    def test_resampling(self):
        file_path = filedialog.askopenfilename()
        msg = Compare_Signals_fir(file_path, self.xx, self.yy)
        messagebox.showinfo(title='Test Case Result', message=msg)

    # show data in grid view
    def __init__(self):
        self.filtered_signal_indicates = None
        self.filtered_signal_values = None
        self.signal_inputs = None
        self.signal_values = None
        self.filter_type = None
        self.fs = None
        self.xx = None
        self.x = None
        self.y = None
        self.yy = None
        self.stop_band = None
        self.transition_band = None
        self.file_path = None
        self.f1 = None
        self.f2 = None
        self.factor_l = tk.StringVar()
        self.factor_l.set('Enter L Factor')
        self.factor_m = tk.StringVar()
        self.factor_m.set('Enter M Factor')
        self.root = tk.Tk()
        self.root.title('Choose Task')
        self.root.geometry('800x500')
        self.button_frame = tk.Frame(self.root)
        self.button_frame.columnconfigure(0, weight=1)
        self.button_frame.columnconfigure(1, weight=1)
        self.task1_btn = tk.Button(self.button_frame, text='Choose signal', command=self.choose_signal)
        self.task1_btn.grid(row=0, column=0, sticky=tk.W + tk.E, padx=10, pady=10)
        self.task1_btn = tk.Button(self.button_frame, text='Choose filter', command=self.choose_filter)
        self.task1_btn.grid(row=0, column=1, sticky=tk.W + tk.E, padx=10, pady=10)
        self.task1_btn = tk.Button(self.button_frame, text='Apply filter', command=self.aplay_filter_to_signal)
        self.task1_btn.grid(row=1, column=0, sticky=tk.W + tk.E, padx=10, pady=10)
        self.task1_btn = tk.Button(self.button_frame, text='Plot Signal', command=self.plot_signal)
        self.task1_btn.grid(row=1, column=1, sticky=tk.W + tk.E, padx=10, pady=10)
        self.task1_btn = tk.Button(self.button_frame, text='Test Applied Filter', command=self.test_applied_filter)
        self.task1_btn.grid(row=2, column=0, sticky=tk.W + tk.E, padx=10, pady=10)
        self.task1_btn = tk.Button(self.button_frame, text='Test Filter Type', command=self.test_filter_type)
        self.task1_btn.grid(row=2, column=1, sticky=tk.W + tk.E, padx=10, pady=10)
        self.task1_btn = tk.Button(self.button_frame, text='Save The Coefficients', command=self.save_in_file)
        self.task1_btn.grid(row=3, column=0, sticky=tk.W + tk.E, padx=10, pady=10)
        self.task1_btn = tk.Button(self.button_frame, text='Resampling', command=self.resampling)
        self.task1_btn.grid(row=3, column=1, sticky=tk.W + tk.E, padx=10, pady=10)
        label = tk.Label(self.button_frame, text="Enter L Factor", font=('Arial', 15))
        label.grid(row=4, column=0, sticky=tk.W)
        label = tk.Label(self.button_frame, text="Enter M Factor", font=('Arial', 15))
        label.grid(row=4, column=1, sticky=tk.W)
        self.factor_l_entry = tk.Entry(self.button_frame, font=('Arial', 16), textvariable=self.factor_l, )
        self.factor_l_entry.grid(row=5, column=0, padx=5, sticky=tk.W + tk.E, pady=18)
        self.factor_m_entry = tk.Entry(self.button_frame, font=('Arial', 16), textvariable=self.factor_m)
        self.factor_m_entry.grid(row=5, column=1, padx=5, sticky=tk.W + tk.E, pady=18)
        self.task1_btn = tk.Button(self.button_frame, text='Test Resampling', command=self.test_resampling)
        self.task1_btn.grid(row=6, column=0, sticky=tk.W + tk.E, padx=10, pady=10)
        self.tree = ttk.Treeview(self.button_frame)
        self.tree["columns"] = (
            "Filter Type", "Sampling Frequency", "Stop Band", "Transition Band", "F1 (FC in low & high)", 'F2')
        # Format the columns
        self.tree.column("#0", width=15, stretch=tk.NO, anchor="center")
        self.tree.column("Filter Type", width=55, anchor="center")
        self.tree.column("Sampling Frequency", width=100, anchor="center")
        self.tree.column("Stop Band", width=55, anchor="center")
        self.tree.column("Transition Band", width=80, anchor="center")
        self.tree.column("F1 (FC in low & high)", width=100, anchor="center")
        self.tree.column("F2", width=22, anchor="center")
        # Add headings for the columns
        self.tree.heading("#0", text="#0", anchor=tk.CENTER)
        self.tree.heading("Filter Type", text="Filter Type", anchor=tk.CENTER)
        self.tree.heading("Sampling Frequency", text="Sampling Frequency", anchor=tk.CENTER)
        self.tree.heading("Stop Band", text="Stop Band", anchor=tk.CENTER)
        self.tree.heading("Transition Band", text="Transition Band", anchor=tk.CENTER)
        self.tree.heading("F1 (FC in low & high)", text="F1 (FC in low & high)", anchor=tk.CENTER)
        self.tree.heading("F2", text="F2", anchor=tk.CENTER)
        self.tree.grid(row=7, sticky=tk.W + tk.E, pady=18, padx=4)
        self.button_frame.pack(fill='x', pady=15)
        self.root.mainloop()


class PracticalTask2:

    def pre_processing_folder_a(self):
        self.dcta, self.signals_a_after_corr, self.signals_a_after_presrv = signal_plot.PracticalTaskTwo.calculate_average_files(
            signal_plot.PracticalTaskTwo().folder_one_path, int(self.min_entry.get()), int(self.max_entry.get()),
            int(self.fs_entry.get()), int(self.newFs_entry.get()))
        print('pre processing in a finish')

    def pre_processing_folder_b(self):
        self.dctb, self.signals_b_after_corr, self.signals_b_after_presrv = signal_plot.PracticalTaskTwo.calculate_average_files(
            signal_plot.PracticalTaskTwo().folder_two_path, int(self.min_entry.get()), int(self.max_entry.get()),
            int(self.fs_entry.get()), int(self.newFs_entry.get()))
        print('pre processing in b finish')

    def pre_processing_folder_test(self):
        self.dcttest, self.signals_test_after_corr, self.signals_test_after_presrv = signal_plot.PracticalTaskTwo.calculate_average_files(
            signal_plot.PracticalTaskTwo().folder_test_path, int(self.min_entry.get()), int(self.max_entry.get()),
            int(self.fs_entry.get()), int(self.newFs_entry.get()))
        print('pre processing in test finish')

    def plot_corr_signal_a(self):
        plt.subplot(6, 1, 1)
        x = [i for i in range(len(self.signals_a_after_corr[0]))]
        signal_plot.SignalsMethods.plot_normal_signal(x, self.signals_a_after_corr[0], 'x',
                                                      'y',
                                                      signal_plot.SignalType.Continuous,
                                                      'Signal A 1 after auto corr')
        plt.subplot(6, 1, 2)
        x = [i for i in range(len(self.signals_a_after_corr[1]))]
        signal_plot.SignalsMethods.plot_normal_signal(x, self.signals_a_after_corr[1], 'x',
                                                      'y',
                                                      signal_plot.SignalType.Continuous,
                                                      'Signal A 2 after auto corr')
        plt.subplot(6, 1, 3)
        x = [i for i in range(len(self.signals_a_after_corr[2]))]
        signal_plot.SignalsMethods.plot_normal_signal(x, self.signals_a_after_corr[2], 'x',
                                                      'y',
                                                      signal_plot.SignalType.Continuous,
                                                      'Signal A 3 after auto corr')
        plt.subplot(6, 1, 4)
        x = [i for i in range(len(self.signals_a_after_corr[3]))]
        signal_plot.SignalsMethods.plot_normal_signal(x, self.signals_a_after_corr[3], 'x',
                                                      'y',
                                                      signal_plot.SignalType.Continuous,
                                                      'Signal A 4 after auto corr')
        plt.subplot(6, 1, 5)
        x = [i for i in range(len(self.signals_a_after_corr[4]))]
        signal_plot.SignalsMethods.plot_normal_signal(x, self.signals_a_after_corr[4], 'x',
                                                      'y',
                                                      signal_plot.SignalType.Continuous,
                                                      'Signal A 5 after auto corr')
        plt.subplot(6, 1, 6)
        x = [i for i in range(len(self.signals_a_after_corr[5]))]
        signal_plot.SignalsMethods.plot_normal_signal(x, self.signals_a_after_corr[5], 'x',
                                                      'y',
                                                      signal_plot.SignalType.Continuous,
                                                      'Signal A 6 after auto corr')
        plt.tight_layout()
        plt.show()

    def plot_corr_signal_b(self):
        plt.subplot(6, 1, 1)
        x = [i for i in range(len(self.signals_b_after_corr[0]))]
        signal_plot.SignalsMethods.plot_normal_signal(x, self.signals_b_after_corr[0], 'x',
                                                      'y',
                                                      signal_plot.SignalType.Continuous,
                                                      'Signal B 1 after auto corr')
        plt.subplot(6, 1, 2)
        x = [i for i in range(len(self.signals_b_after_corr[1]))]
        signal_plot.SignalsMethods.plot_normal_signal(x, self.signals_b_after_corr[1], 'x',
                                                      'y',
                                                      signal_plot.SignalType.Continuous,
                                                      'Signal B 2 after auto corr')
        plt.subplot(6, 1, 3)
        x = [i for i in range(len(self.signals_b_after_corr[2]))]
        signal_plot.SignalsMethods.plot_normal_signal(x, self.signals_b_after_corr[2], 'x',
                                                      'y',
                                                      signal_plot.SignalType.Continuous,
                                                      'Signal B 3 after auto corr')
        plt.subplot(6, 1, 4)
        x = [i for i in range(len(self.signals_b_after_corr[3]))]
        signal_plot.SignalsMethods.plot_normal_signal(x, self.signals_b_after_corr[3], 'x',
                                                      'y',
                                                      signal_plot.SignalType.Continuous,
                                                      'Signal B 4 after auto corr')
        plt.subplot(6, 1, 5)
        x = [i for i in range(len(self.signals_b_after_corr[4]))]
        signal_plot.SignalsMethods.plot_normal_signal(x, self.signals_b_after_corr[4], 'x',
                                                      'y',
                                                      signal_plot.SignalType.Continuous,
                                                      'Signal B 5 after auto corr')
        plt.subplot(6, 1, 6)
        x = [i for i in range(len(self.signals_b_after_corr[5]))]
        signal_plot.SignalsMethods.plot_normal_signal(x, self.signals_b_after_corr[5], 'x',
                                                      'y',
                                                      signal_plot.SignalType.Continuous,
                                                      'Signal B 6 after auto corr')
        plt.tight_layout()
        plt.show()

    def plot_corr_signal_test(self):
        plt.subplot(2, 1, 1)
        x = [i for i in range(len(self.signals_test_after_corr[0]))]
        signal_plot.SignalsMethods.plot_normal_signal(x, self.signals_test_after_corr[0], 'x',
                                                      'y',
                                                      signal_plot.SignalType.Continuous,
                                                      'Test Signal 1 After corr')
        plt.subplot(2, 1, 2)
        x = [i for i in range(len(self.signals_test_after_corr[0]))]
        signal_plot.SignalsMethods.plot_normal_signal(x, self.signals_test_after_corr[1], 'x',
                                                      'y',
                                                      signal_plot.SignalType.Continuous,
                                                      'Test Signal 2 After corr')
        plt.tight_layout()
        plt.show()

    def plot_presrv_signal_a(self):
        plt.subplot(6, 1, 1)
        x = [i for i in range(len(self.signals_a_after_presrv[0]))]
        signal_plot.SignalsMethods.plot_normal_signal(x, self.signals_a_after_presrv[0], 'x',
                                                      'y',
                                                      signal_plot.SignalType.Continuous,
                                                      'Signal A 1 after preserving ')
        plt.subplot(6, 1, 2)
        x = [i for i in range(len(self.signals_a_after_presrv[1]))]
        signal_plot.SignalsMethods.plot_normal_signal(x, self.signals_a_after_presrv[1], 'x',
                                                      'y',
                                                      signal_plot.SignalType.Continuous,
                                                      'Signal A 2 after preserving ')
        plt.subplot(6, 1, 3)
        x = [i for i in range(len(self.signals_a_after_presrv[2]))]
        signal_plot.SignalsMethods.plot_normal_signal(x, self.signals_a_after_presrv[2], 'x',
                                                      'y',
                                                      signal_plot.SignalType.Continuous,
                                                      'Signal A 3 after preserving ')
        plt.subplot(6, 1, 4)
        x = [i for i in range(len(self.signals_a_after_presrv[3]))]
        signal_plot.SignalsMethods.plot_normal_signal(x, self.signals_a_after_presrv[3], 'x',
                                                      'y',
                                                      signal_plot.SignalType.Continuous,
                                                      'Signal A 4 after preserving ')
        plt.subplot(6, 1, 5)
        x = [i for i in range(len(self.signals_a_after_presrv[4]))]
        signal_plot.SignalsMethods.plot_normal_signal(x, self.signals_a_after_presrv[4], 'x',
                                                      'y',
                                                      signal_plot.SignalType.Continuous,
                                                      'Signal A 5 after preserving ')
        plt.subplot(6, 1, 6)
        x = [i for i in range(len(self.signals_a_after_presrv[5]))]
        signal_plot.SignalsMethods.plot_normal_signal(x, self.signals_a_after_presrv[5], 'x',
                                                      'y',
                                                      signal_plot.SignalType.Continuous,
                                                      'Signal A 6 after preserving ')
        plt.tight_layout()
        plt.show()

    def plot_presrv_signal_b(self):
        plt.subplot(6, 1, 1)
        x = [i for i in range(len(self.signals_b_after_presrv[0]))]
        signal_plot.SignalsMethods.plot_normal_signal(x, self.signals_b_after_presrv[0], 'x',
                                                      'y',
                                                      signal_plot.SignalType.Continuous,
                                                      'Signal B 1 after preserving ')
        plt.subplot(6, 1, 2)
        x = [i for i in range(len(self.signals_b_after_presrv[1]))]
        signal_plot.SignalsMethods.plot_normal_signal(x, self.signals_b_after_presrv[1], 'x',
                                                      'y',
                                                      signal_plot.SignalType.Continuous,
                                                      'Signal B 2 after preserving ')
        plt.subplot(6, 1, 3)
        x = [i for i in range(len(self.signals_b_after_presrv[2]))]
        signal_plot.SignalsMethods.plot_normal_signal(x, self.signals_b_after_presrv[2], 'x',
                                                      'y',
                                                      signal_plot.SignalType.Continuous,
                                                      'Signal B 3 after preserving ')
        plt.subplot(6, 1, 4)
        x = [i for i in range(len(self.signals_b_after_presrv[3]))]
        signal_plot.SignalsMethods.plot_normal_signal(x, self.signals_b_after_presrv[3], 'x',
                                                      'y',
                                                      signal_plot.SignalType.Continuous,
                                                      'Signal B 4 after preserving ')
        plt.subplot(6, 1, 5)
        x = [i for i in range(len(self.signals_b_after_presrv[4]))]
        signal_plot.SignalsMethods.plot_normal_signal(x, self.signals_b_after_presrv[4], 'x',
                                                      'y',
                                                      signal_plot.SignalType.Continuous,
                                                      'Signal B 5 after preserving ')
        plt.subplot(6, 1, 6)
        x = [i for i in range(len(self.signals_b_after_presrv[5]))]
        signal_plot.SignalsMethods.plot_normal_signal(x, self.signals_b_after_presrv[5], 'x',
                                                      'y',
                                                      signal_plot.SignalType.Continuous,
                                                      'Signal B 6 after preserving ')
        plt.tight_layout()
        plt.show()

    def plot_presrv_signal_test(self):
        plt.subplot(2, 1, 1)
        x = [i for i in range(len(self.signals_test_after_presrv[0]))]
        signal_plot.SignalsMethods.plot_normal_signal(x, self.signals_test_after_presrv[0], 'x',
                                                      'y',
                                                      signal_plot.SignalType.Continuous,
                                                      'Test Signal 1 after preserving ')
        plt.subplot(2, 1, 2)
        x = [i for i in range(len(self.signals_test_after_presrv[1]))]
        signal_plot.SignalsMethods.plot_normal_signal(x, self.signals_test_after_presrv[1], 'x',
                                                      'y',
                                                      signal_plot.SignalType.Continuous,
                                                      'Test Signal 2 after preserving ')
        plt.tight_layout()
        plt.show()

    def plot_dct_signal_a(self):
        plt.subplot(1, 1, 1)
        x = [i for i in range(len(self.dcta))]
        signal_plot.SignalsMethods.plot_normal_signal(x, self.dcta, 'x',
                                                      'y',
                                                      signal_plot.SignalType.Continuous,
                                                      'Signal A 1 after DCT ')
        plt.tight_layout()
        plt.show()

    def plot_dct_signal_b(self):
        plt.subplot(1, 1, 1)
        x = [i for i in range(len(self.dctb))]
        signal_plot.SignalsMethods.plot_normal_signal(x, self.dctb, 'x',
                                                      'y',
                                                      signal_plot.SignalType.Continuous,
                                                      'Signal B 1 after DCT ')
        plt.tight_layout()
        plt.show()

    def plot_dct_signal_test(self):
        plt.subplot(1, 1, 1)
        print(self.dcttest)
        x = [i for i in range(len(self.dcttest))]
        signal_plot.SignalsMethods.plot_normal_signal(x, self.dcttest, 'x',
                                                      'y',
                                                      signal_plot.SignalType.Continuous,
                                                      'Test Signal 1 after DCT ')
        plt.tight_layout()
        plt.show()

    def plot_all_a(self):
        self.plot_dct_signal_a()
        self.plot_presrv_signal_a()
        self.plot_corr_signal_a()

    def plot_all_b(self):
        self.plot_dct_signal_b()
        self.plot_presrv_signal_b()
        self.plot_corr_signal_b()

    def plot_all_test(self):
        self.plot_dct_signal_test()
        self.plot_presrv_signal_test()
        self.plot_corr_signal_test()

    def template_match(self):
        correlation1 = signal_plot.TaskSeven.calculate_cross_correlation(self.dcta, self.dcttest)
        correlation2 = signal_plot.TaskSeven.calculate_cross_correlation(self.dctb, self.dcttest)
        maxx = correlation1[0]
        maxx1 = correlation2[0]
        if maxx > maxx1:
            msg = 'Test Signal 1 belongs to class B ', 'Test Signal 2 belongs to class A '
        else:
            msg = 'Test Signal 2 belongs to class B ', 'Test Signal 1 belongs to class A'
        msg = f'{msg[0]} , {msg[1]}'
        messagebox.showinfo('Template Matching Result', msg)

    def __init__(self):
        self.signals_test_after_corr = None
        self.dcttest = None
        self.signals_test_after_presrv = None
        self.dcta = None
        self.signals_a_after_corr = None
        self.signals_a_after_presrv = None
        self.dctb = None
        self.signals_b_after_corr = None
        self.signals_b_after_presrv = None
        self.root = tk.Tk()
        self.root.title('Choose Task')
        self.root.geometry('800x500')
        self.button_frame = tk.Frame(self.root)
        self.button_frame.columnconfigure(0, weight=1)
        self.button_frame.columnconfigure(1, weight=1)
        label = tk.Label(self.button_frame, text="Minimum Frequency", font=('Arial', 15))
        label.grid(row=0, column=0, sticky=tk.W)
        label = tk.Label(self.button_frame, text="Maximum Frequency", font=('Arial', 15))
        label.grid(row=0, column=1, sticky=tk.W)
        self.min_entry = tk.Entry(self.button_frame, font=('Arial', 16), )
        self.min_entry.grid(row=1, column=0, padx=5, sticky=tk.W + tk.E, pady=10)
        self.max_entry = tk.Entry(self.button_frame, font=('Arial', 16), )
        self.max_entry.grid(row=1, column=1, padx=5, sticky=tk.W + tk.E, pady=10)
        label = tk.Label(self.button_frame, text="Sampling Frequency", font=('Arial', 15))
        label.grid(row=2, column=0, sticky=tk.W)
        label = tk.Label(self.button_frame, text="New Sampling Frequency", font=('Arial', 15))
        label.grid(row=2, column=1, sticky=tk.W)
        self.fs_entry = tk.Entry(self.button_frame, font=('Arial', 16), )
        self.fs_entry.grid(row=3, column=0, padx=5, sticky=tk.W + tk.E, pady=10)
        self.newFs_entry = tk.Entry(self.button_frame, font=('Arial', 16), )
        self.newFs_entry.grid(row=3, column=1, padx=5, sticky=tk.W + tk.E, pady=10)
        self.task1_btn = tk.Button(self.button_frame, text='PreProcessing Signal A',
                                   command=self.pre_processing_folder_a)
        self.task1_btn.grid(row=4, column=0, sticky=tk.W + tk.E, padx=10, pady=10)
        self.task1_btn = tk.Button(self.button_frame, text='PreProcessing Signal B',
                                   command=self.pre_processing_folder_b)
        self.task1_btn.grid(row=4, column=1, sticky=tk.W + tk.E, padx=10, pady=10)
        self.task1_btn = tk.Button(self.button_frame, text='PreProcessing Signal Test',
                                   command=self.pre_processing_folder_test)
        self.task1_btn.grid(row=4, column=2, sticky=tk.W + tk.E, padx=10, pady=10)
        self.task1_btn = tk.Button(self.button_frame, text='plot Signal A',
                                   command=self.plot_all_a)
        self.task1_btn.grid(row=5, column=0, sticky=tk.W + tk.E, padx=10, pady=10)
        self.task1_btn = tk.Button(self.button_frame, text='plot Signal B',
                                   command=self.plot_all_a)
        self.task1_btn.grid(row=5, column=1, sticky=tk.W + tk.E, padx=10, pady=10)
        self.task1_btn = tk.Button(self.button_frame, text='plot Signal Test',
                                   command=self.plot_all_test)
        self.task1_btn.grid(row=5, column=2, sticky=tk.W + tk.E, padx=10, pady=10)
        self.task1_btn = tk.Button(self.button_frame, text='Template Matching',
                                   command=self.template_match)
        self.task1_btn.grid(row=6, column=1, sticky=tk.W + tk.E, padx=10, pady=10)
        self.button_frame.pack(fill='x', pady=10)
        self.root.mainloop()


class MainGui:

    def __init__(self):
        def open_task_one():
            Task1()

        def open_task_two():
            Task2()

        def open_task_three():
            Task3()

        def open_task_four():
            Task4()

        def open_task_five():
            Task5()

        def open_task_six():
            Task6()

        def open_task_seven():
            Task7()

        def open_task_eight():
            Task8()

        def open_practical_task_one():
            PracticalTask1()

        def open_practical_task_two():
            PracticalTask2()

        self.root = tk.Tk()
        self.root.title('Choose Task')
        self.root.geometry('800x500')
        self.button_frame = tk.Frame(self.root)
        self.button_frame.columnconfigure(0, weight=1)
        self.button_frame.columnconfigure(1, weight=1)
        self.task1_btn = tk.Button(self.button_frame, text='Task 1', command=open_task_one)
        self.task1_btn.grid(row=0, column=0, sticky=tk.W + tk.E, padx=10)
        self.task1_btn = tk.Button(self.button_frame, text='Task 2', command=open_task_two)
        self.task1_btn.grid(row=0, column=1, sticky=tk.W + tk.E, padx=10)
        self.task1_btn = tk.Button(self.button_frame, text='Task 3', command=open_task_three)
        self.task1_btn.grid(row=1, column=0, sticky=tk.W + tk.E, padx=10, pady=10)
        self.task1_btn = tk.Button(self.button_frame, text='Task 4', command=open_task_four)
        self.task1_btn.grid(row=1, column=1, sticky=tk.W + tk.E, padx=10, pady=10)
        self.task1_btn = tk.Button(self.button_frame, text='Task 5', command=open_task_five)
        self.task1_btn.grid(row=3, column=0, sticky=tk.W + tk.E, padx=10, pady=10)
        self.task1_btn = tk.Button(self.button_frame, text='Task 6', command=open_task_six)
        self.task1_btn.grid(row=3, column=1, sticky=tk.W + tk.E, padx=10, pady=10)
        self.task1_btn = tk.Button(self.button_frame, text='Task 7', command=open_task_seven)
        self.task1_btn.grid(row=4, column=0, sticky=tk.W + tk.E, padx=10, pady=10)
        self.task1_btn = tk.Button(self.button_frame, text='Task 8', command=open_task_eight)
        self.task1_btn.grid(row=4, column=1, sticky=tk.W + tk.E, padx=10, pady=10)
        self.task1_btn = tk.Button(self.button_frame, text='Practical Task One', command=open_practical_task_one)
        self.task1_btn.grid(row=5, column=0, sticky=tk.W + tk.E, padx=10, pady=10)
        self.task1_btn = tk.Button(self.button_frame, text='Practical Task Two', command=open_practical_task_two)
        self.task1_btn.grid(row=5, column=1, sticky=tk.W + tk.E, padx=10, pady=10)
        self.button_frame.pack(fill='x', pady=10)
        self.root.mainloop()
