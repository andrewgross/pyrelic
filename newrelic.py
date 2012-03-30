import requests
import logging
from time import sleep
from lxml import etree
from StringIO import StringIO

logger = logging.getLogger(__name__)



class Client(object):
    """A Client for interacting with New Relic resources"""
    def __init__(self, account_id=None, api_key=None, proxy=None, client=None, retries=3, retry_delay=1):
        """
        Create a NewRelic REST API client
        TODO: implement proxy support
        """
        # Get Account Credentials

        if not account_id or not api_key:
            raise NewRelicCredentialException("""
                NewRelic could not find your account credentials. Pass them into the 
                Client like this:

                    client = newrelic.Client(account='12345', apikey='1234567890abcdef123456789')

                """)

        # TODO: Check if pro account

        self.headers = { 'x-api-key': api_key }
        self.proxy = proxy

    def _make_request(self, request):
        attempts = 0
        while attempts < self.retries:
            try:
                response = request()
            except (requests.ConnectionError, HTTPError) as ce:
                logger.error('Error connecting to New Relic API: {}'.format(ce))
                sleep(self.retry_delay)
                attempts += 1
            else:
                break
        if not response:
            raise NewRelicApiException
        if not str(response.status_code).startswith('2') :
            _handle_api_error(response.status_code)
        return _parse_xml(response)

    def _parse_xml(response):
        parser = etree.XMLParser(remove_blank_text=True, strip_cdata=False, ns_clean=True, recover=True)
        try:
            tree = etree.parse(StringIO(response), parser)
        except (XMLSyntaxError, ValueError):
            # The New Relic API likes to response with an unmatched <?xml version...> tag
            # We need to strip this so we can parse the xml properly
            response = ''.join(response.split('\n')[1:])
            tree = etree.parse(StringIO(response), parser)
        return tree


    def _handle_api_error(status_code):
        if 403 == status_code:
            raise NewRelicInvalidApiKeyException
        elif 404 == status_code:
            raise NewRelicUnknownApplicationException
        elif 422 == status_code:
            raise NewRelicInvalidParameterException
        else:
            raise NewRelicApiException


    def _make_get_request(uri):
        """
        Given a request add in the required parameters and return the parsed XML object. 
        """
        return _make_request(requests.get(uri, headers=self.headers, timeout=0.400))
 
    def _make_post_request(uri):
        """
        Given a request add in the required parameters and return the parsed XML object. 
        """
        return _make_request(requests.post(uri, payload, headers=self.headers, timeout=0.400))

    def view_applications(self):
        """
        Requires: account ID
        Returns: a list of Application objects
        Errors: 403 Invalid API Key
        Method: Get
        """
        uri = "https://rpm.newrelic.com/accounts/{0}/applications.xml".format(self.account_id)
        response = _make_get_request(uri)
        applications = []

        for application in response.xpath('/applications/application'):
            application_properties = {}
            for field in application:
                application_properties[field.tag] = field.text
            applications.append(Application(application_properties))
        return applications


    def delete_applications(applications):
        """
        Requires: account ID, application ID (or name).  Input shouuld be a dictionary { 'app_id': 1234 , 'app': 'My Application'}
        Returns:  list of failed deletions (if any)
        Endpoint: api.newrelic.com
        Errors: None Explicit, failed deletions will be in XML
        Method: Post
        """
        uri = "https://api.newrelic.com/api/v1/accounts/{0}/applications/delete.xml".format(self.account_id)
        payload = applications
        response = _make_post_request(uri, payload)
        failed_deletions = {}

        for application in response.xpath('/applications/application'):
            if not 'deleted' in application.xpath('result').text:
                failed_deletions['app_id'] = application.id

        return failed_deletions

    def get_application_summary_metrics():
        """
        Requires: account ID, 
        Optional: application ID, excluding this will return all application metrics 
        Restrictions: Rate limit to 1x per minute
        Endpoint: rpm.newrelic.com
        Errors: 403 Invalid API Key, 404 Unknown application
        Method: Get
        Returns: A dictionary (key = app ID) of lists (of metrics) of tuples (name, start_time, end_time, metric_value, formatted_metric_value, threshold_value)
        """
        pass

    # TODO: Dashboard HTML fragments

    # TODO: Deployment Notification

    def get_metric_names():
        """
        Requires: application ID
        Optional: Regex to filter metric names, limit of results
        Method: Get
        Restrictions: Rate limit to 1x per minute
        Errors: 
        Endpoint: api.newrelic.com
        Returns: A list of tuples, (metric name, [fields])
        """
        pass

    def get_metric_data():
        """
        Requires: account ID, list of application IDs, list of metrics, metric fields, begin_time, end_time 
        Method: Post
        Endpoint: api.newrelic.com
        Restrictions: Rate limit to 1x per minute
        Errors: 403 Invalid API key, 422 Invalid Parameters
        Returns: A list of tuples, (app name, begin_time, end_time, metric_name, [(field name, value),...])
        """
        pass


class NewRelicApiException(Exception):
    """Parent class for New Relic Exceptions"""
    def __init__(self):
        super(NewRelicApiException, self).__init__()
        pass

class NewRelicInvalidApiKeyException(NewRelicApiException):
    """docstring for NewRelicApiKeyException"""
    def __init__(self):
        super(NewRelicInvalidApiKeyException, self).__init__()
        pass

class NewRelicCredentialException(NewRelicApiException):
    """docstring for NewRelicCredentialException"""
    def __init__(self):
        super(NewRelicCredentialException, self).__init__()
        pass

class NewRelicInvalidParameterException(NewRelicApiException):
    """docstring for NewRelicInvalidParameterException"""
    def __init__(self):
        super(NewRelicInvalidParameterException, self).__init__()
        pass
                        
class NewRelicUnknownApplicationException(NewRelicApiException):
    """docstring for NewRelicUnknownApplicationException"""
    def __init__(self):
        super(NewRelicUnknownApplicationException, self).__init__()
        pass
        
class Application(object):
    def __init__(self, properties):
        super(Application, self).__init__()
        name = properties['name']
        app_id = properties['id']
        url = properties['overview-url']


