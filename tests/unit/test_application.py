from pyrelic import Application


def test_application_bad_initialization():
    # When I create a application object without enough data

    # Then it should raise a key error
    Application.when.called_with({}).should.throw(KeyError)


def test_application_good_initialization():
    # When I create a application object with the right data
    fake_properties = {'name': "name_foo",
                       'id': "app_id_foo",
                       'overview-url': "url_foo",
                       }
    a = Application(fake_properties)

    # Then it should transliterate appropriate object attributes
    a.name.should.be('name_foo')
    a.app_id.should.be('app_id_foo')
    a.url.should.be('url_foo')
