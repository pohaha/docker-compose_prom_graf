import pytest

import sys
sys.path.append('../../my_exporter') 

import my_exporter

@pytest.fixture
def exporter():
    test_exporter = my_exporter.system_metrics_exporter()
    return test_exporter

@pytest.mark.start
def test_windows_specific():
    sys.platform = "windows"
    test_exporter = my_exporter.system_metrics_exporter()
    assert test_exporter.current_platform == my_exporter.Platform.windows

@pytest.mark.start
def test_linux_specific():
    sys.platform = "linux"
    test_exporter = my_exporter.system_metrics_exporter()
    assert test_exporter.current_platform == my_exporter.Platform.linux

@pytest.mark.middle
def test_individual_metric_scrapers(exporter):
    assert type(exporter.get_cpu()) == dict
    assert type(exporter.get_mem()) == dict
    assert type(exporter.get_inet()) == dict
