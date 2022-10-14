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
from util.ioUtil import IoUtil
from util.preloader.parse_vendor_product_config import get_vendor_parts_list
from containers.status import throw_exception

class Outputs:

    def __init__(self, output_dir):
        self.__post_init__(output_dir)

    def __post_init__(self, output_dir):
        self.build_prop = os.path.join(output_dir, 'build.prop')
        self.build_config_json = os.path.join(output_dir, 'build_config.json')
        self.parts_json = os.path.join(output_dir, 'parts.json')
        self.parts_config_json = os.path.join(output_dir, 'parts_config.json')
        self.build_gnargs_prop = os.path.join(output_dir, 'build_gnargs.prop')
        self.features_json = os.path.join(output_dir, 'features.json')
        self.syscap_json = os.path.join(output_dir, 'syscap.json')
        self.exclusion_modules_json = os.path.join(output_dir,
                                                   'exclusion_modules.json')
        self.subsystem_config_json = os.path.join(output_dir,
                                                  'subsystem_config.json')
        self.platforms_build = os.path.join(output_dir, 'platforms.build')
        self.systemcapability_json = os.path.join(output_dir, 'SystemCapability.json')


class Dirs:

    def __init__(self, config):
        self.__post_init__(config)

    def __post_init__(self, config):
        self.source_root_dir = config.root_path
        self.built_in_product_dir = config.built_in_product_path
        self.productdefine_dir = os.path.join(self.source_root_dir, 'productdefine/common')
        self.built_in_device_dir = config.built_in_device_path
        self.built_in_base_dir = os.path.join(self.productdefine_dir, 'base')

        # Configs of vendor specified products are stored in ${vendor_dir} directory.
        self.vendor_dir = config.vendor_path
        # Configs of device specified products are stored in ${device_dir} directory.
        self.device_dir = os.path.join(config.root_path, 'device')

        self.subsystem_config_json = os.path.join(config.root_path, config.subsystem_config_json)
        self.lite_components_dir = os.path.join(config.root_path, 'build/lite/components')

        self.preloader_output_dir = os.path.join(config.root_path, 'out/preloader', config.product)


