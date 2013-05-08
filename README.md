# Pyrelic [![Build Status](https://travis-ci.org/andrewgross/pyrelic.png)](https://travis-ci.org/andrewgross/pyrelic)


A NewRelic Client library written in python (since not all of us use ruby).

The documentation for this library is included in the appropriate '__doc__' strings but it was derived by examining the New Relic Ruby API located at:

<https://github.com/newrelic/newrelic_api>

Unfortunately, while the documentation for their API is very solid, the implementation details are pretty sparse since they are centered around the Rails Active Resource helper library.  This made it a bit trickier to reproduce the API in python but it seems to have worked out so far (with some querks).

# Installation

```bash
pip install pyrelic
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

# License

"THE BEER-WARE LICENSE" (Revision 42):
<andrew.w.gross@gmail.com> wrote this file. As long as you retain his notice you can do whatever you want with this stuff. If we meet some day, and you think this stuff is worth it, you can buy me a beer in return. (Original from Poul-Henning Kamp)

# Future Development

Sometime soon I hope to finish implementing the last few TODO's including HTML snippets, application summary metrics and deployment notifications.  Ideally this project can be taken over and maintained by New Relic since it is obvious that they would be best to maintain their own API clients.

# Shout Outs

A special thanks to [Mingwei Gu](https://github.com/Mingweigu) for working with me to get the first version of this working as we wrapped our head around parsing the response XML.

Thanks to [Yipit](https://github.com/Yipit) for letting me divert time to this project so I could clean it up and open source it.

Thanks to [Gabriel Falcão](https://github.com/gabrielfalcao) for helping me add this to pypi.
