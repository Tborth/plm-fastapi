from azure.storage.blob import BlobServiceClient, ResourceTypes, AccountSasPermissions, generate_account_sas, ContainerClient
from fileinput import filename
from fastapi import APIRouter
routes = APIRouter()
from fastapi.templating import Jinja2Templates
from fastapi import APIRouter,Form, Depends, UploadFile,File
from typing import Union,List
from main import * 
import datetime
import shutil
import os
from fastapi.responses import RedirectResponse


templates = Jinja2Templates(directory="templates")
connected={}

@routes.get("/")
async def get_route():
    return templates.TemplateResponse("home.html", { "request": {},"provision_system":get_provision_systems(),
    "register_system":get_register_systems(),"commission_system":get_commission_systems()
    })
    
@routes.get("/search/")
def get_route():
    return templates.TemplateResponse("searchbar.html", { "request": {}})
    
@routes.get("/commision/")
def get_commissions():
    get_all_commissions()
    return templates.TemplateResponse("commisions.html", { "request": {},"comission":  get_all_commissions()})
   

@routes.get("/commision/{id}")
def get_commisiion_by_id(id: str):
    get_all_commissions()
    return templates.TemplateResponse("commisions_select.html", { "request": {},
        "comission":  get_all_commissions(),
        "selected_comission":get_by_id_commissions(id),"active_id":id})

@routes.get("/systems/")
def get_system_info():
    get_all_systems()
    return templates.TemplateResponse("system.html", { "request": {},"systems": get_all_systems() })

@routes.get("/system/{id}")
def get_system_info_id(id: str):
    return templates.TemplateResponse("system_select.html", { "request": {},
        "systems": get_all_systems(),
        "selected_system":get_by_id_systems(id),"active_id":id})
    
@routes.get("/commission/system/{id}")
def get_commission_to_system(id: str):
    return templates.TemplateResponse("system_select.html", { "request": {},
        "systems": get_all_systems(),
        "selected_system":get_commision_to_systems(id),"active_id": get_commision_to_systems(id)[0].get("_id")})
    

@routes.get("/provision/{id}")
def get_prvision_info_id(id: str):
    get_last_commision_systemID()
   
    return templates.TemplateResponse("provision.html", { "request": {},
        "calibration_details":  calibrations_details(),
        "selected_system":get_by_id_systems(id),"active_id":id,
        "system_id":get_last_commision_systemID(),"today": datetime.datetime.now()})


@routes.get("/provision/edit/{id}")
def get_provision_edit_id(id: str):
    selectedsystem=get_by_serialNumber_systems(get_by_id_commissions(id)[0].get('systemInfo').get('systemSerialNumber'))
    commission_data=get_by_id_commissions(id)[0]
    zone=str(commission_data['systemInfo'].get('configuration').get('zoneSize').get('x')) + '*' +str(commission_data['systemInfo'].get('configuration').get('zoneSize').get('y'))+'*' +str(commission_data['systemInfo'].get('configuration').get('zoneSize').get('z'))
    return templates.TemplateResponse("editForm.html", { "request": {},
        "calibration_details":  calibrations_details(),
        "selected_system":selectedsystem ,"active_id":id,
        "calibObjectSelected":commission_data['systemInfo']['calibObjectSerialNumber'],
        "commission_data":commission_data,
        "system_id":commission_data['systemInfo']['systemID'],"zone":zone,"today": datetime.datetime.now()})

@routes.get("/comissioned/{id}")
def set_comission_state(id: str):
    provision_to_comission(id)
    return templates.TemplateResponse("commisions_select.html", { "request": {},
        "comission":  get_all_commissions(),
        "selected_comission":get_by_id_commissions(id),"active_id":id})

@routes.get("/generate_url/{container_name}/{file_name}")
def set_comission_state(container_name: str,file_name: str):
    token_list=generate_sas_token(container_name,file_name)
    file_url= "https://{}.blob.core.windows.net/{}/{}?{}".format(token_list[1],container_name,file_name,token_list[0])
    return RedirectResponse(file_url)

