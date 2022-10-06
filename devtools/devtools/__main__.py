from typing import Callable, List, TypeVar, TypedDict
import click
import logging
from subprocess import Popen, PIPE, STDOUT
from rich.console import Console
import colorama
from colorama import Fore, Style
import coloredlogs
import os

from devtools.ssm_util import SSMUtil

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


class CommonParam(TypedDict):
    """各コマンド共通のパラメータ"""

    debug: bool  # デバッグモード


R = TypeVar("R")


def log_start_and_end(func: Callable[..., R]) -> Callable[..., R]:  # type: ignore
    """処理の開始と終了時にログを出力するようにするデコレータ

    Args:
        func (Callable[P, R]): 関数

    Returns:
        Callable[P, R]: 最初と最後にログ出力処理を追加した関数
    """
    logger: logging.Logger = logging.getLogger(LOGGING_APP_NAME)

    def wrapper(*args, **kwargs) -> R:  # type: ignore
        logger.info(f"{Fore.GREEN}🔨 {func.__doc__}{Style.RESET_ALL}")
        ret: R = func(*args, **kwargs)
        logger.info(f"{Fore.GREEN}✔ 処理完了しました。{Style.RESET_ALL}")
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
    logger.info(f"{Fore.BLUE}⚡ 別プロセスの処理開始: {command=}{Style.RESET_ALL}")
    status_message = f"[blue]別プロセスで処理中: {command=}\n"
    with console.status(status_message, spinner="dots12"):
        with Popen(args, stdout=PIPE, stderr=STDOUT, universal_newlines=True) as proc:
            for line in proc.stdout or []:
                line_without_newline = line.rstrip("\n")
                logger.info(f"{Style.DIM}{line_without_newline}{Style.RESET_ALL}")
    returncode = proc.returncode
    if returncode == 0:
        logger.info(f"{Fore.BLUE}✔ 別プロセスの処理が正常終了: {command=}{Style.RESET_ALL}")
    else:
        logger.error(
            f"{Fore.RED}❌ 別プロセスの処理が異常終了: {returncode=} {command=}{Style.RESET_ALL}"
        )


@click.group()
@click.option("--debug", is_flag=True, default=False, help="デバッグモード", show_default=True)
@click.pass_context
def cli(ctx: click.Context, debug: bool) -> None:
    """開発中に利用するコマンドを手軽に実行するためのラッパースクリプトです。

    Textualize/richと絵文字を使用（Rich works with Linux, OSX, and Windows.
    True color / emoji works with new Windows Terminal,
    classic terminal is limited to 16 colors.）"""
    param: CommonParam = {"debug": debug}
    ctx.obj = param
    logger: logging.Logger = logging.getLogger(LOGGING_APP_NAME)
    logger.setLevel(logging.DEBUG if debug else logging.INFO)


@cli.command()
@click.pass_obj
@log_start_and_end
def deploy_local(obj: CommonParam) -> None:
    """slsでLocalStackに対してデプロイを実行します。"""
    execute_command(["sls", "deploy", "--stage", "local", "--verbose"])


