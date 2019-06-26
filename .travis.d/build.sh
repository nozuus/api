echo "Travis Init"

echo "Setting up serverless..."
# Installing the serverless cli
npm install -g serverless
# Updating serverless from a previous version of serverless
npm update -g serverless
npm install

echo "Setting up AWS CLI..."
pip3 install awscli --upgrade --user

echo "Deploying Serverless Application..."

if [ "$TRAVIS_BRANCH" = "$DEV_BRANCH_NAME" ]; then
  TARGET_BRANCH="$DEV_BRANCH_TARGET"
elif [ "$TRAVIS_BRANCH" = "$PROD_BRANCH_NAME" ]; then
  TARGET_BRANCH="$PROD_BRANCH_TARGET"
else
  exit 1
fi

serverless deploy --stage $TARGET_BRANCH --admin_email=$ADMIN_EMAIL
