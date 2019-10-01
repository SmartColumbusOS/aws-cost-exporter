import datetime
import os
import boto3
import prometheus_client

from mockito import expect, when, mock, verifyNoUnwantedInteractions, any, kwargs
from pytest import mark

import aws_cost_exporter


def test_get_cost():
    now = datetime.datetime.utcnow()
    start_date, stop_date = aws_cost_exporter.get_date_range(now, 1)
    os.environ["ACCOUNT_MAPPINGS"] = '{"1234":"sandbox","2345":"prod"}'

    mock_sts = mock()
    mock_sts_return = {
        "Credentials": {
            "AccessKeyId": mock(),
            "SecretAccessKey": mock(),
            "SessionToken": mock()
        }
    }
    mock_ce = mock()
    mock_ce_return = {
        "ResultsByTime": [
            {
                "Groups": [
                    {
                        "Keys": [
                            "1234"
                        ],
                        "Metrics": {
                            "UnblendedCost": {
                                "Amount": "10"
                            }
                        }
                    },
                    {
                        "Keys": [
                            "2345"
                        ],
                        "Metrics": {
                            "UnblendedCost": {
                                "Amount": "1000"
                            }
                        }
                    }
                ]
            }
        ]
    }

    with when(boto3).client("sts").thenReturn(mock_sts), \
            when(mock_sts).assume_role(**kwargs).thenReturn(mock_sts_return), \
            when(boto3).client("ce", **kwargs).thenReturn(mock_ce), \
            when(mock_ce).get_cost_and_usage(**kwargs).thenReturn(mock_ce_return):

        cost = aws_cost_exporter.get_cost(start_date, stop_date)

        assert cost == [('sandbox', 10.0), ('prod', 1000.0)]


def test_get_date_range():
    start_date = datetime.datetime(2019, 1, 11, 21, 34, 41, 562730)

    assert aws_cost_exporter.get_date_range(start_date, 1) \
        == ("2019-01-10", "2019-01-11")


def test_push_to_prometheus():
    url = "http://prometheus.com"

    with expect(prometheus_client, times=1).push_to_gateway(url, **kwargs).thenReturn(":ok"):
        assert aws_cost_exporter.push_to_prometheus(url, "stuff", 0)

        verifyNoUnwantedInteractions()
