
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


allmodels    = Set([])
sortedmodels = []
sortedvalues = []


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


def sortmodels(seq):
    # sort models on values
    changed = True
    while changed:
        changed = False
        for i in xrange(len(seq) - 1):
            if seq[i] > seq[i+1]:
                seq[i], seq[i+1] = seq[i+1], seq[i]
                sortedmodels[i], sortedmodels[i+1] = sortedmodels[i+1], sortedmodels[i]
                changed = True


def parsefile(file):
    tarjan    = {}
    ufscc1    = {}
    other     = {}
    ufscc64   = {}
    states    = {}
    trans     = {}
    sccs      = {}
    otheralg = "???"
    otheralgt = "???"
    #parse_time(file)
    # check the maximum number of workers
    f = open(file, 'rb')
    reader = csv.DictReader(f)
    for row in reader:
        allmodels.add(row["model"])
        states[row["model"]] = row["ustates"]
        trans[row["model"]]  = row["utrans"]
        sccs[row["model"]]   = row["sccs"]
        if row["alg"] == "tarjan"  and row["workers"] == "1":   addtodict(tarjan, row["model"], row["time"])
        if row["alg"] == "ufscc"   and row["workers"] == "1":   addtodict(ufscc1, row["model"], row["time"])
        if row["alg"] == "ufscc"   and row["workers"] == "64":  addtodict(ufscc64, row["model"], row["time"])
        if row["alg"] == "renault" and row["workers"] == "64":  
            otheralg = "renault"
            otheralgt = "Renault"
            addtodict(other, row["model"], row["time"])
        if row["alg"] == "hong"    and row["workers"] == "64":  
            otheralg = "hong"
            otheralgt = "Hong"
            addtodict(other, row["model"], row["time"])
    f.close()
    for model in allmodels:
        if not model in tarjan:  tarjan[model]  = [100]
        if not model in ufscc1:  ufscc1[model]  = [100]
        if not model in other:   other[model]   = [100]
        if not model in ufscc64: ufscc64[model] = [100]
    #selected_models = ["bakery.6", "cambridge.6", "leader_filters.7", "lup.3", "resistance.1", "sorter.3"]
    #selected_models = ["leader_filters.7", "bakery.6", "cambridge.6","lup.3", "resistance.1", "sorter.3"]
    #selected_models = ["L4L4T16", "L350L350T4", "L1750L1750T1", "Li10Lo200", "Li50Lo40", "Li200Lo10"]
    # sort models on speedup vs Tarjan
    for model in allmodels:
        sortedmodels.append(model)
        time1 = mean_confidence_interval(tarjan[model])[0]
        time2 = mean_confidence_interval(ufscc64[model])[0]
        speedup = time1 / time2
        sortedvalues.append(-speedup)
    sortmodels(sortedvalues)
    print "\documentclass{standalone}"
    print ""
    print "\\begin{document}"
    print "\\begin{tabular}{l|rrr|rr}"
    print "\\hline"
    print " & \multicolumn{3}{c|}{\\bf execution time (s)} & \multicolumn{2}{c}{\\bf UFSCC-64 speedup vs} \\\\"
    print " {{\\bf graph}} & ".format()
    print " {{\\bf Tarjan}} & {{\\bf {}-64}} & {{\\bf UFSCC-64}} &".format(otheralgt)
    print " {{\\bf Tarjan}} & {{\\bf {}-64}} \\\\".format(otheralgt)
    print "\hline"
    arrr = []
    for model in sortedmodels:
        tarjant  = mean_confidence_interval(tarjan[model])
        ufscc1t  = mean_confidence_interval(ufscc1[model])
        othert   = mean_confidence_interval(other[model])
        ufscc64t = mean_confidence_interval(ufscc64[model])
        # speedup
        starjan = tarjant[0] / ufscc64t[0]
        sufscc  = ufscc1t[0] / ufscc64t[0]
        sother  = othert[0] / ufscc64t[0]
        # formatted info
        pmodel    = model.replace("_","\_")
        pstates   = "{:,}".format(int(states[model]))
        ptrans    = "{:,}".format(int(trans[model]))
        psccs     = "{:,}".format(int(sccs[model]))
        ptarjant  = "{0:.3f}".format(tarjant[0])
        pufscc1t  = "{0:.3f}".format(ufscc1t[0])
        pothert   = "{0:.3f}".format(othert[0])
        pufscc64t = "{0:.3f}".format(ufscc64t[0])
        pstarjan  = "{0:.3f}".format(starjan)
        psufscc   = "{0:.3f}".format(sufscc)
        psother   = "{0:.3f}".format(sother)
        if other[model][0] == 100:
            pothert = " - "
            psother = " - "
        print "{{\\tt {}}} & ".format(pmodel)
        print "  {{\\tt {}}} & {{\\tt {}}} & {{\\tt {}}} & ".format(ptarjant,pothert,pufscc64t)
        print "  {{\\tt {}}} & {{\\tt {}}} \\\\".format(pstarjan,psother)
        arrr.append(starjan)
    print "\\hline"
    print "\end{tabular}"
    print "\end{document}"


def main():
    global ALG1, ALG2, WORKERS1, WORKERS2
    N_ARG = len(sys.argv)
    if (N_ARG == 2):
        INFILE   = str(sys.argv[1])
        checkfile(INFILE)
        parsefile(INFILE)
    else:
        print "ERROR: invalid command"
        print "Usage:"
        print " - {} INFILE                 # print table".format(str(sys.argv[0]))


if __name__ == "__main__":
    main()
