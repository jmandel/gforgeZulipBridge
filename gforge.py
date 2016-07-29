import boto3
from boto3.dynamodb.conditions import Key, Attr
import json
import decimal
import StringIO
import unicodecsv
import requests
import zulip
import time
import os
import sys


try:
    import env_values
except e:
    pass

dynamodb = boto3.resource('dynamodb')
issues = dynamodb.Table('gforge')

def get_latest(tracker):
    return int(issues.query(
        KeyConditionExpression=Key('tracker').eq(tracker),
        ScanIndexForward=False,
        Limit=1)['Items'][0]['item'])

def put_latest(tracker, item):
    issues.put_item(Item={
        'tracker': tracker,
        'item': decimal.Decimal(item)
    })

login = {'username':'fhir_bot','password':os.environ['GFORGE_PASSWORD']}
session = requests.Session()

zulip_client = zulip.Client(
    site='https://chat.fhir.org',
    api_key=os.environ['ZULIP_API_KEY'],
    email=os.environ['ZULIP_EMAIL'])

def read_issues(s):
    s.post('http://gforge.hl7.org/gf/account/?action=LoginAction',data=login)
    changes = s.get('http://gforge.hl7.org/gf/project/fhir/tracker/?action=TrackerQueryCSV&tracker_id=677&tracker_query_id=143')
    reader = unicodecsv.reader(StringIO.StringIO(changes.text.encode("utf-8")), encoding='utf-8')
    reader.next()
    return {
        int(row[0]): (int(row[0]), row[1], row[4], row[5]) for row in reader
    }

def post_issue(issue):
    zulip_client.send_message({
        "type": 'stream',
        "content": "GF#%s: **%s** posted by `%s`" % (
                issue[0],
                issue[1],
                issue[2]),
        "subject": "tracker-item",
        "to": "committers",
    })


last_issue = get_latest('fhir')
print("last issue in dynamo", last_issue)

issues = read_issues(session)
print("newest issues on gf", issues)

def lambda_handler(*args, **kwargs):
    for issue_number, issue in issues.iteritems():
        if issue_number > last_issue:
            put_latest('fhir', issue_number)
            post_issue(issue)
            print("so put", issue_number, issue)
