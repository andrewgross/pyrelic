class Threshold(object):
    """
    A simple dumb object for easily containing the data returned from a
    "threshold_values" call
    """
    def __init__(self, properties):
        super(Threshold, self).__init__()
        self.name = properties['name']
        self.metric_value = properties['metric_value']
        self.formatted_metric_value = properties['formatted_metric_value']
        self.threshold_value = properties['threshold_value']
        self.begin_time = properties['begin_time']
        self.end_time = properties['end_time']
