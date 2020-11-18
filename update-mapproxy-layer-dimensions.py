#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import sys

from owslib.wms import WebMapService
import yaml

layer_name = sys.argv[0]
mapproxy_config = sys.argv[1]

url = 'https://geo.weather.gc.ca/geomet?layer={}'.format(layer_name)

wms = WebMapService(url, version='1.3.0')

dimensions = {}

for key, value in wms[layer_name].dimensions.items():
    print("key: ", key)
    print("value: ", value)
    if key == 'time':
        key2 = key
    else:
        key2 = 'dim_{}'.format(key)

    dimensions[key2] = {
        'default': value['default'],
        'values': value['values']
    }
    print(dimensions)

if not dimensions:
    print('No dimensions found')
    sys.exit(1)

with open(mapproxy_config) as fh:
    dict_ = yaml.safe_load(fh)

    for layer in dict_['layers']:
        if layer['name'] == layer_name:
            print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
            for key, value in dimensions.items():
                layer['dimensions'][key] = value

    print(yaml.dump(dict_))

