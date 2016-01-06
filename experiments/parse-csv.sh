
FILE="synthetic"
## create the speedup graph for a given model
#python csv2graph.py results-paper/results-beem.csv bakery.6 tarjan 1 > tmp.tex

## create the time graph for a given model
#python csv2graph.py results-paper/results-beem.csv sorter.3 > tmp.tex

## create a table of the results
#python csv2table.py results-paper/results-beem-selected.csv > tmp.tex

## create a table of the memory usage (re-exploration)
python csv2memtable.py results-paper/results-${FILE}.csv > ${FILE}-memtable.tex

# create a scatterplot of the results
#python csv2scatter.py results-paper/results-beem.csv tarjan 1 ufscc 64 > tmp.tex

## compile the latex file
pdflatex -synctex=1 -interaction=nonstopmode ${FILE}-memtable.tex ;    

