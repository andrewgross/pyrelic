# Pyrelic [![Build Status](https://api.travis-ci.org/andrewgross/pyrelic.png#master)](https://travis-ci.org/andrewgross/pyrelic)


A New Relic client library written in Python.

While New Relic's documentation for their API is very solid, the usage details are pretty sparse and biased toward the Rails Active Resource helper library.

The documentation in this library's docstrings was derived from the [New Relic Ruby API](https://github.com/newrelic/newrelic_api).

## Installation
    $ pip install pyrelic

## Examples

### Setup

    from pyrelic import Client
    from time import sleep
    c = Client(account_id='XXX', api_key='XXXXXX')

### Get some metric data
    metrics = c.get_metric_data(['My Application'], ['Database/my_table/select', 'Database/my_table/update'], ['average_value'], '2012-03-28T15:48:00Z', '2012-03-29T15:48:00Z')

    for metric in metrics:
        if "select" in metric.name:
            print "Average Select Time: %s" % metric.average_value
        if  "update" in metric.name:
            print "Average Update Time: %s" % metric.average_value

### Handle API rate limiting
    try:
        metrics = c.get_metric_data(['My Application'], ['Database/my_table/select', 'Database/my_table/update'], ['average_value'], '2012-03-28T15:48:00Z', '2012-03-29T15:48:00Z')
    except NewRelicApiRateLimitException as e:
        sleep(e.timeout)

### List some metrics
    metrics = c.get_metric_list('123456', re='Database')
    for k,v in metrics.iteritems():
        print "Metric Name: %s" % k
        print "Available Fields: %s " % v

### Figure out what applications you have
    applications = c.view_applications()
    for application in applications:
        print "Name: %s" % application.name
        print "ID: %s" % application.app_id
        print "URL: %s" % application.url

### Delete applications (careful!)
    failed_deletions = c.delete_applications( {'app_id': 1234, 'app': 'My Application'})
    if len(failed_deletions) is 0:
        print "All applications deleted succesfully!"
```
