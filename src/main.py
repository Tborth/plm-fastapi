from azure.storage.blob import BlobServiceClient, ResourceTypes, AccountSasPermissions, generate_account_sas, ContainerClient
from datetime import datetime, timedelta
from pymongo import MongoClient,DESCENDING
import json
from bson.objectid import ObjectId
import os, uuid

from dotenv import load_dotenv

from azure.storage.blob import BlobClient, generate_blob_sas, BlobSasPermissions
load_dotenv()  # take environment variables from .env.
from config import DevelopmentConfig,CloudDevelopmentConfig


IS_CLOUD = os.environ.get("IS_CLOUD")

if IS_CLOUD == "true" or IS_CLOUD == "True" :
    config=CloudDevelopmentConfig()
    CONNECTION_STRING = f'mongodb://{config.PLM_DB_USERNAME}:{config.PLM_DB_PASSWORD}@{config.PLM_DB_HOST}:{config.PLM_DB_PORT}/?ssl=true&replicaSet=globaldb'
    client = MongoClient(CONNECTION_STRING)
    db = client[config.PLM_DB_DATABASE]
    collection = db[config.PLM_COLLECTION]
    # client = document_client.DocumentClient(CONNECTION_URI, {'masterKey': CONNECTION_KEY})
    
else:
    config=DevelopmentConfig()
    CONNECTION_STRING="mongodb://"+config.PLM_DB_USERNAME+":"+config.PLM_DB_PASSWORD+"@"+str(config.PLM_DB_HOST)+":"+str(config.PLM_DB_PORT)+"/"
    client = MongoClient(CONNECTION_STRING)
    db = client[config.PLM_DB_DATABASE]
    collection = db[config.PLM_COLLECTION]

token=generate_account_sas(
            account_name=config.STORAGE_ACC_NAME,
            account_key=config.STORAGE_ACC_KEY,
            resource_types=ResourceTypes.from_string("o"),
            permission=AccountSasPermissions.from_string("rw"),
            protocol="http,https",
            expiry=datetime.utcnow() + timedelta(minutes=60))

def generate_sas_token(AZURE_CONTAINER,file_name):
    sas = generate_blob_sas(account_name=config.STORAGE_ACC_NAME,
                        account_key=config.STORAGE_ACC_KEY,
                        container_name=AZURE_CONTAINER,
                        blob_name=file_name,
                        permission=BlobSasPermissions(read=True),
                        expiry=datetime.utcnow() + timedelta(minutes=60))
    
    return [sas,config.STORAGE_ACC_NAME]
    
def get_file_upload(file_name):
    # block_blob_service = BlockBlobService(account_name=STORAGE_ACC_NAME, account_key=AZURE_PRIMARY_KEY)    
    blob_service_client = BlobServiceClient.from_connection_string(config.STORAGE_CON_STR)
    # Create a unique name for the container
    AZURE_CONTAINER = str(uuid.uuid4())
    # sas_url = block_blob_service.generate_blob_shared_access_signature(AZURE_CONTAINER,AZURE_BLOB,BlobPermissions.READ,datetime.utcnow() + timedelta(hours=1))
    # Create the container
    container_client = blob_service_client.create_container(AZURE_CONTAINER)
    blob_client = blob_service_client.get_blob_client(container=AZURE_CONTAINER, blob=file_name)
    with open("./{}".format(file_name), "rb") as data:
        blob_client.upload_blob(data)
    blob_list = container_client.list_blobs()
   
    for blob in blob_list:
        print("\t" + blob.name)
    # file_url=blob_client.url+"?{}".format(sas)
    file_url=blob_client.url
    return file_url

def get_all_commissions():
    collection = db["commissions​"]

    docs=collection.find({},{'systemInfo':1})
    serial_numbers=[]
    commission_dict={}
    for doc in docs:
        commission_dict={}
        doc["id"]=str(doc["_id"])
        
        commission_dict['id']=str(doc["_id"])
        commission_dict['systemID']=doc["systemInfo"]["systemID"]
        commission_dict['state']=doc["systemInfo"]['state']

        serial_numbers.append(commission_dict)
    return serial_numbers

