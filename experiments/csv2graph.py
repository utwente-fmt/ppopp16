import sys
import re
import os.path
import time
import datetime
import csv
import numpy as np
import scipy as sp
import scipy.stats


results      = {}
failures     = {}
output       = {}
mintime      = sys.float_info.max
maxtime      = -1
minspeedup   = sys.float_info.max
maxspeedup   = -1
maxworkers   = 1
IS_SPEEDUP   = False


def checkfile(file):
    if not (os.path.isfile(file)):
        print "ERROR: cannot find file: {}".format(file)
        sys.exit()


def mean_confidence_interval(data, confidence=0.95):
    global IS_SPEEDUP
    if (len(data) == 1):
        return data[0], 0
    a = 1.0*np.array(data)
    n = len(a)
    m, se = np.mean(a), scipy.stats.sem(a)
    h = se * sp.stats.t._ppf((1+confidence)/2., n-1)
    if IS_SPEEDUP:
        return m, m-h, m+h
    else:
        return m, -h, h


def addtoresults(key, value):
    global results
    if not key in results:
        results[key] = [value]
    else:
        results[key].append(value)


def addtooutput(key, value):
    global output
    if not key in output:
        output[key] = [value]
    else:
        output[key].append(value)


def addfailure(row):
    global failures
    key = "{}-{}-{}".format(row["model"], row["alg"], row["workers"])
    if not key in failures:
        failures[key] = 1
    else:
        failures[key] += 1


def model_alg_time(reader, model, alg):
    global results, mintime, maxtime
    results.clear()
    for row in reader:
        if (row["model"] == model and row["alg"] == alg):
            if (row["time"] != "ERROR"):
                addtoresults(int(row["workers"]), float(row["time"]))
            else:
                addfailure(row)
    for key in sorted(results):
        mean_conf = mean_confidence_interval(results[key])
        maxtime = max(maxtime, mean_conf[0])
        mintime = max(min(mintime, mean_conf[0]), 0.1)
        addtooutput(alg, (key, mean_conf[0], mean_conf[1], mean_conf[2]))
        if (alg == "tarjan"):
            addtooutput(alg, (maxworkers, mean_conf[0], mean_conf[1], mean_conf[2]))


def parse_model_time(file, model):
    f = open(file, 'rb')
    reader = csv.DictReader(f)
    # get all algorithms
    algs = set()
    for row in reader:
        algs.add(row["alg"])
    for alg in algs:
        f.seek(0)
        model_alg_time(reader, model, alg)
    f.close()


def parse_time(file):
    # get all models
    f = open(file, 'rb')
    reader = csv.DictReader(f)
    models = set()
    for row in reader:
        models.add(row["model"])
    f.close()
    for model in models:
        parse_model_time(file, model)


def parsefile(file, model):
    #parse_time(file)
    # check the maximum number of workers
    f = open(file, 'rb')
    reader = csv.DictReader(f)
    global maxworkers
    for row in reader:
        maxworkers = max(maxworkers, int(row["workers"]))
    f.close()
    parse_model_time(file, model)


def printitem(item):
    print  "({},{}) -= (0,{}) += (0,{})".format(
        str(item[0]).ljust(2),
        str(item[1]).ljust(14),
        str(item[2]),
        str(item[3]))


def printtime():
    global output, mintime, maxtime

    print "\\documentclass{standalone}"
    print ""
    print "\\usepackage{pgfplots}"
    print ""
    print "\\definecolor{darkgreen}{RGB}{0,104,0}"
    print "\\renewcommand{\\familydefault}{\\sfdefault}"
    print "\\pgfplotsset{compat=1.9}"
    print ""
    print "\\newcommand{\DASHEDPLOT}{\\addplot[color=darkgray, mark=none, dashed]}"
    print "\\newcommand{\TARJANPLOT}{\\addplot[color=darkgreen, mark=none, thick,",
    print "error bars/.cd, y dir=both, y explicit, error bar style={thick}, error mark options={rotate=90,thick}]}"
    print "\\newcommand{\TARJANPLOT} {\\addplot[color=darkgreen, mark=none, thick,",
    print "error bars/.cd, y dir=both, y explicit, error bar style={thick}, error mark options={rotate=90,thick}]}"
    print "\\newcommand{\RENAULTPLOT}{\\addplot[color=red, mark=triangle*, thick,",
    print "error bars/.cd, y dir=both, y explicit, error bar style={thick}, error mark options={rotate=90,thick}]}"
    print "\\newcommand{\UFPLOT}     {\\addplot[color=blue, mark=oplus*, thick,",
    print "error bars/.cd, y dir=both, y explicit, error bar style={thick}, error mark options={rotate=90,thick}]}"
    print ""
    print ""
    print "\\begin{document}"
    print "\\begin{tikzpicture}"
    print "\\begin{axis}["
    print "    xlabel={Number of workers},"
    print "    xmin=0.7, xmax=90.5,"
    print "    ymin={}, ymax={},".format(mintime/2.0, maxtime*2.0)
    print "    ymode=log, log basis y={2},"
    print "    xmode=log, log basis x={2},"
    print "    log ticks with fixed point,"
    print "    ylabel={Time used (sec)},"
    print "    y dir=normal,"
    print "    grid style=dashed,"
    print "    grid=both,"
    print "    legend pos=outer north east"
    print "]"
    print ""
    if ("tarjan" in output):
        print "\\TARJANPLOT"
        print "coordinates {"
        for item in output["tarjan"]:
            printitem(item)
        print "};"
        print "\\addlegendentry{{Tarjan}}"
        print ""
    if ("renault" in output):
        print "\\RENAULTPLOT"
        print "coordinates {"
        for item in output["renault"]:
            printitem(item)
        print "};"
        print "\\addlegendentry{{Renault}}"
        print ""
    if ("hong" in output):
        print "\\RENAULTPLOT"
        print "coordinates {"
        for item in output["hong"]:
            printitem(item)
        print "};"
        print "\\addlegendentry{{Renault}}"
        print ""
    if ("ufscc" in output):
        print "\\UFPLOT"
        print "coordinates {"
        for item in output["ufscc"]:
            printitem(item)
        print "};"
        print "\\addlegendentry{{UFSCC}}"
        print ""
    print "\\end{axis}"
    print "\\end{tikzpicture}"
    print "\\end{document}"


