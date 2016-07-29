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

def get_latest(tracker, table):
    return int(table.query(
        KeyConditionExpression=Key('tracker').eq(tracker),
        ScanIndexForward=False,
        Limit=1)['Items'][0]['item'])

def put_latest(tracker, item, table):
    table.put_item(Item={
        'tracker': tracker,
        'item': decimal.Decimal(item)
    })

login = {'username':'fhir_bot','password':os.environ['GFORGE_PASSWORD']}

def read_issues(s):
    s.post('http://gforge.hl7.org/gf/account/?action=LoginAction',data=login)
    changes = s.get('http://gforge.hl7.org/gf/project/fhir/tracker/?action=TrackerQueryCSV&tracker_id=677&tracker_query_id=143')
    reader = unicodecsv.reader(StringIO.StringIO(changes.text.encode("utf-8")), encoding='utf-8')
    reader.next()
    return {
        int(row[0]): (int(row[0]), row[1], row[4], row[5]) for row in reader
    }

def post_issue(issue, zulip_client):
    zulip_client.send_message({
        "type": 'stream',
        "content": "GF#%s: **%s** posted by `%s`" % (
                issue[0],
                issue[1],
                issue[2]),
        "subject": "tracker-item",
        "to": "committers",
    })

def lambda_handler(event, context):

    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('gforge')

    zulip_client = zulip.Client(
        site='https://chat.fhir.org',
        api_key=os.environ['ZULIP_API_KEY'],
        email=os.environ['ZULIP_EMAIL'])


    last_issue = get_latest('fhir', table)
    print("last issue in dynamo", last_issue)

    session = requests.Session()
    issues = read_issues(session)
    print("newest issues on gf", issues)

    num_posted = 0
    for issue_number, issue in issues.iteritems():
        if issue_number > last_issue:
            put_latest('fhir', issue_number, table)
            post_issue(issue, zulip_client)
            num_posted += 1
            print("so put", issue_number, issue)

    return "Posted %s issues"%num_posted
