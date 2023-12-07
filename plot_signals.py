import math
from decimal import Decimal, getcontext
from tkinter import filedialog
import os
import matplotlib.pyplot as plt
from enum import Enum
import numpy as np

from DerivativeSignal import DerivativeSignal


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
        for i in range(len_of_values):
            result = signal_values[i] - DCTTransform.calculate_mean_of_signal(signal_values)
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
    def convolve():
        _, _, len_signal_1, indexes_1, signal_1 = SignalsMethods.read_signal_from_file('inputs/Input_conv_Sig1.txt')
        _, _, len_signal_2, indexes_2, signal_2 = SignalsMethods.read_signal_from_file('inputs/Input_conv_Sig2.txt')
        # Length of the output signal
        len_output_signal = len_signal_1 + len_signal_2 - 1
        output_signal = []
        for i in range(len_output_signal):
            output_signal.append(0)

        for n in range(len_output_signal):
            for k in range(max(0, n - len_signal_2 + 1), min(len_signal_1, n + 1)):
                output_signal[n] += signal_1[k] * signal_2[n - k]

        output_indexes = indexes_1 + indexes_2
        x = list(set(output_indexes))
        x.sort()
        return x, output_signal


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
    def calculate_normalized_cross_correlation(signal1,signal2,indicates):
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
