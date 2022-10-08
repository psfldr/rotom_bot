# docker pull archlinux/archlinux:latest
# AWS_SESSION_TOKEN_TTL=4h aws-vault exec psfldr-aws --region ap-northeast-1 --no-session -- env | grep AWS > .env
AWS_SESSION_TOKEN_TTL=4h aws-vault exec psfldr-aws --region ap-northeast-1 -- env | grep AWS > .env
echo 'AWS_ENDPOINT_URL=http://localhost:4566' >> .env