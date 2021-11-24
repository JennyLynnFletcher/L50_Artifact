from subprocess import Popen, PIPE
import matplotlib.pyplot as plt
import matplotlib.colors as col
import shlex
from time import sleep, strptime
import numpy as np
from numpy import average
import paramiko
from re import findall
from math import ceil, floor, sqrt

def local_cmd(command):
    stdout = Popen(command, shell=True, stdout=PIPE).stdout
    return stdout.read()

def ssh_connect(host):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.MissingHostKeyPolicy())
    ssh.load_host_keys("./id_rsa_keyset4")
    ssh.connect(host, username='root', key_filename="id_rsa_keyset4", passphrase="PefR8nub")
    return ssh

def ssh_cmd(command, ssh):
    output = ""
    stdout = ssh.exec_command(command)[1]
    for line in stdout:
        output += line
    if (len(output) > 0):
        return output
    
def getrtts(directory,name,from_ip,to_ip): 
    rtts= [[] for i in range(10)]
    for i in range(10):
        with open(directory+'/'+name+'_'+from_ip+'_to_'+to_ip+"_"+str(i), "r+") as f:
            for line in f:
                rt = findall(r'time=(.*?) ms',line)[0]
                rtts[i].append(float(rt)*1000)
        rtts[i] = sorted(rtts[i])
    return rtts

def getrtts_hping3(directory,name,from_ip,to_ip): 
    rtts= [[] for i in range(10)]
    for i in range(10):
        with open(directory+'/'+name+'_'+from_ip+'_to_'+to_ip+"_"+str(i), "r+") as f:
            for line in f:
                rt = findall(r'rtt=(.*?) ms',line)[0]
                rtts[i].append(float(rt)*1000)
        rtts[i] = sorted(rtts[i])
    return rtts

def getrtts_nping(directory,name,from_ip,to_ip): 
    rtts= [[] for i in range(10)]
    for i in range(10):
        with open(directory+'/'+name+'_'+from_ip+'_to_'+to_ip+"_"+str(i), "r+") as f:
            send_time = 0
            for line in f:
                r = findall(r'rtt: (.*?)ms',line)
                if len(r) > 0:
                    rtts[i].append(float(r[0])*1000.)
                    rtts[i].append(float(r[1])*1000.)
                    rtts[i].append(float(r[2])*1000.)
    return rtts

def getrtts_nping_mod(directory,name,from_ip,to_ip):
    rtts= [[] for i in range(10)]
    for i in range(10):
        with open(directory+'/'+name+'_'+from_ip+'_to_'+to_ip+"_"+str(i), "r+") as f:
            for line in f:
                rt = findall(r'packet rtt: (.*?)ms',line)[0]
                rtts[i].append(float(rt)*1000)
        rtts[i] = sorted(rtts[i])
    return rtts
    
def get_conf_int(data):
    x_bar = np.mean(data) 
    s = np.std(data)
    n = len(data)
    z = 1.96 # for a 95% CI

    lower = x_bar - (z * (s/sqrt(n)))
    upper = x_bar + (z * (s/sqrt(n)))
    med = np.median(data)

    return lower, med, upper

def get_mean(data):
    return np.mean(data) 

