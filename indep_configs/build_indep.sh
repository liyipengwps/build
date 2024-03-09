#!/bin/bash
# Copyright (c) 2024 Huawei Device Co., Ltd.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

echo $1 $2
starttime=`date +'%Y-%m-%d %H:%M:%S'`
VARIANTS="default"
if [ -n "$3" ]; then
  VARIANTS=$3
fi
rm -rf out
rm -rf .gn
rm -rf binarys

kernel_path="kernel/linux/patches"
if [ -d "$kernel_path" ]; then
    echo "kernel_path already exist."
else
    echo "kernel_path not exist."
    mkdir -p kernel/linux
    ln -s $1/binarys/kernel/linux/innerapis/patches kernel/linux/patches
fi

mkdir -p out/$VARIANTS
mkdir -p out/preloader
mkdir -p out/$VARIANTS/build_configs/parts_info
cp -rf build/indep_configs/mapping/component_mapping.json out/$VARIANTS/build_configs

mkdir -p out/$VARIANTS/obj/binarys/third_party/musl/usr/include/arm-linux-ohos
mkdir -p out/$VARIANTS/obj/binarys/third_party/musl/usr/lib/arm-linux-ohos
cp -rf $1/binarys/third_party/musl/innerapis/includes/* out/$VARIANTS/obj/binarys/third_party/musl/usr/include/arm-linux-ohos
cp -rf $1/binarys/third_party/musl/innerapis/libs/* out/$VARIANTS/obj/binarys/third_party/musl/usr/lib/arm-linux-ohos

ln -s build/indep_configs/dotfile.gn .gn
ln -s $1/binarys binarys

export SOURCE_ROOT_DIR="$PWD"

# set python3
HOST_DIR="linux-x86"
HOST_OS="linux"
NODE_PLATFORM="linux-x64"

PYTHON3_DIR=${SOURCE_ROOT_DIR}/prebuilts/python/${HOST_DIR}/current/
PYTHON3=${PYTHON3_DIR}/bin/python3
PYTHON=${PYTHON3_DIR}/bin/python
export PATH=${SOURCE_ROOT_DIR}/prebuilts/build-tools/${HOST_DIR}/bin:${PYTHON3_DIR}/bin:$PATH

${PYTHON3} ${SOURCE_ROOT_DIR}/build/indep_configs/scripts/generate_components.py -hp $1 -sp $2 -v ${VARIANTS} -rp ${SOURCE_ROOT_DIR}
${PYTHON3} ${SOURCE_ROOT_DIR}/build/indep_configs/scripts/generate_target_build_gn.py -p $2 -rp ${SOURCE_ROOT_DIR}
${PYTHON3} ${SOURCE_ROOT_DIR}/build/indep_configs/scripts/variants_info_handler.py -rp ${SOURCE_ROOT_DIR} -v ${VARIANTS}

prebuilts/build-tools/linux-x86/bin/gn gen --args="ohos_indep_compiler_enable=true product_name=\"$VARIANTS\"" -C out/$VARIANTS
prebuilts/build-tools/linux-x86/bin/ninja -C out/$VARIANTS

endtime=`date +'%Y-%m-%d %H:%M:%S'`
start_seconds=$(date --date="$starttime" +%s);
end_seconds=$(date --date="$endtime" +%s);
echo "本次运行时间： "$((end_seconds-start_seconds))"s"
exit 0