@routes.post("/searched/")
def set_comission_state(searchtext: str = Form(...), searchtype: str =Form(1)):
    data={"searchtext":searchtext,"searchtype":searchtype}
    search_commision(data)
    return templates.TemplateResponse("searchbar_value.html", { "request": {},"search_data":    search_commision(data)})

@routes.post("/provisioned/{id}")
async def add_airline_data(id:str,calibration: str = Form(""),zone: str = Form(""), customerName: str =Form(""),imageTag: str =Form(""),oiml: str =Form(""),lastcalibartiondate: str =Form(""),country: str =Form(""),\
            site: str =Form(""),installationlocation: str =Form(""),assignedpublicIP: str =Form(""),subnetmask: str =Form(""),gateway: str =Form(""),\
            routers: str =Form(""),camera1user: str =Form(8),camera1pass: str =Form(9),camera2user: str =Form(10),camera2pass: str =Form(11),\
            camera3user: str =Form(""),camera3pass: str =Form(13),camera4user: str =Form(14),camera4pass: str =Form(""),\
            customerapp_dbuser:str =Form(""),customerapp_dbpass:str =Form(""),logging_dbuser:str=Form(""),logging_dbpass:str=Form(""),
            miniouser:str =Form(""), miniopass:str =Form(""),accessinfousername:str =Form(""), accessinfopassword:str =Form(""),\
            accessinfoapi_auth_key:str =Form(""),vpnlogin:str =Form(""),vpnpassword:str=Form(""),vpnotpmethod:str=Form(""),vpnanyotherremark:str=Form(""),\
            zohodevicename:str=Form(""),zohoaccount:str=Form(""),iothubassigned:str=Form(""),iotdpsscopeid:str=Form(""),iotedgedeployment:str=Form(""),\
                changelogs:str=Form(""),remarks:str=Form(""),solutioningfiles: List[UploadFile] = File(...)):

    vpn_dict,file_urls,zoho_dict={},[],{}
    
    if solutioningfiles:
        for solutioningfile in solutioningfiles:
            file_names=[]
            if solutioningfile.filename:
                with open(f'./{solutioningfile.filename}', 'wb') as buffer:
                    shutil.copyfileobj(solutioningfile.file,buffer)
                file_names.append(solutioningfile.filename)
                file_name=get_file_upload(solutioningfile.filename)
                f_name=file_name.split("/")[-1]
                container_name=file_name.split("/")[-2]
                file_url="/generate_url/{}/{}".format(container_name,f_name)
                file_names.append(file_url)
                os.remove(solutioningfile.filename)  
        file_urls.append(file_names)

    
    
    
    system_register_provision(id)
   
    if vpnlogin and vpnpassword:
        vpn_dict["login"]=vpnlogin
        vpn_dict["password"]=vpnpassword
        vpn_dict["vpnotpmethod"]=vpnotpmethod
        vpn_dict["vpnanyotherremark"]=vpnanyotherremark

    if zohodevicename and zohoaccount:
        zoho_dict["devicename"]=zohodevicename
        zoho_dict["account"]=zohoaccount

    zone_x,zone_y,zone_z=0,0,0

    if zone:
        zone_list=zone.split('*')
        if zone_list:
            zone_x=zone_list[0]
            zone_y=zone_list[1]
            zone_z=zone_list[2]
  
    systemInfo=get_by_id_systems(id)
    provision_dict={"systemInfo": {
    "systemID": get_last_commision_systemID(),
    "commissionedDate": systemInfo[0].get("createDateTime"),
    "state": "provisioned",
    "systemSerialNumber":systemInfo[0].get("serialNumber"),
    "calibObjectSerialNumber": calibration,
    "configuration": {
      "numberOfCameras": len(systemInfo[0].get("modules")),
      "zoneSize": {
        "x": zone_x,
        "y": zone_y,
        "z": zone_z
      }
    },
        "imageTag":imageTag,
        "oiml":oiml,
        "lastcalibartiondate":lastcalibartiondate
     },
    "customerInfo": {
    "name": customerName if customerName else "",
    "country": country,
    "site": site,
    "installationLocation": installationlocation
    },
    "networkInfo": {
    "addresses": [
      assignedpublicIP
    ],
    "dhcp": "yes",
    "gateway4": gateway,
    "address": subnetmask,
    "routes": routers
    },
    "uiAccessInfo": {
    "userName": "admin@cargoeye.com",
    "password":  systemInfo[0].get("credentials").get('uiKeys')[0],
     "apiauthkey" :  systemInfo[0].get("credentials").get('api').get('apiAuthKey')
    },
    "remoteAccess": {
        "vpn":vpn_dict,
        "zoho":zoho_dict
    },
    "iotHub": {
    "assignedHub": iothubassigned,
    "scopeID": iotdpsscopeid,
    "deviceName": get_last_commision_systemID(),
    "iotedgedeployment":iotedgedeployment
    },
    "changeLogs": [
    {
      "date": datetime.datetime.now(),
      "details": [changelogs]
        }
        ],
    "remarks": remarks,
    "solutioning_url": file_urls
    }
    id_data=register_to_provision(provision_dict)
    return templates.TemplateResponse("commisions_select.html", { "request": {},
        "comission":  get_all_commissions(),
        "selected_comission":get_by_id_commissions(str(id_data)),"active_id":str(id_data)})