def heatmap_conf_int(mat, low_mat, high_mat, ax_lab, title="", colbarlab=""):
    fig, ax = plt.subplots()
    mat_min = np.nanmin(low_mat)
    mat_max = np.nanmax(high_mat)
    im = ax.imshow(mat, vmin=mat_min, vmax=mat_max)
    norm = col.Normalize(vmin=mat_min, vmax=mat_max)

    # Show all ticks and label them with the respective list entries
    ax.set_xticks(np.arange(len(ax_lab)))
    ax.set_yticks(np.arange(len(ax_lab)))
    ax.set_xticklabels(ax_lab)
    ax.set_yticklabels(ax_lab)

    # Rotate the tick labels and set their alignment.
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right",
             rotation_mode="anchor")
    
    cbar = ax.figure.colorbar(im, ax=ax)
    
    cbar.ax.set_ylabel(colbarlab, rotation=-90, va="bottom")

    # Loop over data dimensions and create text annotations.
    for i in range(len(ax_lab)):
        for j in range(len(ax_lab)):
            text = ax.text(j, i, mat[i, j],
                           ha="center", va="center", color="w")
            low_conf = ax.plot(j, i+0.25, 'o', color=im.cmap(norm(low_mat[i,j])))
            high_conf = ax.plot(j, i-0.25, 'o', color=im.cmap(norm(high_mat[i,j])))

    ax.set_title(title)
    fig.tight_layout()
    plt.show()
    
def heatmap(mat, ax_lab, title="", colbarlab=""):
    fig, ax = plt.subplots()
    im = ax.imshow(mat)

    # Show all ticks and label them with the respective list entries
    ax.set_xticks(np.arange(len(ax_lab)))
    ax.set_yticks(np.arange(len(ax_lab)))
    ax.set_xticklabels(ax_lab)
    ax.set_yticklabels(ax_lab)

    # Rotate the tick labels and set their alignment.
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right",
             rotation_mode="anchor")
    
    cbar = ax.figure.colorbar(im, ax=ax)
    cbar.ax.set_ylabel(colbarlab, rotation=-90, va="bottom")

    # Loop over data dimensions and create text annotations.
    for i in range(len(ax_lab)):
        for j in range(len(ax_lab)):
            text = ax.text(j, i, mat[i, j],
                           ha="center", va="center", color="w")

    ax.set_title(title)
    fig.tight_layout()
    plt.show()
    
def ind_of(value,arr):
    for j in range(len(arr)):
            if (arr[j] == value or j == len(arr)-1):
                return j
            elif (arr[j] > value):
                return j-0.5
            
def smallest_index(value, arrarr):
    smalls = []
    for i in range(10):
        smalls.append(ind_of(value,arrarr[i]))
    return min(smalls)

def largest_index(value, arrarr):
    larges = []
    for i in range(10):
        larges.append(ind_of(value,arrarr[i]))
    return max(larges)
    
def rtt_cumulative_graph(directory,name,from_ip,to_ip,div,num,hping=False, xlim=None, nping=False):
    fig, ax = plt.subplots()
    if hping:
        rtts= getrtts_hping3(directory,name,from_ip,to_ip)
        for i in range(10):
            rtts[i] = [rtt if rtt < 100000. else np.median(rtts[i]) for rtt in rtts[i]]
            rtts[i] = sorted(rtts[i])   
    elif nping:
        rtts= getrtts_nping_mod(directory,name,from_ip,to_ip)
    else:
        rtts= getrtts(directory,name,from_ip,to_ip)
    avgs = []
    
    for i in range(num):
        avg = np.median([rtts[j][i] for j in range(10)])
        avgs.append(avg)
    values, base = np.histogram(avgs, bins=1000)
    cumulative = np.cumsum(values/float(num))
    ax.plot(base[:-1], cumulative)
    plt.ylabel("Cumulative probability")
    plt.xlabel("RTT (us)")

    minn = int(ceil(avgs[0]/ div)*div)
    maxx = int(floor(avgs[num-1] / div)*div)
    errxs = np.arange(minn,maxx+1,div)
    minsmaxs = [[],[]]
    errys = []
    for i in errxs:
        ind = ind_of(i,avgs)
        errys.append((ind+1)/float(num))
        sml = smallest_index(i, rtts)
        minsmaxs[0].append(abs(ind-sml)/float(num))
        lrg = largest_index(i, rtts)
        minsmaxs[1].append(abs(ind-lrg)/float(num))
    ax.errorbar(errxs, errys, yerr=minsmaxs,linestyle="none")
    if xlim != None:
        ax.set_xlim(xlim)
    plt.show()
    