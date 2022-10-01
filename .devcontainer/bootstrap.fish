# /usr/bin/fish
sudo chmod 666 /var/run/docker.sock

# 設定ファイルコピー
mkdir -p ~/.config/fish/
mkdir -p ~/.config/neofetch/
ln -sf ~/backup_slack/.devcontainer/phoenix_files/.bashrc ~/
ln -sf ~/backup_slack/.devcontainer/phoenix_files/.config/fish/config.fish ~/.config/fish/
ln -sf ~/backup_slack/.devcontainer/phoenix_files/.config/neofetch/config.conf ~/.config/neofetch/
ln -sf ~/backup_slack/.devcontainer/phoenix_files/.aws/ ~/.aws

source ~/.config/fish/config.fish

# fishプラグイン設定
curl -sL https://git.io/fisher | source && fisher install jorgebucaran/fisher
fisher install PatrickF1/fzf.fish
fisher install oh-my-fish/plugin-pbcopy

# Pipfileの内容を仮想環境にインストール
yes | pipenv install --dev
