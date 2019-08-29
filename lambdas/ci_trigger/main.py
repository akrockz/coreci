"""
Deploy one 'CI Trigger Lambda' per Jenkins Job.

Example: ABC have a Jenkins job for all their branches.
Control who can invoke (IAM/access key) each copy of the trigger lambda.
Control portfolio, app.
Don't allow master branch for now. Can make configurable later.

FIXME Copypaste from core-automation/lambdas/codecommit_listener/main.py
"""

import boto3
from os import environ
import time


def __validate_invoke(event):
    if 'master' in event['branch'].lower():
        raise ValueError('master branches not permitted.')


def __get_new_build_number(deployment):
    client = boto3.client('ssm')

    param_name = '/{}/{}/{}/build_time'.format(deployment['portfolio'], deployment['app'], deployment['branch'])
    current_time = str(int(round(time.time() * 1000)))

    print('Update SSM PS param_name={}, current_time={}'.format(param_name, current_time))

    response = client.put_parameter(Name=param_name, Value=current_time, Type='String', Overwrite=True)
    print('__get_new_build_number param_name={}, current_time={}, response={}'.format(param_name, current_time, response))
    return response['Version']


def __invoke_codebuild_project(deployment, automation_region, automation_bucket_name, run_sh_s3_path, client_name):
    """
    Invoke a codebuild project setup for the app.
    http://boto3.readthedocs.io/en/docs/reference/services/codebuild.html#CodeBuild.Client.start_build
    """
    project_name = '{}-{}'.format(deployment['portfolio'], deployment['app'])
    branch = deployment['branch']
    new_build_number = __get_new_build_number(deployment)

    env_vars = [
        {'name': 'CLIENT', 'value': client_name, 'type': 'PLAINTEXT'},
        {'name': 'PORTFOLIO', 'value': deployment['portfolio'], 'type': 'PLAINTEXT'},
        {'name': 'APP', 'value': deployment['app'], 'type': 'PLAINTEXT'},
        {'name': 'BRANCH', 'value': deployment['branch'], 'type': 'PLAINTEXT'},
        {'name': 'BUILD_NUMBER', 'value': str(new_build_number), 'type': 'PLAINTEXT'},
        # Env var set in deploy.sh
        {'name': 'BUCKET_NAME', 'value': automation_bucket_name, 'type': 'PLAINTEXT'},
        {'name': 'RUN_SH_S3_PATH', 'value': run_sh_s3_path, 'type': 'PLAINTEXT'}
    ]

    print('__invoke_codebuild_project client_name={}, project_name={}, branch={}, env_vars={}'.format(
        client_name, project_name, branch, env_vars
    ))

    boto3_client = boto3.client('codebuild', region_name=automation_region)
    response = boto3_client.start_build(
        projectName=project_name,
        sourceVersion=deployment['branch'],
        environmentVariablesOverride=env_vars
    )

    print('__invoke_codebuild_project response={}'.format(response))
    return response


def handler(event, context):
    print('event={}'.format(event))

    __validate_invoke(event)

    deployment = {
        'portfolio': environ['PIPELINE_PORTFOLIO'],
        'app': environ['PIPELINE_APP'],
        'branch': event['branch'],  # Literally, the one input from Jenkins :)
        # build number set later
    }

    print('deployment={}'.format(deployment))

    response = __invoke_codebuild_project(
        deployment,
        environ['AUTOMATION_REGION'],
        environ['AUTOMATION_BUCKET_NAME'],
        environ['RUN_SH_S3_PATH'],
        environ['CLIENT_NAME']
    )

    return {
        'id': response['build']['id']
    }
