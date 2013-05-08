class Application(object):
    """
    A simple dumb object for easily containing the data returned from a
    "view_applications" call
    """
    def __init__(self, properties):
        super(Application, self).__init__()
        self.name = properties['name']
        self.app_id = properties['id']
        self.overview_url = properties['overview-url']
        self.servers_url = properties['servers-url']
