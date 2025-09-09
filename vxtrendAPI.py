# -*- coding: utf-8 -*-
import http.client, urllib, json
conn = http.client.HTTPSConnection('apis.tianapi.com')  #接口域名
params = urllib.parse.urlencode({'key':'你的APIKEY'})
headers = {'Content-type':'application/x-www-form-urlencoded'}
conn.request('POST','/wxhottopic/index',params,headers)
tianapi = conn.getresponse()
result = tianapi.read()
data = result.decode('utf-8')
dict_data = json.loads(data)
print(dict_data)