import matplotlib.pyplot as plt
from enum import Enum
import numpy as np


class SignalsMethods:
    @staticmethod
    def plot_normal_signal(indexes, values, x_label, y_label, signal_type, is_first):
        label = 'Continuous' if signal_type == SignalType.Continuous else 'Discrete'
        new_label = 'First' if is_first else 'Second'
        plt.title(f'{new_label} {label} Signal')
        if signal_type == SignalType.Continuous:
            plt.plot(indexes, values, )
        else:
            plt.stem(indexes, values, )
        plt.xlabel(x_label)
        plt.ylabel(y_label)

    @staticmethod
    def generate_signal(amp, phase_shift, angular_freq, sampling_freq, signal_type):
        signal = None
        t = np.arange(0, sampling_freq, 1)
        theta = 2 * np.pi * (angular_freq / sampling_freq)
        if signal_type == 'sine':
            signal = amp * np.sin(theta * t + phase_shift)
        elif signal_type == 'cosine':
            signal = amp * np.cos(theta * t + phase_shift)
        return t, signal


class SignalType(Enum):
    Continuous = 1
    Discrete = 2
    Cosine = 3
    Sine = 4
