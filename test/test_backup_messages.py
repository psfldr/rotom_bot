from importlib.resources import contents
import time
from backup_slack.backup_messages import NotionMessageBackupClient
from backup_slack.backup_messages import NotionMessageBackupSetting
import functools
from notion_client import Client
import os
from typing import Any



class TestNotionMessageBackupClient():
    client: NotionMessageBackupClient
    BACKUP_PARENT_PAGE_NAME: str = 'Slackバックアップ'
    BACKUP_PARENT_PAGE_ID: str
    raw_client = Client(auth=os.environ["NOTION_API_KEY"])

    def get_child_database_id(self, database_name: str) -> str:
        """BACKUP_PARENT_PAGE_NAMEを親に持つデータベースのIDを取得する

        Args:
            database_name (str): データベース名

        Returns:
            str: データベースID
        """
        search_result = self.raw_client.search(  # type: ignore
            query=database_name,
            filter={'property': 'object', 'value': 'database'}
        )['results']
        children = [i for i in search_result if i['parent']['page_id'] == self.BACKUP_PARENT_PAGE_ID]  # type: ignore
        return str(children[-1]['id'])


    def setup(self) -> None:
        self.raw_client = Client(auth=os.environ["NOTION_API_KEY"])
        self.BACKUP_PARENT_PAGE_ID: str = self.raw_client.search(query=self.BACKUP_PARENT_PAGE_NAME)['results'][0]['id']  # type: ignore
        setting: NotionMessageBackupSetting = {
            # 親ページを親に持つデータベースのIDを取得する
            'MESSAGES_DATABASE_ID': self.get_child_database_id('メッセージ'),
            'CHANNELS_DATABASE_ID': self.get_child_database_id('チャンネル'),
            'USERS_DATABASE_ID': self.get_child_database_id('ユーザー'),
            'CHANNEL_KEY_NAME': 'チャンネルID',
            'USER_KEY_NAME': 'ユーザーID',
        }
        self.client = NotionMessageBackupClient(setting)

    def test_create_message_backup(self, mocker: Any) -> None:
        # mocking
        mock_targets = [
            'get_page_properties_dict',
            'get_page_content_dict',
            'get_channel_relation_id',
            'get_user_relation_id',
        ]
        patch_nmbc = functools.partial(mocker.patch.object, NotionMessageBackupClient)
        mocks = {i: patch_nmbc(i) for i in mock_targets}
        mock_create = mocker.patch.object(self.client.pages, 'create')
        # 実行
        ts = f'{time.time():10.6f}'
        response = self.client.create_message_backup(
            ts=ts,
            channel_id='AAAAAAAAAAAA',
            user_id='BBBBBBBBBBBB',
            content=f'テスト本文（{ts}）',
            slack_workspace_name='CCCCCCCCCCCC'
        )
        # 検証
        # 戻り値はcreateリクエストのレスポンス
        assert response == mock_create.return_value  # type: ignore
        # createリクエストでは親DB、プロパティ、ページコンテンツ（子ブロック）を渡す
        self.client.pages.create.assert_called_with(  # type: ignore
            parent={"database_id": self.client.setting['MESSAGES_DATABASE_ID']},
            properties=mocks['get_page_properties_dict'].return_value,
            children=mocks['get_page_content_dict'].return_value
        )
        # プロパティ作成では、タイムスタンプ、チャンネルID、ユーザーID、生のメッセージ本文を渡す
        mocks['get_page_properties_dict'].assert_called_with(
            ts=ts,
            channel_relation_id=mocks['get_channel_relation_id'].return_value,
            user_relation_id=mocks['get_user_relation_id'].return_value,
            content=f'テスト本文（{ts}）',
            slack_workspace_name='CCCCCCCCCCCC'
        )

    # def test_create_message_backup_nomock(self) -> None:
    #     # 実行
    #     ts: str = f'{time.time():10.6f}'
    #     response = self.client.create_message_backup(
    #         ts=ts,
    #         channel_id='TEST1',
    #         user_id='TEST1',
    #         content=f'テスト本文（{ts}）',
    #         slack_workspace_name='DEBUG'
    #     )
    #     print(response)
