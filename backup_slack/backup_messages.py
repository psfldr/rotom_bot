import os
from notion_client import Client


class NotionMessageBackupClient():
    client: Client
    BACKUP_PARENT_PAGE_ID: str
    MESSAGES_DATABASE_ID: str
    CHANNELS_DATABASE_ID: str
    USERS_DATABASE_ID: str
    CHANNEL_KEY_NAME = 'チャンネルID'
    USER_KEY_NAME = 'ユーザーID'

    def __init__(self):
        # Notionクライアントを作成
        self.client = Client(auth=os.environ["NOTION_API_KEY"])
        # 親ページ（名前が「Slackバックアップ」のページ）のIDを取得
        self.BACKUP_PARENT_PAGE_ID = self.client.search(query='Slackバックアップ')['results'][0]['id']
        # 親ページを親に持つデータベースのIDを取得する
        self.MESSAGES_DATABASE_ID = self.get_child_database_id('メッセージ')
        self.CHANNELS_DATABASE_ID = self.get_child_database_id('チャンネル')
        self.USERS_DATABASE_ID = self.get_child_database_id('ユーザー')

    def get_child_database_id(self, database_name: str) -> str:
        """BACKUP_PARENT_PAGE_IDを親に持つデータベースのIDを取得する

        Args:
            database_name (str): データベース名

        Returns:
            str: データベースID
        """
        search_result = self.client.search(
            query=database_name,
            filter={'property': 'object', 'value': 'database'}
        )['results']
        children = [i for i in search_result if i['parent']['page_id'] == self.BACKUP_PARENT_PAGE_ID]
        return children[0]['id']

    def get_user_relation_id(self, user_id: str) -> str:
        """ユーザーのリレーションに設定するレコードのIDを取得する

        Args:
            user_id (str): Slack上のユーザーID

        Returns:
            str: ユーザーに対応するNotion上のページID
        """
        query_parameter = {
            "database_id": self.USERS_DATABASE_ID,
            "filter": {
                "property": self.USER_KEY_NAME,
                "rich_text": {"contains": user_id}
            },
        }
        results = self.client.databases.query(**query_parameter).get("results")
        if len(results) == 0:
            # TODO: 該当しない場合、新規作成する？
            return None
        elif len(results) == 1:
            return results[0]['id']
        else:
            # TODO: 複数該当する場合。すべて採用にする？
            return None

    def get_channel_relation_id(self, channel_id: str) -> str:
        """チャンネルのリレーションに設定するレコードのIDを取得する

        Args:
            channel_id (str): Slack上のチャンネルID

        Returns:
            str: チャンネルに対応するNotion上のページID
        """
        query_parameter = {
            "database_id": self.CHANNELS_DATABASE_ID,
            "filter": {
                "property": self.CHANNEL_KEY_NAME,
                "rich_text": {"contains": channel_id}
            },
        }
        results = self.client.databases.query(**query_parameter).get("results")
        if len(results) == 0:
            # TODO: 該当しない場合、新規作成する？
            return None
        elif len(results) == 1:
            return results[0]['id']
        else:
            # TODO: 複数該当する場合。すべて採用にする？
            return None


    def get_page_properties_dict(
            self,
            ts: str,
            channel_relation_id: str,
            user_relation_id: str,
            content: str
            ) -> dict:
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


    def get_page_content_dict(self, content: str) -> list[dict]:
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
            ) -> None:
        # ユーザーとチャンネルのリレーションに登録するページのIDを取得する。
        create_parameter = {
            "parent": {"database_id": self.MESSAGES_DATABASE_ID},
            "properties": self.get_page_properties_dict(
                ts=ts,
                channel_relation_id=self.get_channel_relation_id(channel_id),
                user_relation_id=self.get_user_relation_id(user_id),
                content=content
            ),
            "children": self.get_page_content_dict(content),
        }
        return self.client.pages.create(**create_parameter)
