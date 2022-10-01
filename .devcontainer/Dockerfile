# syntax=docker/dockerfile:1
FROM archlinux/archlinux:latest
# base-develパッケージインストール
RUN pacman -Syy \
    && pacman -S --noconfirm base-devel
# ユーザー作成
RUN groupadd docker
RUN useradd -m -G wheel,docker --shell /bin/bash devuser
RUN echo "%docker ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers
RUN echo "%wheel ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers
USER devuser
WORKDIR /home/devuser/rotom_bot
# 一般的なパッケージインストール
RUN sudo pacman -Syy \
    && sudo pacman -S --noconfirm \
    git go docker xsel neovim neofetch fish fzf fd bat zip unzip
# yayインストール
RUN git clone https://aur.archlinux.org/yay.git && cd yay && \
    makepkg -si --noconfirm && cd ../ && rm -r yay
RUN yay -S --noconfirm asdf-vm

# プロジェクト特有のパッケージ
# asdfで必要ツールインストール
RUN . /opt/asdf-vm/asdf.sh \
    && asdf plugin add python https://github.com/danhper/asdf-python.git \
    && asdf plugin add awscli https://github.com/MetricMike/asdf-awscli.git \
    && asdf plugin add nodejs https://github.com/asdf-vm/asdf-nodejs.git \
    && asdf install awscli 2.7.35 \
    && asdf local awscli 2.7.35 \
    && asdf install nodejs 16.17.0 \
    && asdf local nodejs 16.17.0 \
    && asdf install python 3.9.14
RUN sudo pacman -Syy \
    && sudo pacman -S --noconfirm python python-pip python-pipenv \
    && pip install setuptools \
    # https://stackoverflow.com/questions/7446187/no-module-named-pkg-resources
    && yay -S --noconfirm ngrok git-secrets
