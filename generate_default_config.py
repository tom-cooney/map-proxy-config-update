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

import yaml

def write_config(input_layers):
    layer_list = input_layers.split(",")
    sources = {}
    caches = {}
    layers = []
    
    for layer_name in layer_list:
        caches['{}_cache'.format(layer_name)] = {'grids': ['GLOBAL_GEODETIC'], 'sources': ['{}_source'.format(layer_name)]}
        sources['{}_source'.format(layer_name)] = {'forward_req_params': ['time', 'dim_reference_time'], 'req': {'layers': layer_name, 'transparent': True, 'url': 'https://geo.wxod-dev.cmc.ec.gc.ca/geomet'}, 'type': 'wms'}
        if 'RADAR' in layer_name:
            layers.append({'name': layer_name, 'title': layer_name, 'sources': ['{}_cache'.format(layer_name)], 'dimensions':{'time':{'default': None, 'values': []}}})
        else:
            layers.append({'name': layer_name, 'title': layer_name, 'sources': ['{}_cache'.format(layer_name)], 'dimensions':{'time': {'default': None, 'values': []}, 'reference_time': {'default': None, 'values': []}}})
        
    dict_ = {'sources': sources, 'caches': caches, 'layers': layers, 'globals': None, 'services':{'demo': None, 'wms':{'md': {'title': 'Canada Meteo Example'}, 'versions': ['1.3.0']}}}
    return dict_

@click.command()
#@click.pass_context
@click.option('--input_layers', 'input_layers', default='GDPS.ETA_TT,RADAR_1KM_RRAI,RADAR_1KM_RDBR,RADAR_1KM_RSNO,GDPS.ETA_UU,GDPS.ETA_NT,HRDPS.CONTINENTAL_TT,HRDPS.CONTINENTAL_HR,RADAR_COVERAGE_RRAI.INV,HRDPS.CONTINENTAL_TD,GDPS.ETA_RT,HRDPS.CONTINENTAL_NT,GDPS.ETA_SD,HRDPS.CONTINENTAL_PR,GDPS.ETA_PR,GDPS.ETA_HR,HRDPS.CONTINENTAL_WGE,RDPS.ETA_SD,HRDPS.CONTINENTAL.DIAG_PTYPE,HRDPS.CONTINENTAL_PN-SLP,RDPS.ETA_NT,RDPS.ETA_SN,GDPS.ETA_WSPD,RDPS.ETA_TT,RADAR_COVERAGE_RRAI,CGSL.ETA_ICEC,GDPS.ETA_SN,RDPS.DIAG_NW_PT1H,GDPS.ETA_WD,RDPS.ETA_WGE,RDPS.ETA_PR,GDPS.ETA_RN,GDPS.ETA_WGE,RDPS.ETA_PN,REPS.DIAG.3_PRMM.ERGE1,REPS.DIAG.3_PRMM.ERGE5,REPS.DIAG.3_PRMM.ERMEAN,RDPS.ETA_RT', help='layers to update dimensions of in mapproxy config. if no layers provided, all layers are updated')
def cli(input_layers):
    output_dict = write_config(input_layers)
    
    print(yaml.dump(output_dict, default_flow_style=False))

if __name__ == '__main__':
    cli()
