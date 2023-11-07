import math

from plot_signals import SignalsMethods, FourierTransform

# import gui_file as gui

# gui.MainGui()
values = [1,3,5,7,9,11,13,15]
x = FourierTransform.calculate_dft_and_idft(values)
y = FourierTransform.calculate_fundamentel_freq(4, 4)
z = FourierTransform.calculate_ampl(x)
zz = FourierTransform.calculate_phase_shift(x)
print(x)
print(z)
print(zz)