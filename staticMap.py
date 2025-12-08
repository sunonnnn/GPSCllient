import requests
from PIL import Image
from io import BytesIO
from PyQt5.QtGui import QImage, QPixmap
from urllib.parse import quote


URL = "https://maps.apigw.ntruss.com/map-static/v2/raster"


class StaticMap:
    def __init__(self):
        self.client_id = None
        self.client_key = None

        self.params = {
            "center": "127.1054328,37.3595963",
            "level": 10,
            "maptype": "basic",
            "w": 1620,
            "h": 1080
        }

        self.markers = []

    def setLogininfo(self, id, key):
        self.client_id = id
        self.client_key = key

    def setSize(self, width, height):
        self.params["w"] = width
        self.params["h"] = height

    def setCenter(self, lng, lat):
        self.params["center"] = f"{lng},{lat}"

    def setZoom(self, level):
        self.params["level"] = level

    def setMaptype(self, maptype):          # basic, traffic(교통 정보 지도), satellite(위성 지도), satellite_base(위성 배경 지도), terrain(지형도)
        self.params["maptype"] = maptype

    def getCenter(self):
        return self.params["center"]
    
    def getZoom(self):
        return self.params["level"]

    def addMarker(self, lng, lat, marker="d", size="mid", color="red", label=None):
        if label:
            mark = f"type:{marker}|size:{size}|color:{color}|label:{label}|pos:{lng} {lat}|viewSizeRatio:2.0"
        else:
            mark = f"type:{marker}|size:{size}|color:{color}|pos:{lng} {lat}|viewSizeRatio:2.0"
    
        self.markers.append(mark)
        self.params["markers"] = self.markers

    def clearMarkers(self):
        self.markers = []
        del self.params["markers"]


    def getMapImage(self):
        self.headers = {
            "X-NCP-APIGW-API-KEY-ID": self.client_id,
            "X-NCP-APIGW-API-KEY": self.client_key
        }

        res = requests.get(URL, headers=self.headers, params=self.params)
        img = Image.open(BytesIO(res.content))
        pix = self.pil2pixmap(img)
        return pix
    
    def pil2pixmap(self,im):
        im = im.convert("RGBA")
        data = im.tobytes("raw", "RGBA")
        qimage = QImage(data, im.width, im.height, QImage.Format_RGBA8888)
        return QPixmap.fromImage(qimage)