from pychuck import *

n = 1000000000000000000000000000.0
for _ in range(20):
    n *= n
print(np.isinf(n))

n *= 0
print(np.isnan(n))

print(np.inf)
