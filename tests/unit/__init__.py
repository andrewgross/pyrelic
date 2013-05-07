import re
import httpretty
import requests
import datetime

from nose.tools import nottest

from pyrelic import (Client,
                     NewRelicCredentialException,
                     NewRelicApiException,
                     NewRelicInvalidApiKeyException,
                     NewRelicUnknownApplicationException,
                     NewRelicInvalidParameterException)

NEW_RELIC_URI_REGEX = re.compile(".*.newrelic.com/.*")


# Client Initialization
def test_client_account_id():
    # When I create a client without a client id

    # Then it should fail with a NewRelicCredentialException
    Client.when.called_with(account_id=None)\
        .should.throw(NewRelicCredentialException)


def test_client_api_key():
    # When I create a client without an api_key

    # Then it should fail with a NewRelicCredentialException
    Client.when.called_with(api_key=None)\
        .should.throw(NewRelicCredentialException)


def test_client_proxy_string():
    # When I create a client with a proxy as a string
    proxy = "baz:1234"
    c = Client(account_id="foo", api_key="bar", proxy=proxy)

    # Then the Client should create the proxy config as a dictionary
    c.proxy.should.be({"http": proxy, "https": proxy})


def test_client_proxy_dict():
    # When I create a client with a proxy as a string
    proxy = {"baz": "1234"}
    c = Client(account_id="foo", api_key="bar", proxy=proxy)

    # Then the Client should create the proxy config as a dictionary
    c.proxy.should.be(proxy)


# _make_request Tests
@nottest  # Skip until we can properly simulate timeouts
@httpretty.activate
def test_make_request_timeout():
    httpretty.register_uri(httpretty.GET, NEW_RELIC_URI_REGEX,
                           body=None,
                           )
    # When I make an API request and receive no response
    c = Client(account_id="foo", api_key="bar")

    # Then I should raise a NewRelicApiException
    c._make_request.when.called_with(requests.get, "http://rpm.newrelic.com", timeout=0.05, retries=1)\
        .should.throw(NewRelicApiException)


@httpretty.activate
def test_make_request_non_200():
    httpretty.register_uri(httpretty.GET, NEW_RELIC_URI_REGEX,
                           body=None,
                           status=400
                           )
    # When I make an API request and receive a 400
    c = Client(account_id="foo", api_key="bar")

    # Then I should raise a NewRelicApiException
    c._make_request.when.called_with(requests.get, "http://rpm.newrelic.com")\
        .should.throw(NewRelicApiException)


# Handle API Error
def test_handle_api_error_400():
    # When I make an API request and receive a 400
    c = Client(account_id="foo", api_key="bar")

    # Then I should raise a NewRelicApiException
    c._handle_api_error.when.called_with(400, "foobar")\
        .should.throw(NewRelicApiException)


def test_handle_api_error_403():
    # When I make an API request and receive a 400
    c = Client(account_id="foo", api_key="bar")

    # Then I should raise a NewRelicApiException
    c._handle_api_error.when.called_with(403, "foobar")\
        .should.throw(NewRelicInvalidApiKeyException)


def test_handle_api_error_404():
    # When I make an API request and receive a 400
    c = Client(account_id="foo", api_key="bar")

    # Then I should raise a NewRelicApiException
    c._handle_api_error.when.called_with(404, "foobar")\
        .should.throw(NewRelicUnknownApplicationException)


def test_handle_api_error_422():
    # When I make an API request and receive a 400
    c = Client(account_id="foo", api_key="bar")

    # Then I should raise a NewRelicApiException
    c._handle_api_error.when.called_with(422, "foobar")\
        .should.throw(NewRelicInvalidParameterException)


# API Rate Limiting
def test_api_rate_limit_exceeded_no_previous_call():
    # When I make an API request with a rate limit and I am have no previous requests
    def foobar():
        pass

    c = Client(account_id="foo", api_key="bar")

    # Then I should not receive a API Rate Limit Timeout
    c._api_rate_limit_exceeded(foobar).should.be.false


def test_api_rate_limit_exceeded_outside_window():
    # When I make an API request with a rate limit and I am have a previous
    # request outside of the time window
    def foobar():
        pass

    c = Client(account_id="foo", api_key="bar")
    c.foobar_window = datetime.datetime.now() - datetime.timedelta(seconds=61)

    # Then I should not receive a API Rate Limit Timeout
    c._api_rate_limit_exceeded(foobar, window=60).should.be.false


def test_api_rate_limit_exceeded_inside_window():
    # When I make an API request with a rate limit and I am have a previous
    # request inside of the time window
    def foobar():
        pass

    c = Client(account_id="foo", api_key="bar")
    c.foobar_window = datetime.datetime.now() - datetime.timedelta(seconds=59)

    # Then I should receive a wait time
    c._api_rate_limit_exceeded(foobar, window=60).should.equal(1)
