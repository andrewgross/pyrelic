import requests
import httpretty

from nose.tools import nottest

from pyrelic import BaseClient


# _make_request Tests
@nottest  # Skip until we can properly simulate timeouts
@httpretty.activate
def test_make_request_timeout():
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
    httpretty.register_uri(httpretty.GET, "https://www.github.com",
                           body=None,
                           status=400
                           )
    # When I make an API request and receive a 400
    c = BaseClient()

    # Then I should raise the appropriate requests exception
    c._make_request.when.called_with(requests.get,
                                     "https://www.github.com")\
     .should.throw(requests.HTTPError)


def test_client_proxy_string():
    # When I create a client with a proxy as a string
    proxy = "baz:1234"
    c = BaseClient()

    # Then the Client should create the proxy config as a dictionary
    c._normalize_proxy.should.be({"http": proxy, "https": proxy})


def test_client_proxy_dict():
    # When I create a client with a proxy as a string
    proxy = {"baz": "1234"}
    c = BaseClient()

    # Then the Client should create the proxy config as a dictionary
    c._normalize_proxy.should.be(proxy)
