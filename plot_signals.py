import matplotlib.pyplot as plt
from enum import Enum


class SignalPlot:
    @staticmethod
    def plot_normal_signal(indexes, values, x_label, y_label, signal_type, is_first):
        label = 'Continuous' if signal_type == SignalType.Continuous else 'Discrete'
        new_label = 'First' if is_first else 'Last'
        plt.title(f'{new_label} {label} Signal')
        if signal_type == SignalType.Continuous:
            plt.plot(indexes, values, )
        else:
            plt.stem(indexes, values, )
        plt.xlabel(x_label)
        plt.ylabel(y_label)


class SignalType(Enum):
    Continuous = 1
    Discrete = 2
