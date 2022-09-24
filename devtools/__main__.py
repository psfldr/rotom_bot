from typing import IO, Callable, List, TypeVar, TypedDict
import click
import logging
from subprocess import Popen, PIPE, STDOUT
from rich.console import Console
import colorama
from colorama import Fore, Back, Style
import coloredlogs

from devtools.ssm_manager import SSMManager

colorama.init()
console = Console()  # 

# ログ
LOGGING_APP_NAME = 'Devtools'
logger: logging.Logger = logging.getLogger(LOGGING_APP_NAME)
coloredlogs.install(
    level=logging.DEBUG,
    fmt='%(asctime)s %(levelname)s %(message)s',
    datefmt='[%y-%m-%d %H:%M:%S]',
    logger=logger
)


class CommonParam(TypedDict):
    """各コマンド共通のパラメータ"""
    debug: bool  # デバッグモード


R = TypeVar('R')


def log_start_and_end(func: Callable[..., R]) -> Callable[..., R]:  # type: ignore
    """処理の開始と終了時にログを出力するようにするデコレータ

    Args:
        func (Callable[P, R]): 関数

    Returns:
        Callable[P, R]: 最初と最後にログ出力処理を追加した関数
    """
    logger: logging.Logger = logging.getLogger(LOGGING_APP_NAME)
    def wrapper(*args, **kwargs) -> R:  # type: ignore
        logger.info(f'{Fore.GREEN}🔨 {func.__doc__}{Style.RESET_ALL}')
        ret: R = func(*args, **kwargs)
        logger.info(f'{Fore.GREEN}✔ 処理完了しました。{Style.RESET_ALL}')
        return ret
    wrapper.__name__ = func.__name__
    return wrapper


def execute_command(args: List[str]) -> None:
    """コマンドを別プロセスで実行する。

    Args:
        args (list[str]): コマンドの引数
    """
    command = " ".join(args)
    logger: logging.Logger = logging.getLogger(LOGGING_APP_NAME)
    logger.info(f'{Fore.BLUE}⚡ 別プロセスの処理開始: {command=}{Style.RESET_ALL}')
    status_message = f'[blue]別プロセスで処理中: {command=}\n'
    with console.status(status_message, spinner='dots12') as status:
        with Popen(args, stdout=PIPE, stderr=STDOUT, universal_newlines=True) as proc:
            for line in proc.stdout or []:
                line_without_newline = line.rstrip("\n")
                logger.info(f'{Style.DIM}{line_without_newline}{Style.RESET_ALL}')
    logger.info(f'{Fore.BLUE}✔ 別プロセスの処理終了: {command=}{Style.RESET_ALL}')


@click.group()
@click.option('--debug', is_flag=True, default=False, help='デバッグモード', show_default=True)
@click.pass_context
def cli(ctx: click.Context, debug: bool) -> None:
    """開発中に利用するコマンドを手軽に実行するためのラッパースクリプトです。

    Textualize/richと絵文字を使用（Rich works with Linux, OSX, and Windows.
    True color / emoji works with new Windows Terminal,
    classic terminal is limited to 16 colors.）"""
    param: CommonParam = {'debug': debug}
    ctx.obj = param
    logger: logging.Logger = logging.getLogger(LOGGING_APP_NAME)
    logger.setLevel(logging.DEBUG if debug else logging.INFO)


@cli.command()
@click.pass_obj
@log_start_and_end
def deploy_local(obj: CommonParam) -> None:
    """slsでLocalStackに対してデプロイを実行します。"""
    execute_command(['sls', 'deploy', '--stage', 'local', '--verbose'])


@cli.command()
@click.option('--function_name', '-f', required=True, help='関数名')
@click.pass_obj
@log_start_and_end
def deploy_local_function(obj: CommonParam, function_name: str) -> None:
    """slsでLocalStackに対して関数単体のデプロイを実行します。"""
    execute_command([
        'sls', 'deploy', 'function', '--function', function_name,
        '--stage', 'local', '--verbose'
    ])


@cli.command()
@click.option('--function_name', '-f', help='関数名')
@click.pass_obj
@log_start_and_end
def invoke_lambda(obj: CommonParam, function_name: str) -> None:
    """LocalStack上の指定されたLambdaを実行します。"""
    full_function_name = f'backup-slack-local-{function_name}'
    execute_command([
        'aws', '--profile=local', '--endpoint-url=http://localstack:4566',
        'lambda', 'invoke', f'--function-name={full_function_name}', '/dev/stdout',
    ])


@cli.command()
@click.pass_obj
@log_start_and_end
def copy_param_to_local(obj: CommonParam) -> None:
    """AWSのSSMからパラメータをLocalStackにコピーします。"""
    ssm_manager = SSMManager(
        prod_profile='prod',
        local_profile='local',
        local_endpoint='http://localstack:4566'
    )
    ssm_manager.copy_parameters(mode='prod_to_local', path='/Eggmuri/Local/Slack')


@cli.command()
@click.pass_obj
@log_start_and_end
def setup_notion_param(obj: CommonParam) -> None:
    """SSMに、Notionのバックアップ先のpage ID、DB IDを設定します。"""
    ssm_manager = SSMManager(
        prod_profile='prod',
        local_profile='local',
        local_endpoint='http://localstack:4566'
    )
    ssm_manager.setup_notion_param_prod()
    ssm_manager.copy_parameters(mode='prod_to_prod', path='/eggmuri/prod/rotom_bot/notion/')
    ssm_manager.copy_parameters(mode='prod_to_local', path='/eggmuri/prod/rotom_bot/notion')


@cli.command()
@click.option('--follow', is_flag=True, default=False, help='最新のログを随時表示するモード', show_default=True)
@click.option('--since', default='5m', help='取得期間（ex. 30s, 5m, 1h）', show_default=True)
@click.option('--function_name', '-f', required=True, help='関数名')
@click.pass_obj
@log_start_and_end
def get_lambda_logs(obj: CommonParam, follow: bool, since: str, function_name: str) -> None:
    """LocalStack上のLambdaのログを取得します。"""
    full_function_name = f'backup-slack-local-{function_name}'
    logger: logging.Logger = logging.getLogger(LOGGING_APP_NAME)
    logger.info(f'{full_function_name=}')
    if follow:
        logger.info('待機状態になり、最新のログを随時表示します。')
        args = [
            'aws', '--profile=local', '--endpoint-url=http://localstack:4566',
            'logs', 'tail', '--follow', f'/aws/lambda/{full_function_name}',
        ]
    else:
        logger.info(f'ログを最新の [{since}] 前から表示します。')
        args = [
            'aws', '--profile=local', '--endpoint-url=http://localstack:4566',
            'logs', 'tail', f'/aws/lambda/{full_function_name}',
        ]
    execute_command(args)


if __name__ == '__main__':
    cli()
