import logging
import boto3
from boto3.session import Session
import notion_client
import os
from colorama import Style

LOGGING_APP_NAME = "Devtools"


class SSMManager:
    local_ssm_client: boto3.client
    notion_client: notion_client.Client

    def __init__(self) -> None:
        # ローカル環境クライアント
        session = Session(profile_name="local")
        self.local_ssm_client = session.client(
            "ssm", endpoint_url=os.environ["AWS_ENDPOINT_URL"]
        )
        # Notionクライアント
        param_name = "/rotom_bot/local/notion/NOTION_API_KEY"
        api_key = self.get_parameter(param_name)
        self.notion_client = notion_client.Client(auth=api_key)

    def get_parameter(self, path: str) -> str:
        """ssm clientのget_parameterをシンプルにするラッパー

        Args:
            path (str): パラメータパス

        Returns:
            str: 対応するパラメータ
        """
        response = self.local_ssm_client.get_parameter(Name=path)
        value: str = response["Parameter"]["Value"]
        return value

    def get_child_database_id_and_set_prod(self, parent_page_id: str, path: str) -> str:
        """NotionデータベースのIDを取得する

        Args:
            parent_page_id (str): データベースの親ページのID
            path (str): データベース名を記録しているSSMパラメータパス

        Returns:
            str: データベースID
        """
        database_name: str = self.get_parameter(path)
        search_result = self.notion_client.search(  # type: ignore
            query=database_name, filter={"property": "object", "value": "database"}
        )["results"]
        children = [i for i in search_result if i["parent"]["page_id"] == parent_page_id]  # type: ignore
        database_id = str(children[-1]["id"])
        return database_id

    def setup_notion_param_local(self) -> None:
        logger: logging.Logger = logging.getLogger(LOGGING_APP_NAME)
        logger.info("バックアップの親ページ名からIDを取得し、SSMに登録します。")
        path_format = "/rotom_bot/local/notion/{}"
        parent_page_name_path = path_format.format("BACKUP_PARENT_PAGE_NAME")
        parent_page_name: str = self.get_parameter(parent_page_name_path)
        parent_page_id: str = self.notion_client.search(query=parent_page_name)["results"][0]["id"]  # type: ignore
        self.local_ssm_client.put_parameter(
            Name=path_format.format("BACKUP_PARENT_PAGE_ID"),
            Value=parent_page_id,
            Type="String",
            Overwrite=True,
            Tier="Standard",
            DataType="text",
        )
        logger.info("DB名からIDを取得し、SSMに登録します。")
        database_name_keys = [
            "BACKUP_MESSAGES_DATABASE_NAME",
            "BACKUP_CHANNELS_DATABASE_NAME",
            "BACKUP_USERS_DATABASE_NAME",
        ]
        for i, key in enumerate(database_name_keys, start=1):
            database_name_path = path_format.format(key)
            logger.info(
                f"{Style.DIM}ID取得 {i}/{len(database_name_keys)} {database_name_path=}{Style.RESET_ALL}"
            )
            database_id = self.get_child_database_id_and_set_prod(
                parent_page_id, database_name_path
            )
            database_id_path = database_name_path.replace("NAME", "ID")
            self.local_ssm_client.put_parameter(
                Name=database_id_path,
                Value=database_id,
                Type="String",
                Overwrite=True,
                Tier="Standard",
                DataType="text",
            )
            logger.info(
                f"{Style.DIM}SSM登録 {i}/{len(database_name_keys)} {database_id_path=}{Style.RESET_ALL}"
            )
