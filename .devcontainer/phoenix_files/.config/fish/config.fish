# https://asdf-vm.com/guide/getting-started.html#_3-install-asdf
source /opt/asdf-vm/asdf.fish
# https://github.com/localstack/awscli-local
alias awslocal="AWS_ACCESS_KEY_ID=dummy AWS_SECRET_ACCESS_KEY=dummy AWS_DEFAULT_REGION=ap-northeast-1 aws --endpoint-url=http://localstack:4566"

if not set -q CONFIG_FISH_NO_NEOFETCH
    neofetch
end
