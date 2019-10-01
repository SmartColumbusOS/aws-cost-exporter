#!/usr/bin/env python3

import time
import datetime
import json
import os
import re
import boto3
import sys
import requests
import prometheus_client
from uuid import uuid4
from functools import partial
from itertools import starmap

def main():
    url = os.environ.get("PUSHGATEWAY_URL")

    push_cost_metrics_to_prometheus(url)


def push_cost_metrics_to_prometheus(url):
    yesterday, today = get_date_range(
        ending=datetime.datetime.utcnow(),
        previous_days=1
    )
    cost_tuples = get_cost(
        starting=yesterday,
        ending=today
    )

    return list(starmap(partial(push_to_prometheus, url), cost_tuples))


def get_date_range(ending, previous_days):
    stop_raw = datetime.datetime(
        year=ending.year,
        month=ending.month,
        day=ending.day
    )
    start_raw = stop_raw - datetime.timedelta(days=previous_days)

    start_date = start_raw.strftime("%Y-%m-%d")
    stop_date = stop_raw.strftime("%Y-%m-%d")

    return start_date, stop_date


def get_cost(starting, ending):
    sts = boto3.client("sts")
    credentials = sts.assume_role(
        RoleArn=os.environ.get("PARENT_COST_ROLE_ARN"),
        RoleSessionName=uuid4().hex
    ).get("Credentials")

    ce = boto3.client(
        "ce",
        aws_access_key_id=credentials.get("AccessKeyId"),
        aws_secret_access_key=credentials.get("SecretAccessKey"),
        aws_session_token=credentials.get("SessionToken")
    )

    response = ce.get_cost_and_usage(
        TimePeriod={
            "Start": starting,
            "End":  ending
        },
        Granularity="DAILY",
        Metrics=["UnblendedCost"],
        GroupBy=[
            {
                "Type": "DIMENSION",
                "Key": "LINKED_ACCOUNT"
            }
        ],
        Filter={
            "Dimensions": {
                "Key": "LINKED_ACCOUNT",
                "Values": list(__account_mappings().keys())
            }
        }
    )

    return list(map(__extract_cost, __extract_accounts(response)))


def push_to_prometheus(url, env_name, cost):
    registry = prometheus_client.CollectorRegistry()
    gauge = prometheus_client.Gauge(
        name="aws_daily_cost",
        documentation="Daily cost of AWS charges",
        labelnames=["environment"],
        registry=registry
    )
    gauge.labels(environment=env_name).set(cost)

    return prometheus_client.push_to_gateway(
        url,
        job="aws",
        grouping_key={
            "environment": env_name
        },
        registry=registry
    )


def __extract_accounts(response):
    return response.get("ResultsByTime")[0].get("Groups")


def __extract_cost(account):
    return (
        __account_mappings().get(account.get("Keys")[0]),
        float(account.get("Metrics").get("UnblendedCost").get("Amount"))
    )

def __account_mappings():
    return json.loads(os.environ.get("ACCOUNT_MAPPINGS"))

if __name__ == "__main__":
    main()
