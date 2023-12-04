import boto3
import json


def lambda_handler(event, context):
    ssm_client = boto3.client("ssm")
    instance_id = "XXXXXX"

    commands = ["the commands script"]

    try:
        response = ssm_client.send_command(
            InstanceIds=[instance_id],
            DocumentName="AWS-RunShellScript",
            Parameters={"commands": commands},
        )

        command_id = response["Command"]["CommandId"]

        # Have to comment the logic below to make the function from synchronous to asynchronous since it is waiting
        # for the result of the script to resolve before it proceeds, so instead, we take the command_id above and poll
        # for it instead with another lambda function

        # waiter = ssm_client.get_waiter("command_executed")
        # waiter.wait(CommandId=command_id, InstanceId=instance_id)
        #
        # output = ssm_client.get_command_invocation(
        #     CommandId=command_id, InstanceId=instance_id
        # )

        return {"statusCode": 200, "body": json.dumps({"commandId": command_id})}

    except Exception as e:
        print(e)
        return {
            "statusCode": 500,
            "body": json.dumps("Error executing command on EC2 instance."),
        }
