import requests
import logging
import sys

from time import time
from time import sleep
from lxml import etree
from lxml.etree import XMLSyntaxError

logger = logging.getLogger(__name__)

class Client(object):
    """
    A Client for interacting with New Relic resources
    """
    def __init__(self, account_id=None, api_key=None, proxy=None, retries=3, retry_delay=1, timeout=1.000, debug=False):
        """
        Create a NewRelic REST API client
        Required Parameters: account_id, api_key
        Optional Parameters: proxy, retries, retry_delay, timeout, debug
        """
        # Get Account Credentials

        if not account_id or not api_key:
            raise NewRelicCredentialException("""
                NewRelic could not find your account credentials. Pass them into the 
                Client like this:

                    client = pyrelic.Client(account='12345', apikey='1234567890abcdef123456789')

                """)

        # TODO: Check if pro account (For now we can assume a pro account since that is the main use case)
        self.account_id = account_id
        self.api_key = api_key
        self.headers = { 'x-api-key': api_key }
        self.retries = retries
        self.retry_delay = retry_delay
        self.timeout = timeout

        # Figure out what kind of information we were given for proxy settings (if any)
        self.proxy = proxy
        if type(proxy) is 'str' and ':' in proxy:
            self.proxy = {
                          "http" : proxy,
                          "https" : proxy,
                         }
        elif type(proxy) is 'dict':
            self.proxy = proxy

        # Set our debug state. For now this just prints the request string,
        # additional debugging may be added in the future although most debugging can be
        # done by examining the exceptions returned
        self.debug = debug
        if self.debug is True:
            self.config = {'verbose': sys.stderr}
        else:
            self.config = {}

    def _make_request(self, request, uri, **kwargs):
        """
        This is final step of calling out to the remote API.  We set up our headers, proxy, debugging etc.
        The only things in **kwargs are parameters that are overridden on an API method basis (like timeout)

        We have a simple attempt/while loop to implement retries w/ delays to avoid the brittleness of talking
        over the network to remote services.  These settings can be overridden when creating the Client.

        We catch the 'requests' exceptions during our retries and eventually raise our own NewRelicApiException
        if we are unsuccessful in contacting the New Relic API. Additionally we process any non 200 HTTP Errors
        and raise an appropriate exception according to the New Relic API documentation.  

        Finally we pass back the response text to our XML parser since we have no business parsing that here. It could
        be argued that handling API exceptions/errors shouldn't belong in this method but it is simple enough
        for now. 
        """
        attempts = 1
        response = None
        while attempts <= self.retries:
            try:
                response = request(uri, config=self.config, headers=self.headers, proxies=self.proxy, **kwargs)
            except (requests.ConnectionError, requests.HTTPError) as ce:
                logger.error('Error connecting to New Relic API: {}'.format(ce))
                sleep(self.retry_delay)
                attempts += 1
            else:
                break
        if not response and attempts > 1:
            raise NewRelicApiException('Unable to connect to the NewRelic API after {} attempts'.format(attempts))
        if not response:
            raise NewRelicApiException('No response received from NewRelic API')
        if not str(response.status_code).startswith('2'):
            self._handle_api_error(response.status_code)
        return self._parse_xml(response.text)

    def _parse_xml(self, response):
        """
        Run our XML parser (lxml in this case) over our response text.  Lxml doesn't enjoy having xml/encoding
        information in the header so we strip that out if necessary. We return a parsed XML object that can be
        used by the calling API method and massaged into a more appropriate format.
        """
        parser = etree.XMLParser(remove_blank_text=True, strip_cdata=False, ns_clean=True, recover=True)
        if response.startswith('<?xml version="1.0" encoding="UTF-8"?>'):
            response = '\n'.join(response.split('\n')[1:])
        tree = etree.XML(response, parser)
        return tree

    def _handle_api_error(self, status_code, error_message):
        """
        New Relic cheerfully provides expected API error codes depending on your API call deficiencies so we
        convert these to exceptions and raise them for the user to handle as they see fit.
        """
        if 403 == status_code:
            raise NewRelicInvalidApiKeyException(error_message)
        elif 404 == status_code:
            raise NewRelicUnknownApplicationException(error_message)
        elif 422 == status_code:
            raise NewRelicInvalidParameterException(error_message)
        else:
            raise NewRelicApiException(error_message)


    def _make_get_request(self, uri, parameters=None, timeout=None):
        """
        Given a request add in the required parameters and return the parsed XML object. 
        """
        if not timeout:
            timeout = self.timeout
        return self._make_request(requests.get, uri, params=parameters, timeout=timeout)
 
    def _make_post_request(self, uri, payload, timeout=None):
        """
        Given a request add in the required parameters and return the parsed XML object. 
        """
        if not timeout:
            timeout = self.timeout
        return self._make_request(requests.post, uri, payload, timeout=timeout)

    def _api_rate_limit_exceeded(self, api_call, window=60):
        """
        We want to keep track of the last time we sent a request to the NewRelic API, but only for certain operations.
        This method will dynamically add an attribute to the Client class with a unix timestamp with the name of the API api_call
        we make so that we can check it later.  We return the amount of time until we can perform another API call so that appropriate waiting
        can be implemented.
        """
        # The structure of this could be handled a little bit more cleanly using the python datetime libraries 
        current_call_time = int(time())
        try:
            previous_call_time = getattr(self, api_call.__name__ + ".window")
            # Force the calling of our property so we can handle not having set it yet.
            previous_call_time.__str__
        except AttributeError:
            previous_call_time = 0
        
        if current_call_time - previous_call_time > window:
            setattr(self, api_call.__name__ + ".window", current_call_time)
            return False
        else:
            return window - (current_call_time - previous_call_time)


    def view_applications(self):
        """
        Requires: account ID (taken from Client object)
        Returns: a list of Application objects
        Errors: 403 Invalid API Key
        Method: Get
        """
        uri = "https://rpm.newrelic.com/accounts/{0}/applications.xml".format(self.account_id)
        response = self._make_get_request(uri)
        applications = []

        for application in response.xpath('/applications/application'):
            application_properties = {}
            for field in application:
                application_properties[field.tag] = field.text
            applications.append(Application(application_properties))
        return applications


    def delete_applications(self, applications):
        """
        Requires: account ID, application ID (or name).  Input should be a dictionary { 'app_id': 1234 , 'app': 'My Application'}
        Returns:  list of failed deletions (if any)
        Endpoint: api.newrelic.com
        Errors: None Explicit, failed deletions will be in XML
        Method: Post
        """
        uri = "https://api.newrelic.com/api/v1/accounts/{0}/applications/delete.xml".format(self.account_id)
        payload = applications
        response = self._make_post_request(uri, payload)
        failed_deletions = {}

        for application in response.xpath('/applications/application'):
            if not 'deleted' in application.xpath('result').text:
                failed_deletions['app_id'] = application.id

        return failed_deletions

    def get_application_summary_metrics(self, application_ids):
        """
        Requires: account ID, 
        Optional: list of application IDs, excluding this will return all application metrics 
        Restrictions: Rate limit to 1x per minute
        Endpoint: rpm.newrelic.com
        Errors: 403 Invalid API Key, 404 Unknown application
        Method: Get
        Returns: A dictionary (key = app ID) of lists (of metrics) of tuples (name, start_time, end_time, metric_value, formatted_metric_value, threshold_value)
        """
        pass

    def get_dashboard_html_fragment(self):
        # TODO: Dashboard HTML fragments
        pass
    
    def notify_deployment(self):
        # TODO: Deployment Notification
        pass

    def get_metric_names(self, app_id, re=None, limit=5000):
        """
        Requires: application ID
        Optional: Regex to filter metric names, limit of results
        Returns: A dictionary, key => metric name, value => list of fields available for a given metric
        Method: Get
        Restrictions: Rate limit to 1x per minute
        Errors: 403 Invalid API Key, 422 Invalid Parameters
        Endpoint: api.newrelic.com
        """
        # Make sure we play it slow
        if self._api_rate_limit_exceeded(self.get_metric_data):
            raise NewRelicApiRateLimitException(str(self._api_rate_limit_exceeded(self.get_metric_data)))

        # Construct our GET request parameters into a nice dictionary
        parameters = {'re': re, 'limit': limit}

        uri = "https://api.newrelic.com/api/v1/applications/{0}/metrics.xml".format(str(app_id))
        # A longer timeout is needed due to the amount of data that can be returned without a regex search
        response = self._make_get_request(uri, parameters=parameters, timeout=5.000)
        
        # Parse the response. It seems clearer to return a dict of metrics/fields instead of a list of metric objects.
        # It might be more consistent with the retrieval of metric data to make them objects but since the attributes
        # in each type of metric object are different (and we aren't going to make heavyweight objects) we don't want to. 
        metrics = {}
        for metric in response.xpath('/metrics/metric'):
            fields = []
            for field in metric.xpath('fields/field'):
                fields.append(field.get('name'))
            metrics[metric.get('name')] = fields
        return metrics

    def get_metric_data(self, applications, metrics, field, begin, end, summary=False):
        """
        Requires: account ID, list of application IDs, list of metrics, metric fields, begin, end 
        Method: Get
        Endpoint: api.newrelic.com
        Restrictions: Rate limit to 1x per minute
        Errors: 403 Invalid API key, 422 Invalid Parameters
        Returns: A list of metric objects, each will have information about its start/end time, application, metric name and 
                 any associated values
        """
        # TODO: it may be nice to have some helper methods that make it easier to query by common time frames based off
        #       the time period folding of the metrics returned by the New Relic API.

        # Make sure we aren't going to hit an API timeout
        if self._api_rate_limit_exceeded(self.get_metric_data):
            raise NewRelicApiRateLimitException(str(self._api_rate_limit_exceeded(self.get_metric_data)))

        # Just in case the API needs parameters to be in order
        parameters = {}

        # Figure out what we were passed and set our parameter correctly
        # TODO: allow querying by something other than an application name/id, such as server id or agent id        
        try:
            int(applications[0])
        except ValueError:
            app_string = "app"
        else:
            app_string = "app_id"

        if len(applications) > 1:
            app_string = app_string + "[]"

        # Set our parameters
        parameters[app_string] = applications
        parameters['metrics[]'] = metrics
        parameters['field'] = field
        parameters['begin'] = begin
        parameters['end'] = end
        parameters['summary'] = int(summary)

        uri = "https://api.newrelic.com/api/v1/accounts/{0}/metrics/data.xml".format(str(self.account_id))
        # A longer timeout is needed due to the amount of data that can be returned
        response = self._make_get_request(uri, parameters=parameters, timeout=5.000)

        # Parsing our response into lightweight objects and creating a list.  The dividing factor is the time period
        # covered by the metric , there should be no overlaps in time. 
        metrics = []
        for metric in response.xpath('/metrics/metric'):
            metrics.append(Metric(metric))
        return metrics

