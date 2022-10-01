# https://asdf-vm.com/guide/getting-started.html#_3-install-asdf
source /opt/asdf-vm/asdf.fish
# https://github.com/localstack/awscli-local
alias awslocal="aws --endpoint-url=http://localstack:4566 --profile=local"

fish_add_path $HOME/backup_slack/node_modules/.bin

set TZ 'Asia/Tokyo'; export TZ
set fzf_fd_opts --hidden --exclude=.git
set theme_color_scheme nord

if status is-interactive
    sleep 1
    neofetch
end
