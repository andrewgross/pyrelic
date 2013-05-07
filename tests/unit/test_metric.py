from mock import Mock, MagicMock

from pyrelic import Metric


def test_metric_initialization():
    fake_items = [("foo", "bar"), ("foobar", "baz")]

    fake_xpath = Mock(attrib={"name": "xpath_values"}, text="xpath_text")

    metric_mock = Mock()
    metric_mock.items = MagicMock(return_value=fake_items)
    metric_mock.findall = MagicMock(return_value=[fake_xpath])

    # When I create a metric with xpath
    m = Metric(metric_mock)

    # Then it should assign object attributes
    m.xpath_values.should.be("xpath_text")
    m.foo.should.be("bar")
    m.foobar.should.be("baz")
