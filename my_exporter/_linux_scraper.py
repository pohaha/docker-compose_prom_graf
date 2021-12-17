import os
import Metric as library
from enum import IntEnum as Enum

inet_help_string = "number of [transmitted,recieved] (direction) [bytes, packets,errors,drops] (monitored_data_type) on a specific [web interface] (device_name)"
class Inet_Metric(library.Base_Metric_With_Labels):
    class Label_Names(library.Base_Label_Names, Enum):
        monitored_data_type = 1
        device_name = 2
        direction = 3
        def __str__(self):
            if(self.value == Inet_Metric.Label_Names.monitored_data_type):
                return "monitored_data_type"
            elif(self.value == Inet_Metric.Label_Names.device_name):
                return "device:name"
            elif(self.value == Inet_Metric.Label_Names.direction):
                return "direction"
            else:
                return "unknown label"
    def __init__(self):
        super().__init__("inet", library.Metric_Type.Counter, inet_help_string)

#unavalible symbols in metric names are : -, \, /, [], +, *, $, !, @, #, %, (пробел), |, ^, &, (), =, ", ', {}, ;, <>, (запятая), (точка), ?, `, ~
def get_inet():
    inet = Inet_Metric()
    lines = open("/proc/net/dev", "r").readlines()
    i = 0
    data = {}
    types = ["bytes","packets","errs","drops"]
    tx_rx = ["tx", "rx"]
    for line in lines:
        if(i < 2):
            pass
        else:
            name_and_data = line.split(':')
            iface_name = name_and_data[0].strip()
            l_iface_name = library.Label(Inet_Metric.Label_Names.device_name,iface_name)
            full_data = name_and_data[1]
            full_data = full_data.split()
            data["tx"] = full_data[0:7]
            data["rx"] = full_data[8:]
            for direction in tx_rx:
                l_direction = library.Label(Inet_Metric.Label_Names.direction,direction)
                index = 0
                for typename in types:
                    l_type = library.Label(Inet_Metric.Label_Names.monitored_data_type, typename)
                    labels = [l_iface_name, l_direction, l_type]
                    inet.add_or_update_pushables(labels, data[direction][index])
                    index=index+1
        i=i+1
    return inet
    
cpu_help_string = "information about CPU [cpu_count, cpu_load_avg](monitored_data_type)"
class Cpu_Metric(library.Base_Metric_With_Labels):
    class Label_Names(library.Base_Label_Names, Enum):
        monitored_data_type = 1
        def __str__(self):
            if(self.value == Inet_Metric.Label_Names.monitored_data_type):
                return "monitored_data_type"
            else:
                return "unknown label"
    def __init__(self):
        super().__init__("cpu", library.Metric_Type.Gauge, cpu_help_string)


def get_cpu():
    cpu = Cpu_Metric()
    l_cpu_count = library.Label(Cpu_Metric.Label_Names.monitored_data_type, "cpu_count")
    l_cpu_load_avg = library.Label(Cpu_Metric.Label_Names.monitored_data_type, "cpu_load_avg")
    # Get Physical and Logical CPU Count
    physical_and_logical_cpu_count = os.cpu_count()
    cpu.add_or_update_pushables([l_cpu_count], physical_and_logical_cpu_count)    
    # count load average
    cpu_load_value = [x / os.cpu_count() * 100 for x in os.getloadavg()][-1]
    cpu.add_or_update_pushables([l_cpu_load_avg], cpu_load_value)
    return cpu

def get_mem():
    mem_info = []
    mem_info = map(int, os.popen('free -t --mega').readlines()[-1].split()[1:])
    ram = library.Metric("ram", library.Metric_Type.Gauge, "information about current RAM state")
    subsets = ["total","used","free"]
    index = 0
    for info in mem_info:
        labels = [library.Label(library.Label_Names.ram_subset, subsets[index])]
        ram.add_or_update_pushables(labels, info)
        index +=1
    return ram





