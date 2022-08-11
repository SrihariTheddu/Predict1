#    ***  Django Web Application ***  
# @Import all the required Modules Here.......
from turtle import screensize
from typing import Any, Dict
from django.shortcuts import render
from django.views.generic import TemplateView
import pandas as pd
import numpy as np
from pickle import load
import pickle
from django.urls import path
import os
from pathlib import Path
from django.core.wsgi import get_wsgi_application
from django.core.handlers.wsgi import WSGIRequest
from django.http.response import HttpResponse
# ===========================================================================================================================
# It is the basic path of the file..
BASE_DIR: path = Path(__file__).resolve().parent.parent

SECRET_KEY: str = 'django-insecure-o%8(4ywbwpd4v5yaz%r#kvn2*z07b)ur-v#zbu#!($ime$&p15'
# for production environment we set the debug value to true....
DEBUG: bool = True
ALLOWED_HOSTS: list = []
HOST: str = "http://127.0.0.1:8000"
APP_NAME: str = __name__
# Here are the installed applications which are used inside these projects.........
INSTALLED_APPS: list[str] = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles'   
]
MIDDLEWARE: list[str] = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware'
]
LANGUAGE_CODE: str = 'en-us'
TIME_ZONE: str = 'UTC'
USE_I18N: bool= True
USE_L10N: bool = True
USE_TZ: bool = True
STATIC_URL: str = '/static/'
STATIC_ROOT: str = os.getcwd() + "\static\\"

TEMPLATES: list[dict] = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [ os.getcwd() + "\Templates"],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]


# ======================================================================================================================================
"""
   Here this driver is load the data, trained models and predict the price of the given model...
"""
class Driver:
    def __init__(self, filepath):
        try:
            self.dataframe = pd.read_csv(filepath)
        except FileNotFoundError as e:
            print(e)

    def parse(self):
        self.dataAsDictFormat = {}
        for key in list(self.dataframe.columns):
            self.dataAsDictFormat[key.lower() + 's'] = set(list(self.dataframe[key]))
        return True

    def getData(self):
        return self.dataAsDictFormat

CarPricePredictionModel: Driver
LaptopPricePredictionModel: Driver


pipe: None
df: None
car: None
pipe1: None

responseAsJsonObject: Dict = {
    "carUrlPattern" : HOST + "/cars/",
    "laptopUrlPattern" :  HOST + "/laptops/",
    "predictedPrice" : "$ 1234.5678",
    "carObjectResultBlock": False,
    "laptopObjectResultBlock": False,
    "laptopObjectPricePredictionBlock": False,
    "carObjectPricePredictionBlock": False,
    "HomePageBlock": True
}

def setEnviron() -> None:
    global CarPricePredictionModel
    global LaptopPricePredictionModel
    global pipe
    global df
    global car
    global pipe1
    if DEBUG == True:
        pipe=pickle.load(open(STATIC_ROOT + 'resources/pipe.pkl','rb'))
        df=pickle.load(open(STATIC_ROOT + 'resources/df.pkl','rb'))
        car = pd.read_csv(STATIC_ROOT + 'resources/Cleaned_Car_data.csv')
        pipe1 = pickle.load(open(STATIC_ROOT + 'resources/LinearRegressionModel.pkl','rb'))
    else:
        LaptopPricePredictionModel = Driver(STATIC_ROOT + "resources\LaptopDataAsCsv.csv")
        LaptopPricePredictionModel.parse()
        CarPricePredictionModel = Driver(STATIC_ROOT + "resources\CarDataAsCsv.csv")
        CarPricePredictionModel.parse()

def setResponseObject(dict = {}, **kwargs)-> Dict:
    dict["carObjectResultBlock"] = kwargs.pop("carObjectResultBlock", False)
    dict["laptopObjectResultBlock"] = kwargs.pop("laptopObjectResultBlock", False)
    dict["laptopObjectPricePredictionBlock"] = kwargs.pop("laptopObjectPricePredictionBlock", False)
    dict["carObjectPricePredictionBlock"] = kwargs.pop("carObjectPricePredictionBlock", False)
    dict["HomePageBlock"] = kwargs.pop("HomePageBlock", False)
    return dict

    
def main(request: WSGIRequest) -> HttpResponse:
    try:
        setEnviron()
        setResponseObject(HomePageBlock=True)
        return render(request, "IndexPage.html", responseAsJsonObject | {"main_template":"HomePage.html" } )
    except ZeroDivisionError as e:
        return HttpResponse("<h1>Application Configuration Failed </h1>")

class HomePage(TemplateView):
    template_name: str = "IndexPage.html"

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        responseAsJsonObject.update(setResponseObject(HomePageBlock=True))
        return super().get_context_data(**kwargs, **responseAsJsonObject, main_template = "HomePage.html")

