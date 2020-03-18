from stacker.blueprints.base import Blueprint
from troposphere import GetAtt, Join, ImportValue, Sub
from troposphere import Ref, Output
from troposphere.apigateway import ApiKey, StageKey
from troposphere.apigateway import Deployment, Stage
from troposphere.apigateway import Integration, IntegrationResponse
from troposphere.apigateway import Resource
from troposphere.apigateway import RestApi, Method


class TemplateBuilder(Blueprint):
    VARIABLES = {
        "Imports": {
            "type": dict,
            "description": "Key-value pairs that align with stack exports",
            "default": {},
        },
        "Name": {
            "type": str,
            "description": "The resources base name.",
        },
        "InvokeLambda": {
            "type": str,
            "description": "The lambda to invoke.",
        },
        "InvokeLambdaRole": {
            "type": str,
            "description": "The role of the lambda to invoke.",
        },
        "Region": {
            "type": str,
            "description": "AWS region.",
        }
    }

    def pseudo_init(self):
        self.imports = self.get_variables().get('Imports', {})
        self.my_env = self.get_variables().get('Environment', {})
        self.role_arn = self.get_variables().get('Role')

    def create_template(self):
        self.pseudo_init()
        self.create_api_gateway_resources()

    def create_api_gateway_resources(self):
        template = self.template

        invoke_lambda = ImportValue(self.get_variables()['InvokeLambda'])
        invoke_lambda_role = ImportValue(self.get_variables()['InvokeLambdaRole'])
        region = self.get_variables()['Region']

        name = self.get_variables()['Name']

        # Create the Api Gateway
        rest_api = template.add_resource(RestApi(
            name,
            Name=name
        ))

        # Create a resource to map the lambda function to
        resource = template.add_resource(Resource(
            "FoobarResource",
            RestApiId=Ref(rest_api),
            PathPart="time",
            ParentId=GetAtt(name, "RootResourceId"),
        ))

        # Create a Lambda API method for the Lambda resource
        method = template.add_resource(Method(
            "LambdaMethod",
            RestApiId=Ref(rest_api),
            AuthorizationType="NONE",
            ResourceId=Ref(resource),
            HttpMethod="GET",
            Integration=Integration(
                Credentials=invoke_lambda_role,
                Type="AWS",
                IntegrationHttpMethod='POST',
                IntegrationResponses=[
                    IntegrationResponse(
                        StatusCode='200'
                    )
                ],
                Uri=Join("", [
                    "arn:aws:apigateway:", region, ":lambda:path/2020-03-17/functions/",
                    invoke_lambda,
                    "/invocations"
                ])
            )
        ))

        # Create a deployment
        stage_name = name

        deployment = template.add_resource(Deployment(
            "%sDeployment" % stage_name,
            RestApiId=Ref(rest_api),
        ))

        stage = template.add_resource(Stage(
            '%sStage' % stage_name,
            StageName=stage_name,
            RestApiId=Ref(rest_api),
            DeploymentId=Ref(deployment)
        ))

        key = template.add_resource(ApiKey(
            "ApiKey",
            StageKeys=[StageKey(
                RestApiId=Ref(rest_api),
                StageName=Ref(stage)
            )]
        ))

        # Add the deployment endpoint as an output
        template.add_output([
            Output(
                "ApiEndpoint",
                Value=Join("", [
                    "https://",
                    Ref(rest_api),
                    ".execute-api.", region,".amazonaws.com/",
                    stage_name
                ]),
                Description="Endpoint for this stage of the api"
            ),
            Output(
                "ApiKey",
                Value=Ref(key),
                Description="API key"
            ),
        ])

