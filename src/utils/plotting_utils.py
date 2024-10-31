import matplotlib.pyplot as plt

def plot_data(mds):
    plt.figure()
    plt.plot(mds.Q, mds.I, label="Intensity")
    plt.xlabel("Q")
    plt.ylabel("I")
    plt.legend()
    plt.show()
