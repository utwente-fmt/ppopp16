#!/bin/bash

# update PATH
prefix=`pwd`
mkdir install
installdir="${prefix}"/install
export PATH=$PATH:"${installdir}":"${installdir}"/bin

# install patched DiVinE
cd "${prefix}"
git clone https://github.com/utwente-fmt/divine2.git
cd divine2
mkdir _build && cd _build
cmake .. -DGUI=OFF -DRX_PATH= -DCMAKE_INSTALL_PREFIX="${installdir}" -DMURPHI=OFF
make
make install

# Fetch LTSmin from github, configure and build.
cd "${prefix}"
git clone https://github.com/vbloemen/ltsmin.git -b vincent3
cd ltsmin
git submodule update --init
./ltsminreconf
./configure  --prefix="${installdir}"
make && make install

# Fetch hong-ufscc from github and make.
cd "${prefix}"
git clone https://github.com/vbloemen/hong-ufscc.git
cd hong-ufscc
make
cp scc "${installdir}"

cd "${prefix}"