@routes.post("/provisioned/update/{serialNumber}/{id}")
async def update_data(serialNumber:str,id:str,calibration: str = Form(""),zone: str = Form(""), customerName: str =Form(""),imageTag: str =Form(""),oiml: str =Form(""),lastcalibartiondate: str =Form(""),country: str =Form(""),\
            site: str =Form(""),installationlocation: str =Form(""),assignedpublicIP: str =Form(""),subnetmask: str =Form(""),gateway: str =Form(""),\
            routers: str =Form(""),camera1user: str =Form(""),camera1pass: str =Form(""),camera2user: str =Form(""),camera2pass: str =Form(""),\
            camera3user: str =Form(""),camera3pass: str =Form(""),camera4user: str =Form(""),camera4pass: str =Form(""),\
            customerapp_dbuser:str =Form(""),customerapp_dbpass:str =Form(17),logging_dbuser:str=Form(18),logging_dbpass:str=Form(""),
            miniouser:str =Form(""), miniopass:str =Form(""),accessinfousername:str =Form(""), accessinfopassword:str =Form(""),\
            accessinfoapi_auth_key:str =Form(""),vpnlogin:str =Form(""),vpnpassword:str=Form(""),vpnotpmethod:str=Form(""),vpnanyotherremark:str=Form(""),\
            zohodevicename:str=Form(""),zohoaccount:str=Form(""),iothubassigned:str=Form(""),iotdpsscopeid:str=Form(""),iotedgedeployment:str=Form(""),\
                changelogs:str=Form(""),remarks:str=Form(""),urls_documents:str=Form(""),solutioningfiles: List[UploadFile] = File(...)):

    vpn_dict,file_urls,all_url={},[],[]
    if solutioningfiles:
        for solutioningfile in solutioningfiles:
            file_names=[]
            if solutioningfile.filename:
                with open(f'./{solutioningfile.filename}', 'wb') as buffer:
                    shutil.copyfileobj(solutioningfile.file,buffer)
                file_names.append(solutioningfile.filename)
                file_name=get_file_upload(solutioningfile.filename)
                f_name=file_name.split("/")[-1]
                container_name=file_name.split("/")[-2]
                file_url="/generate_url/{}/{}".format(container_name,f_name)
                file_names.append(file_url)
                os.remove(solutioningfile.filename)  
        file_urls.append(file_names)

    if urls_documents:
        if eval(urls_documents):
            all_url.extend(eval(urls_documents))

    if file_urls:
        all_url.extend(file_urls)
    all_url = [url for url in all_url if url != []]
    system_register_provision(id)

    if vpnlogin and vpnpassword:
        vpn_dict["login"]=str(vpnlogin).strip(" ")
        vpn_dict["password"]=str(vpnpassword).strip(" ")
        vpn_dict["vpnotpmethod"]=str(vpnotpmethod).strip(" ")
        vpn_dict["vpnanyotherremark"]=str(vpnanyotherremark).strip(" ")

    zoho_dict={}
    if zohodevicename and zohoaccount:
        zoho_dict["devicename"]=str(zohodevicename)
        zoho_dict["account"]=str(zohoaccount)

    zone_x,zone_y,zone_z=0,0,0

    if zone:
        zone_list=zone.split('*')
        if zone_list:
            zone_x=zone_list[0]
            zone_y=zone_list[1]
            zone_z=zone_list[2]
    
    systemInfo=get_by_serialNumber_systems(serialNumber)
    old_data=get_by_id_commissions(id)[0]
    old_changelogs=  old_data.get('changeLogs') if old_data.get('changeLogs') else []

    #<<<<<<<<<<-------------- change logs------->>>>>>>>
    Changelogs=[]
    zone_size=old_data['systemInfo']['configuration']['zoneSize']

    if zone_size['x'] !=zone_x or zone_size['y'] !=zone_y or zone_size['z'] !=zone_z:
        Changelogs.append("zone size change from {} to {}"\
            .format(zone_size['x'] +"*"+zone_size['y'] +"*"+zone_size['z'],zone_x +'*'+zone_y+'*'+ zone_z))

    if  old_data['systemInfo']['calibObjectSerialNumber'] !=  calibration:
        Changelogs.append("calibObjecct SerialNumber Change from {} to {}".format( old_data['systemInfo']['calibObjectSerialNumber'],calibration))
    
    if  old_data['systemInfo']['imageTag'] !=  imageTag:
        Changelogs.append("imageTag Change from {} to {}".format( old_data['systemInfo']['imageTag'],imageTag))
    
    if  old_data['systemInfo']['oiml'] !=  oiml:
        Changelogs.append("oiml Change from {} to {}".format( old_data['systemInfo']['oiml'],oiml))
    
    if  old_data['systemInfo']['lastcalibartiondate'] !=  lastcalibartiondate:
        Changelogs.append("last calibartion date Change from {} to {}".format( old_data['systemInfo']['lastcalibartiondate'],lastcalibartiondate))
    
    if  old_data['customerInfo']['name'] != customerName:
        Changelogs.append(" Customer name  Change from {} to {}".format(old_data['customerInfo']['name'],customerName))
    
    if  old_data['customerInfo']['country'] != country:
        Changelogs.append(" Customer country Change from {} to {}".format( old_data['customerInfo']['country'],country))
    
    if  old_data['customerInfo']['site'] != site:
        Changelogs.append(" Customer site Change from {} to {} ".format( old_data['customerInfo']['site'],site))
    
    if  old_data['customerInfo']['installationLocation'] != installationlocation:
        Changelogs.append(" Customer installationlocation Change from {} to {}".format( old_data['customerInfo']['installationLocation'],installationlocation))
    
    if  old_data['networkInfo']['addresses'] != [assignedpublicIP]:
        Changelogs.append(" networkInfo Assigned public IP Change from {} to {}".format(old_data['networkInfo']['addresses'],[assignedpublicIP]))

    if  old_data['networkInfo']['gateway4'] != gateway:
        Changelogs.append("networkInfo gateway has Change from {} to {}".format(old_data['networkInfo']['gateway4'],gateway))

    if  old_data['networkInfo']['address'] != subnetmask:
        Changelogs.append("networkInfo subnetmask has Change from {} to {}".format( old_data['networkInfo']['address'],subnetmask))

    # if  old_data['networkInfo']['address'] != subnetmask:
    #     Changelogs.append("NetworkInfo subnetmask has Change")

    if  old_data['networkInfo']['routes'] != routers:
        Changelogs.append("NetworkInfo routers has Change from {} to {}".format( old_data['networkInfo']['routes'],routers))
    
    # if  old_data['remarks'] != remarks:
    #     Changelogs.append("Remarks has Change")
    

    # raise ValueError(vpn_dict)
    vps_details=old_data['remoteAccess']['vpn']

    if  str(vps_details['login']).strip(" ") != str(vpnlogin).strip(" "):
        Changelogs.append("Remote Access VPN login has Change from {} to {}".format(str(vps_details['login']).strip(" "),str(vpnlogin).strip(" ")))

    if str(vps_details['password']).strip(" ") != str(vpnpassword).strip(" "):
        Changelogs.append("Remote Access VPN Password has Change from {} to {}".format(str(vps_details['password']).strip(" "),str(vpnpassword).strip(" ")))
            
    if str(vps_details['vpnotpmethod']).strip(" ") != str(vpnotpmethod).strip(" "):
        Changelogs.append("Remote Access VPN OTP Method has Change from {} to {}".format(str(vps_details['vpnotpmethod']).strip(" "),str(vpnotpmethod).strip(" "))) 
    
    if str(vps_details['vpnanyotherremark']).strip(" ") != str(vpnanyotherremark).strip(" "):
        Changelogs.append("Remote Access VPN login has Change from {} to {}".format(str(vps_details['vpnanyotherremark']).strip(" "),str(vpnanyotherremark).strip(" "))) 
    
        

    zoho_details =old_data['remoteAccess']['zoho']

    if  zoho_details['devicename'] != zohodevicename :
        Changelogs.append("Remote Access Zoho Device Name has Change from {} to {}".format( zoho_details['devicename'], zohodevicename))

    if  zoho_details['account'] != zohoaccount:
        Changelogs.append("Remote Access Zoho Account has Change from {} to {}".format( zoho_details['account'],  zohoaccount))


    iot_hub =old_data['iotHub']
    if  iot_hub.get('assignedHub') != iothubassigned :
        Changelogs.append("IOT Hub Assigned Hub has Change from {} to {}".format(iot_hub.get('assignedHub'),iothubassigned ))

    if iot_hub.get('scopeID') != iotdpsscopeid:
        Changelogs.append("IOT Hub Scope ID has Change from {} to {}".format(iot_hub.get('scopeID') ,iotdpsscopeid))

    if iot_hub.get('iotedgedeployment') != iotedgedeployment:
        Changelogs.append("IOT Hub Edge Deployment has Change from {} to {}".format(iot_hub.get('iotedgedeployment') ,iotedgedeployment))
                   
    if Changelogs:
        old_changelogs.append( {
                "date": datetime.datetime.now(),
                "details": Changelogs,
                "remarks":remarks
                })

    provision_dict={"systemInfo": {
    "systemID":old_data.get('systemInfo').get('systemID'),
    "commissionedDate": systemInfo[0].get("createDateTime"),
    "state": "provisioned",
    "systemSerialNumber":systemInfo[0].get("serialNumber"),
    "calibObjectSerialNumber": calibration,
    "configuration": {
      "numberOfCameras": len(systemInfo[0].get("modules")),
      "zoneSize": {
        "x": zone_x,
        "y": zone_y,
        "z": zone_z
      }
    },
    "imageTag":imageTag,
    "oiml":oiml,
    "lastcalibartiondate":lastcalibartiondate
     },
    "customerInfo": {
    "name": customerName if customerName else "",
    "country": country,
    "site": site,
    "installationLocation": installationlocation
    },
    "networkInfo": {
    "addresses": [
      assignedpublicIP
    ],
    "dhcp": "yes",
    "gateway4": gateway,
    "address": subnetmask,
    "routes": routers
    },
    "uiAccessInfo": {
    "userName": "admin@cargoeye.com",
    "password":  systemInfo[0].get("credentials").get('uiKeys')[0],
     "apiauthkey" :  systemInfo[0].get("credentials").get('api').get('apiAuthKey')
    },
    "remoteAccess": {
        "vpn":vpn_dict,
        "zoho":zoho_dict
    },
    "iotHub": {
    "assignedHub": iothubassigned,
    "scopeID": iotdpsscopeid,
    "deviceName": old_data.get('systemInfo').get('systemID'),
    "iotedgedeployment":iotedgedeployment
    },
    "changeLogs":old_changelogs,
    "solutioning_url": all_url
    }
    update=collection.update_one({"_id":ObjectId(id)},{"$set":provision_dict}, upsert = True)

    return templates.TemplateResponse("commisions_select.html", { "request": {},
        "comission":  get_all_commissions(),
        "selected_comission":get_by_id_commissions(str(id)),"active_id":str(id)})

