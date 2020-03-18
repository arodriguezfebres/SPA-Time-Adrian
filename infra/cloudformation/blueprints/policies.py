from awacs import logs, sts
from awacs.aws import Allow, Statement, Principal, Policy
from troposphere import Join, Region, AccountId


def lambda_basic_execution_statements(function_name):
    log_group = Join("/", ["/aws/lambda", function_name])
    return cloudwatch_logs_write_statements(log_group)


def cloudwatch_logs_write_statements(log_group=None, log_stream=None):
    if log_stream:
        log_stream = "log_stream:%s" % log_stream
    else:
        log_stream = "*"
    resources = ["arn:aws:logs:*:*:*"]
    if log_group:
        log_group_parts = ["arn:aws:logs:", Region, ":", AccountId,
                           ":log-group:", log_group]
        log_group_arn = Join("", log_group_parts)
        log_stream_wild = Join(
            "",
            log_group_parts + [":" + log_stream]
        )

        resources = [log_group_arn, log_stream_wild]

    return [
        Statement(
            Effect=Allow,
            Resource=resources,
            Action=[
                logs.CreateLogGroup,
                logs.CreateLogStream,
                logs.PutLogEvents
            ]
        )
    ]


def lambda_api_gateway_assume_role_policy():
    return Policy(
        Statement=[
            Statement(
                Principal=Principal('Service', ['lambda.amazonaws.com', 'apigateway.amazonaws.com']),
                Effect=Allow,
                Action=[sts.AssumeRole]
            )
        ],
        Version="2012-10-17"
    )