import numpy as np

def mzi_model(wl, A, B, wl0, FSR, phi):
    return A + B * (np.cos(np.pi * (wl - wl0) / FSR + phi)) ** 2

def diode_model(v_val, Is, n):
    Vt = 0.02585
    return Is * (np.exp(np.clip(v_val / (n * Vt), -700, 700)) - 1)