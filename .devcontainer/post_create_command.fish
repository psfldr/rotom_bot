# /usr/bin/fish
# 設定ファイルコピー
mkdir -p ~/.config/fish/completions
mkdir -p ~/.config/neofetch/
ln -sf ~/rotom_bot/.devcontainer/phoenix_files/.bashrc ~/
ln -sf ~/rotom_bot/.devcontainer/phoenix_files/.config/fish/config.fish ~/.config/fish/
ln -sf ~/rotom_bot/.devcontainer/phoenix_files/.config/fish/fish_history ~/.config/fish/
ln -sf ~/rotom_bot/.devcontainer/phoenix_files/.config/fish/completions/devtools.fish ~/.config/fish/completions
ln -sf ~/rotom_bot/.devcontainer/phoenix_files/.config/neofetch/config.conf ~/.config/neofetch/
ln -sf ~/rotom_bot/.devcontainer/phoenix_files/.actrc ~/.actrc

# fishプラグイン設定
curl -sL https://git.io/fisher | source && fisher install jorgebucaran/fisher
fisher install PatrickF1/fzf.fish
fisher install oh-my-fish/plugin-pbcopy

source ~/.config/fish/config.fish

# Pipfileの内容を仮想環境にインストール
yes | pipenv install --dev

if not test -e .git/hooks/commit-msg
    git secrets --register-aws --global
    git secrets --install --force
end
