import logging

from awacs.aws import Policy
from awacs.helpers.trust import get_lambda_assumerole_policy
from stacker.blueprints.base import Blueprint
from stacker.blueprints.variables.types import TroposphereType
from troposphere import (
    awslambda,
    events,
    iam,
    NoValue,
    Output,
    Ref,
    Sub,
    Export,
    ImportValue,
    Join
)

from policies import lambda_basic_execution_statements, lambda_api_gateway_assume_role_policy

LOGGER = logging.getLogger(name=__name__)


def hook_output(stacker_context, hook_name, function_name):
    hook_data = stacker_context.hook_data.get(hook_name, {})
    return hook_data.get(
        function_name,
        awslambda.Code(
            S3Bucket='<<unresolved: hook data not resolvable>>',
            S3Key='<<unresolved: hook data not resolvable>>'
        ))


class Function(Blueprint):
    MAX_FUNCTION_NAME_LENGTH = 64
    VARIABLES = {
        "Imports": {
            "type": dict,
            "description": "Key-value pairs that align with stack exports",
            "default": {},
        },
        "InlineCode": {
            "type": str,
            "description": "Inline code for lambda function",
            "default": ""
        },
        "Description": {
            "type": str,
            "description": "Description of the function.",
            "default": "",
        },
        "Environment": {
            "type": dict,
            "description": "Key-value pairs that Lambda caches and makes "
                           "available for your Lambda functions.",
            "default": {},
        },
        "Handler": {
            "type": str,
            "description": "The name of the function (within your source "
                           "code) that Lambda calls to start running your "
                           "code.",
            "default": "lambda_handler",
        },
        "ReservedConcurrentExecutions": {
            "type": int,
            "description": "The number of simultaneous executions to reserve for the function.",
            "default": 5,
        },
        "MemorySize": {
            "type": int,
            "description": "The amount of memory, in MB, that is allocated "
                           "to your Lambda function. Default: 128",
            "default": 128,
        },
        "Runtime": {
            "type": str,
            "description": "The runtime environment for the Lambda function "
                           "that you are uploading.",
        },
        "Timeout": {
            "type": int,
            "description": "The function execution time (in seconds) after "
                           "which Lambda terminates the function. Default: 3",
            "default": 895,
        },
        "Role": {
            "type": str,
            "description": "Arn of the Role to create the function as - if "
                           "not specified, a role will be created with the "
                           "basic permissions necessary for Lambda to run.",
            "default": "",
        }
    }

    def pseudo_init(self):
        self.imports = self.get_variables().get('Imports', {})
        self.my_env = self.get_variables().get('Environment', {})
        self.role_arn = self.get_variables().get('Role')

    def create_template(self):
        self.pseudo_init()
        if not self.role_arn:
            self.role_arn = self.create_role()
        self.create_function()

    def create_function(self):
        template = self.template
        variables = self.get_variables()
        aws_function = awslambda.Function(
            self.name,
            Code=self.code(),
            Description=variables["Description"] or NoValue,
            Environment=self.environment(),
            FunctionName=self.gen_function_name(self.name),
            Handler=variables["Handler"],
            MemorySize=variables["MemorySize"],
            ReservedConcurrentExecutions=variables["ReservedConcurrentExecutions"] or NoValue,
            Role=self.role_arn,
            Runtime=variables["Runtime"],
            Timeout=variables["Timeout"],
        )

        function = template.add_resource(aws_function)

        template.add_output(
            Output(
                f"{self.name}Name",
                Value=function.Ref(),
                Export=Export(Join("", [Sub('${AWS::StackName}'), f'-{self.name}Name']))
            )
        )
        template.add_output(
            Output(
                f"{self.name}Arn",
                Value=function.GetAtt("Arn"),
                Export=Export(Join("", [Sub('${AWS::StackName}'), f'-{self.name}Arn']))
            )
        )
        template.add_output(
            Output(
                f"{self.name}RoleArn",
                Value=self.role_arn,
                Export=Export(Join("", [Sub('${AWS::StackName}'), f'-{self.name}RoleArn']))
            )
        )

        function_version = template.add_resource(
            awslambda.Version(
                "LatestVersion",
                FunctionName=function.Ref()
            )
        )

        template.add_output(
            Output("LatestVersion",
                   Value=function_version.GetAtt("Version"))
        )
        template.add_output(
            Output("LatestVersionArn",
                   Value=function_version.Ref())
        )

        return function

    def code(self):
        return hook_output(self.context, 'lambda', self.name)

    def environment(self):
        return awslambda.Environment(Variables=self.my_env) or NoValue

    def format_env(self):
        environment_imports = {}
        to_remove = []

        for key, value in self.imports.items():
            if 'Environment_' in key:
                to_remove.append(key)
                new_key = key.replace("Environment_", "")
                environment_imports[new_key] = ImportValue(value)

        for key in to_remove:
            del self.imports[key]

        self.imports.update(environment_imports)
        self.my_env.update(environment_imports)

    def generate_policy_statements(self):
        statements = []

        statements.extend(lambda_basic_execution_statements(self.context.namespace + "*"))

        return statements

    def get_lambda_managed_policy_arns(self):
        managed_policies = []
        return managed_policies

    def create_role(self):
        self.format_env()

        new_policy = iam.Policy(
            PolicyName=Sub("${AWS::StackName}-policy"),
            PolicyDocument=Policy(Statement=self.generate_policy_statements())
        )

        role = iam.Role("Role",
                        AssumeRolePolicyDocument=lambda_api_gateway_assume_role_policy(),
                        ManagedPolicyArns=[],
                        Policies=[new_policy]
                        )

        self.template.add_output(Output("RoleName", Value=Ref(role)))
        self.template.add_output(Output("RoleArn", Value=role.GetAtt("Arn")))

        self.template.add_resource(role)
        return role.GetAtt("Arn")

    def gen_function_name(self, function_name):
        max_length = self.MAX_FUNCTION_NAME_LENGTH
        truncated = self.context.namespace[:max_length - len(function_name)].strip('-')

        return f"{truncated}-{function_name}"
