# 対話シェルの場合のみneofetch表示
if status is-interactive
    sleep 1
    neofetch
end

# 初回のみプラグインインストールを自動で実行
if test -d ~/.config/nvim/site/autoload/
    if test "$(ls ~/.config/nvim/site/autoload/)" = 'plug.vim'
        nvim --headless +'PlugInstall --sync' +'PlugUpdate' +qa 2>/dev/null
    end
end

# https://asdf-vm.com/guide/getting-started.html#_3-install-asdf
source /opt/asdf-vm/asdf.fish

set --export TZ 'Asia/Tokyo'; export TZ
set --export fzf_fd_opts --hidden --exclude=.git
set --export theme_color_scheme nord

# https://github.com/localstack/awscli-local
alias awslocal="aws --endpoint-url=$AWS_ENDPOINT_URL"

fish_add_path $HOME/rotom_bot/node_modules/.bin

starship init fish | source
