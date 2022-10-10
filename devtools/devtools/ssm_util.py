import os
from typing import Literal

import boto3
import notion_client


class SSMUtil:
    notion_client: notion_client.Client
    client: dict[str, boto3.client] = {}

    def __init__(self) -> None:
        # ローカル環境クライアント
        self.client["local"] = boto3.client(
            "ssm",
            endpoint_url=os.environ["AWS_ENDPOINT_URL"],
            aws_access_key_id="test",
            aws_secret_access_key="test",
        )
        self.client["prod"] = boto3.client("ssm")
        # Notionクライアント

    def get_parameter_name_list(self, env: Literal["prod", "local"]) -> list[str]:
        """AWS上のパラメータの名前のリストを返す

        Returns:
            list[str]: パラメータ名のリスト
        """
        paginator = self.client[env].get_paginator("describe_parameters")
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

    def get_parameter_by_path(
        self, path: str, env: Literal["prod", "local"]
    ) -> dict[str, str]:
        paginator = self.client[env].get_paginator("get_parameters_by_path")
        params: dict[str, str] = {}
        for response in paginator.paginate(Path=path, Recursive=True):
            params |= {p["Name"]: p["Value"] for p in response["Parameters"]}
        return params

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
