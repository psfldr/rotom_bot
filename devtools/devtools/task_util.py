import logging
import os
from subprocess import PIPE, STDOUT, Popen
from typing import List

import colorama
import coloredlogs
from colorama import Fore, Style
from rich.console import Console

AWS_ENDPOINT_URL = os.environ["AWS_ENDPOINT_URL"]
colorama.init()
console = Console()  #

# ログ
LOGGING_APP_NAME = "Devtools"
logger: logging.Logger = logging.getLogger(LOGGING_APP_NAME)
coloredlogs.install(
    level=logging.DEBUG,
    fmt="%(asctime)s %(levelname)s %(message)s",
    datefmt="[%y-%m-%d %H:%M:%S]",
    logger=logger,
)


def execute_command(args: List[str], cwd: str = "") -> int:
    """コマンドをサブプロセスで実行する。

    Args:
        args (list[str]): コマンドの引数
        cwd (str): 実行時のディレクトリ
    Returns:
        int: リターンコード
    """
    command = " ".join(args)
    logger: logging.Logger = logging.getLogger(LOGGING_APP_NAME)
    logger.info(f"{Fore.BLUE}⚡ サブプロセスの処理開始: {command=}{Style.RESET_ALL}")
    status_message = f"[blue]サブプロセスで処理中: {command=}\n"
    cwd = cwd or os.getcwd()
    with console.status(status_message, spinner="simpleDotsScrolling"):
        with Popen(
            args, stdout=PIPE, stderr=STDOUT, universal_newlines=True, cwd=cwd
        ) as proc:
            try:
                for line in proc.stdout or []:
                    line_without_newline = line.rstrip("\n")
                    logger.info(f"{Style.DIM}{line_without_newline}{Style.RESET_ALL}")
            except KeyboardInterrupt:
                for line in proc.stdout or []:
                    line_without_newline = line.rstrip("\n")
                    logger.info(f"{Style.DIM}{line_without_newline}{Style.RESET_ALL}")
    returncode = proc.returncode
    if returncode == 0:
        logger.info(f"{Fore.BLUE}✔ サブプロセスの処理が正常終了: {command=}{Style.RESET_ALL}")
    else:
        logger.error(
            f"{Fore.RED}❌ サブプロセスの処理が異常終了: {returncode=} {command=}{Style.RESET_ALL}"
        )
    return returncode
