import matplotlib.pyplot as plt
import sys
import dpkt
import struct
import socket

def bandwidth(bytes):
    return (bytes*8.00)/(1024*1024*50)

# check argument
if len(sys.argv) < 2:
    print("please specify the dump files to read")
    sys.exit(1)

graph = open('graph.txt','w')
    # open dump file
for filename in sys.argv[1:]:
    print filename
    try:
        reader = dpkt.pcap.Reader(open(filename))
    except IOError as e:
        print(e)
        sys.exit(1)
    except dpkt.Error as e:
        print(e)
        sys.exit(1)

    # check for ieee802.11 dump
    if not reader.datalink() == dpkt.pcap.DLT_IEEE802_11_RADIO:
        print("pcap file is not from an 802.11 device")
        sys.exit(1)

    # initialize values
    subtypes = (
            dpkt.ieee80211.D_QOS_DATA,
            dpkt.ieee80211.D_DATA
            )
    sequence_index = 22

    # initialize counters
    retries = 0
    errors = 0
    other_frames = 0
    rts_frames = 0
    cts_frames = 0
    ack_frames = 0
    tcp_frames = 0
    tcp_acks = 0
    tcp_bytes = 0
    rts_bytes = 0
    cts_bytes = 0
    ack_bytes = 0
    tcp_ack_bytes = 0
    tcp_segment_bytes = 0

    # loop packets
    for ts,data in reader:
        # read tap header length
        try:
            tap = dpkt.radiotap.Radiotap(data)
        except dpkt.Error as e:
            errors += 1
            continue

        tap_len = socket.ntohs(tap.length)
        # print tap_len
        # parse ieee80211 header
        try:
            wlan = dpkt.ieee80211.IEEE80211(data[tap_len:])
        except dpkt.Error as e:
            errors += 1
            continue

        # check frame type
        if wlan.subtype not in subtypes:
            if wlan.subtype == dpkt.ieee80211.C_RTS:
            	rts_frames += 1;rts_bytes += len(data);
            elif wlan.subtype == dpkt.ieee80211.C_CTS:
            	cts_frames += 1;cts_bytes += len(data);
            elif wlan.subtype == dpkt.ieee80211.C_ACK:
            	ack_frames += 1;ack_bytes += len(data);
            else:
            	# print wlan.subtype
            	other_frames += 1
            continue

    	tcp_bool = False
        try:
            tcp = dpkt.tcp.TCP(wlan.data)
            tcp_bool = True
        except dpkt.Error as e:
            other_frames += 1

        if tcp_bool == True:
            tcp_frames += 1
            # print dpkt.tcp(tcp).TH_ACK
            # print tcp.sport
            if ( tcp.flags & dpkt.tcp.TH_ACK ) != 0:
                tcp_acks +=1
                tcp_ack_bytes += len(data)
            if len(tcp.data)>0 :
                tcp_segment_bytes += len(data)
            # print len(wlan.data);
            tcp_bytes += len(wlan.data)
                # print "flags: " + hex(tcp.flags) + " TH_ACK: " +hex(dpkt.tcp.TH_ACK)
            # print ack_flag
            # if tcp.__hdr__[3][2]:
            #     print 1

        # count retries
        if wlan.retry:
            retries += 1

    print("Bandwidth for RTS:  {:6} mbps".format(bandwidth(rts_bytes)))
    print("Bandwidth for CTS:  {:6} mbps".format(bandwidth(cts_bytes)))
    print("Bandwidth for ACK:  {:6} mbps".format(bandwidth(ack_bytes)))
    print("Bandwidth for TCP ACK:  {:6} mbps".format(bandwidth(tcp_ack_bytes)))
    print("Bandwidth for TCP SEGMENT:  {:6} mbps".format(bandwidth(tcp_segment_bytes)))
    print("TCP throughput at each node:  {:6} MB".format(tcp_bytes/(1024.00*1024.00*2)))

    graph.write(filename.split()[0] + " " +  str(bandwidth(rts_bytes)) + " " + str(bandwidth(cts_bytes)) + " " +str(bandwidth(ack_bytes)) + " " +str(bandwidth(tcp_ack_bytes)) + " " + str(bandwidth(tcp_segment_bytes)) + " " + str(tcp_bytes/(1024.00*1024.00*2)) + "\n")

graph.close()

plots = []
plot_bool = 0
with open('graph.txt') as f:
    for line in f:
        points = line.split()
        for i in range(0,len(points)):
            points[i] = float(points[i])
        print points
        x = len(points) - 1
        if plot_bool == 0:
            for i in range(0,x):
                plots.append([])
            plot_bool = 1
        for i in range(0,x):
            plots[i].append(points[i + 1])

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
