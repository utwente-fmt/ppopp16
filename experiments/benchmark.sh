
# binaries
BEEM_SCC="dve2lts-mc"
SYNTHETIC_SCC="prom2lts-mc"
OFFLINE_SCC="${HOME}/code/hong/scc-par/scc"

# variables
TIMEOUT_TIME="600s" # 10 minutes timeout
WORKER_LIST="1 2 4 6 8 12 16 24 32 48 64"

# misc fields
BENCHDIR=`pwd`
TMPFILE="${BENCHDIR}/test.out" # Create a temporary file to store the output
FAILFOLDER="${BENCHDIR}/failures"

# input graphs folders
BEEMFOLDER="${BENCHDIR}/graphs/beem"
BEEMSELECTEDFOLDER="${BENCHDIR}/graphs/beem-selected"
OFFLINEFOLDER="${BENCHDIR}/graphs/real-offline"
SYNTHETICFOLDER="${BENCHDIR}/graphs/synthetic"
OFFLINECONSTRUCTEDFOLDER="${BENCHDIR}/graphs/constructed-offline"

# results
RESULTS_BEEM="${BENCHDIR}/results/results-beem.csv"
RESULTS_BEEM_SELECTED="${BENCHDIR}/results/results-beem-selected.csv"
RESULTS_REAL_OFFLINE="${BENCHDIR}/results/results-real-offline.csv"
RESULTS_SYNTHETIC="${BENCHDIR}/results/results-synthetic.csv"
RESULTS_CONSTRUCTED_OFFLINE="${BENCHDIR}/results/results-constructed-offline.csv"

trap "exit" INT #ensures that we can exit this bash program

# create new output file, or append to the exisiting one
create_results() {
    output_file=${1}
    if [ ! -e ${output_file} ]
    then 
        touch ${output_file}
        # Add column info to output CSV
        echo "model,alg,workers,time,date,sccs,ustates,utrans,tstates,ttrans,initstates,selfloop,claimdead,claimfound,claimsuccess" > ${output_file}
    fi
}

# create necessary files
init() {
    touch ${TMPFILE}
    create_results ${RESULTS_BEEM}
    create_results ${RESULTS_BEEM_SELECTED}
    create_results ${RESULTS_REAL_OFFLINE}
    create_results ${RESULTS_SYNTHETIC}
    create_results ${RESULTS_CONSTRUCTED_OFFLINE}
}


# test_beem MODEL ALG WORKERS
# e.g. test_beem at.4.dve ufscc 64
test_beem() {
    model=${1}
    alg=${2}
    workers=${3}
    base=${model%.dve} # without the .dve
    echo "Running ${alg} on ${base} with ${workers} worker(s)"
    timeout ${TIMEOUT_TIME} "${BEEM_SCC}" --strategy=${alg} --threads=${workers} -s28 ${BEEMFOLDER}/${model} &> ${TMPFILE}
    python parse-output.py "${base}" "${alg}" "${workers}" "${FAILFOLDER}" "${TMPFILE}" "${RESULTS_BEEM}"
}


# test_all_beem ALG WORKERS
# e.g. test_all_beem ufscc 64
test_all_beem() {
    alg=${1}
    workers=${2}
    for file in ${BEEMFOLDER}/*.dve
    do
        name=${file##*/} # remove preceding path
        test_beem ${name} ${alg} ${workers}
    done
}



# test_beem_selected MODEL ALG WORKERS
# e.g. test_beem_selected at.4.dve ufscc 64
test_beem_selected() {
    model=${1}
    alg=${2}
    workers=${3}
    base=${model%.dve} # without the .dve
    echo "Running ${alg} on ${base} with ${workers} worker(s)"
    timeout ${TIMEOUT_TIME} "${BEEM_SCC}" --strategy=${alg} --threads=${workers} -s28 ${BEEMFOLDER}/${model} &> ${TMPFILE}
    python parse-output.py "${base}" "${alg}" "${workers}" "${FAILFOLDER}" "${TMPFILE}" "${RESULTS_BEEM_SELECTED}"
}


# test_all_beem_selected ALG WORKERS
# e.g. test_all_beem_selected ufscc 64
test_all_beem_selected() {
    alg=${1}
    workers=${2}
    for file in ${BEEMSELECTEDFOLDER}/*.dve
    do
        name=${file##*/} # remove preceding path
        test_beem_selected ${name} ${alg} ${workers}
    done
}


# test_synthetic MODEL ALG WORKERS
# e.g. test_synthetic L4L4T16.prm.spins ufscc 64
test_synthetic() {
    model=${1}
    alg=${2}
    workers=${3}
    base=${model%.prm.spins} # without the .spins
    echo "Running ${alg} on ${base} with ${workers} worker(s)"
    timeout ${TIMEOUT_TIME} "${SYNTHETIC_SCC}" --strategy=${alg} --threads=${workers} -s28 ${SYNTHETICFOLDER}/${model} &> ${TMPFILE}
    python parse-output.py "${base}" "${alg}" "${workers}" "${FAILFOLDER}" "${TMPFILE}" "${RESULTS_SYNTHETIC}"
}