def calibrations_details():
    MONGO_COLLECTION="calibration_objects"
    client = MongoClient(CONNECTION_STRING)
    db = client[config.PLM_DB_DATABASE]
    collection = db[MONGO_COLLECTION]
    docs=collection.find({},{'serialNumber':1,'state':1})
    serial_numbers=[]
   
    for doc in docs:
        calibrations_dict={}
        if doc['state'] == "registered":
            doc["id"]=str(doc["_id"])
            
            calibrations_dict['id']=str(doc["_id"])
            calibrations_dict['serialNumber']=doc["serialNumber"]
            calibrations_dict['state']=doc['state']

            serial_numbers.append(calibrations_dict)
    return serial_numbers


def get_by_id_commissions(id):
  
    collection = db["commissions​"]
    # id="62e7a0a69f6d5aeaaf5e5dbe"
    docs=collection.find({"_id":ObjectId(id)})
    serial_numbers=[]
    for doc in docs:
        doc["_id"]=str(doc["_id"])
        serial_numbers.append(doc)
    return serial_numbers

def get_all_systems():
    MONGO_COLLECTION="systems"
    collection = db[MONGO_COLLECTION]
    docs=collection.find({},{'serialNumber':1,'state':1})
    serial_numbers=[]
    system_dict={}
    for doc in docs:
        system_dict={}
      
        if doc.get("serialNumber"):
            doc["id"]=str(doc["_id"])
            system_dict['id']=str(doc["_id"])
            system_dict['serialNumber']=doc["serialNumber"]
            system_dict['state']=doc['state']

            serial_numbers.append(system_dict)
    return serial_numbers

def get_by_id_systems(id):
    MONGO_COLLECTION="systems"
    collection = db[MONGO_COLLECTION]

    docs=collection.find({"_id":ObjectId(id)})
    serial_numbers=[]
    for doc in docs:
        doc["_id"]=str(doc["_id"])
        serial_numbers.append(doc)
    return serial_numbers

def get_by_serialNumber_systems(serialNumber):
    MONGO_COLLECTION="systems"
    collection = db[MONGO_COLLECTION]    
    docs=collection.find({"serialNumber":serialNumber})
    serial_numbers=[]
    for doc in docs:
        doc["_id"]=str(doc["_id"])
        serial_numbers.append(doc)
    return serial_numbers


def get_commision_to_systems(sn_number):
    MONGO_COLLECTION="systems"
    collection = db[MONGO_COLLECTION]
    docs=collection.find({"serialNumber":sn_number})
    serial_numbers=[]
    for doc in docs:
        doc["_id"]=str(doc["_id"])
        serial_numbers.append(doc)
    return serial_numbers

# def get_system_id_from_sn(sn_number):
#     MONGO_COLLECTION="systems"
#     collection = db[MONGO_COLLECTION]
#     # id="62e7a0a69f6d5aeaaf5e5dbe"
#     print(id)
    
#     docs=collection.find({"serialNumber":sn_number})
#     print(type(docs))
#     print(docs)
#     serial_numbers=[]



def system_register_provision(id):
    MONGO_COLLECTION="systems"
    client = MongoClient(CONNECTION_STRING)
    db = client[config.PLM_DB_DATABASE]
    collection = db[MONGO_COLLECTION]
    update=collection.update_one({"_id":ObjectId(id)},{"$set":{"state":"provisioned"}}, upsert = True)

def system_provision_commission(id):
    MONGO_COLLECTION="systems"
    client = MongoClient(CONNECTION_STRING)
    db = client[config.PLM_DB_DATABASE]
    collection = db[MONGO_COLLECTION]
    update=collection.update_one({"_id":ObjectId(id)},{"$set":{"state":"comissioned"}}, upsert = True)


