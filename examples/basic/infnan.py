from pychuck import *

n = 1000000000000000000000000000.0
for _ in range(20):
    n *= n
print(np.isinf(n))

n *= 0
print(np.isnan(n))

# print(np.isinf(1.0 / 0.0))
# print(np.isnan(0.0 / 0.0))
print(np.inf, -np.inf)
print(np.isinf(np.inf))
