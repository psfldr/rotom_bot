# /usr/bin/fish

# 設定ファイルコピー
mkdir -p ~/.config/fish/
mkdir -p ~/.config/neofetch/
cp .devcontainer/phoenix_files/.bashrc ~/.bashrc
cp .devcontainer/phoenix_files/.config/fish/config.fish ~/.config/fish/config.fish
cp .devcontainer/phoenix_files/.config/neofetch/config.conf ~/.config/neofetch/config.conf

source ~/.config/fish/config.fish

# fisher
curl -sL https://git.io/fisher | source && fisher install jorgebucaran/fisher
fisher install PatrickF1/fzf.fish


asdf install awscli latest
asdf local awscli latest
asdf install nodejs 16.17.0
asdf local nodejs 16.17.0

cp -r .devcontainer/phoenix_files/.aws/ ~/.aws/