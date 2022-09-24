import os
import boto3
import time
from backup_slack.backup_message_notion import BackupMessageNotionClient
from backup_slack.backup_message_notion import BackupMessageNotionSetting

ENV = os.environ['ENV']
ssm_client: boto3.client = boto3.client('ssm')


def get_parameter(path: str) -> str:
    param_name = f'/Eggmuri/{ENV.title()}/{path}'
    param: str = ssm_client.get_parameter(Name=param_name)['Parameter']['Value']
    return param


def lambda_handler(event, context):  # type: ignore
    # Notionクライアントを取得
    setting: BackupMessageNotionSetting = {
        # 親ページを親に持つデータベースのIDを取得する
        'MESSAGES_DATABASE_ID': os.environ['BACKUP_MESSAGES_DATABASE_ID'],
        'CHANNELS_DATABASE_ID': os.environ['BACKUP_CHANNELS_DATABASE_ID'],
        'USERS_DATABASE_ID': os.environ['BACKUP_USERS_DATABASE_ID'],
        'CHANNEL_KEY_NAME': 'チャンネルID',
        'USER_KEY_NAME': 'ユーザーID',
    }
    notion_client = BackupMessageNotionClient(setting)
    ts: str = f'{time.time():10.6f}'
    response = notion_client.create_message_backup(
        ts=ts,
        channel_id='TEST1',
        user_id='TEST1',
        content=f'テスト本文（{ts}）',
        slack_workspace_name='DEBUG'
    )
    print(response)
    return
