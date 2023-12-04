import boto3
import json


def lambda_handler(event, context):
    ssm_client = boto3.client("ssm")
    command_id = event['queryStringParameters']['commandId']
    instance_id = "i-004f7d453b841d11d"

    try:
        output = ssm_client.get_command_invocation(
            CommandId=command_id, InstanceId=instance_id
        )
        return {"statusCode": 200, "body": json.dumps(output)}
    except Exception as e:
        print(e)
        return {
            "statusCode": 500,
            "body": json.dumps("Error checking status of the command."),
        }
