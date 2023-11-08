import gui_file as gui

from plot_signals import FourierTransform

gui.MainGui()

x = [(64+0j), (-7.999999999999976+19.313708498984745j), (-8.000000000000071+7.999999999999986j), (-8.000000000000002+3.3137084989847536j), (-8-2.5848713190921388e-14j), (-8.000000000000002-3.3137084989847536j), (-8.000000000000071-7.999999999999986j), (-7.999999999999976-19.313708498984745j)]
data = FourierTransform.calculate_dft_and_idft(x, 'idft')
#print(data)
signal = open("data.txt")
u = signal.readline().strip()
u = signal.readline().strip()
u = signal.readline().strip()