class Product():

    def __init__(self, product_name, config_dirs, config_json):
        self._name = product_name
        self._dirs = config_dirs
        self._device = None
        self._config = {}
        self._build_vars = {}
        self._parts = {}
        self._syscap_info = {}
        self._parsed = False
        self._config_file = config_json

    def _sanitize(self, config):
        if config and self._name != config.get('product_name'):
            raise Exception(
                "product name configuration incorrect for '{}'".format(
                    self._name))

    @throw_exception
    def _get_base_parts(self, base_config_dir, os_level):
        system_base_config_file = os.path.join(base_config_dir,
                                               '{}_system.json'.format(os_level))
        if not os.path.exists(system_base_config_file):
            raise Exception("product configuration '{}' doesn't exist.".format(
                system_base_config_file))
        return IoUtil.read_json_file(system_base_config_file)

    def _get_inherit_parts(self, inherit, source_root_dir):
        inherit_parts = {}
        for _config in inherit:
            _file = os.path.join(source_root_dir, _config)
            _info = IoUtil.read_json_file(_file)
            parts = _info.get('parts')
            if parts:
                inherit_parts.update(parts)
            else:
                inherit_parts.update(get_vendor_parts_list(_info))
        return inherit_parts

    def _get_sys_relate_parts(self, system_component_info, _parts, source_root_dir):
        _info = IoUtil.read_json_file(os.path.join(source_root_dir, system_component_info))
        ret = {}
        parts = _info.get('parts')
        if not parts:
            parts = get_vendor_parts_list(_info)
        for part, featrue in parts.items():
            if not _parts.get(part):
                ret[part] = featrue
        return ret

    def _get_product_specific_parts(self):
        part_name = 'product_{}'.format(self._name)
        subsystem_name = part_name
        info = {}
        info['{}:{}'.format(subsystem_name, part_name)] = {}
        return info

    def _get_product_specific_subsystem(self):
        info = {}
        self._do_parse()
        subsystem_name = 'product_{}'.format(self._name)
        if self._get_product_build_path():
            info[subsystem_name] = {
                'name': subsystem_name,
                'path': self._get_product_build_path()
            }
        return info

    def _get_product_build_path(self):
        return self._config.get('product_build_path')

    def _get_parts_and_build_vars(self):
        self._config = IoUtil.read_json_file(self._config_file)
        version = self._config.get('version', '3.0')
        self._update_parts(self._config, version)
        self._update_build_vars(self._config, version)
        return self._parts, self._build_vars

    def _get_device(self):
        self._do_parse()
        return self._device

    def _remove_excluded_components(self):
        items_to_remove = []
        for part, val in self._parts.items():
            if "exclude" in val and val["exclude"] == "true":
                items_to_remove.append(part)
        for item in items_to_remove:
            del self._parts[item]

    def _do_parse(self):
        self._config = IoUtil.read_json_file(self._config_file)
        version = self._config.get('version', '3.0')
        product_name = self._config.get('product_name')
        if product_name == None:
            product_name = ""
        os_level = self._config.get('type')
        if os_level == None:
            os_level = ""
        api_version = self._config.get('api_version')
        if api_version == None:
            api_version = 0
        manufacturer_id = self._config.get('manufacturer_id')
        if manufacturer_id == None:
            manufacturer_id = 0
        
        self._syscap_info = {'product': product_name, 'api_version': api_version,
                             'system_type': os_level, 'manufacturer_id': manufacturer_id}

        self._sanitize(self._config)
        self._update_device(self._config, version)
        self._update_parts(self._config, version)
        self._update_build_vars(self._config, version)
        if version == '3.0':
            if os.path.dirname(self._config_file) != self._dirs.built_in_product_dir and not hasattr(self._config,
                                                                                                     'product_build_path'):
                self._config['product_build_path'] = os.path.relpath(os.path.dirname(self._config_file),
                                                                     self._dirs.source_root_dir)
        self._remove_excluded_components()
        self._parsed = True

    # Generate build_info needed for V3 configuration
    def _get_device_info(self, config):
        # NOTE:
        # Product_name, device_company are necessary for
        # config.json, DON NOT use .get to replace []
        device_info = {
            'device_name': config['board'],
            'device_company': config['device_company']
        }
        if config.get('target_os'):
            device_info['target_os'] = config.get('target_os')
        else:
            device_info['target_os'] = 'ohos'
        if config.get('target_cpu'):
            device_info['target_cpu'] = config['target_cpu']
        else:
            # Target cpu is used to set default toolchain for standard system.
            print(
                "The target_cpu needs to be specified, default target_cpu=arm")
            device_info['target_cpu'] = 'arm'
        if config.get('kernel_version'):
            device_info['kernel_version'] = config.get('kernel_version')
        if config.get('device_build_path'):
            device_info['device_build_path'] = config.get('device_build_path')
        else:
            device_build_path = os.path.join(self._dirs.device_dir,
                                             config['device_company'],
                                             config['board'])
            if not os.path.exists(device_build_path):
                device_build_path = os.path.join(self._dirs.device_dir,
                                                 'board',
                                                 config['device_company'],
                                                 config['board'])
            device_info['device_build_path'] = device_build_path
        return device_info

    # Update the _build_vars based on the product configuration in the vendor warehouse
    def _update_build_vars(self, config, version):
        build_vars = {}
        if version == "1.0":
            build_vars = {"os_level": 'large'}
        else:
            if version == "2.0":
                build_vars['os_level'] = config.get("type", "standard")
                device_name = config.get('product_device')
                if device_name:
                    build_vars['device_name'] = device_name
                else:
                    build_vars['device_name'] = ''
                build_vars['product_company'] = config.get('product_company')
            else:
                build_vars['os_level'] = config.get('type', 'mini')
                build_vars['device_name'] = config.get('board')
                if config.get('product_company'):
                    build_vars['product_company'] = config.get('product_company')
                elif os.path.dirname(self._config_file) != self._dirs.built_in_product_dir:
                    relpath = os.path.relpath(self._config_file, self._dirs.vendor_dir)
                    build_vars['product_company'] = relpath.split('/')[0]
                else:
                    build_vars['product_company'] = config.get('device_company')
            build_vars['product_name'] = config.get('product_name')
            if 'enable_ramdisk' in config:
                build_vars['enable_ramdisk'] = config.get('enable_ramdisk')
            if 'build_selinux' in config:
                build_vars['build_selinux'] = config.get('build_selinux')
            if 'build_seccomp' in config:
                build_vars['build_seccomp'] = config.get('build_seccomp')
            if 'support_jsapi' in config:
                build_vars['support_jsapi'] = config.get('support_jsapi')
        self._build_vars = build_vars

    # Update the _device based on the product configuration in the vendor warehouse
    def _update_device(self, config, version):
        if version == "2.0":
            device_name = config.get('product_device')
            if device_name:
                self._device = _MyDevice(device_name, self._dirs)
        else:
            device_name = config.get('board')
            if device_name:
                device_info = self._get_device_info(config)
                self._device = _MyDevice(device_name, self._dirs, device_info)

    # Update the _parts based on the product configuration in the vendor warehouse
    def _update_parts(self, config, version):
        if version == "1.0":
            _parts = {}
            self._parts = _parts
        else:
            # 1. inherit parts information from base config
            if version == "2.0":
                os_level = config.get("type", "standard")
            else:
                os_level = config.get("type", "mini")
            # 2. product config based on default minimum system
            based_on_mininum_system = config.get('based_on_mininum_system')
            if based_on_mininum_system == "true":
                self._parts = self._get_base_parts(self._dirs.built_in_base_dir, os_level)
            # 3. inherit parts information from inherit config
            inherit = config.get('inherit')
            if inherit:
                self._parts.update(
                    self._get_inherit_parts(inherit, self._dirs.source_root_dir))

            # 4. chipset products relate system parts config
            sys_info_path = config.get('system_component')
            if sys_info_path:
                sys_parts = self._get_sys_relate_parts(sys_info_path, self._parts, self._dirs.source_root_dir)
                self._parts.update(sys_parts)
            all_parts = {}
            if version == "2.0":
                current_product_parts = config.get("parts")
                if current_product_parts:
                    all_parts.update(current_product_parts)
            else:
                all_parts.update(get_vendor_parts_list(config))
                all_parts.update(self._get_product_specific_parts())

                device_name = config.get('board')
                if device_name:
                    all_parts.update(self._device.get_device_specific_parts())
            self._parts.update(all_parts)


