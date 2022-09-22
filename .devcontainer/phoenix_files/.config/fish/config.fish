# https://asdf-vm.com/guide/getting-started.html#_3-install-asdf
source /opt/asdf-vm/asdf.fish
# https://github.com/localstack/awscli-local
alias awslocal="aws --endpoint-url=http://localstack:4566 --profile=local"

if not set -q CONFIG_FISH_NO_NEOFETCH
    neofetch
end

fish_add_path $HOME/backup_slack/node_modules/.bin