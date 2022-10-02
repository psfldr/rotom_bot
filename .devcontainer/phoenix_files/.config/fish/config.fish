# 対話シェルの場合のみneofetch表示
if status is-interactive
    neofetch
end

# https://asdf-vm.com/guide/getting-started.html#_3-install-asdf
source /opt/asdf-vm/asdf.fish

set --export TZ 'Asia/Tokyo'; export TZ
set --export fzf_fd_opts --hidden --exclude=.git
set --export theme_color_scheme nord
# AWSクレデンシャル環境変数のexport
if test -e psfldr-aws.env; and type -q bass
    bass export $(cat psfldr-aws.env)
else
    echo 'AWSクレデンシャル環境変数のexport: envファイルがないかbassがインストールされていない'
end

# https://github.com/localstack/awscli-local
alias awslocal="aws --profile=local --endpoint-url=$AWS_ENDPOINT_URL"

fish_add_path $HOME/rotom_bot/node_modules/.bin
