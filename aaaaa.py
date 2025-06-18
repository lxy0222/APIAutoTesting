import requests

url = "https://jingrantest.dev.mfspm.com/itg/rest2/dm/requestTypes"
response = requests.get(url, verify=False, auth=("admin", "!QAZ@WSX3edc"), proxies={'https':"http://web-proxy.uk.softwaregrp.net:8080"})
print(response.status_code)
print(response.content)
