#!/usr/bin/env python
# encoding: utf-8

import sys
import datetime
import boto3
import os
import logging
import urllib.parse
import urllib.request

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# LINE notify's API
LINE_NOTIFY_URL = "https://notify-api.line.me/api/notify"
LINE_TOKEN = os.environ.get("LINE_NOTIFY_API_KEY")

response = boto3.client('cloudwatch', region_name='us-east-1')


def get_metric_statistics():
    metric_statistics = response.get_metric_statistics(
        Namespace='AWS/Billing',
        MetricName='EstimatedCharges',
        Dimensions=[
            {
                'Name': 'Currency',
                'Value': 'USD'
            }
        ],
        StartTime=datetime.datetime.today() - datetime.timedelta(days=1),
        EndTime=datetime.datetime.today(),
        Period=86400,
        Statistics=['Maximum'])
    return metric_statistics


def build_message():
    metric_statistics = get_metric_statistics()
    cost = metric_statistics['Datapoints'][0]['Maximum']
    date = metric_statistics['Datapoints'][0]['Timestamp'].strftime(
        '%Y年%m月%d日')
    msg = "%sまでのAWSの料金は、$%sです。" % (date, cost)
    return msg


def send_message(msg):
    method = "POST"
    headers = {"Authorization": "Bearer %s" % LINE_TOKEN}
    payload = {"message": msg}
    try:
        payload = urllib.parse.urlencode(payload).encode("utf-8")
        req = urllib.request.Request(
            url=LINE_NOTIFY_URL, data=payload, method=method, headers=headers)
        urllib.request.urlopen(req)
    except Exception as e:
        print("Exception Error: ", e)
        sys.exit(1)


def lambda_handler(event, context):
    msg = build_message()
    print(msg)
    send_message(msg)
