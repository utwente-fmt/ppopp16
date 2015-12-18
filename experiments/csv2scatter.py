
import sys
import re
import os.path
import time
import datetime
import csv
import numpy as np
import scipy as sp
import scipy.stats
from sets import Set


ALG1     = ""
ALG2     = ""
WORKERS1 = ""
WORKERS2 = ""
allmodels    = Set([])
sortedmodels = []
sortedvalues = []
minspeedup = 99999999.0
maxspeedup = 1.0
mintime = 99999999.0
maxtime = 1.0


def checkfile(file):
    if not (os.path.isfile(file)):
        print "ERROR: cannot find file: {}".format(file)
        sys.exit()


def mean_confidence_interval(data, confidence=0.95):
    if (len(data) == 1):
        return data[0], 0
    a = 1.0*np.array(data)
    n = len(a)
    m, se = np.mean(a), scipy.stats.sem(a)
    h = se * sp.stats.t._ppf((1+confidence)/2., n-1)
    return m, h


def addtodict(dictx, model, time):
    if not model in dictx:
        dictx[model] = []
    dictx[model].append(float(time))


def printstart():
    global ALG1, ALG2, WORKERS1, WORKERS2, minspeedup, maxspeedup, mintime, maxtime
    print "\documentclass{standalone}"
    print ""
    print "\\usepackage{pgfplots}"
    print "\\pgfplotsset{compat=1.9}"
    print ""
    #print "\pgfplotsset{myerr/.append style={mark=.,only marks,error bars/.cd, y dir=both,y explicit, x dir=both,x explicit} }"
    print "\pgfplotsset{myerr/.append style={mark=oplus,only marks} }"
    print ""
    print "\\begin{document}"
    print "\\begin{tikzpicture}"
    print "\\begin{axis}["
    if ALG1 == "tarjan":
        print "    xlabel={Time in sec for Tarjan},"
    elif WORKERS1 > 1:
        print "    xlabel={{Time in sec for {} with {} workers}},".format(ALG1,WORKERS1)
    else:
        print "    xlabel={{Time in sec for {} with {} worker}},".format(ALG1,WORKERS1)
    if WORKERS2 > 1:
        print "    ylabel={{Speedup for {} with {} workers}},".format(ALG2,WORKERS2)
    else:
        print "    ylabel={{Speedup for {} with {} worker}},".format(ALG2,WORKERS2)
    print "    xmin={}, ymin={},".format(mintime*0.8, minspeedup*0.8)
    print "    xmax={}, ymax={},".format(maxtime*1.2, maxspeedup*1.2)
    print "    ymode=log, log basis y={10},"
    print "    xmode=log, log basis x={10},"
    print "    log ticks with fixed point,"
    print "    ytick={0.125,0.25,0.5,1,5,10,20,30,40,50,60,70},"
    print "    y dir=normal,"
    print "    grid style=dotted,"
    print "    grid=both,"
    print "    legend pos=north west"
    print "]"


def printscatter(x, y, errorx, errory):
    #print "\\addplot[myerr] coordinates {{({},{}) +- ({},{})}};".format(x,y,errorx,errory)
    print "\\addplot[myerr] coordinates {{({},{}) +- (0,0)}};".format(x,y)


def printend():
    print "\end{axis}"
    print "\end{tikzpicture}"
    print "\end{document}"


def printscatterplot(dict1, dict2):
    global minspeedup, maxspeedup, mintime, maxtime
    # calculate minspeedup, maxspeedup
    for model in allmodels:
        if (not model in dict1) or (not model in dict2):
            continue
        mean_conf1 = mean_confidence_interval(dict1[model])
        mean_conf2 = mean_confidence_interval(dict2[model])
        speedup = mean_conf1[0]/mean_conf2[0]
        mintime = min(mintime, mean_conf1[0])
        maxtime = max(maxtime, mean_conf1[0])
        minspeedup = min(minspeedup, speedup)
        maxspeedup = max(maxspeedup, speedup)
    printstart();
    geom = []
    for model in allmodels:
        if (not model in dict1) or (not model in dict2):
            continue
        mean_conf1 = mean_confidence_interval(dict1[model])
        mean_conf2 = mean_confidence_interval(dict2[model])
        geom.append(mean_conf1[0] / mean_conf2[0])
        speedup = mean_conf1[0]/mean_conf2[0]
        speedup_conf = (mean_conf1[0] + mean_conf1[1]) / (mean_conf2[0] - mean_conf2[1])
        printscatter(mean_conf1[0],speedup,mean_conf1[1],speedup_conf - speedup)
    printend()


def parsefile(file):
    dict1 = {}
    dict2 = {}
    states = {}
    sccs   = {}
    # check the maximum number of workers
    f = open(file, 'rb')
    reader = csv.DictReader(f)
    for row in reader:
        allmodels.add(row["model"])
        if row["alg"] == ALG1 and row["workers"] == WORKERS1:
            addtodict(dict1, row["model"], row["time"])
        elif row["alg"] == ALG2 and row["workers"] == WORKERS2:
            addtodict(dict2, row["model"], row["time"])
        states[row["model"]] = row["ustates"]
        sccs[row["model"]] = row["sccs"]
    f.close()
    printscatterplot(dict1, dict2)


def main():
    global ALG1, ALG2, WORKERS1, WORKERS2
    N_ARG = len(sys.argv)
    if (N_ARG == 6):
        INFILE   = str(sys.argv[1])
        ALG1     = str(sys.argv[2])
        WORKERS1 = str(sys.argv[3])
        ALG2     = str(sys.argv[4])
        WORKERS2 = str(sys.argv[5])
        checkfile(INFILE)
        parsefile(INFILE)
    else:
        print "ERROR: invalid command"
        print "Usage:"
        print " - {} INFILE ALG1 WORKERS1 ALG2 WORKERS2".format(str(sys.argv[0]))


if __name__ == "__main__":
    main()
