import os
from notion_client import Client
from typing import Any
from typing import TypedDict


class NotionMessageBackupSetting(TypedDict):
    # データベースID
    MESSAGES_DATABASE_ID: str  # メッセージ
    CHANNELS_DATABASE_ID: str  # チャンネル
    USERS_DATABASE_ID: str  # ユーザー
    # リレーションの列の名前
    CHANNEL_KEY_NAME: str  # チャンネル
    USER_KEY_NAME: str  # ユーザー


class NotionMessageBackupClient(Client):
    setting: NotionMessageBackupSetting

    def __init__(self, setting: NotionMessageBackupSetting) -> None:
        super().__init__(auth=os.environ["NOTION_API_KEY"])
        self.setting = setting

    def get_user_relation_id(self, user_id: str) -> str:
        """ユーザーのリレーションに設定するレコードのIDを取得する

        Args:
            user_id (str): Slack上のユーザーID

        Returns:
            str: ユーザーに対応するNotion上のページID
        """
        query_parameter = {
            "database_id": self.setting['USERS_DATABASE_ID'],
            "filter": {
                "property": self.setting['USER_KEY_NAME'],
                "rich_text": {"contains": user_id}
            },
        }
        results = self.databases.query(**query_parameter).get("results")  # type: ignore
        if len(results) == 0:
            # TODO: 該当しない場合、新規作成する？
            return 'NOT_FOUND'
        elif len(results) == 1:
            return str(results[0]['id'])
        else:
            # TODO: 複数該当する場合。すべて採用にする？
            return 'NOT_FOUND'

    def get_channel_relation_id(self, channel_id: str) -> str:
        """チャンネルのリレーションに設定するレコードのIDを取得する

        Args:
            channel_id (str): Slack上のチャンネルID

        Returns:
            str: チャンネルに対応するNotion上のページID
        """
        query_parameter = {
            "database_id": self.setting['CHANNELS_DATABASE_ID'],
            "filter": {
                "property": self.setting['CHANNEL_KEY_NAME'],
                "rich_text": {"contains": channel_id}
            },
        }
        results = self.databases.query(**query_parameter).get("results")  # type: ignore
        if len(results) == 0:
            # TODO: 該当しない場合、新規作成する？
            return 'NOT_FOUND'
        elif len(results) == 1:
            return str(results[0]['id'])
        else:
            # TODO: 複数該当する場合。すべて採用にする？
            return 'NOT_FOUND'


    def get_page_properties_dict(
            self,
            ts: str,
            channel_relation_id: str,
            user_relation_id: str,
            content: str
            ) -> dict[str, Any]:
        """登録するプロパティの辞書を返す。

        Args:
            ts (str): 投稿日時のUNIXタイムスタンプ
            channel_relation_id (str): チャンネルのリレーションに登録するページID
            user_relation_id (str): ユーザーのリレーションに登録するページID
            content (str): 生のメッセージ本文

        Returns:
            dict: プロパティの辞書
        """
        properties = {
            "ts": {
                "title": [
                    {"text": {"content": ts}}
                ]
            },
            "コンテンツの先頭": {
                "type": "rich_text",
                "rich_text": [
                    {
                        "type": "text",
                        "text": {"content": content[:20]},
                    },
                ],
            },
            "チャンネル": {
                "type": "relation",
                "relation": [{"id": channel_relation_id}]
            },
            "ユーザー": {
                "type": "relation",
                "relation": [{"id": user_relation_id}]
            },
        }
        return properties


    def get_page_content_dict(self, content: str) -> list[dict[str, Any]]:
        """メッセージ本文から、ページコンテンツを作成して返す。

        Args:
            content (str): 生のメッセージ本文

        Returns:
            list[dict]: ページコンテンツの辞書（ページの子Blockのリスト）
        """
        children = [
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{
                        "type": "text",
                        "text": {"content": content}
                    }],
                    "color": "red",
                },
            },
        ]
        return children


    def create_message_backup(
            self,
            ts: str,
            channel_id: str,
            user_id: str,
            content: str
            ) -> dict[str, Any]:
        # ユーザーとチャンネルのリレーションに登録するページのIDを取得する。
        create_parameter = {
            "parent": {"database_id": self.setting['MESSAGES_DATABASE_ID']},
            "properties": self.get_page_properties_dict(
                ts=ts,
                channel_relation_id=self.get_channel_relation_id(channel_id),
                user_relation_id=self.get_user_relation_id(user_id),
                content=content
            ),
            "children": self.get_page_content_dict(content),
        }
        return self.pages.create(**create_parameter)  # type: ignore
