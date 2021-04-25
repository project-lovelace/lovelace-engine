import numpy as np

def light_time(distance):
    # Allocate 2^28 float64's, roughly ~2 GiB of memory, much more than the 512 MiB container memory limit.
    # For why we're not using `np.zeros` see: https://stackoverflow.com/questions/27574881/why-does-numpy-zeros-takes-up-little-space
    A = np.repeat(0, 2**28)
    return 0
