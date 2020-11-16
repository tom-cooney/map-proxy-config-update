#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import sys

from owslib.wms import WebMapService
import yaml

layer_name = sys.argv[1]
mapproxy_config = sys.argv[2]

url = 'https://geo.weather.gc.ca/geomet?layer={}'.format(layer_name)

wms = WebMapService(url, version='1.3.0')

dimensions = {}

for key, value in wms[layer_name].dimensions.items():
    dimensions[key] = { 
        'default': value['default'],
        'values': value['values']
    }

if not dimensions:
    print('No dimensions found')
    sys.exit(1)

with open(mapproxy_config) as fh:
    dict_ = yaml.safe_load(fh)

    for layer in dict_['layers']:
        if layer['name'] == layer_name:
            for key, value in dimensions.items():
                layer['dimensions'][key] = value

    print(yaml.dump(dict_))

