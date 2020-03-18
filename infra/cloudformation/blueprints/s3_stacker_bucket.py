from stacker.blueprints.base import Blueprint
from troposphere import s3


class TemplateBuilder(Blueprint):
    VARIABLES = {
        'BucketName': {
            'type': str,
            'description': 'Stacker bucket name'
        }
    }

    def create_template(self):
        template = self.template
        variables = self.get_variables()

        template.set_version('2010-09-09')

        bucket_name = variables['BucketName']
        _ = template.add_resource(s3.Bucket(
            'StackerBucket',
            AccessControl=s3.LogDeliveryWrite,
            BucketName=f'{bucket_name}',
            BucketEncryption=s3.BucketEncryption(
                ServerSideEncryptionConfiguration=[
                    s3.ServerSideEncryptionRule(
                        ServerSideEncryptionByDefault=s3.ServerSideEncryptionByDefault(
                            SSEAlgorithm='AES256'))]
            )))
