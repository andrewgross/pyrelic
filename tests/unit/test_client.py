import datetime
import httpretty
import re

from mock import Mock

from pyrelic import (Client,
                     NewRelicCredentialException,
                     NewRelicApiException,
                     NewRelicApiRateLimitException,
                     NewRelicInvalidApiKeyException,
                     NewRelicUnknownApplicationException,
                     NewRelicInvalidParameterException)

from ..fixtures.sample_responses import (METRIC_DATA_SAMPLE,
                                         METRIC_NAMES_SAMPLE,
                                         VIEW_APPLICATIONS_SAMPLE,
                                         THRESHOLD_VALUES_SAMPLE,
                                         DELETE_APPLICATION_SUCCESS_SAMPLE,
                                         VIEW_SERVERS_SAMPLE,
                                         DELETE_SERVERS_SUCCESS_SAMPLE,
                                         DELETE_SERVERS_FAILURE_SAMPLE,
                                         NOTIFY_DEPLOYMENT_SUCCESS
                                         )

NEW_RELIC_REGEX = re.compile(".*.newrelic.com/.*")


# Client Initialization
def test_client_account_id():
    """
    Create Client without ID
    """
    # When I create a client without a client id

    # Then it should fail with a NewRelicCredentialException
    Client.when.called_with(account_id=None)\
        .should.throw(NewRelicCredentialException)


def test_client_api_key():
    """
    Create Client without API Key
    """
    # When I create a client without an api_key

    # Then it should fail with a NewRelicCredentialException
    Client.when.called_with(api_key=None)\
        .should.throw(NewRelicCredentialException)


# Handle API Error
def test_handle_api_error_400():
    """
    Client should error on HTTP 400
    """
    # When I make an API request and receive a 400
    c = Client(account_id="foo", api_key="bar")
    response = Mock(status_code=400)
    error = Mock(message="foo", response=response)

    # Then I should raise a NewRelicApiException
    c._handle_api_error.when.called_with(error)\
        .should.throw(NewRelicApiException)


def test_handle_api_error_403():
    """
    Client should raise API key error on HTTP 403
    """
    # When I make an API request and receive a 403
    c = Client(account_id="foo", api_key="bar")
    response = Mock(status_code=403)
    error = Mock(message="foo", response=response)

    # Then I should raise a NewRelicApiException
    c._handle_api_error.when.called_with(error)\
        .should.throw(NewRelicInvalidApiKeyException)


def test_handle_api_error_404():
    """
    Client should raise Unknown Application error on HTTP 404
    """
    # When I make an API request and receive a 404
    c = Client(account_id="foo", api_key="bar")
    response = Mock(status_code=404)
    error = Mock(message="foo", response=response)

    # Then I should raise a NewRelicApiException
    c._handle_api_error.when.called_with(error)\
        .should.throw(NewRelicUnknownApplicationException)


def test_handle_api_error_422():
    """
    Client should raise Invalid Parameter error on HTTP 422
    """
    # When I make an API request and receive a 422
    c = Client(account_id="foo", api_key="bar")
    response = Mock(status_code=422)
    error = Mock(message="foo", response=response)

    # Then I should raise a NewRelicApiException
    c._handle_api_error.when.called_with(error)\
        .should.throw(NewRelicInvalidParameterException)


# API Rate Limiting
def test_api_rate_limit_exceeded_no_previous_call():
    """
    API Rate limit should not trigger on first call
    """
    # When I make an API request with a rate limit and I am have no previous requests
    def foobar():
        pass

    c = Client(account_id="foo", api_key="bar")

    # Then I should not receive a API Rate Limit Timeout
    c._api_rate_limit_exceeded(foobar).should.be.false


def test_api_rate_limit_exceeded_outside_window():
    """
    API Rate limit should not trigger outside of rate limit window
    """
    # When I make an API request with a rate limit and I am have a previous
    # request outside of the time window
    def foobar():
        pass

    c = Client(account_id="foo", api_key="bar")
    c.foobar_window = datetime.datetime.now() - datetime.timedelta(seconds=61)

    # Then I should not receive a API Rate Limit Timeout
    c._api_rate_limit_exceeded(foobar, window=60).should.be.false


def test_api_rate_limit_exceeded_inside_window():
    """
    API Rate limit should trigger inside of rate limit window
    """
    # When I make an API request with a rate limit and I am have a previous
    # request inside of the time window
    def foobar():
        pass

    c = Client(account_id="foo", api_key="bar")
    c.foobar_window = datetime.datetime.now() - datetime.timedelta(seconds=59)

    # Then I should receive a wait time
    c._api_rate_limit_exceeded.when.called_with(foobar, window=60)\
        .should.throw(NewRelicApiRateLimitException)


@httpretty.activate
def test_view_applications():
    """
    Client should be able to list Applications
    """
    httpretty.register_uri(httpretty.GET, NEW_RELIC_REGEX,
                           body=VIEW_APPLICATIONS_SAMPLE,
                           status=200
                           )

    # When I make an API request to view applications
    c = Client(account_id="1", api_key="2")

    # Then I should receive an array of Applications
    c.view_applications().should.be.an('list')
    c.view_applications()[0].should.be.an('pyrelic.Application')


@httpretty.activate
def test_get_metric_names():
    """
    Client should be able to list Metric names
    """
    httpretty.register_uri(httpretty.GET,
                           NEW_RELIC_REGEX,
                           body=METRIC_NAMES_SAMPLE,
                           status=200
                           )

    # When I make an API request to view applications
    c = Client(account_id="1", api_key="2")

    # Then I should receive an array of Applications
    result = c.get_metric_names("foo")
    result.should.be.a('dict')
    result.should.have.key('WebTransaction')
    result['WebTransaction'].should.be.a('list')
    result['WebTransaction'].should.have.length_of(8)


