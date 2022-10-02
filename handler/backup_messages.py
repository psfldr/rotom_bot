import os
from slack_bolt import App
from slack_bolt.adapter.aws_lambda import SlackRequestHandler
import time
from unittest.mock import patch
import boto3

# FaaS で実行するときは process_before_response を True にする必要があります
app = App(process_before_response=True)


def respond_to_slack_within_3_seconds(body, ack):
    text = body.get("text")
    if text is None or len(text) == 0:
        ack(":x: Usage: /start-process (description here)")
    else:
        ack(f"Accepted! (task: {body['text']})")


import time


def run_long_process(respond, body):
    time.sleep(5)  # 3 秒より長い時間を指定します
    respond(f"Completed! (task: {body['text']})")


app.command("/start-process")(
    ack=respond_to_slack_within_3_seconds,  # `ack()` の呼び出しを担当します
    lazy=[run_long_process],  # `ack()` の呼び出しはできません。複数の関数を持たせることができます。
)


boto3_client_alias = boto3.client


def patched_boto3_client(*args, **kwargs):  # type: ignore
    """LocalStack上での実行時のみエンドポイントを設定するboto3.client関数"""
    # https://docs.localstack.cloud/integrations/sdks/python/
    LOCALSTACK_HOSTNAME = os.environ.get("LOCALSTACK_HOSTNAME")
    EDGE_PORT = os.environ.get("EDGE_PORT")
    if "endpoint_url" not in kwargs and LOCALSTACK_HOSTNAME:
        kwargs["endpoint_url"] = f"http://{LOCALSTACK_HOSTNAME}:{EDGE_PORT}"
    return boto3_client_alias(*args, **kwargs)


@patch("boto3.client", patched_boto3_client)
def handler(event, context):
    slack_handler = SlackRequestHandler(app=app)
    return slack_handler.handle(event, context)


# def lambda_handler(event, context):  # type: ignore
#     # Notionクライアントを取得
#     setting: BackupMessageNotionSetting = {
#         # 親ページを親に持つデータベースのIDを取得する
#         'MESSAGES_DATABASE_ID': os.environ['BACKUP_MESSAGES_DATABASE_ID'],
#         'CHANNELS_DATABASE_ID': os.environ['BACKUP_CHANNELS_DATABASE_ID'],
#         'USERS_DATABASE_ID': os.environ['BACKUP_USERS_DATABASE_ID'],
#         'CHANNEL_KEY_NAME': 'チャンネルID',
#         'USER_KEY_NAME': 'ユーザーID',
#     }
#     notion_client = BackupMessageNotionClient(setting)
#     ts: str = f'{time.time():10.6f}'
#     response = notion_client.create_message_backup(
#         ts=ts,
#         channel_id='TEST1',
#         user_id='TEST1',
#         content=f'テスト本文（{ts}）',
#         slack_workspace_name='DEBUG'
#     )
#     print(response)
#     return
