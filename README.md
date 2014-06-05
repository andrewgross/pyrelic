# Pyrelic [![Build Status](https://api.travis-ci.org/andrewgross/pyrelic.png#master)](https://travis-ci.org/andrewgross/pyrelic)


A New Relic client library written in Python.

While New Relic's documentation for their API is very solid, the usage details are pretty sparse and biased toward the Rails Active Resource helper library.

The documentation in this library's docstrings was derived from the [New Relic Ruby API](https://github.com/newrelic/newrelic_api).

## Installation
```bash
$ pip install pyrelic
```

## Examples

### Setup

```python
from pyrelic import Client
from time import sleep
c = Client(account_id='XXX', api_key='XXXXXX')
```

### Get some metric data

```python
metrics = c.get_metric_data(['My Application'], ['Database/my_table/select', 'Database/my_table/update'], ['average_value'], '2012-03-28T15:48:00Z', '2012-03-29T15:48:00Z')

for metric in metrics:
    if "select" in metric.name:
        print "Average Select Time: {}".format(metric.average_value)
    if  "update" in metric.name:
        print "Average Update Time: {}".format(metric.average_value)
```

### Handle API rate limiting

```python
try:
    metrics = c.get_metric_data(['My Application'], ['Database/my_table/select', 'Database/my_table/update'], ['average_value'], '2012-03-28T15:48:00Z', '2012-03-29T15:48:00Z')
except NewRelicApiRateLimitException as e:
    sleep(e.timeout)
```


### List some metrics
```python
metrics = c.get_metric_list('123456', re='Database')
for k,v in metrics.iteritems():
    print "Metric Name: {}".format(k)
    print "Available Fields: {}".format(v)
```

### Figure out what applications you have

```python
applications = c.view_applications()
for application in applications:
    print "Name: {}".format(application.name)
    print "ID: {}".format(application.app_id)
    print "URL: {}".format(application.url)
```

### Delete applications (careful!)
```python
failed_deletions = c.delete_applications( {'app_id': 1234, 'app': 'My Application'})
if len(failed_deletions) is 0:
    print "All applications deleted succesfully!"
```

### View servers
```python
servers = c.view_servers()
for server in servers:
    print "Hostname: {}".format(server.hostname)
    print "Server ID: {}".format(server.server_id)
    print "Overview URL: {}".format(server.overview_url)
```

### Delete Servers
```python
failed_deletion = c.delete_servers("server_id")
if len(failed_deletions) is 0:
    print "Server deleted succesfully!"
```
