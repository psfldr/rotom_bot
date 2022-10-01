# https://asdf-vm.com/guide/getting-started.html#_3-install-asdf
source /opt/asdf-vm/asdf.fish

set --export TZ 'Asia/Tokyo'; export TZ
set --export fzf_fd_opts --hidden --exclude=.git
set --export theme_color_scheme nord
set --export AWS_ACCESS_KEY_ID test
set --export AWS_SECRET_ACCESS_KEY test
set --export AWS_DEFAULT_REGION ap-northeast-1
set --export AWS_ENDPOINT_URL http://localstack:4566

# https://github.com/localstack/awscli-local
alias awslocal="aws --endpoint-url=$AWS_ENDPOINT_URL"

fish_add_path $HOME/rotom_bot/node_modules/.bin

if status is-interactive
    neofetch
end
