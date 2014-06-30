from pyrelic import Server


def test_server_bad_initialization():
    """
    Create a server with bad data
    """
    # When I create a server object without enough data

    # Then it should raise a key error
    Server.when.called_with({}).should.throw(KeyError)


def test_server_good_initialization():
    """
    Create a server with good data
    """
    # When I create a server object with the right data
    fake_properties = {'overview-url': "overview_url_foo",
                       'hostname': "hostname_foo",
                       'id': "server_id_foo",
                       }
    s = Server(fake_properties)

    # Then it should transliterate appropriate object attributes
    s.overview_url.should.equal('overview_url_foo')
    s.hostname.should.equal('hostname_foo')
    s.server_id.should.equal('server_id_foo')