from enum import IntEnum as Enum
from os import error, name
import requests
import json

class Label_Encoder(json.JSONEncoder):
    def default(self, obj):
        if(isinstance(obj,Label)):
            return str(obj)

#as system metrics are given via the OS - the code should be platform-specific

class Base_Label_Names:
    pass

class Label_Names(Base_Label_Names,Enum):
    metric_name = 0
    monitored_data_type = 1
    device_name = 2
    ram_subset = 3
    direction = 4
    metrics_subset = 5
    def __str__(self):
        if(self.value == Label_Names.metric_name):
            return "metric_name"
        elif(self.value == Label_Names.monitored_data_type):
            return "monitored_data_type"
        elif(self.value == Label_Names.device_name):
            return "device_name"
        elif(self.value == Label_Names.ram_subset):
            return "ram_subset"
        elif(self.value == Label_Names.direction):
            return "direction"
        elif(self.value == Label_Names.metrics_subset):
            return "metrics_subset"
        else:
            return "unknown label"

        
class Metric_Type(Enum):
    Undefined = 0
    Gauge = 1
    Counter = 2
    Histogram = 3
    def __str__(self):
        if(self.value == Metric_Type.Undefined):
            return "undefined"
        elif(self.value == Metric_Type.Gauge):
            return "gauge"
        elif(self.value == Metric_Type.Counter):
            return "counter"
        elif(self.value == Metric_Type.Histogram):
            return "histogram"
        else:
            print("some unexpected error ocured")
            return error

    

class Label:
    name = 0
    value = 0
    def __init__(self, name, value):
        if(not issubclass(type(name), Base_Label_Names)):
            print("some error")
            return error
        if(type(value)!=str):
            return error
        self.name = name
        self.value = value
    def __str__(self, /):
        return F"{self.name}=\"{self.value}\""

def get_label_pos(label):
    return int(label.name)

def get_name(labels):
    if(type(labels)!= list):
        print("Error - not a list")
        return error
    for label in labels:
        if(label.name == Label_Names.metric_name):
            return(label.value)
    print("Error - no \"name\" label")
    return error

class Base_Metric_With_Labels:
    pushables = {}
    metric_type = "none"
    help_string = "none"
    name_label = "none"

    class Base_Label_Names(Base_Label_Names, Enum):
        metric_name = 0
        def __str__(self) -> str:
            if(self.value == Base_Metric_With_Labels.Label_Names.metric_name):
                return "metric_name"

    def __init__(self, name, metric_type, help_string):
        self.name_label = Label(self.Base_Label_Names.metric_name, name)
        self.metric_type = metric_type
        self.help_string = help_string
        self.pushables = {}

    def add_or_update_pushables(self, labels, data):
        if(type(labels) != list):
            print("labels should be in a list")
            return error
        name_exists = False
        for label in labels:
            if(type(label) != Label):
                print("element of a given list is not a label")
                return error
            if(label.name == self.Base_Label_Names.metric_name):
                name_exists = True
                if(label.value != self.name_label.value):
                    print(F"error - name labels do not match. {label.value} != {self.name_label.value}")
                    return error
        if (not name_exists):
            labels.append(self.name_label)
        pushable = Single_pushable(labels, data)
        self.pushables[pushable.get_container_id] = pushable

    def __str__(self):
        rt_string = F"# TYPE {self.name_label.value} {self.metric_type}\n"
        rt_string+= F"# HELP {self.name_label.value} {self.help_string}\n"
        return rt_string

class Single_pushable:
    data = 0
    labels = 0

    def __init__(self, labels, data):
        error_state = False
        if(type(labels)!=list):
            return error
        for label in labels:
            if(type(label)!=Label):
                error_state = True
        self.labels = sorted(labels, key = get_label_pos)
        self.data = data
        if(error_state):
            return error
    
    def get_container_id(self):
        return json.dumps(self.labels, cls = Label_Encoder)

    def __str__(self, /):
        rt_string = F"{get_name(self.labels)}{{" 
        for label in self.labels:
            if(label.name == Label_Names.metric_name):
                continue
            rt_string+=str(label)+", "
        rt_string = rt_string[:-2]
        rt_string +=F"}} {self.data}"
        return rt_string



class Metric:
    name = "none"
    pushables = {}
    metric_type = "none"
    help_string = "none"

    def __init__(self, name, metric_type, help_string):
        self.name = name
        self.metric_type = metric_type
        self.help_string = help_string
        self.pushables = {}

    def add_or_update_pushables(self, labels, data):
        if(type(labels) != list):
            print("labels should be in a list")
            return error
        name_exists = False
        for label in labels:
            if(type(label) != Label):
                print("element of a given list is not a label")
                return error
            if(label.name == Label_Names.metric_name):
                name_exists = True
                if(label.value != self.name):
                    print("error - names do not match. Check Metric name and label \"name\"")
                    return error
        if (not name_exists):
            name_label = Label(Label_Names.metric_name, self.name)
            labels.append(name_label)
        pushable = Single_pushable(labels, data)
        self.pushables[pushable.get_container_id] = pushable

    def __str__(self):
        rt_string = F"# TYPE {self.name} {self.metric_type}\n"
        rt_string+= F"# HELP {self.name} {self.help_string}\n"
        return rt_string


#unavalible symbols in metric names are : -, \, /, [], +, *, $, !, @, #, %, (пробел), |, ^, &, (), =, ", ', {}, ;, <>, (запятая), (точка), ?, `, ~
class prom_exporter:
    metrics = {}
    pushables = {}
    name = "none"
    time_interval = 0
    last_push_time = 0
    def __init__(self, name, interval = 0):
        self.name = name
        self.time_interval = interval

    def push_to_gateway(self):
        r = requests.post(F"http://localhost:9091/metrics/job/{self.name}", data=self.convert_pushables())
        print(r)

    def set_metric(self, metric):
        self.metrics[metric.name_label.value] = metric
        self.pushables[metric.name_label.value] = {}

    def scrape_metrics(self):
        for metric in self.metrics.values():
            prom_exporter.pushables[metric.name_label.value].update(metric.pushables)

    def convert_pushables(self):
        rt_string = ""
        for metric_name in prom_exporter.pushables.keys():
            rt_string+=str(self.metrics[metric_name])
            for pushable in prom_exporter.pushables[metric_name].values():
                rt_string+=str(pushable)+"\n"
        return rt_string