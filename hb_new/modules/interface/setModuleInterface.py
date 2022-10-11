#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# Copyright (c) 2020 Huawei Device Co., Ltd.
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
#

from abc import abstractmethod

from modules.interface.moduleInterface import ModuleInterface
from resolver.interface.argsResolver import ArgsResolver
from services.interface.menuInterface import MenuInterface


class SetModuleInterface(ModuleInterface):

    def __init__(self, args_dict: dict, argsResolver: ArgsResolver, menu: MenuInterface):
        super().__init__(args_dict, argsResolver)
        self._menu = menu

    @property
    def menu(self):
        return self._menu

    @abstractmethod
    def set_product(self):
        pass

    @abstractmethod
    def set_parameter(self):
        pass

    def run(self):
        if not self.args_dict['all'].argValue:
            self.set_product()
        self.set_parameter()
