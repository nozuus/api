echo "Travis Init"

echo "Setting up serverless..."
# Installing the serverless cli
npm install -g serverless
# Updating serverless from a previous version of serverless
npm update -g serverless
npm install

echo "Setting up AWS CLI..."
# Instal AWS CLI
pip3 install awscli --upgrade --user

echo "Deploying Serverless Application..."
pyenv virtualenv -p python3.6 3.6.3
pyenv local otter-pond-ci

serverless deploy --stage dev
