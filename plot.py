import matplotlib.pyplot as plt

plots = [[],[],[],[],[],[]]
with open('graph.txt') as f:
    for line in f:
        points = line.split()
        for i in range(0,len(points)):
            points[i] = float(points[i])
        print points
        plots[0].append(points[1])
        plots[1].append(points[2])
        plots[2].append(points[3])
        plots[3].append(points[4])
        plots[4].append(points[5])
        plots[5].append(points[6])
print plots

bar_width = 100.0
values = [0,256,512,1000]
# plt.xlabel('Bandwidth')
ylabels = ["Bandwidth for RTS","Bandwidth for CTS","Bandwidth for ACK","Bandwidth for TCP ACK","Bandwidth for TCP SEGMENT","TCP throughput"]
i = 0
for plot in plots:
    plt.ylabel(ylabels[i])
    plt.xlabel('RTS threshold')
    i+=1
    plt.bar(values, plot,bar_width)
    plt.tight_layout()
    plt.show()
