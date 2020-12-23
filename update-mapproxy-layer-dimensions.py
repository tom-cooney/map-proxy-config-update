# =================================================================
#
# Author: Tom Cooney <tom.cooney@canada.ca>
#
# Copyright (c) 2020 Tom Cooney
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation
# files (the "Software"), to deal in the Software without
# restriction, including without limitation the rights to use,
# copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following
# conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
#
# =================================================================

import click
import os

from owslib.wms import WebMapService
import mappyfile
import yaml


def update_config(mapproxy_config, layers_to_update):
    with open(mapproxy_config) as fh:
        dict_ = yaml.safe_load(fh)
        for layer in dict_['layers']:
            layer_name = layer['name']
            if layer_name in layers_to_update:
                for dim in layers_to_update[layer_name].keys():
                    layer['dimensions'][dim]['default'] = layers_to_update[layer_name][dim]['default']
                    layer['dimensions'][dim]['values'] = layers_to_update[layer_name][dim]['values']
                    
    return dict_


def update_from_wms(input_layers, mapproxy_config):
    layer_list = input_layers.split(",")
    layers_to_update = {}
    for layer_name in layer_list:
        url = 'https://geo.weather.gc.ca/geomet?layer={}'.format(layer_name)
        wms = WebMapService(url, version='1.3.0')

        dimensions_list = ['time', 'reference_time']
        for dimension in dimensions_list:
            if dimension in wms[layer_name].dimensions.keys():
                if layer_name not in layers_to_update.keys():
                    layers_to_update[layer_name] = {}
                layers_to_update[layer_name][dimension] = {
                    'default': wms[layer_name].dimensions[dimension]['default'],
                    'values': wms[layer_name].dimensions[dimension]['values']
                }

    dict_ = update_config(mapproxy_config, layers_to_update)

    return dict_

def update_from_xml(input_layers, mapproxy_config):
    layer_list = input_layers.split(",")
    layers_to_update = {}
    with open('/data/web/geomet2-nightly/latest/build/conf/geomet-wms-1.3.0-capabilities-en.xml', 'rb') as fh:
        buffer = fh.read()

        wms = WebMapService('url', version='1.3.0', xml=buffer)

        for layer_name in layer_list:
            dimensions_list = ['time', 'reference_time']
            for dimension in dimensions_list:
                if dimension in wms[layer_name].dimensions.keys():
                    if layer_name not in layers_to_update.keys():
                        layers_to_update[layer_name] = {}
                    layers_to_update[layer_name][dimension] = {
                        'default': wms[layer_name].dimensions[dimension]['default'],
                        'values': wms[layer_name].dimensions[dimension]['values']
                    }

    dict_ = update_config(mapproxy_config, layers_to_update)

    return dict_


def update_from_mapfile(input_layers, mapproxy_config, MAPPROXY_MAPFILE_DIR):
    layer_list = input_layers.split(",")
    layers_to_update = {}
    for layer_name in layer_list:
        filepath = os.path.join(MAPPROXY_MAPFILE_DIR, 'geomet-{}-en.map'.format(layer_name))
        f = mappyfile.open(filepath)
        
        if layer_name not in layers_to_update.keys():
            layers_to_update[layer_name] = {}
        if ('wms_timeextent' in f['layers'][0]['metadata'].keys()):
            layers_to_update[layer_name]['time'] = {
                'default': f['layers'][0]['metadata']['wms_timedefault'],
                'values': [f['layers'][0]['metadata']['wms_timeextent']]
            }
        if ('wms_reference_time_default' in f['layers'][0]['metadata'].keys()):
            layers_to_update[layer_name]['reference_time'] = {
                'default': f['layers'][0]['metadata']['wms_reference_time_default'],
                'values': [f['layers'][0]['metadata']['wms_reference_time_extent']]
            }

    dict_ = update_config(mapproxy_config, layers_to_update)                   

    return dict_


@click.command()
#@click.pass_context
@click.option('--input_layers', 'input_layers', help='layers to update dimensions of in mapproxy config')
@click.option('--mapproxy_config', 'mapproxy_config', help='mapproxy config to update layers and dimensions')
@click.option('--mode', 'mode', type=click.Choice(['wms', 'xml', 'mapfile']), default='wms', help='select either wms or mapfile')
def cli(input_layers, mapproxy_config, mode):
    if 'wms' in mode:
        output_dict = update_from_wms(input_layers, mapproxy_config)
    elif 'xml' in mode:
        output_dict = update_from_xml(input_layers, mapproxy_config)
    elif 'mapfile' in mode:
        # if the MAPPROXY_MAPFILE_DIR environment variable doesn't exist it will set it to None by default
        # in bash `export MAPPROXY_MAPFILE_DIR=/data/web/geomet2-nightly/latest/build/conf/`
        MAPPROXY_MAPFILE_DIR = os.getenv('MAPPROXY_MAPFILE_DIR', None)
        output_dict = update_from_mapfile(input_layers, mapproxy_config, MAPPROXY_MAPFILE_DIR)
        
    print(yaml.dump(output_dict))

    
if __name__ == '__main__':
    cli()
