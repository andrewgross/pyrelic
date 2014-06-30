from pyrelic import Application


def test_application_bad_initialization():
    """
    Create an Application Object with bad arguments
    """

    # When I create a application object without enough data

    # Then it should raise a key error
    Application.when.called_with({}).should.throw(KeyError)


def test_application_good_initialization():
    """
    Create an Application Object with proper arguments
    """
    # When I create a application object with the right data
    fake_properties = {'name': "name_foo",
                       'id': "app_id_foo",
                       'overview-url': "overview_url_foo",
                       'servers-url': "servers_url_foo",
                       }
    a = Application(fake_properties)

    # Then it should transliterate appropriate object attributes
    a.name.should.be('name_foo')
    a.app_id.should.be('app_id_foo')
    a.overview_url.should.be('overview_url_foo')
    a.servers_url.should.be('servers_url_foo')
