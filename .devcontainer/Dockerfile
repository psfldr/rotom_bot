FROM archlinux/archlinux:latest

# アップデート
RUN pacman -Syu --noconfirm

# ユーザー作成
RUN useradd --create-home --gid wheel --shell /bin/bash devuser

# 基本パッケージインストール
RUN pacman -S --noconfirm base-devel git
RUN echo "%wheel ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers
# yayインストール
USER devuser
WORKDIR /home/devuser
RUN git clone https://aur.archlinux.org/yay.git && cd yay && makepkg -si --noconfirm && cd ../ && rm -r yay

# パッケージインストール
RUN sudo pacman -S --noconfirm \
    neovim \
    neofetch \
    fish \
    fzf \
    fd \
    bat \
    zip \
    unzip \
    python-pipenv
RUN yay -S --noconfirm \
    asdf-vm

# asdf: install plugin
RUN . /opt/asdf-vm/asdf.sh && asdf plugin add python https://github.com/danhper/asdf-python.git
RUN . /opt/asdf-vm/asdf.sh && asdf plugin add awscli https://github.com/MetricMike/asdf-awscli.git
