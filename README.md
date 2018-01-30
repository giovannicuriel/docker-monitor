# docker-monitor


[![License badge](https://img.shields.io/badge/license-GPL-blue.svg)](https://opensource.org/licenses/GPL-3.0)

It is a service to monitor the docker infrastructure that runs dojot platform.

It provides a REST API to query some statistic metrics of the containers such as
percentage of CPU and memory in use. It also generates alarms for container's events
(die, stop, start, pause, and unpause). 

## Dependencies

It has the following dependencies:

- flask
- docker
- requests
- gunicorn
- gevent

## Usage

The API for getting container's metrics are given in the table bellow. 

| Http Method   | URI                                                                 | Action                                |
| ------------- |---------------------------------------------------------------------| --------------------------------------|
| GET           | http://<hostname>/docker-monitor/api/v1.0/metrics                   | Retrieve metrics for all containers   |
| GET           | http://<hostname>/docker-monitor/api/v1.0/metrics/<container-name>  | Retrieve metrics for a given container|


In case of success, the GETs return, respectively, a list of container's metrics:
```json
[
{
 "<container-name-1>": {"status": "<status>",
                        "cpu":    "<percentage_of_cpu>",
                        "mem":    "<percentage_of_mem>"}
},

...

{
 "<container-name-n>": {"status": "<status>",
                         "cpu":    "<percentage_of_cpu>",
                         "mem":    "<percentage_of_mem>"}

}
]
``` 
 
and the requested container's metrics:
```json
{
 "<container-name>": {"status": "<status>",
                      "cpu":    "<percentage_of_cpu>",
                      "mem":    "<percentage_of_mem>"}
}
```

The docker-monitor also runs a background thread which listen to docker-events generating the following alarms:

- Container went down (docker events: die, stop)
```json
{
 "namespace":      "dojot.docker.container",
 "domain":         "docker container status change",
 "eventTimestamp": "<timestamp>",
 "description":    "container went down",
 "severity":       "Major",
 "primarySubject": {"container": "<container-name>",
                    "image":     "<image-name>"}
 }
```

- Container went up (docker event: start)
```json
{
 "namespace":      "dojot.docker.container",
 "domain":         "docker container status change",
 "eventTimestamp": "<timestamp>",
 "description":    "container went up",
 "severity":       "Clear",
 "primarySubject": {"container": "<container-name>",
                    "image":     "<image-name>}"}
 }
```

- Container processes were paused (docker event: pause)
```json
{
 "namespace":      "dojot.docker.container",
 "domain":         "docker container status change",
 "eventTimestamp": "<timestamp>",
 "description":    "container processes were paused",
 "severity":       "Major",
 "primarySubject": {"container": "<container-name>",
                    "image":     "<image-name>}"}
 }
```

- Container processes were unpaused (docker event: unpaused)
```json
{
 "namespace":      "dojot.docker.container",
 "domain":         "docker container status change",
 "eventTimestamp": "<timestamp>",
 "description":    "container processes were unpaused",
 "severity":       "Clear",
 "primarySubject": {"container": "<container-name>",
                    "image":     "<image-name>"}
 }
```


