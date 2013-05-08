# Pyrelic [![Build Status](https://travis-ci.org/andrewgross/pyrelic.png)](https://travis-ci.org/andrewgross/pyrelic)


A NewRelic Client library written in python (since not all of us use ruby).

The documentation for this library is included in the appropriate `__doc__` strings but it was derived by examining the [New Relic Ruby API](https://github.com/newrelic/newrelic_api).

Unfortunately, while the documentation for their API is very solid, the implementation details are pretty sparse since they are centered around the Rails Active Resource helper library.  This made it a bit trickier to reproduce the API in python but it seems to have worked out so far (with some querks).

# Installation
```bash
$ pip install pyrelic
```
# Examples

```python
from pyrelic import Client
from time import sleep

c = Client(account_id='12345', api_key='1234567890abcdef1234567890abcdef')

# Get some metric data
metrics = c.get_metric_data(['My Application'], ['Database/my_table/select', 'Database/my_table/update'], ['average_value'], '2012-03-28T15:48:00Z', '2012-03-29T15:48:00Z')

for metric in metrics:
    if metric.name contains "select":
        print "Average Select Time: %s" % metric.average_value
    if metric.name contains "update":
        print "Average Update Time: %s" % metric.average_value

# Careful of API timeouts!
try:
    metrics = c.get_metric_data(['My Application'], ['Database/my_table/select', 'Database/my_table/update'], ['average_value'], '2012-03-28T15:48:00Z', '2012-03-29T15:48:00Z')
except NewRelicApiRateLimitException as e:
    sleep(e.timeout)

# List some metrics
metrics = c.get_metric_list('123456', re='Database')

for k,v in metrics.iteritems():
    print "Metric Name: %s" % k
    print "Available Fields: %s " % v

# Figure out what applications you have
applications = c.view_applications()

for application in applications:
    print "Name: %s" % application.name
    print "ID: %s" % application.app_id
    print "URL: %s" % application.url

# Delete your application
failed_deletions = c.delete_applications( {
                                           'app_id': 1234,
                                           'app': 'My Application'
                                          })

if len(failed_deletions) is 0:
    print "All applications deleted succesfully!"
```


# How to contribute

1. Fork it
2. Create your feature branch (`git checkout -b my-new-feature`)
3. Run the tests before making any changes (`make unit`)
4. Commit your changes (`git commit -am 'Add some feature'`)
5. Push to the branch (`git push origin my-new-feature`)
6. Create new Pull Request


# Contributors

[Ryan Gooler](https://github.com/jippen)
