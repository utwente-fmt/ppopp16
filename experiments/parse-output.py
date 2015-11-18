
import sys
import re
import os.path
import time
import datetime
import csv
import shutil

INFILE      = ""
FAILFOLDER  = ""
OUTFILE     = ""
CORRECTFILE = ""
dict        = {}

def exitparser():
    # try to print the contents to an output file
    global dict, INFILE, FAILFOLDER
    counter = 0
    while True:
        counter += 1
        failname = "{}/{}_{}_{}_{}.out".format(FAILFOLDER,dict["model"],dict["alg"],dict["workers"],counter)
        if not (os.path.isfile(failname)):
            break
    shutil.copy2(INFILE, failname)
    # and exit the program
    sys.exit()
    

def checkfile(file):
    if not (os.path.isfile(file)):
        print "ERROR: cannot find file: {}".format(file)
        exitparser()


def parsevar(varname, line, regex):
    pattern = re.compile(regex)
    searchpattern = pattern.search(line)
    if (searchpattern):
        global dict
        if (dict.get(varname)):
            print "ERROR: multiple matches for {}".format(varname)
            exitparser()
        else:
            dict[varname] = searchpattern.group(1)


def parseerror(line, regex):
    pattern = re.compile(regex)
    searchpattern = pattern.search(line)
    if (searchpattern):
        print "ERROR: {}".format(line)
        exitparser()


def parseline(line):
    parseerror(line, r"Error")
    # LTSmin output
    parsevar("time",         line, r"Total exploration time ([\S]+) sec")
    parsevar("tstates",      line, r"Explored ([\S]+) states [\S]+ transitions, fanout: [\S]+")
    parsevar("ttrans",       line, r"Explored [\S]+ states ([\S]+) transitions, fanout: [\S]+")
    parsevar("sccs",         line, r"total scc count: [\s]+ ([\S]+)")
    # Offline output
    parsevar("mstime",       line, r"running_time\(ms\)=([\S]+)") # TODO: divide by 1000 or so
    parsevar("sccs",         line, r"Total # SCCs = ([\S]+)")
    parsevar("tstates",      line, r"total states count: [\s]+ ([\S]+)")
    parsevar("ttrans",       line, r"total transitions count: [\s]+ ([\S]+)")
    parsevar("initstates",   line, r"initial states count: [\s]+ ([\S]+)")
    parsevar("N",            line, r"N = ([\S]+), M = [\S]+")
    parsevar("M",            line, r"N = [\S]+, M = ([\S]+)")
    # both outputs
    parsevar("ustates",      line, r"unique states count: [\s]+ ([\S]+)")
    parsevar("utrans",       line, r"unique transitions count:[\s]+ ([\S]+)")
    parsevar("selfloop",     line, r"self-loop count: [\s]+ ([\S]+)")
    parsevar("claimdead",    line, r"claim dead count: [\s]+ ([\S]+)")
    parsevar("claimfound",   line, r"claim found count: [\s]+ ([\S]+)")
    parsevar("claimsuccess", line, r"claim success count: [\s]+ ([\S]+)")


def afterparse():
    global dict
    # Offline output shows time in ms, we use seconds
    if (dict.get("mstime")):
        sectime = float(dict["mstime"])
        sectime /= 1000
        dict["time"] = str(sectime)
    if not (dict.get("initstates")): dict["initstates"] = "1"
    if (dict["alg"] != "ufscc"):
        if not (dict.get("ustates")):
            if not (dict.get("N")):
                print "ERROR: Cannot find N"
                exitparser()
            dict["ustates"] = dict["N"]
        if not (dict.get("utrans")):
            if not (dict.get("M")):
                print "ERROR: Cannot find M"
                exitparser()
            dict["utrans"] = dict["M"]


def checkitemcorrect(correct, item):
    global dict
    if not (dict.get(item)):
        print "ERROR: Cannot find {}".format(item)
        exitparser()
    if (dict[item] != correct):
        print "ERROR: {} = {} is incorrect (should be {}) ".format(item, dict[item], correct)
        exitparser()


def checkcorrect():
    global dict, CORRECTFILE
    # only check if we have a correct file
    if (os.path.isfile(CORRECTFILE)):
        f = open(CORRECTFILE, 'rb')
        reader = csv.DictReader(f)
        for row in reader:
            if (row["model"] == dict["model"]):
                # check if variables are the same
                checkitemcorrect(row["sccs"], "sccs")
                checkitemcorrect(row["utrans"], "utrans")
                checkitemcorrect(row["ustates"], "ustates")


def parsefile(file):
    f = open(file, 'r')
    for line in f:
        parseline(line)
    f.close()
    afterparse()
    checkcorrect()


def trytoprint(varname):
    global dict
    if (dict.get(varname)):
        return dict.get(varname)
    else:
        if (varname == "time" or 
            varname == "sccs" or 
            varname == "utrans" or 
            varname == "ustates") :
            print "ERROR: cannot find {}".format(varname)
            exitparser()
        if (dict["alg"] != "ufscc"):
            return "-1"
        else:
            print "ERROR: cannot find {}".format(varname)
            exitparser()


def printtofile(outfile):
    # First line of OUTFILE should contain comma-separated info on column names
    global dict
    f = open(outfile, 'r+')
    s = f.readline().strip()
    names = s.split(",")
    output  = ""
    for name in names:
        output += trytoprint(name) + ","
    output = output[:-1] # remove last ","
    f.read() # go to the last line
    f.write("\n"+output) # write the new line
    f.close()


def printtostdout():
    # find longest key name (for formatting)
    global dict
    maxlen = 1
    for varname in dict:
        maxlen = max(maxlen, len(varname))
    # print everything to stdout
    for varname in dict:
        print varname + ":" +  " " * (maxlen+1-len(varname)) + dict[varname]


def addextra():
    # Add timestamp
    global dict
    ts = time.time()
    dict["date"] = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d.%H:%M:%S')


def main():
    global dict, INFILE, OUTFILE, FAILFOLDER, CORRECTFILE
    N_ARG = len(sys.argv)
    if (N_ARG == 6):
        dict["model"]   = str(sys.argv[1])
        dict["alg"]     = str(sys.argv[2])
        dict["workers"] = str(sys.argv[3])
        FAILFOLDER      = str(sys.argv[4])
        INFILE          = str(sys.argv[5])
        checkfile(INFILE)
        parsefile(INFILE)
        addextra()
        printtostdout()
    elif (N_ARG == 7):
        dict["model"]   = str(sys.argv[1])
        dict["alg"]     = str(sys.argv[2])
        dict["workers"] = str(sys.argv[3])
        FAILFOLDER      = str(sys.argv[4])
        INFILE          = str(sys.argv[5])
        OUTFILE         = str(sys.argv[6])
        checkfile(INFILE)
        checkfile(OUTFILE)
        parsefile(INFILE)
        addextra()
        printtofile(OUTFILE)
    else:
        print "ERROR: invalid command"
        print "Usage:"
        print " - python parse_output.py  MODEL  ALG  WORKERS  FAILFOLDER  INFILE           # writes all output to the stdout"
        print " - python parse_output.py  MODEL  ALG  WORKERS  FAILFOLDER  INFILE  OUTFILE  # appends the data to the OUTFILE in the same format used"


if __name__ == "__main__":
    main()