@httpretty.activate
def test_get_metric_data():
    """
    Client should be able to list Metrics
    """
    httpretty.register_uri(httpretty.GET,
                           NEW_RELIC_REGEX,
                           body=METRIC_DATA_SAMPLE,
                           status=200
                           )
    # When I make an API request to get metric data
    c = Client(account_id="1", api_key="2")

    # Then I should receive an array of Metrics
    result = c.get_metric_data("foo", "bar", "baz", "foobar", "foobaz")
    result.should.be.a('list')
    result[0].should.be.a('pyrelic.Metric')


@httpretty.activate
def test_get_threshold_values():
    """
    Client should be able to list Thresholds
    """
    httpretty.register_uri(httpretty.GET,
                           NEW_RELIC_REGEX,
                           body=THRESHOLD_VALUES_SAMPLE,
                           status=200
                           )
    # When I make an API request to view threshold values
    c = Client(account_id="1", api_key="2")

    # Then I should receive an array of Threshold values
    result = c.get_threshold_values("foo")
    result.should.be.a('list')
    result[0].should.be.a('pyrelic.Threshold')


@httpretty.activate
def test_delete_applications():
    """
    Client should be able to delete Applications
    """
    httpretty.register_uri(httpretty.POST,
                           NEW_RELIC_REGEX,
                           body=DELETE_APPLICATION_SUCCESS_SAMPLE,
                           status=200
                           )
    # When I make an API request to view threshold values
    c = Client(account_id="1", api_key="2")

    # Then I should receive an array of Threshold values
    result = c.delete_applications({"app_id": "1234"})
    result.should.have.length_of(1)


@httpretty.activate
def test_view_servers():
    """
    Client should be able to list Servers
    """
    httpretty.register_uri(httpretty.GET, NEW_RELIC_REGEX,
                           body=VIEW_SERVERS_SAMPLE,
                           status=200
                           )

    # When I make an API request to view servers
    c = Client(account_id="1", api_key="2")

    # Then I should receive an array of Servers
    result = c.view_servers()
    result.should.be.an('list')
    result.should.have.length_of(2)

    result[0].should.be.an('pyrelic.Server')
    result[0].overview_url.should.equal('https://rpm.newrelic.com/accounts/1/servers/555')
    result[0].hostname.should.equal('my-hostname.newrelic.com')
    result[0].server_id.should.equal('555')

    result[1].should.be.an('pyrelic.Server')
    result[1].overview_url.should.equal('https://rpm.newrelic.com/accounts/1/servers/556')
    result[1].hostname.should.equal('my-hostname-2.newrelic.com')
    result[1].server_id.should.equal('556')



@httpretty.activate
def test_delete_servers_success():
    """
    Client should be able to delete Servers
    """
    httpretty.register_uri(httpretty.DELETE,
                           NEW_RELIC_REGEX,
                           body=DELETE_SERVERS_SUCCESS_SAMPLE,
                           status=200
                           )
    # When I make an API request to delete a server
    c = Client(account_id="1", api_key="2")
    result = c.delete_servers(server_id="123456")

    # Then I should receive an array of failed deletions
    result.should.equal([])


@httpretty.activate
def test_delete_servers_failure():
    """
    Client should be able return failed server deletions
    """
    httpretty.register_uri(httpretty.DELETE,
                           NEW_RELIC_REGEX,
                           body=DELETE_SERVERS_FAILURE_SAMPLE,
                           status=200
                           )
    # When I make an API request to delete a server
    c = Client(account_id="1", api_key="2")
    result = c.delete_servers(server_id="123456")

    # Then I should receive an array of failed deletions
    result.should.equal([{'server_id': '123456'}])

@httpretty.activate
def test_notify_deployment_failure():
    """
    Client should fail to notify_deployment with bad data
    """
    httpretty.register_uri(httpretty.POST,
                           NEW_RELIC_REGEX,
                           body=NOTIFY_DEPLOYMENT_SUCCESS,
                           status=200
                           )
    # When I make an API request to notify of deployment with no arguments
    c = Client(account_id="1", api_key="2")

    # Then I should receive a failure
    c.notify_deployment.when.called_with(None).should.throw(NewRelicInvalidParameterException)


@httpretty.activate
def test_notify_deployment_by_id_success():
    """
    Client should be able to notify deployments with application id
    """
    httpretty.register_uri(httpretty.POST,
                           NEW_RELIC_REGEX,
                           body=NOTIFY_DEPLOYMENT_SUCCESS,
                           status=200
                           )
    # When I make an API request to notify of deployment
    c = Client(account_id="1", api_key="2")

    # Then I should receive a valid response
    result = c.notify_deployment(application_id=123, description='description',
                                 revision='1.2.3', user='stevemac',
                                 changelog='orange')

    result.should.be.an('dict')

    result.should.have.key('account-id')
    result['account-id'].should.equal('123')

    result.should.have.key('agent-id')
    result['agent-id'].should.equal('456')


@httpretty.activate
def test_notify_deployment_by_name_success():
    """
    Client should be able to notify deployments with application name
    """
    httpretty.register_uri(httpretty.POST,
                           NEW_RELIC_REGEX,
                           body=NOTIFY_DEPLOYMENT_SUCCESS,
                           status=200
                           )
    # When I make an API request to notify of deployment
    c = Client(account_id="1", api_key="2")

    # Then I should receive a valid response
    result = c.notify_deployment(application_name=123, description='description',
                                 revision='1.2.3', user='stevemac',
                                 changelog='orange')

    result.should.be.an('dict')

    result.should.have.key('account-id')
    result['account-id'].should.equal('123')

    result.should.have.key('agent-id')
    result['agent-id'].should.equal('456')