def get_last_commision_systemID():
    MONGO_COLLECTION="commissions​"
    client = MongoClient(CONNECTION_STRING)
    db = client[config.PLM_DB_DATABASE]
    collection = db[MONGO_COLLECTION]
    doc_count=collection.count_documents({})
    if doc_count >= 1:
        doc = collection.find().limit(1).sort([('$natural', -1)]).next()
        last_id =doc.get('systemInfo').get('systemID')
        new_id=int(last_id.split("-")[1])+1
        if len(str(new_id)) ==1:
            new_id="ces-000"+str(new_id)
        elif len(str(new_id)) ==2:
            new_id="ces-00"+str(new_id)
        elif len(str(new_id)) >=3:
            new_id="ces-0"+str(new_id)
        return new_id
    else:
        return "ces-0001"

def register_to_provision(data):
    MONGO_COLLECTION="commissions​"
    client = MongoClient(CONNECTION_STRING)
    db = client[config.PLM_DB_DATABASE]
    collection = db[MONGO_COLLECTION]
    x = collection.insert_one(data)
    return x.inserted_id
    
def edit_provision(data):
    MONGO_COLLECTION="commissions​"
    client = MongoClient(CONNECTION_STRING)
    db = client[config.PLM_DB_DATABASE]
    collection = db[MONGO_COLLECTION]
    x = collection.insert_one(data)
    return x.inserted_id

def provision_to_comission(id):
    MONGO_COLLECTION="commissions​"
    client = MongoClient(CONNECTION_STRING)
    db = client[config.PLM_DB_DATABASE]
    collection = db[MONGO_COLLECTION]
    docs=collection.find({"_id":ObjectId(id)})
    for doc in docs:
        sn_number=doc.get('systemInfo').get("systemSerialNumber")
        system_id=get_commision_to_systems(sn_number)[0].get('_id')
        system_provision_commission(system_id)
    update=collection.update_one({"_id":ObjectId(id)},{"$set":{"systemInfo.state":"commissioned"}}, upsert = True)

def search_commision(data):
    MONGO_COLLECTION="commissions​"
    client = MongoClient(CONNECTION_STRING)
    db = client[config.PLM_DB_DATABASE]
    collection = db[MONGO_COLLECTION]
    cursor=collection.find({str(data.get("searchtype").strip(" ")):{'$regex' : str(data.get("searchtext").strip(" ")), '$options' : 'i'}})
    list_doc=[]
    for doc in cursor:
        doc["_id"]=str(doc["_id"])
        list_doc.append(doc)
    return list_doc



def get_provision_systems():
    MONGO_COLLECTION="systems"
    collection = db[MONGO_COLLECTION]
    docs=collection.find({"state":"provisioned"})
    module_count_3=0
    module_count_4=0
    for doc in docs:
        if doc.get('modules'):
            if len(doc['modules'])==3: 
                module_count_3 +=1
            elif len(doc['modules'])==4:
                module_count_4 +=1 
        
    return {"ces3":module_count_3,"ces4":module_count_4}

def get_commission_systems():
    MONGO_COLLECTION="systems"
    collection = db[MONGO_COLLECTION]
    docs=collection.find({"state":"comissioned"})
    serial_numbers=[]
    module_count_3=0
    module_count_4=0
    count=0
    for doc in docs:
        count=count+1
        if doc.get('modules'):
                if len(doc['modules'])==3: 
                    module_count_3 +=1
                elif len(doc['modules'])==4:
                    module_count_4 +=1         
    return {"ces3":module_count_3,"ces4":module_count_4}

def get_register_systems():
    MONGO_COLLECTION="systems"
    collection = db[MONGO_COLLECTION]
    docs=collection.find({"state":"registered"})
    count=0
    module_count_3=0
    module_count_4=0
    for doc in docs:
        count=count+1
        if doc.get('modules'):
                if len(doc['modules'])==3: 
                    module_count_3 +=1
                elif len(doc['modules'])==4:
                    module_count_4 +=1 
        
    return {"ces3":module_count_3,"ces4":module_count_4}
