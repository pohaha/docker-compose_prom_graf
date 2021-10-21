# cat < metrics_to_push.txt | curl --data-binary @- http://localhost:9091/metrics/job/some_job

import requests
with open('../metrics_to_push.txt', 'rb') as file:
    r = requests.post("http://localhost:9091/metrics/job/some_job", data=file)

print(r)