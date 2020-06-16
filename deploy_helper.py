import json
import sys

import boto3

if __name__ == "__main__":
    with open("zappa_settings.json") as json_file:
        data = json.load(json_file)

    queues_to_create = [
        event["event_source"]["arn"].split(":")[-1]
        for event in data[sys.argv[1]]["events"]
        if "event_source" in event
    ]

    client = boto3.client("sqs")

    for queue in queues_to_create:
        print(
            client.create_queue(
                QueueName=queue, Attributes={"VisibilityTimeout": "180"}
            )
        )
