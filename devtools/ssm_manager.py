import logging
import boto3
from boto3.session import Session
import notion_client
from colorama import Fore, Back, Style

LOGGING_APP_NAME = 'Devtools'


class SSMManager():
    prod_ssm_client: boto3.client
    local_ssm_client: boto3.client
    notion_client: notion_client.Client

    def __init__(self, prod_profile: str, local_profile: str, local_endpoint: str) -> None:
        # 本番環境クライアント
        prod_session = Session(profile_name='prod')
        self.prod_ssm_client = prod_session.client('ssm')
        # ローカル環境クライアント
        local_session = Session(profile_name='local')
        self.local_ssm_client = local_session.client('ssm', endpoint_url='http://localstack:4566')
        # Notionクライアント
        response = self.prod_ssm_client.get_parameter(Name='/Eggmuri/Prod/Notion/Rotom_API_KEY')
        api_key = response['Parameter']['Value']
        self.notion_client = notion_client.Client(auth=api_key)

    def copy_parameters(self, mode: str, path: str) -> None:
        logger: logging.Logger = logging.getLogger(LOGGING_APP_NAME)
        logger.info(f'SSMパラメータストアからパラメータを取得します。')
        logger.info(f'{path=}')
        response = self.prod_ssm_client.get_parameters_by_path(
            Path=path,
            Recursive=True,
            MaxResults=10
        )
        params_count = len(response.get("Parameters"))
        logger.info(f'{params_count}件取得しました。')
        if params_count >= 10:
            logger.warn(f'10件に達しているのでpagenatorで取得しないと取りこぼしているかも。')
        if mode == 'prod_to_prod':
            logger.info('本番環境のパラメータのコピーをローカル環境の参照用にコピーします。')
            client = self.prod_ssm_client
        elif mode == 'prod_to_local':
            logger.info('本番環境のパラメータをローカル環境（LocalStack）に登録します。')
            client = self.local_ssm_client
        for i, p in enumerate(response['Parameters'], start=1):
            logger.info(f'{Style.DIM}{i}/{params_count} {p.get("Name")}{Style.RESET_ALL}')
            name = p.get('Name').replace('Prod', 'Local')
            client.put_parameter(
                Name=name,
                Value=p.get('Value'),
                Type=p.get('Type'),
                Overwrite=True,
                Tier='Standard',
                DataType=p.get('DataType')
            )

    def get_child_database_id_and_set_prod(self, path: str) -> None:
        """NotionデータベースのIDを取得する

        Args:
            path (str): データベース名を記録しているSSMパラメータパス

        Returns:
            str: データベースID
        """
        parent_page_id_path = '/Eggmuri/Prod/Notion/BackupParentPageID'
        parent_page_id: str = self.prod_ssm_client.get_parameter(Name=parent_page_id_path)['Parameter']['Value']
        database_name: str = self.prod_ssm_client.get_parameter(Name=path)['Parameter']['Value']
        search_result = self.notion_client.search(  # type: ignore
            query=database_name,
            filter={'property': 'object', 'value': 'database'}
        )['results']
        children = [i for i in search_result if i['parent']['page_id'] == parent_page_id]  # type: ignore
        database_id = str(children[-1]['id'])
        database_id_path = f'{path.rstrip("Name")}ID'
        self.prod_ssm_client.put_parameter(
            Name=database_id_path, Value=database_id,
            Type='String', Overwrite=True, Tier='Standard', DataType='text'
        )

    def setup_notion_param_prod(self) -> None:
        logger: logging.Logger = logging.getLogger(LOGGING_APP_NAME)
        logger.info(f'バックアップの親ページ名からIDを取得し、SSMに登録します。')
        parent_page_name_path = '/Eggmuri/Prod/Notion/BackupParentPageName'
        parent_page_name: str = self.prod_ssm_client.get_parameter(Name=parent_page_name_path)['Parameter']['Value']
        parent_page_id: str = self.notion_client.search(query=parent_page_name)['results'][0]['id']  # type: ignore
        self.prod_ssm_client.put_parameter(
            Name=f'/Eggmuri/Prod/Notion/BackupParentPageID', Value=parent_page_id,
            Type='String', Overwrite=True, Tier='Standard', DataType='text'
        )
        logger.info(f'DB名からIDを取得し、SSMに登録します。')
        database_name_paths = [
            '/Eggmuri/Prod/Notion/BackupMessagesDatabaseName',
            '/Eggmuri/Prod/Notion/BackupChannelsDatabaseName',
            '/Eggmuri/Prod/Notion/BackupUsersDatabaseName',
        ]
        for i, path in enumerate(database_name_paths, start=1):
            logger.info(f'{Style.DIM}{i}/{len(database_name_paths)} {path=}{Style.RESET_ALL}')
            self.get_child_database_id_and_set_prod(path)