@cli.command()
@click.pass_obj
@log_start_and_end
def setup_ssm_parameters(obj: CommonParam) -> None:
    """必要なSSMパラメータを登録します"""
    env: str = "local"
    logger: logging.Logger = logging.getLogger(LOGGING_APP_NAME)
    ssm = SSMUtil()
    required_parameters = [
        f"/rotom_bot/{env}/notion/NOTION_API_KEY",
        f"/rotom_bot/{env}/NGROK_AUTHTOKEN",
        f"/rotom_bot/{env}/slack/SLACK_BOT_TOKEN",
        f"/rotom_bot/{env}/slack/SLACK_SIGNING_SECRET",
        f"/rotom_bot/{env}/notion/BACKUP_PARENT_PAGE_NAME",
        f"/rotom_bot/{env}/notion/BACKUP_MESSAGES_DATABASE_NAME",
        f"/rotom_bot/{env}/notion/BACKUP_CHANNELS_DATABASE_NAME",
        f"/rotom_bot/{env}/notion/BACKUP_USERS_DATABASE_NAME",
    ]
    logger.info("SSMパラメータの名前のリストを取得します")
    paramter_names_on_aws = ssm.get_parameter_name_list("prod")
    for path in required_parameters:
        logger.info(f"SSMパラメータ登録の有無をチェックします: {path=}")
        if path in paramter_names_on_aws:
            logger.info(
                f"{Style.DIM}SSMパラメータが登録されているので入力スキップします: {path=}{Style.RESET_ALL}"
            )
        else:
            # パラメータが設定されていない→プロンプトで入力する
            value = click.prompt(f"SSMパラメータが登録されていません。入力してください: {path}", type=str)
            ssm.put_parameter(path, value, "prod")
            logger.info(f"SSMパラメータを登録しました: {path=}")
    # Notionデータベースの名前からIDを取得してSSMに登録
    logger.info("NotionデータベースIDを名前から取得してSSMに登録します")
    api_key: str = ssm.get_parameter(f"/rotom_bot/{env}/notion/NOTION_API_KEY", "prod")
    ssm.set_notion_client(api_key)
    parent_page_id: str = ssm.get_notion_page_id(
        f"/rotom_bot/{env}/notion/BACKUP_PARENT_PAGE_NAME"
    )
    db_name_parameters = [
        f"/rotom_bot/{env}/notion/BACKUP_MESSAGES_DATABASE_NAME",
        f"/rotom_bot/{env}/notion/BACKUP_CHANNELS_DATABASE_NAME",
        f"/rotom_bot/{env}/notion/BACKUP_USERS_DATABASE_NAME",
    ]
    for i, db_name_path in enumerate(db_name_parameters, start=1):
        logger.info(
            f"{Style.DIM}ID取得 {i}/{len(db_name_parameters)} {db_name_path=}{Style.RESET_ALL}"
        )
        db_id = ssm.get_notion_db_id(db_name_path, parent_page_id)
        db_id_path = db_name_path.replace("NAME", "ID")
        logger.info(
            f"{Style.DIM}SSM登録 {i}/{len(db_name_parameters)} {db_id_path=}{Style.RESET_ALL}"
        )
        ssm.put_parameter(db_id_path, db_id, "prod")


@cli.command()
@click.pass_obj
@log_start_and_end
def sync_ssm_parameters_to_localstack(obj: CommonParam) -> None:
    """AWSのSSMパラメータのうちlocalのパスのものをlocalstackにコピーします"""
    logger: logging.Logger = logging.getLogger(LOGGING_APP_NAME)
    ssm = SSMUtil()
    logger.info("AWSのSSMからパラメータを取得します")
    params = ssm.get_parameter_by_path("/rotom_bot/local", "prod")
    logger.info(f"{Style.DIM}{params.keys()=}{Style.RESET_ALL}")
    logger.info("localstackに登録します")
    for k, v in params.items():
        ssm.put_parameter(k, v, "local")


# @cli.command()
# @click.option("--function_name", "-f", required=True, help="関数名")
# @click.pass_obj
# @log_start_and_end
# def deploy_local_function(obj: CommonParam, function_name: str) -> None:
#     """slsでLocalStackに対して関数単体のデプロイを実行します。"""
#     execute_command(
#         [
#             "sls",
#             "deploy",
#             "function",
#             "--function",
#             function_name,
#             "--stage",
#             "local",
#             "--verbose",
#         ]
#     )


# @cli.command()
# @click.option("--function_name", "-f", help="関数名", required=True)
# @click.pass_obj
# @log_start_and_end
# def invoke_lambda(obj: CommonParam, function_name: str) -> None:
#     """LocalStack上の指定されたLambdaを実行します。"""
#     full_function_name = f"backup-slack-local-{function_name}"
#     execute_command(
#         [
#             "aws",
#             "--profile=local",
#             f"--endpoint-url={AWS_ENDPOINT_URL}",
#             "lambda",
#             "invoke",
#             f"--function-name={full_function_name}",
#             "/dev/stdout",
#         ]
#     )


# @cli.command()
# @click.option("--function_name", "-f", help="関数名")
# @click.pass_obj
# @log_start_and_end
# def invoke_api_request(obj: CommonParam, function_name: str) -> None:
#     """LocalStack上の指定されたAPIへリクエストする試験をします。"""
#     # full_function_name = f"backup-slack-local-{function_name}"

