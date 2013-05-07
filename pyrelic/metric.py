class Metric(object):
    """
    An object to contain the data for one time period in a "get_metric_data"
    call. The properties are dynamic and based off the field names in the XML
    response
    """
    def __init__(self, metric):
        super(Metric, self).__init__()
        for k, v in metric.items():
            setattr(self, k, v)
        for field in metric.findall('.//field'):
            # Each field has a 'name=metric_type' section.
            # We want to have this accessible in the object by calling the
            # metric_type property of the object directly
            setattr(self, field.attrib['name'], field.text)