class LaptopPredictionPage(TemplateView):
    template_name: str = "IndexPage.html"

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        try:
            kwargs['companies' ]= set(df['Company'])
        except:
            setEnviron()
        #data = LaptopPricePredictionModel.getData()
        responseAsJsonObject.update(setResponseObject(laptopObjectPricePredictionBlock=True))
        kwargs['companies' ]= set(df['Company'])
        kwargs['typenames'] = set(df['TypeName'])
        kwargs['touchscreens'] = ['No','Yes']
        kwargs['ips'] = ['No','Yes']
        kwargs['resolutions'] = ['1920x1080','1366x768','1600x900','3840x2160','3200x1800','2880x1800','2560x1600','2560x1440','2304x1440']
        kwargs['cpus'] = set(df['Cpu brand'])
        kwargs['hdds'] = [0,128,256,512,1024,2048]
        kwargs['ssds'] = [0,8,128,256,512,1024]
        kwargs['gpus'] = set(df['Gpu Brand'])
        kwargs['oss'] = set(df['os'])
        return super().get_context_data(**kwargs, **responseAsJsonObject,  main_template = "ObjectPricePredictionPage.html")

    def post(self, request: WSGIRequest, **kwargs: Any) -> HttpResponse:
        parsedDataAsDict = {key: value for key,value in request.POST.items()}
        company = request.POST["company"]
        typename = request.POST["typename"]
        ram = int(request.POST["ram"])
        weight = float(request.POST["weight"])
        touchscreen = int(request.POST["touchscreen"])
        screensize = float(request.POST["screensize"])
        resolution = request.POST["resolution"]
        ips = int(request.POST["ips"])
        cpu = request.POST["cpu"]
        gpu = request.POST["gpu"]
        hdd = int(request.POST["hdd"])
        ssd = int(request.POST["sdd"])
        os = request.POST["os"]
        x_res = int(resolution.split('x')[0])
        y_res = int(resolution.split('x')[1])
        ppi = ((x_res**2) + (y_res**2))**0.5/screensize
        query = np.array([company,typename,ram,weight,touchscreen,ips,ppi,cpu,hdd,ssd,gpu,os])
        query = query.reshape(1,12)
        responseAsJsonObject["predictedPrice"] = str(int(np.exp(pipe.predict(query)[0]))*82.27)
        responseAsJsonObject.update(setResponseObject(laptopObjectResultBlock=True))
        return render(request, "IndexPage.html", responseAsJsonObject | parsedDataAsDict |{"main_template": "ObjectResultPage.html"})

class CarPredictionPage(TemplateView):
    template_name = "IndexPage.html"

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        try:
            kwargs['companies'] = sorted(car['company'].unique())
        except:
            setEnviron()
        responseAsJsonObject.update(setResponseObject(carObjectPricePredictionBlock=True))
        kwargs['companies'] = sorted(car['company'].unique())
        kwargs['models'] = sorted(car['name'].unique())
        kwargs['years'] = sorted(car['year'].unique(),reverse=True)
        kwargs['fuel_types'] = car['fuel_type'].unique()
        return super().get_context_data(**kwargs, **responseAsJsonObject, main_template = "ObjectPricePredictionPage.html")

    def post(self, request: WSGIRequest, **kwargs: Any) -> HttpResponse:
        parsedDataAsDict = {key: value for key,value in request.POST.items()}
        company = request.POST["company"]
        model = request.POST["model"]
        year = request.POST["year"]
        kms_driven = request.POST["kms_driven"]
        fuel_type = request.POST["fuel_type"]
        responseAsJsonObject["predictedPrice"]=pipe1.predict(pd.DataFrame(columns=['name', 'company', 'year', 'kms_driven', 'fuel_type'],
                                                         data=np.array([model,company,year,kms_driven,fuel_type]).reshape(1, 5)))
        responseAsJsonObject.update(setResponseObject(carObjectResultBlock=True))
        return render(request, "IndexPage.html", responseAsJsonObject | parsedDataAsDict | {"main_template": "ObjectResultPage.html"})

class ApplicationNotConfiguredView(TemplateView):
    template_name: str = "ApplicationNotConfiguredPage.html"

ROOT_URLCONF = __name__

urlpatterns: list[str, Any, str] = [
    path("", main, name="main"),
    path("home/", HomePage.as_view(), name="HomePageView"), 
    path("laptops/", LaptopPredictionPage.as_view(), name="PredictLaptopPriceView"),
    path("cars/", CarPredictionPage.as_view(), name="PredictCarPriceView"),
    path("error/", ApplicationNotConfiguredView.as_view(), name="AppNotConfigured")
]

os.environ.setdefault('DJANGO_SETTINGS_MODULE', __name__)
application: Any = get_wsgi_application()
WSGI_APPLICATION = f'{__name__}.application'


def run():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', __name__)
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "To run this application you need to install django... "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line([" ", "runserver"])
#=================================================================================================
if __name__ == '__main__':
    run()

