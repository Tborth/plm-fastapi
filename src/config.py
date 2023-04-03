import os
from dotenv import load_dotenv

class BaseConfig():
    STORAGE_ACC_NAME = os.environ.get('STORAGE_ACC_NAME')
    STORAGE_ACC_KEY = os.environ.get('STORAGE_ACC_KEY')
    STORAGE_CON_STR = os.environ.get('STORAGE_CON_STR')
    PLM_COLLECTION =  os.environ.get('PLM_COLLECTION')
class DevelopmentConfig(BaseConfig):
    """Development configuration"""
    DEBUG_TB_ENABLED = True
    APP_SETTINGS = os.environ.get('APP_SETTINGS', 'cargodbinterface.project.config.DevelopmentConfig')
    PLM_DB_USERNAME = os.environ.get('PLM_DB_USERNAME', 'user')
    PLM_DB_PASSWORD = os.environ.get('PLM_DB_PASSWORD', 'password')
    PLM_DB_DATABASE = os.environ.get('PLM_DB_DATABASE', 'cargodetails')
    PLM_DB_HOST = os.environ.get('PLM_DB_HOST', '192.168.1.115')
    PLM_DB_PORT = int(os.environ.get('PLM_DB_PORT', 27019))
    TENANT_ID = os.getenv('TENANT_ID', '')
    
    MONGODB_SETTINGS = {
        'db': PLM_DB_DATABASE,
        'host': PLM_DB_HOST,
        'port': PLM_DB_PORT,
        'username': PLM_DB_USERNAME,
        'password': PLM_DB_PASSWORD,
        "authentication_source": "admin"
    }

class CloudDevelopmentConfig(BaseConfig):
    """Development configuration"""
    DEBUG_TB_ENABLED = True
    APP_SETTINGS = os.environ.get('APP_SETTINGS', 'cargodbinterface.project.config.CloudDevelopmentConfig')
    PLM_DB_USERNAME = os.environ.get('CLOUD_DB_USERNAME', 'cge-cosmos-dev')
    PLM_DB_PASSWORD = os.environ.get('CLOUD_DB_PASSWORD', '<password>')
    PLM_DB_DATABASE = os.environ.get('CLOUD_DB_DATABASE', 'cargodetails')
    PLM_DB_HOST = os.environ.get('CLOUD_DB_HOST', 'cge-cosmos-dev.mongo.cosmos.azure.com')
    PLM_DB_PORT = int(os.environ.get('CLOUD_DB_PORT', 10255))
    TENANT_ID = os.getenv('TENANT_ID', '')
    MONGODB_SETTINGS = {
        'db': PLM_DB_DATABASE,
        'host': PLM_DB_HOST,
        'port': PLM_DB_PORT,
        'username': PLM_DB_USERNAME,
        'password': PLM_DB_PASSWORD,
        "ssl": True,
        "replicaSet": "globaldb",
        "retrywrites": False
    }