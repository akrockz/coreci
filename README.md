# core-ci

## What's this?

Need untrusted jenkins jobs to trigger our CI/CD process.

Currently it's:
CodeCommit -> (core-automation/lambdas/codecommit_listener/main.py + autoincrementing build number) -> CodeBuild (run.sh)

For Jenkins jobs, it will be:
Jenkins (IAM+access key) -> (custom core-ci per portfolio/app + autoincrementing build number) -> CodeBuild (run.sh)

## Auto incrementing build number?

Uses SSM Parameter Store. See core-ci/lambdas/ci_trigger/main.py.

## Example CodeBuild BuildSpec for core-ci itself

See core-codecommit/core-codecommit-resources.yaml

```
version: 0.2
  phases:
    pre_build:
      commands:
        - chmod +x ./bin/package.sh
        - ./bin/package.sh
        - aws s3 cp $RUN_SH_S3_PATH ./_staging/
        - chmod +x ./_staging/run.sh
    build:
      commands:
        - cd ./_staging
        - ./run.sh package upload compile deploy -c $CLIENT -p $PORTFOLIO -a $APP -b $BRANCH -n $BUILD_NUMBER --automation-type deployspec
    post_build:
      commands:
        - cat compile-response.txt || true
        - cat deploy-response.txt || true
```

## Invoking the ci trigger

Example via awcli:

```bash
AWS_PROFILE=sia-automation aws lambda invoke --function-name core-ci-demo-app --payload '{ "branch": "single" }' /dev/stdout
```
