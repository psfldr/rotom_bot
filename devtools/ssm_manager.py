from typing import Literal
import boto3
from boto3.session import Session
import notion_client
import os


class SSMManager:
    notion_client: notion_client.Client
    client: dict[str, boto3.client] = {}

    def __init__(self) -> None:
        # ローカル環境クライアント
        session = Session(profile_name="local")
        self.client["local"] = session.client(
            "ssm", endpoint_url=os.environ["AWS_ENDPOINT_URL"]
        )
        self.client["prod"] = boto3.client("ssm")
        # Notionクライアント

    def get_parameter_name_list(self, env: Literal["prod", "local"]) -> list[str]:
        """AWS上のパラメータの名前のリストを返す

        Returns:
            list[str]: パラメータ名のリスト
        """
        paginator = self.client[env].get_paginator('describe_parameters')
        names: list[str] = []
        for response in paginator.paginate():
            names += [p["Name"] for p in response["Parameters"]]
        return names

    def get_parameter(self, path: str, env: Literal["prod", "local"]) -> str:
        """ssm clientのget_parameterをシンプルにするラッパー

        Args:
            path (str): パラメータパス

        Returns:
            str: 対応するパラメータ
        """
        response = self.client[env].get_parameter(Name=path)
        value: str = response["Parameter"]["Value"]
        return value

    def put_parameter(
        self, path: str, value: str, env: Literal["prod", "local"]
    ) -> None:
        """ssm clientのput_parameterをシンプルにするラッパー

        Args:
            path (str): パラメータパス
            value (str): パラメータの値
        """
        self.client[env].put_parameter(
            Name=path, Value=value, Overwrite=True, Type="String"
        )

    def set_notion_client(self, api_key: str) -> None:
        self.notion_client = notion_client.Client(auth=api_key)

    def get_notion_db_id(self, db_name_path: str, parent_page_id: str) -> str:
        """NotionデータベースのIDを取得する

        Args:
            parent_page_id (str): データベースの親ページのID
            path (str): データベース名を記録しているSSMパラメータパス

        Returns:
            str: データベースID
        """
        db_name: str = self.get_parameter(db_name_path, "prod")
        search_result = self.notion_client.search(  # type: ignore
            query=db_name, filter={"property": "object", "value": "database"}
        )["results"]
        children = [i for i in search_result if i["parent"]["page_id"] == parent_page_id]  # type: ignore
        db_id = str(children[-1]["id"])
        return db_id

    def get_notion_page_id(self, path: str) -> str:
        """Notionのページ名のSSMパラメータパスからIDを取得する

        Args:
            name (str): Notionページ名のSSMパラメータパス

        Returns:
            str: ページID
        """
        page_name = self.get_parameter(path, "prod")
        parent_page_id: str = self.notion_client.search(query=page_name)["results"][0]["id"]  # type: ignore
        return parent_page_id

        # self.local_ssm_client.put_parameter(
        #     Name=path_format.format("BACKUP_PARENT_PAGE_ID"),
        #     Value=parent_page_id,
        #     Type="String",
        #     Overwrite=True,
        #     Tier="Standard",
        #     DataType="text",
        # )
        # logger.info("DB名からIDを取得し、SSMに登録します。")
        # database_name_keys = [
        #     "BACKUP_MESSAGES_DATABASE_NAME",
        #     "BACKUP_CHANNELS_DATABASE_NAME",
        #     "BACKUP_USERS_DATABASE_NAME",
        # ]
        # for i, key in enumerate(database_name_keys, start=1):
        #     database_name_path = path_format.format(key)
        #     logger.info(
        #         f"{Style.DIM}ID取得 {i}/{len(database_name_keys)} {database_name_path=}{Style.RESET_ALL}"
        #     )
        #     database_id = self.get_child_database_id_and_set_prod(
        #         parent_page_id, database_name_path
        #     )
        #     database_id_path = database_name_path.replace("NAME", "ID")
        #     self.local_ssm_client.put_parameter(
        #         Name=database_id_path,
        #         Value=database_id,
        #         Type="String",
        #         Overwrite=True,
        #         Tier="Standard",
        #         DataType="text",
        #     )
        #     logger.info(
        #         f"{Style.DIM}SSM登録 {i}/{len(database_name_keys)} {database_id_path=}{Style.RESET_ALL}"
        #     )
