# AWS Lambda Deployment Instructions

This document provides step-by-step instructions for deploying the Slackbot to AWS Lambda and configuring the Slack App to use it.

## Prerequisites

1. AWS Account with appropriate permissions
2. AWS CLI installed and configured
3. Slack App created with the following scopes:
   - `chat:write`
   - `channels:history`
   - `im:history`
   - `users:read`

## AWS Lambda Setup

1. Create a new Lambda function:
   ```bash
   aws lambda create-function \
     --function-name slack-word-count-bot \
     --runtime python3.12 \
     --handler app.lambda_handler.lambda_handler \
     --role <YOUR_LAMBDA_ROLE_ARN> \
     --zip-file fileb://deployment-package.zip
   ```

2. Create an IAM role for the Lambda function:
   ```bash
   # Create a JSON file named trust-policy.json
   {
     "Version": "2012-10-17",
     "Statement": [
       {
         "Effect": "Allow",
         "Principal": {
           "Service": "lambda.amazonaws.com"
         },
         "Action": "sts:AssumeRole"
       }
     ]
   }

   # Create the role
   aws iam create-role \
     --role-name slack-word-count-bot-role \
     --assume-role-policy-document file://trust-policy.json

   # Attach basic Lambda execution policy
   aws iam attach-role-policy \
     --role-name slack-word-count-bot-role \
     --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
   ```

3. Create the deployment package:
   ```bash
   # Install dependencies to a local directory
   pip install -r requirements.txt --target ./package
   
   # Add your Lambda function code
   cp -r app/* ./package/
   
   # Create ZIP file
   cd package
   zip -r ../deployment-package.zip .
   cd ..
   ```

4. Create an API Gateway trigger:
   ```bash
   # Create HTTP API
   aws apigatewayv2 create-api \
     --name slack-word-count-bot-api \
     --protocol-type HTTP \
     --target <YOUR_LAMBDA_ARN>
   ```

## Environment Variables

Set these environment variables in your Lambda function:

1. `SLACK_BOT_TOKEN`: Your Slack Bot User OAuth Token
2. `SLACK_SIGNING_SECRET`: Your Slack App's Signing Secret

```bash
aws lambda update-function-configuration \
  --function-name slack-word-count-bot \
  --environment "Variables={SLACK_BOT_TOKEN=xoxb-your-token,SLACK_SIGNING_SECRET=your-secret}"
```

## Slack App Configuration

1. Go to your [Slack App settings](https://api.slack.com/apps)
2. Select your app
3. Under "Event Subscriptions":
   - Enable Events
   - Set the Request URL to your API Gateway URL
   - Subscribe to bot events:
     - `message.channels`
     - `message.im`
4. Save Changes

## Testing

1. Test the Lambda function directly:
   ```bash
   aws lambda invoke \
     --function-name slack-word-count-bot \
     --payload '{"body": "test"}' \
     response.json
   ```

2. Monitor Lambda logs:
   ```bash
   aws logs get-log-events \
     --log-group-name /aws/lambda/slack-word-count-bot \
     --log-stream-name <LOG_STREAM_NAME>
   ```

## Troubleshooting

1. Check Lambda logs for errors
2. Verify environment variables are set correctly
3. Ensure Slack App permissions and event subscriptions are configured
4. Verify API Gateway endpoint is accessible
5. Check Slack App's Event Subscriptions page for delivery attempts and errors

## Security Notes

1. Never commit sensitive values (tokens, secrets) to version control
2. Use AWS Secrets Manager or Parameter Store for sensitive values in production
3. Regularly rotate Slack tokens and signing secrets
4. Monitor Lambda function permissions and access logs

## Maintenance

1. Update the deployment package when code changes:
   ```bash
   # Create new deployment package
   zip -r deployment-package.zip .
   
   # Update Lambda function
   aws lambda update-function-code \
     --function-name slack-word-count-bot \
     --zip-file fileb://deployment-package.zip
   ```

2. Monitor Lambda metrics:
   - Execution time
   - Memory usage
   - Error rates
   - Concurrent executions
