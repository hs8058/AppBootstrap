A serverless web app using AWS Cognito User Pools as an OIDC identity provider with basic CRUD operations on AWS DynamoDB, as a good starting bootstrap to build serverless web apps using Python and the AWS serverless stack.

You would need to create a .env file in the root with the following values that you should get from AWS after creating a Cognito user pool and a DynamoDB table and an IAM user to access the DynamoDB table


COGNITO_DOMAIN=<your user pool name>.auth.us-east-1.amazoncognito.com
CLIENT_ID=<your user pool 's app client id>
CLIENT_SECRET=<your user pool 's app client secret'>
REDIRECT_URI=http://localhost:5000/login/callback
POST_LOGOUT_REDIRECT_URI=http://localhost:5000/postlogout
SECRET_KEY=<your secret key for handling sessions>
COGNITO_REGION=<your aws region>
USER_POOL_ID=<your user pool id>
AWS_ACCESS_KEY_ID=<the access key id of the IAM user for dynamo db>
AWS_SECRET_ACCESS_KEY=<the access secret of the IAM user for dynamo db>
USER_POOL_NAME=<your user pool name>