class _MyDevice():

    def __init__(self, device_name, config_dirs, device_info=None):
        self._name = device_name
        self._dirs = config_dirs
        if device_info is None:
            self._device_info = self._make_device_info(
                self._name, self._dirs.built_in_device_dir)
        else:
            self._device_info = device_info

    def get_device_info(self):
        return self._device_info

    def _make_device_info(self, device_name, config_dir):
        device_config_file = os.path.join(config_dir,
                                          '{}.json'.format(device_name))
        device_info = IoUtil.read_json_file(device_config_file)
        if device_info and device_info.get('device_name') != device_name:
            raise Exception("device name configuration incorrect in '{}'".format(
                device_config_file))
        return device_info

    def get_device_specific_parts(self):
        info = {}
        if self._device_info:
            device_build_path = self._device_info.get('device_build_path')
            if device_build_path:
                subsystem_name = 'device_{}'.format(self._name)
                part_name = subsystem_name
                info['{}:{}'.format(subsystem_name, part_name)] = {}
        return info

    def get_device_specific_subsystem(self):
        info = {}
        subsystem_name = 'device_{}'.format(self._name)
        if self._get_device_build_path():
            info[subsystem_name] = {
                'name': subsystem_name,
                'path': self._get_device_build_path()
            }
        return info

    def _get_device_build_path(self):
        if self._device_info:
            return self._device_info.get('device_build_path')
        else:
            return None
