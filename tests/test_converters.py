#/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 2020  The SymbiFlow Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC

import os
import unittest
import json
import yaml
from yaml import CSafeLoader as SafeLoader, CDumper as Dumper

from fpga_interchange.json_support import to_json, from_json
from fpga_interchange.yaml_support import to_yaml, from_yaml
from fpga_interchange.rapidyaml_support import to_rapidyaml, from_rapidyaml
from fpga_interchange.compare import compare_capnp
import ryml
from fpga_interchange.capnp_utils import get_module_from_id
from fpga_interchange.interchange_capnp import Interchange
from example_netlist import example_logical_netlist, example_physical_netlist
import pytest
import psutil


def check_mem():
    return psutil.virtual_memory().total < 7 * 1024 * 1024


class TestConverterRoundTrip(unittest.TestCase):
    def round_trip_json(self, in_message):
        value = to_json(in_message)
        json_string = json.dumps(value)

        value_out = json.loads(json_string)
        message = get_module_from_id(in_message.schema.node.id).new_message()
        from_json(message, value_out)
        compare_capnp(self, in_message, message)

        value2 = to_json(message)
        json_string2 = json.dumps(value2)

        self.assertTrue(json_string == json_string2)

    def round_trip_yaml(self, prefix, in_message):
        value = to_yaml(in_message)
        yaml_string = yaml.dump(value, sort_keys=False, Dumper=Dumper)

        with open(prefix + '_test_yaml.yaml', 'w') as f:
            f.write(yaml_string)

        value_out = yaml.load(yaml_string, Loader=SafeLoader)
        message = get_module_from_id(in_message.schema.node.id).new_message()
        from_yaml(message, value_out)
        compare_capnp(self, in_message, message)

        value2 = to_yaml(message)
        yaml_string2 = yaml.dump(value2, sort_keys=False, Dumper=Dumper)

        with open(prefix + '_test_yaml2.yaml', 'w') as f:
            f.write(yaml_string2)

        self.assertTrue(yaml_string == yaml_string2)

    def round_trip_rapidyaml(self, prefix, in_message):
        strings, value = to_rapidyaml(in_message)
        yaml_string = ryml.emit(value)

        with open(prefix + '_test_rapidyaml.yaml', 'w') as f:
            f.write(yaml_string)

        value_out = ryml.parse(yaml_string)
        message = get_module_from_id(in_message.schema.node.id).new_message()
        from_rapidyaml(message, value_out)
        compare_capnp(self, in_message, message)

        strings, value2 = to_rapidyaml(message)
        yaml_string2 = ryml.emit(value2)

        with open(prefix + '_test_rapidyaml2.yaml', 'w') as f:
            f.write(yaml_string2)

        self.assertTrue(yaml_string == yaml_string2)

    def test_logical_netlist_json(self):
        logical_netlist = example_logical_netlist()

        interchange = Interchange(
            schema_directory=os.environ['INTERCHANGE_SCHEMA_PATH'])
        netlist_capnp = logical_netlist.convert_to_capnp(interchange)

        self.round_trip_json(netlist_capnp)

    def test_physical_netlist_json(self):
        phys_netlist = example_physical_netlist()

        interchange = Interchange(
            schema_directory=os.environ['INTERCHANGE_SCHEMA_PATH'])
        netlist_capnp = phys_netlist.convert_to_capnp(interchange)

        self.round_trip_json(netlist_capnp)

    @pytest.mark.skipif(check_mem(), reason='This test needs ~7-8 GB of RAM')
    def test_device_json(self):
        phys_netlist = example_physical_netlist()

        interchange = Interchange(
            schema_directory=os.environ['INTERCHANGE_SCHEMA_PATH'])

        with open(
                os.path.join(os.environ['DEVICE_RESOURCE_PATH'],
                             phys_netlist.part + '.device'), 'rb') as f:
            dev_message = interchange.read_device_resources_raw(f)

        self.round_trip_json(dev_message)

    def test_logical_netlist_yaml(self):
        logical_netlist = example_logical_netlist()

        interchange = Interchange(
            schema_directory=os.environ['INTERCHANGE_SCHEMA_PATH'])
        netlist_capnp = logical_netlist.convert_to_capnp(interchange)

        self.round_trip_yaml('log', netlist_capnp)

    def test_physical_netlist_yaml(self):
        phys_netlist = example_physical_netlist()

        interchange = Interchange(
            schema_directory=os.environ['INTERCHANGE_SCHEMA_PATH'])
        netlist_capnp = phys_netlist.convert_to_capnp(interchange)

        self.round_trip_yaml('phys', netlist_capnp)

    def test_logical_netlist_rapidyaml(self):
        logical_netlist = example_logical_netlist()

        interchange = Interchange(
            schema_directory=os.environ['INTERCHANGE_SCHEMA_PATH'])
        netlist_capnp = logical_netlist.convert_to_capnp(interchange)

        self.round_trip_rapidyaml('log', netlist_capnp)

    def test_physical_netlist_rapidyaml(self):
        phys_netlist = example_physical_netlist()

        interchange = Interchange(
            schema_directory=os.environ['INTERCHANGE_SCHEMA_PATH'])
        netlist_capnp = phys_netlist.convert_to_capnp(interchange)

        self.round_trip_rapidyaml('phys', netlist_capnp)

    @pytest.mark.skipif(check_mem(), reason='This test needs ~7-8 GB of RAM')
    def test_device_rapidyaml(self):
        phys_netlist = example_physical_netlist()

        interchange = Interchange(
            schema_directory=os.environ['INTERCHANGE_SCHEMA_PATH'])

        with open(
                os.path.join(os.environ['DEVICE_RESOURCE_PATH'],
                             phys_netlist.part + '.device'), 'rb') as f:
            dev_message = interchange.read_device_resources_raw(f)

        self.round_trip_rapidyaml('device', dev_message)
