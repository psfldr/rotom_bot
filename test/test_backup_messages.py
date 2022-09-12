from importlib.resources import contents
import time
from backup_slack.backup_messages import NotionMessageBackupClient
import functools


class TestNotionMessageBackupClient():
    def setup(self):
        self.client = NotionMessageBackupClient()

    def test_create_message_backup(self, mocker):
        # mocking
        mock_targets = [
            'get_page_properties_dict',
            'get_page_content_dict',
            'get_channel_relation_id',
            'get_user_relation_id',
        ]
        patch_nmbc = functools.partial(mocker.patch.object, NotionMessageBackupClient)
        mocks = {i: patch_nmbc(i) for i in mock_targets}
        self.client.client = mocker.Mock()
        # 実行
        ts = f'{time.time():10.6f}'
        response = self.client.create_message_backup(
            ts=ts,
            channel_id='AAAAAAAAAAAA',
            user_id='BBBBBBBBBBBB',
            content=f'テスト本文（{ts}）'
        )
        # 検証
        # 戻り値はcreateリクエストのレスポンス
        assert response == self.client.client.pages.create.return_value
        # createリクエストでは親DB、プロパティ、ページコンテンツ（子ブロック）を渡す
        self.client.client.pages.create.assert_called_with(
            parent={"database_id": self.client.MESSAGES_DATABASE_ID},
            properties=mocks['get_page_properties_dict'].return_value,
            children=mocks['get_page_content_dict'].return_value
        )
        # プロパティ作成では、タイムスタンプ、チャンネルID、ユーザーID、生のメッセージ本文を渡す
        mocks['get_page_properties_dict'].assert_called_with(
            ts=ts,
            channel_relation_id=mocks['get_channel_relation_id'].return_value,
            user_relation_id=mocks['get_user_relation_id'].return_value,
            content=f'テスト本文（{ts}）'
        )

    # def test_create_message_backup_nomock(self):
    #     # 実行
    #     ts = f'{time.time():10.6f}'
    #     response = self.client.create_message_backup(
    #         ts=ts,
    #         channel_id='TEST1',
    #         user_id='TEST1',
    #         content=f'テスト本文（{ts}）'
    #     )