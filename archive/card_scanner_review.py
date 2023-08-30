
#System imports
import io
import sys
import time
import logging
import RPi.GPIO as GPIO
import picamera
import picamera.array

#3rd-party imports
#evonove/mkm-sdk
from mkmsdk.mkm import Mkm
from mkmsdk.api_map import _API_MAP

#Cloud Vision API
from google.cloud import vision
from google.cloud.vision import types

#Cloud Translation API
from google.cloud import translate

#Local source imports
import settings

#Environ
#evonove/mkm-sdk
os.environ['MKM_APP_TOKEN'] = ''
os.environ['MKM_APP_SECRET'] = ''
os.environ['MKM_ACCESS_TOKEN'] = ''
os.environ['MKM_ACCESS_TOKEN_SECRET'] = ''
#Google
os.environ["GOOGLE_APPLICATION_CREDENTIALS"]= 'your path.json'

#############################	
#START FUNCTIONS
#############################

def _createlog():
    log = logging.getLogger() # 'root' Logger
	
    console = logging.StreamHandler()
    format_str = '%(asctime)s\t%(levelname)s -- %(processName)s %(filename)s:%(lineno)s -- %(message)s'
    console.setFormatter(logging.Formatter(format_str))
    log.addHandler(console) # prints to console.
    log.setLevel(logging.WARNING)

    return(log)

def _initCSrv(_name, _pin, _position):
     log.info('Start _initCSrv')
	
     GPIO.setmode(GPIO.BOARD)
     GPIO.setup(_pin,GPIO.OUT)
     _srvCSrv = GPIO.PWM(_pin, 50)
     _srvCSrv.start(_position)
	
     return (_srvCSrv)

def _init():
     log.info('Start _init')
	
     GPIO.setmode(GPIO.BOARD)
     GPIO.setup(mainProp["PIN_BBEAM"],GPIO.IN)
     _srvScan = _initCSrv("Scanner",mainProp["PIN_SRV_SCAN"], mainProp["DOWN"])
	
     return (_srvScan)

def _changeDutyCycle(_srv, _position):
     log.info('Start _changeDutyCycle')
	
     _srv.ChangeDutyCycle(_position)
	
     return ()

def _photoCards(_path):
     log.info('Start _photoCards')
	
     log.info('Picture saved @: ' + _path)
     with picamera.PiCamera() as camera:
       camera.resolution = (1024,768)
       camera.capture(_path)
	
     return ()

def _detect_text(path):
    log.info('Start _detect_text')
	
    client = vision.ImageAnnotatorClient()

    with io.open(path, 'rb') as image_file:
        content = image_file.read()
        image = types.Image(content=content)

        response = client.text_detection(image=image)
        texts = response.text_annotations
        _strText = texts[0].description

    if _strText.find("\n",0) > 0:
        _intPosName = _strText.find("\n",0)
        _strCardName = _strText[:_intPosName]
    else:
        _strCardName = "Nothing found!"

    for _name in mainProp["LST_EXP_NAME"]:
        if _strText.find(_name) > 0:
            _intPosSetNameStart = _strText.find(_name)
            _intPosSetNameEnd = _strText.find("\n",_intPosSetNameStart)
            _strCardInfo = _strText[_intPosSetNameStart:_intPosSetNameEnd]
            break
        else:
            _strCardInfo = "Nothing found!"

    translate_client = translate.Client()
    result = translate_client.translate(_strText, target_language="en")
    _strCardLang = result['detectedSourceLanguage']

    return (_strCardName, _strCardInfo, _strCardLang)

def _mkmSDK_products(_name, _game, _language, _match):
    log.info('Start _mkmSDK_products')
	
    # Using API v1.1
    mkm = Mkm(_API_MAP["1.1"]["api"], _API_MAP["1.1"]["api_root"])
    try:
        response = mkm.market_place.products(name=_name, game=_game, language=_language, match=_match)
	
    except exceptions.ConnectionError as e:
        log.error(e.response)

    return(response)

#############################	
#END FUNCTIONS
#############################

#START MAIN

if __name__ == '__main__':
    log = _createlog()
    log.info(sys.version)
    mainProp = settings.main()
    srvScan = _init()
    mainProp["RUNS"] = 0
    try:
        while mainProp["START"] != 0 and mainProp["RUNS"] < 3:
            log.warning("Run number: " + str(mainProp["RUNS"]))
            mainProp["RUNS"] += 1
            _changeDutyCycle(srvScan,mainProp["UP"])
            time.sleep(10)
            file = mainProp["PATH"] + "image" +str(mainProp["RUNS"])+".jpg"
            _photoCards(file)
            time.sleep(5)
            strCardName, strCardInfo, strCardLang = _detect_text(file)
            log.warning(strCardName +" - "+ strCardInfo + " - "+ strCardLang)
            intLNG = int(mainProp["LST_LANG"].index(strCardLang)) + 1
            time.sleep(5)
            response = _mkmSDK_products(strCardName, 2, intLNG, 0)
            json_response = response.json()
            count = 0
            for cards in json_response['product']:
                log.warning(str(json_response['product'][count]["name"]["1"]["productName"]) +" - Price Trend "+ str(json_response['product'][count]["priceGuide"]["TREND"]) + " â‚¬")
                count = count +1
            time.sleep(5)
            _changeDutyCycle(srvScan,mainProp["DOWN"])
            time.sleep(1)


    except (KeyboardInterrupt, SystemExit):
        srvScan.stop()
        GPIO.cleanup()