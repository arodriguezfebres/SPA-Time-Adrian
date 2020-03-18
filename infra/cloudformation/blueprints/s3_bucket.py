from awacs import AWSHelperFn
from stacker.blueprints.base import Blueprint
from troposphere import Export, Output, ImportValue, s3, Sub


class TemplateBuilder(Blueprint):
    VARIABLES = {
        'BucketName': {
            'type': str,
            'description': 'Bucket name'
        },
        'Imports': {
            "type": object,
            "description": "Import variables"
        },
        'LogBucket': {
            "type": str,
            "description": "Bucket to store access logs in."
        }
    }

    def create_template(self):
        template = self.template
        variables = self.get_variables()

        template.set_version('2010-09-09')

        s3_bucket = template.add_resource(s3.Bucket(
            f'{variables["BucketName"]}Bucket',
            AccessControl=s3.LogDeliveryWrite,
            BucketName=Sub(f'{variables["BucketName"]}-${{AWS::Region}}'),
            BucketEncryption=s3.BucketEncryption(
                ServerSideEncryptionConfiguration=[
                    s3.ServerSideEncryptionRule(
                        ServerSideEncryptionByDefault=s3.ServerSideEncryptionByDefault(
                            SSEAlgorithm='AES256'))]
            ),
            LoggingConfiguration=s3.LoggingConfiguration(
                DestinationBucketName=self.get_variables()['LogBucket'],
                LogFilePrefix='DataAccessLogs/')
        ))

        template.add_output(Output(
            f'{variables["BucketName"]}Bucket',
            Value=s3_bucket.Ref(),
            Export=Export(Sub(f'${AWS::StackName}-{variables["BucketName"]}Bucket'))
        ))