def calculatespeedup(basis="tarjan", basisworkers="1"):
    global output, minspeedup, maxspeedup
    # in case we want to compare to sequential algorithms
    if (basisworkers == "1"):
        # find the base time
        basetime = 1
        for item in output[basis]:
            if (item[0] == 1):
                basetime = item[1]
        # update every value in output
        for alg in output:
            alglist = []
            for item in output[alg]:
                average = basetime / item[1]
                minconf = basetime / item[3]
                maxconf = basetime / item[2]
                alglist.append((item[0],  average, average - minconf, maxconf-average))
                maxspeedup = max(maxspeedup, basetime / item[1])
                minspeedup = min(minspeedup, basetime / item[1])
            output[alg] = alglist
    # in case we want to compare with the same number of workers
    else:
        # find the base times
        basetime = {}
        for item in output[basis]:
            basetime[item[0]] = item[1]

        # update every value in output
        for alg in output:
            if (alg == "tarjan"):
                continue
            alglist = []
            for item in output[alg]:
                alglist.append((item[0], basetime[item[0]] / item[1] , 0, 0))
                maxspeedup = max(maxspeedup, basetime[item[0]] / item[1])
                minspeedup = min(minspeedup, basetime[item[0]] / item[1])
            output[alg] = alglist


def printspeedup(basis="tarjan", basisworkers="1"):
    global output, minspeedup, maxspeedup
    calculatespeedup(basis, basisworkers)
    print "\\documentclass{standalone}"
    print ""
    print "\\usepackage{figstyle}"
    print ""
    print "\\begin{document}"
    print "\\begin{tikzpicture}"
    print "\\begin{axis}["
    print "    xlabel={Number of workers},"
    print "    xmin=0.7, xmax=90.5,"
    print "    ymin={}, ymax={},".format(minspeedup/2.0, maxspeedup*2.0)
    print "    ymode=log, log basis y={2},"
    print "    xmode=log, log basis x={2},"
    print "    log ticks with fixed point,"
    if basis == "tarjan":
        print "    ylabel={Speedup vs. Tarjan},"
    else:
        print "    ylabel={Speedup vs. {" + basis + "$_{\\mbox{" + basisworkers + "}}$}},"
    print "    y dir=normal,"
    print "    grid style=dashed,"
    print "    grid=both,"
    print "    legend pos=outer north east"
    print "]"
    print ""
    print "\\TARJANPLOT"
    print "coordinates {"
    # find the base time
    printitem((1,1,0,0))
    printitem((maxworkers,1,0,0))
    print "};"
    if basis == "tarjan":
        print "\\addlegendentry{Tarjan}"
    else:
        print "\\addlegendentry{{" + basis + "$_{\\mbox{" + basisworkers + "}}$}}"
    print ""
    if ( ("renault" != basis or basisworkers == "1") and "renault" in output):
        print "\\RENAULTPLOT"
        print "coordinates {"
        for item in output["renault"]:
            printitem(item)
        print "};"
        print "\\addlegendentry{{Renault}}"
        print ""
    if ( ("hong" != basis or basisworkers == "1") and "hong" in output):
        print "\\RENAULTPLOT"
        print "coordinates {"
        for item in output["hong"]:
            printitem(item)
        print "};"
        print "\\addlegendentry{{Hong}}"
        print ""
    if ( ("ufscc" != basis or basisworkers == "1") and "ufscc" in output):
        print "\\UFPLOT"
        print "coordinates {"
        for item in output["ufscc"]:
            printitem(item)
        print "};"
        print "\\addlegendentry{{UFSCC}}"
        print ""
    if (basisworkers == "1"):
        print "\\DASHEDPLOT"
        print "coordinates {"
        printitem((1,1,0,0))
        printitem((maxspeedup*2,maxspeedup*2,0,0))
        print "};"
        print ""
    print "\\end{axis}"
    print "\\end{tikzpicture}"
    print "\\end{document}"


def main():
    global IS_SPEEDUP
    N_ARG = len(sys.argv)
    if (N_ARG == 3):
        IS_SPEEDUP = False
        INFILE  = str(sys.argv[1])
        MODEL   = str(sys.argv[2])
        checkfile(INFILE)
        parsefile(INFILE, MODEL)
        printtime()
    elif (N_ARG == 5):
        IS_SPEEDUP = True
        INFILE  = str(sys.argv[1])
        MODEL   = str(sys.argv[2])
        ALG     = str(sys.argv[3])
        WORKERS = str(sys.argv[4])
        checkfile(INFILE)
        parsefile(INFILE, MODEL)
        printspeedup(ALG,WORKERS)
    else:
        print "ERROR: invalid command"
        print "Usage:"
        print " - {} INFILE  MODEL          # time usage".format(str(sys.argv[0]))
        print " - {} INFILE  MODEL  ALG  N  # Speedup vs ALG_N".format(str(sys.argv[0]))


if __name__ == "__main__":
    main()
