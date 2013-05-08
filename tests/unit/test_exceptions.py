from pyrelic import NewRelicApiRateLimitException


def test_api_rate_limit_message():
    # When I create an api_rate_limit exception
    e = NewRelicApiRateLimitException("60")

    # It should have a timeout field with the remaining wait time
    e.timeout.should.be("60")
