import pyrelic.packages.requests as requests
import httpretty

from nose.tools import nottest

from pyrelic import BaseClient


@nottest  # Skip until we can properly simulate timeouts
@httpretty.activate
def test_make_request_timeout():
    """
    Remote calls should time out
    """
    httpretty.register_uri(httpretty.GET, "www.example.com",
                           body=None,
                           )
    # When I make an API request and receive no response
    c = BaseClient()

    # Then I should raise a NewRelicApiException
    c._make_request.when.called_with(requests.get,
                                     "http://www.example.com",
                                     timeout=0.05,
                                     retries=1)\
     .should.throw(requests.RequestException)


@httpretty.activate
def test_make_request_non_200():
    """
    Bad HTTP Responses should throw an error
    """
    httpretty.register_uri(httpretty.GET, "http://foobar.com",
                           body="123", status=400)
    # When I make an API request and receive a 400
    c = BaseClient()

    # Then I should raise the appropriate requests exception
    c._make_request.when.called_with(requests.get,
                                     "http://foobar.com")\
     .should.throw(requests.RequestException)


def test_client_proxy_string():
    """
    Base Client should parse proxy strings
    """
    # When I create a client with a proxy as a string
    proxy = "baz:1234"
    c = BaseClient(proxy=proxy)

    # Then the Client should create the proxy config as a dictionary
    c.proxy.should.equal({"http": proxy, "https": proxy})


def test_client_proxy_dict():
    """
    Base Client should parse proxy dicts
    """
    # When I create a client with a proxy as a dict
    proxy = {"baz": "1234"}
    c = BaseClient(proxy=proxy)

    # Then the Client should create the proxy config as a dictionary
    c.proxy.should.equal(proxy)