# Exceptions

class NewRelicApiException(Exception):
    def __init__(self, message):
        super(NewRelicApiException, self).__init__()
        print message

class NewRelicInvalidApiKeyException(NewRelicApiException):
    def __init__(self, message):
        super(NewRelicInvalidApiKeyException, self).__init__(message)
        pass

class NewRelicCredentialException(NewRelicApiException):
    def __init__(self, message):
        super(NewRelicCredentialException, self).__init__(message)
        pass

class NewRelicInvalidParameterException(NewRelicApiException):
    def __init__(self, message):
        super(NewRelicInvalidParameterException, self).__init__(message)
        pass
                        
class NewRelicUnknownApplicationException(NewRelicApiException):
    def __init__(self, message):
        super(NewRelicUnknownApplicationException, self).__init__(message)
        pass

class NewRelicApiRateLimitException(NewRelicApiException):
    def __init__(self, message):
        super(NewRelicApiRateLimitException, self).__init__(message)
        self.timeout = message
        
# Data Classes
        
class Application(object):
    """
    A simple dumb object for easily containing the data returned from a "view_applications" call
    """
    def __init__(self, properties):
        super(Application, self).__init__()
        self.name = properties['name']
        self.app_id = properties['id']
        self.url = properties['overview-url']

class Metric(object):
    """
    An object to contain the data for one time period in a "get_metric_data" call. The properties are
    dynamic and based off the field names in the XML response
    """
    def __init__(self, metric):
        super(Metric, self).__init__()
        for k,v in metric.items():
            setattr(self, k, v)
        for field in metric.xpath('field'):
            # Each field has a 'name=metric_type' section. We want to have this accessible in the object by calling the 
            # metric_type property of the object directly  
            setattr(self, field.values()[0], field.text)


