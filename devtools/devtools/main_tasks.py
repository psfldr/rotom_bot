from .task_util import execute_command, LOGGING_APP_NAME
from .ssm_util import SSMUtil
from invoke import call, run, task, Collection
import logging
from colorama import Style


@task  # type: ignore
def start_localstack(c, background=False):  # type: ignore
    """LocalStackを起動します"""
    args = [
        "docker-compose",
        "--file",
        "localstack/docker-compose.yml",
        "up",
    ]
    if background:
        args.append("-d")
    run(" ".join(args), pty=True)


@task  # type: ignore
def stop_localstack(c):  # type: ignore
    """LocalStackを停止します"""
    args = [
        "docker-compose",
        "--file",
        "localstack/docker-compose.yml",
        "down",
    ]
    run(" ".join(args), pty=True)


@task  # type: ignore
def setup_ssm_parameters(c):  # type: ignore
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
            value = input(f"SSMパラメータが登録されていません。入力してください: {path}")
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


@task(call(start_localstack, background=True), setup_ssm_parameters)  # type: ignore
def sync_ssm_parameters_to_localstack(c):  # type: ignore
    """AWSからlocalstackMへSSMパラメータをコピーします"""
    logger: logging.Logger = logging.getLogger(LOGGING_APP_NAME)
    ssm = SSMUtil()
    logger.info("AWSのSSMからパラメータを取得します")
    params = ssm.get_parameter_by_path("/rotom_bot/local", "prod")
    logger.info(f"{Style.DIM}{params.keys()=}{Style.RESET_ALL}")
    logger.info("localstackに登録します")
    for k, v in params.items():
        ssm.put_parameter(k, v, "local")


@task(sync_ssm_parameters_to_localstack)  # type: ignore
def deploy_local(c):  # type: ignore
    """slsでLocalStackに対してデプロイを実行します。"""
    execute_command(["sls", "deploy", "--stage", "local", "--verbose"])


ns: Collection = Collection()
ns.add_task(start_localstack)
ns.add_task(stop_localstack)
ns.add_task(setup_ssm_parameters)
ns.add_task(sync_ssm_parameters_to_localstack)
ns.add_task(deploy_local)