# test_all_synthetic ALG WORKERS
# e.g. test_all_synthetic ufscc 64
test_all_synthetic() {
    alg=${1}
    workers=${2}
    for file in ${SYNTHETICFOLDER}/*.prm.spins
    do
        name=${file##*/} # remove preceding path
        test_synthetic ${name} ${alg} ${workers}
    done
}


# test_real_offline MODEL ALG WORKERS
# e.g. test_real_offline livej.bin ufscc 64
test_real_offline() {
    model=${1}
    alg=${2}
    if [ "${alg}" = "hong" ]
    then
        algnumber=2
    elif [ "${alg}" = "tarjan" ]
    then
        algnumber=3
    elif [ "${alg}" = "ufscc" ]
    then
        algnumber=5
    fi
    workers=${3}
    base=${model%.bin} # without the .bin
    echo "Running ${alg} (${algnumber}) on ${base} with ${workers} worker(s)"
    timeout ${TIMEOUT_TIME} ${OFFLINE_SCC} ${OFFLINEFOLDER}/${model} ${workers} ${algnumber} &> ${TMPFILE}
    python parse-output.py "${base}" "${alg}" "${workers}" "${FAILFOLDER}" "${TMPFILE}" "${RESULTS_REAL_OFFLINE}" 
}


# test_all_real_offline ALG WORKERS
# e.g. test_all_real_offline ufscc 64
test_all_real_offline() {
    alg=${1}
    workers=${2}
    if [ ! "$(ls -A ${OFFLINEFOLDER})" ]; then
        echo "graphs/real-offline folder is empty"
    else
        for file in ${OFFLINEFOLDER}/*.bin
        do
            name=${file##*/} # remove preceding path
            test_real_offline ${name} ${alg} ${workers}
        done
    fi
}


# test_constructed_offline MODEL ALG WORKERS
# e.g. test_constructed_offline livej.bin ufscc 64
test_constructed_offline() {
    model=${1}
    alg=${2}
    if [ "${alg}" = "hong" ]
    then
        algnumber=2
    elif [ "${alg}" = "tarjan" ]
    then
        algnumber=3
    elif [ "${alg}" = "ufscc" ]
    then
        algnumber=5
    fi
    workers=${3}
    base=${model%.bin} # without the .bin
    echo "Running ${alg} (${algnumber}) on ${base} with ${workers} worker(s)"
    timeout ${TIMEOUT_TIME} ${OFFLINE_SCC} ${OFFLINECONSTRUCTEDFOLDER}/${model} ${workers} ${algnumber} &> ${TMPFILE}
    python parse-output.py "${base}" "${alg}" "${workers}" "${FAILFOLDER}" "${TMPFILE}" "${RESULTS_CONSTRUCTED_OFFLINE}" 
}


# test_all_constructed_offline ALG WORKERS
# e.g. test_all_constructed_offline ufscc 64
test_all_constructed_offline() {
    alg=${1}
    workers=${2}
    if [ ! "$(ls -A ${OFFLINECONSTRUCTEDFOLDER})" ]; then
        echo "graphs/constructed-offline folder is empty"
    else
        for file in ${OFFLINECONSTRUCTEDFOLDER}/*.bin
        do
            name=${file##*/} # remove preceding path
            test_constructed_offline ${name} ${alg} ${workers}
        done
    fi
}


# only tests for 1 and 64 workers due to number of graphs
do_beem_tests() {
    test_all_beem tarjan 1
    test_all_beem ufscc 1
    test_all_beem renault 1
    test_all_beem ufscc 64
    test_all_beem renault 64
}


do_beem_selected_tests() {
    test_all_beem_selected tarjan 1
    for workers in `echo ${WORKER_LIST}`
    do
        test_all_beem_selected ufscc "${workers}"
        test_all_beem_selected renault "${workers}"
    done
}


do_synthetic_tests() {
    test_all_synthetic tarjan 1
    for workers in `echo ${WORKER_LIST}`
    do
        test_all_synthetic ufscc "${workers}"
        test_all_synthetic renault "${workers}"
    done
}


do_real_offline_tests() {
    test_all_real_offline tarjan 1
    for workers in `echo ${WORKER_LIST}`
    do
        test_all_real_offline ufscc "${workers}"
        test_all_real_offline hong "${workers}"
    done
}


do_constructed_offline_tests() {
    test_all_constructed_offline tarjan 1
    for workers in `echo ${WORKER_LIST}`
    do
        test_all_constructed_offline ufscc "${workers}"
        test_all_constructed_offline hong "${workers}"
    done
}


# do_all_experiments ITERATIONS
do_all_experiments() {
    iterations=${1}
    for experiments in `seq 1 ${iterations}`
    do
        do_beem_tests
        do_beem_selected_tests
        do_synthetic_tests
        do_real_offline_tests
        do_constructed_offline_tests
    done
}



# initialize
init


############################################################




# performs all experiments N times
do_all_experiments 1



############################################################



# cleanup
rm "${TMPFILE}"