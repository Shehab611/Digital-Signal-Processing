import math

from plot_signals import SignalsMethods, FourierTransform

# import gui_file as gui

# gui.MainGui()

ampl = [64.0, 20.905007438022025, 11.313708498984761, 8.659137602339156, 8.0, 8.659137602339177, 11.31370849898479, 20.905007438021983]
theta = [0.0, 1.9634954084936211, 2.3561944901923453, 2.748893571891068, -3.1415926535897922, -2.7488935718910676, -2.356194490192346, -1.963495408493619]

values = FourierTransform.convert_from_polar_form(ampl,theta)
f = FourierTransform.calculate_dft_and_idft(values,'idft')
print(f)