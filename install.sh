

# Fetch LTSmin from github, configure and build.
git clone https://github.com/vbloemen/ltsmin.git -b vincent3
prefix=`pwd`
cd ltsmin
git submodule update --init
./ltsminreconf
./configure  --prefix="${prefix}"/experiments
make && make install


# Fetch hong-ufscc from github and make.
git clone https://github.com/vbloemen/hong-ufscc.git
cd hong-ufscc
make
mv scc "${prefix}"/experiments



