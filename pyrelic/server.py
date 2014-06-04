class Server(object):
    """
    A simple dumb object for easily containing the data returned from a
    "view_servers" call
    """
    def __init__(self, properties):
        self.overview_url = properties['overview-url']
        self.hostname = properties['hostname']
        self.server_id = properties['id']
