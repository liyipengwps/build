#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2021 Huawei Device Co., Ltd.
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

import os
import sys
import subprocess


def run_cmd(cmd: str):
    res = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE)
    sout, serr = res.communicate()

    return res.pid, res.returncode, sout, serr


def check_darwin_system() -> int:
    check_system_cmd = "uname -s"
    res = run_cmd(check_system_cmd)
    if res[1] == 0 and res[2] != "":
        if "Darwin" in res[2].strip().decode():
            print("system is darwin")

    return 0


def check_cpu() -> int:
    check_host_cpu_cmd = "sysctl machdep.cpu.brand_string"
    res = run_cmd(check_host_cpu_cmd)
    if res[1] == 0 and res[2] != "":
        host_cpu = res[2].strip().decode().split("brand_string:")[-1]
        host_cpu_list = ['M1', 'M2', 'M3']
        for host_cpu_num in host_cpu_list:
            if host_cpu_num in host_cpu:
                print("host cpu is", host_cpu_num)
                break

    return 0


def main():
    if sys.argv[1] == "cpu":
        return check_cpu()
    elif sys.argv[1] == "system":
        return check_darwin_system()
    else:
        return 0

if __name__ == '__main__':
    sys.exit(main())
