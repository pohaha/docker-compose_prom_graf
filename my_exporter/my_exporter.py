# cat < metrics_to_push.txt | curl --data-binary @- http://localhost:9091/metrics/job/some_job

from enum import IntEnum as Enum
import time
from os import name
import requests
import sys
import Metric as library

exports  = False

#as system metrics are given via the OS - the code should be platform-specific

#platforms
class Platform(Enum):
    windows = 1
    linux = 2
    macos = 3

class system_metrics_exporter(library.prom_exporter):
    current_platform = "none"
    get_cpu = []
    get_inet = []
    get_mem = []
    metrics = {}

    #show the scraped metrics on the screen
    def show(self):
        for item in self.metrics:
            if(item.endswith("ram")):
                print(F"{item} = {self.metrics[item].data} Mb")
            else:
                if(type(item)!=str):
                    value = "{:.3f}".format(self.metrics[item].data)
                    print(F"{item} = {value}")
                else:
                    print(F"{item} = {self.metrics[item].data}")
    
    #scrape all needed metrics
    def get_metrics(self):
        self.metrics.update(self.get_cpu())
        self.metrics.update(self.get_inet())
        self.metrics.update(self.get_mem())

    #get os specific scrapers
    def __init__(self, name):
        super().__init__(name)
        if(sys.platform.startswith("linux")):
            self.current_platform = Platform.linux
            import _linux_scraper as scraper
            self.get_cpu = scraper.get_cpu
            self.get_inet = scraper.get_inet
            self.get_mem = scraper.get_mem
        if(sys.platform.startswith("mac")):
            self.current_platform = Platform.macos
            import _macos_scraper as scraper
            self.get_cpu = scraper.get_cpu
            self.get_inet = scraper.get_inet
            self.get_mem = scraper.get_mem
        if(sys.platform.startswith("win")):
            self.current_platform = Platform.windows
            import _windows_scraper as scraper
            self.get_cpu = scraper.get_cpu
            self.get_inet = scraper.get_inet
            self.get_mem = scraper.get_mem
            

    #scrape+show for now (exporter pending)
    def scrape(self):
        self.get_metrics()
        for metric in self.metrics.values():
            self.set_metric(metric)
        self.show()
        print(self.convert_metrics())
        self.push_to_gateway()
    
    def get_metric(self, index):
        dict_keys = list(self.metrics.keys())
        return self.metrics[dict_keys[index]]

#example!!!
#sys.platform = "windows"
some_exporter = system_metrics_exporter("simple exporter")
while(True):
    some_exporter.scrape()
    time.sleep(15)
    print("metrics are exported")



#end example
if(exports): 
    with open('../metrics_to_push.txt', 'rb') as file:
        r = requests.post("http://localhost:9091/metrics/job/some_job", data=file)
    print(r)
