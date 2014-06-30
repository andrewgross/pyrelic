from pyrelic import Threshold


def test_threshold_bad_initialization():
    """
    Create Threshold object with bad data
    """
    # When I create a threshold object without enough data

    # Then it should raise a key error
    Threshold.when.called_with({}).should.throw(KeyError)


def test_threshold_good_initialization():
    """
    Create Threshold object with good data
    """
    # When I create a threshold object with the right data
    fake_properties = {'name': "name_foo",
                       'metric_value': "metric_value_foo",
                       'formatted_metric_value': "formatted_metric_value_foo",
                       'threshold_value': "threshold_value_foo",
                       'begin_time': "begin_time_foo",
                       'end_time': "end_time_foo"
                       }
    t = Threshold(fake_properties)

    # Then it should assign object attributes
    t.name.should.be("name_foo")
    t.metric_value.should.be('metric_value_foo')
    t.formatted_metric_value.should.be('formatted_metric_value_foo')
    t.threshold_value.should.be('threshold_value_foo')
    t.begin_time.should.be('begin_time_foo')
    t.end_time.should.be('end_time_foo')
