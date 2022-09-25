import scipy.stats as stat
from matplotlib import pyplot as plt

def get_statistics():
    step = 10000
    ppf_val = [i / step for i in range(1, step, 25)]

    ppf = stat.norm.ppf(ppf_val, loc=0, scale=1)
    pdf = stat.norm.pdf(ppf, loc=0, scale=1)

    return ppf_val, ppf, pdf

p, x, y = get_statistics()
y = [round(i, 3) for i in y]
p = [round(i, 3) for i in p]
x = [round(i, 3) for i in x]
p = p[1:]
x = x[1:]
y = y[1:]
max_x = max(x)
max_y = max(y)
min_x = min(x)
min_y = min(y)
# print(len(x))
res = {"x":{"max":max_x, "min":min_x, "data":x}, "y":{"max":max_y, "min":min_y, "data":y}, "p":p}
print(res)
# print(x[0:20])
# print(p[0:20])
# print(y[0:20])
plt.plot(x, y)
plt.show()