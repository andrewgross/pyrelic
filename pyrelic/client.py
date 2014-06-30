import datetime

from pyrelic.packages.elementtree import ElementTree as etree

from .exceptions import (
    NewRelicApiRateLimitException,
    NewRelicApiException,
    NewRelicCredentialException,
    NewRelicInvalidApiKeyException,
    NewRelicInvalidParameterException,
    NewRelicUnknownApplicationException
)
from .application import Application
from .base_client import BaseClient
from .metric import Metric
from .threshold import Threshold
from .server import Server


class Client(BaseClient):
    """
    A Client for interacting with New Relic resources
    """
    def __init__(self, account_id=None, api_key=None, proxy=None, retries=3, retry_delay=1, timeout=1.000):
        """
        Create a NewRelic REST API client
        Required Parameters: account_id, api_key
        Optional Parameters: proxy, retries, retry_delay, timeout
        """
        super(Client, self).__init__(proxy=proxy, retries=retries, retry_delay=retry_delay, timeout=timeout)

        if not account_id or not api_key:
            raise NewRelicCredentialException("""
Pyrelic could not find your account credentials. Pass them into the
Client like this:

client = pyrelic.Client(account_id='12345', api_key='1234567890abcdef123456789')
""")

        self.account_id = account_id
        self.api_key = api_key
        self.headers = {'x-api-key': api_key}
        self._parser = self._parse_xml

    def _parse_xml(self, response):
        """
        Run our XML parser (lxml in this case) over our response text.  Lxml
        doesn't enjoy having xml/encoding information in the header so we strip
        that out if necessary. We return a parsed XML object that can be
        used by the calling API method and massaged into a more appropriate
        format.
        """
        if response.startswith('\n'):
            response = response[1:]
        tree = etree.fromstring(response)
        return tree

    def _handle_api_error(self, error):
        """
        New Relic cheerfully provides expected API error codes depending on your
        API call deficiencies so we convert these to exceptions and raise them
        for the user to handle as they see fit.
        """
        status_code = error.response.status_code
        message = error.message

        if 403 == status_code:
            raise NewRelicInvalidApiKeyException(message)
        elif 404 == status_code:
            raise NewRelicUnknownApplicationException(message)
        elif 422 == status_code:
            raise NewRelicInvalidParameterException(message)
        else:
            raise NewRelicApiException(message)

    def _api_rate_limit_exceeded(self, api_call, window=60):
        """
        We want to keep track of the last time we sent a request to the NewRelic
        API, but only for certain operations. This method will dynamically add
        an attribute to the Client class with a unix timestamp with the name of
        the API api_call we make so that we can check it later.  We return the
        amount of time until we can perform another API call so that appropriate
        waiting can be implemented.
        """
        current = datetime.datetime.now()
        try:
            previous = getattr(self, api_call.__name__ + "_window")
            # Force the calling of our property so we can
            # handle not having set it yet.
            previous.__str__
        except AttributeError:
            now = datetime.datetime.now()
            outside_window = datetime.timedelta(seconds=window+1)
            previous = now - outside_window

        if current - previous > datetime.timedelta(seconds=window):
            setattr(self, api_call.__name__ + "_window", current)
        else:
            timeout = window - (current - previous).seconds
            raise NewRelicApiRateLimitException(str(timeout))

    def view_applications(self):
        """
        Requires: account ID (taken from Client object)
        Returns: a list of Application objects
        Endpoint: rpm.newrelic.com
        Errors: 403 Invalid API Key
        Method: Get
        """
        endpoint = "https://rpm.newrelic.com"
        uri = "{endpoint}/accounts/{id}/applications.xml".format(endpoint=endpoint, id=self.account_id)
        response = self._make_get_request(uri)
        applications = []

        for application in response.findall('.//application'):
            application_properties = {}
            for field in application:
                application_properties[field.tag] = field.text
            applications.append(Application(application_properties))
        return applications

    def delete_applications(self, applications):
        """
        Requires: account ID, application ID (or name).
        Input should be a dictionary { 'app_id': 1234 , 'app': 'My Application'}
        Returns:  list of failed deletions (if any)
        Endpoint: api.newrelic.com
        Errors: None Explicit, failed deletions will be in XML
        Method: Post
        """
        endpoint = "https://api.newrelic.com"
        uri = "{endpoint}/api/v1/accounts/{account_id}/applications/delete.xml"\
              .format(endpoint=endpoint, account_id=self.account_id)
        payload = applications
        response = self._make_post_request(uri, payload)
        failed_deletions = {}

        for application in response.findall('.//application'):
            if not 'deleted' in application.findall('.//result')[0].text:
                failed_deletions['app_id'] = application.get('id')

        return failed_deletions

    def get_application_summary_metrics(self, application_ids):
        """
        Requires: account ID
        Optional: list of application IDs,
                  excluding this will return all application metrics
        Restrictions: Rate limit to 1x per minute
        Endpoint: rpm.newrelic.com
        Errors: 403 Invalid API Key, 404 Unknown application
        Method: Get
        Returns: A dictionary (key = app ID)
                 of lists (of metrics)
                 of tuples (name,
                            start_time,
                            end_time,
                            metric_value,
                            formatted_metric_value,
                            threshold_value)
        """
        raise NotImplemented

    def get_dashboard_html_fragment(self):
        raise NotImplemented

    def notify_deployment(self, application_id=None, application_name=None, description=None, revision=None, changelog=None, user=None):
        """
        Notify NewRelic of a deployment.
        http://newrelic.github.io/newrelic_api/NewRelicApi/Deployment.html

        :param description:
        :param revision:
        :param changelog:
        :param user:
        :return: A dictionary containing all of the returned keys from the API
        """

        endpoint = "https://rpm.newrelic.com"
        uri = "{endpoint}/deployments.xml".format(endpoint=endpoint)

        deploy_event = {}

        if not application_id is None:
            deploy_event['deployment[application_id]'] = application_id
        elif not application_name is None:
            deploy_event['deployment[app_name]'] = application_name
        else:
            raise NewRelicInvalidParameterException("Must specify either application_id or application_name.")

        if not description is None:
            deploy_event['deployment[description]'] = description

        if not revision is None:
            deploy_event['deployment[revision]'] = revision

        if not changelog is None:
            deploy_event['deployment[changelog]'] = changelog

        if not user is None:
            deploy_event['deployment[user]'] = user

        response = self._make_post_request(uri, deploy_event)
        result = {}

        for value in response:
            result[value.tag] = value.text

        return result

    def get_metric_names(self, agent_id, re=None, limit=5000):
        """
        Requires: application ID
        Optional: Regex to filter metric names, limit of results
        Returns: A dictionary,
                    key => metric name,
                    value => list of fields available for a given metric
        Method: Get
        Restrictions: Rate limit to 1x per minute
        Errors: 403 Invalid API Key, 422 Invalid Parameters
        Endpoint: api.newrelic.com
        """
        # Make sure we play it slow
        self._api_rate_limit_exceeded(self.get_metric_names)

        # Construct our GET request parameters into a nice dictionary
        parameters = {'re': re, 'limit': limit}

        endpoint = "https://api.newrelic.com"
        uri = "{endpoint}/api/v1/applications/{agent_id}/metrics.xml"\
              .format(endpoint=endpoint, agent_id=agent_id)

        # A longer timeout is needed due to the amount of
        # data that can be returned without a regex search
        response = self._make_get_request(uri, parameters=parameters, timeout=max(self.timeout, 5.0))

        # Parse the response. It seems clearer to return a dict of
        # metrics/fields instead of a list of metric objects. It might be more
        # consistent with the retrieval of metric data to make them objects but
        # since the attributes in each type of metric object are different
        # (and we aren't going to make heavyweight objects) we don't want to.
        metrics = {}
        for metric in response.findall('.//metric'):
            fields = []
            for field in metric.findall('.//field'):
                fields.append(field.get('name'))
            metrics[metric.get('name')] = fields
        return metrics

    def get_metric_data(self, applications, metrics, field, begin, end, summary=False):
        """
        Requires: account ID,
                  list of application IDs,
                  list of metrics,
                  metric fields,
                  begin,
                  end
        Method: Get
        Endpoint: api.newrelic.com
        Restrictions: Rate limit to 1x per minute
        Errors: 403 Invalid API key, 422 Invalid Parameters
        Returns: A list of metric objects, each will have information about its
                 start/end time, application, metric name and any associated
                 values
        """
        # TODO: it may be nice to have some helper methods that make it easier
        #       to query by common time frames based off the time period folding
        #       of the metrics returned by the New Relic API.

        # Make sure we aren't going to hit an API timeout
        self._api_rate_limit_exceeded(self.get_metric_data)

        # Just in case the API needs parameters to be in order
        parameters = {}

        # Figure out what we were passed and set our parameter correctly
        # TODO: allow querying by something other than an application name/id,
        # such as server id or agent id
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

        endpoint = "https://api.newrelic.com"
        uri = "{endpoint}/api/v1/accounts/{account_id}/metrics/data.xml"\
              .format(endpoint=endpoint, account_id=self.account_id)
        # A longer timeout is needed due to the
        # amount of data that can be returned
        response = self._make_get_request(uri, parameters=parameters, timeout=max(self.timeout, 5.0))

        # Parsing our response into lightweight objects and creating a list.
        # The dividing factor is the time period covered by the metric,
        # there should be no overlaps in time.
        metrics = []
        for metric in response.findall('.//metric'):
            metrics.append(Metric(metric))
        return metrics

    def get_threshold_values(self, application_id):
        """
        Requires: account ID, list of application ID
        Method: Get
        Endpoint: api.newrelic.com
        Restrictions: ???
        Errors: 403 Invalid API key, 422 Invalid Parameters
        Returns: A list of threshold_value objects, each will have information
                 about its start/end time, metric name, metric value, and the
                 current threshold
        """
        endpoint = "https://rpm.newrelic.com"
        remote_file = "threshold_values.xml"
        uri = "{endpoint}/accounts/{account_id}/applications/{app_id}/{xml}".format(endpoint=endpoint, account_id=self.account_id, app_id=application_id, xml=remote_file)
        response = self._make_get_request(uri)
        thresholds = []

        for threshold_value in response.findall('.//threshold_value'):
            properties = {}
            # a little ugly, but the output works fine.
            for tag, text in threshold_value.items():
                properties[tag] = text
            thresholds.append(Threshold(properties))
        return thresholds

    def view_servers(self):
        """
        Requires: account ID (taken from Client object)
        Returns: a list of Server objects
        Endpoint: api.newrelic.com
        Errors: 403 Invalid API Key
        Method: Get
        """
        endpoint = "https://api.newrelic.com"
        uri = "{endpoint}/api/v1/accounts/{id}/servers.xml".format(endpoint=endpoint, id=self.account_id)
        response = self._make_get_request(uri)
        servers = []

        for server in response.findall('.//server'):
            server_properties = {}
            for field in server:
                server_properties[field.tag] = field.text
            servers.append(Server(server_properties))
        return servers

    def delete_servers(self, server_id):
        """
        Requires: account ID, server ID
        Input should be server id
        Returns: list of failed deletions (if any)
        Endpoint: api.newrelic.com
        Errors: 403 Invalid API Key
        Method: Delete
        """
        endpoint = "https://api.newrelic.com"
        uri = "{endpoint}/api/v1/accounts/{account_id}/servers/{server_id}.xml".format(
            endpoint=endpoint,
            account_id=self.account_id,
            server_id=server_id)
        response = self._make_delete_request(uri)
        failed_deletions = []
        for server in response.findall('.//server'):
            if not 'deleted' in server.findall('.//result')[0].text:
                failed_deletions.append({'server_id': server.get('id')})

        return failed_deletions
