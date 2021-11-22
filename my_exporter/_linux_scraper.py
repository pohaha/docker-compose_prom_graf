import os
import Metric as library

def get_cpu():

    statistics = {}

    # Get Physical and Logical CPU Count
    physical_and_logical_cpu_count = os.cpu_count()
    labels = {'metric_part':'cpu','name':'count'}
    help_string = "total amount of physical and logical cpu's"
    statistics['cpu_count'] = library.Metric(labels,physical_and_logical_cpu_count,None,library.Metric_Type.Counter,help_string)
    
    # count load average
    labels = {'metric_part':'cpu','name':'load'}
    help_string = "average load of cpu's in %"
    cpu_load = [x / os.cpu_count() * 100 for x in os.getloadavg()][-1]
    statistics['cpu_load'] = library.Metric(labels,cpu_load,None,library.Metric_Type.Counter,help_string)
    return statistics

def get_mem():
    mem_info = []
    mem_info = map(int, os.popen('free -t --mega').readlines()[-1].split()[1:])
    statistics = {}
    names = ["mem_total_ram_megabytes","mem_used_ram_megabytes","mem_free_ram_megabytes"]
    label_names = ["metric_part","mem_info","memory_specifier","name"]
    help_strings = ["total ram of a pc","currently used ram of a pc", "free (not avalible!!) ram memory of a pc"]
    index = 0
    for info in mem_info:
        labels = dict(zip(label_names,library.name_to_label(names[index])))
        statistics[names[index]] = library.Metric(labels,info,None,library.Metric_Type.Counter,help_strings[index])
    return statistics

#unavalible symbols in metric names are : -, \, /, [], +, *, $, !, @, #, %, (пробел), |, ^, &, (), =, ", ', {}, ;, <>, (запятая), (точка), ?, `, ~
#avalible symbols are: 0-9, :, a-z, A-Z, _, 

def get_inet():
    lines = open("/proc/net/dev", "r").readlines()
    i = 0
    statistics = {}
    data = {}
    label_names = ["metric_part","iface_name","tx_or_rx","type_of_tx_rx_entites"]
    types = ["bytes","packets","errs","drops"]
    tx_rx = ["tx", "rx"]
    help_string = "number of transmitted/recieved (tx/rx) [bytes, packets,errors,drops](name) on a specific web interface (iface_name)"
    for line in lines:
        if(i < 2):
            i=i+1
            continue
        elif(i < 7):
            name_and_data = line.split(':')
            iface_name = name_and_data[0].strip()
            if(i == 6):
                iface_name = "br:1cbb20ab016d"
            full_data = name_and_data[1]
            full_data = full_data.split()
            data["tx"] = full_data[0:7]
            data["rx"] = full_data[8:]
            for direction in tx_rx:
                index = 0
                for typename in types:
                    full_name = F"inet_{iface_name}_{direction}_{typename}"
                    labels = dict(zip(label_names,library.name_to_label(full_name)))
                    labels.update({'name':full_name})
                    statistics[full_name] = library.Metric(labels,data[direction][index],None,library.Metric_Type.Counter,help_string)
                    index=index+1
        i=i+1
    return statistics



