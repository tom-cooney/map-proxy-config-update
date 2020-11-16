#!/usr/bin/env python
# coding: utf-8

# In[ ]:


from owslib.wms import WebMapService
import sys 

layer_name = sys.argv[1]

url = 'https://geo.weather.gc.ca/geomet?layer={}'.format(layer_name)

wms = WebMapService(url, version='1.3.0')

dimensions = {}

for key, value in wms[layer_name].dimensions.items():
    dimensions[key] = { 
        'default': value['default'],
        'values': value['values']
    }   

print(dimensions)

