# docker pull archlinux/archlinux:latest
AWS_SESSION_TOKEN_TTL=4h aws-vault exec psfldr-aws --region ap-northeast-1 -- env | grep AWS > psfldr-aws.env
echo 'AWS_ENDPOINT_URL=http://localstack:4566' >> psfldr-aws.env