FROM golang:latest
COPY . /DU_exporter
WORKDIR /DU_exporter
CMD go build -o DU_exporter; ./DU_exporter -c /config/disk_usage_exporter.yaml