#     # TODO
#     # rest-api-idと、resource-idがわかればtest-invoke-methodが使える
#     # awslocal apigateway test-invoke-method --rest-api-id qv0i98brzo --resource-id j0jskyl5ve --http-method POST
#     # または直接URL叩く
#     # curl -XPOST http://localstack:4566/restapis/qv0i98brzo/local/_user_request_/slack/events
#     # それか、ngrokで設定した公開URLを叩くか？

#     # execute_command([
#     #     'aws', '--profile=local', f'--endpoint-url={AWS_ENDPOINT_URL}',
#     #     'lambda', 'invoke', f'--function-name={full_function_name}', '/dev/stdout',
#     # ])


# @cli.command()
# @click.pass_obj
# @log_start_and_end
# def setup_notion_param(obj: CommonParam) -> None:
#     """SSMに、Notionのバックアップ先のpage ID、DB IDを設定します。"""
#     SSMUtil().setup_notion_param_local()


# @cli.command()
# @click.option(
#     "--follow", is_flag=True, default=False, help="最新のログを随時表示するモード", show_default=True
# )
# @click.option("--since", help="取得期間（ex. 30s, 5m, 1h）")
# @click.option("--function_name", "-f", required=True, help="関数名")
# @click.pass_obj
# @log_start_and_end
# def get_lambda_logs(
#     obj: CommonParam, follow: bool, since: str, function_name: str
# ) -> None:
#     """LocalStack上のLambdaのログを取得します。"""
#     full_function_name = f"backup-slack-local-{function_name}"
#     logger: logging.Logger = logging.getLogger(LOGGING_APP_NAME)
#     logger.info(f"{full_function_name=}")
#     if follow:
#         logger.info("待機状態になり、最新のログを随時表示します。")
#         args = [
#             "aws",
#             "--profile=local",
#             f"--endpoint-url={AWS_ENDPOINT_URL}",
#             "logs",
#             "tail",
#             "--follow",
#             f"/aws/lambda/{full_function_name}",
#         ]
#     elif since:
#         logger.info(f"ログを最新の [{since}] 前から表示します。")
#         args = [
#             "aws",
#             "--profile=local",
#             f"--endpoint-url={AWS_ENDPOINT_URL}",
#             "logs",
#             "tail",
#             f"/aws/lambda/{full_function_name}",
#             f"--since={since}",
#         ]
#     else:
#         logger.info("最新のログストリームのログを表示します。")
#         args = [
#             "aws",
#             "--profile=local",
#             f"--endpoint-url={AWS_ENDPOINT_URL}",
#             "logs",
#             "describe-log-streams",
#             "--log-group-name",
#             f"/aws/lambda/{full_function_name}",
#             "--max-items",
#             "1",
#             "--order-by",
#             "LastEventTime",
#             "--descending",
#             "--query",
#             "logStreams[].logStreamName",
#             "--output",
#             "text",
#         ]
#         latest_log_stream_name = check_output(args, universal_newlines=True).split(
#             "\n"
#         )[0]
#         logger.info(f"{latest_log_stream_name=}")
#         args = [
#             "aws",
#             "--profile=local",
#             f"--endpoint-url={AWS_ENDPOINT_URL}",
#             "logs",
#             "tail",
#             f"/aws/lambda/{full_function_name}",
#             "--log-stream-names",
#             latest_log_stream_name,
#             "--since",
#             "30d",
#         ]
#     execute_command(args)


# @cli.command()
# @click.pass_obj
# @click.option("--name", help="パラメータのパス", required=True)
# @click.option("--value", help="パラメータの値", required=True)
# @log_start_and_end
# def put_parameter(obj: CommonParam, name: str, value: str) -> None:
#     """SSMにパラメータを登録します。"""
#     full_path = f"/rotom_bot/local/{name}"
#     logger: logging.Logger = logging.getLogger(LOGGING_APP_NAME)
#     logger.info(f"{full_path=}")
#     logger.info(f"{value=}")
#     args = [
#         "awslocal",
#         "ssm",
#         "put-parameter",
#         f"--name={full_path}",
#         f"--value={value}",
#         "--type=String",
#         "--overwrite",
#     ]
#     execute_command(args)


if __name__ == "__main__":
    cli()
