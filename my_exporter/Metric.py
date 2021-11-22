from enum import IntEnum as Enum
import requests
import json

#as system metrics are given via the OS - the code should be platform-specific



class Metric_Type(Enum):
    Undefined = 0
    Gauge = 1
    Counter = 2
    Histogram = 3

types_as_string = ["undefined", "gauge", "counter", "histogram"]

class Metric:
    kind = Metric_Type.Undefined
    data = 0
    scraper = None
    labels = {}
    help_string = "none"

    def __init__(self, labels, data, scraper = None,kind = None, help_string = None):
        if(kind):
            self.kind = kind
        if(help_string):
            self.help_string = help_string
        if(scraper):
            self.scraper = scraper
        self.labels = labels
        self.data = data

    def labels_as_string(self):
        rt_string = ""
        for item in self.labels.items():
            rt_string = rt_string+F"{item[0]}=\"{item[1]}\","
        return rt_string[:-1]

    def to_string(self):
        string_form = ""
        name = self.labels["name"]
        if(self.kind):
            if(self.kind!=Metric_Type.Undefined):
                string_form=string_form+F"# TYPE {name} {types_as_string[int(self.kind)]}\n"
        if(self.help_string!="none"):
                string_form=string_form+F"# HELP {name} {self.help_string}\n"
        string_form=string_form+F"{name}{{{self.labels_as_string()}}}"
        if(self.scraper):
            self.data = self.scraper()
        string_form=string_form+F" {self.data}\n"
        return string_form

    def get_container_id(self):
        return json.dumps(dict(sorted(self.labels.items())))

#note that names should be parced as: ValueOfLabel1_ValueOfLabel2_..._ValueOfLastLabel
def name_to_label(name_as_string):
    return list(name_as_string.split('_'))



class prom_exporter:
    metrics = {}
    name = "none"
    time_interval = 0
    last_push_time = 0
    def __init__(self, name, interval = 0):
        self.name = name
        self.time_interval = interval

    def push_to_gateway(self):
        r = requests.post(F"http://localhost:9091/metrics/job/some_job_2", data=self.convert_metrics())
        print(r)

    def set_metric(self, metric):
        prom_exporter.metrics[metric.get_container_id()] = metric

    def convert_metrics(self):
        rt_string = ""
        for metric in prom_exporter.metrics.values():
            rt_string = rt_string+metric.to_string()
        return rt_string