import requests
from PIL import Image
from io import BytesIO
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QLabel
from PyQt5.QtCore import Qt, QTimer
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
        if "markers" in self.params:
            del self.params["markers"]


    def getMapImage(self):
        self.headers = {
            "X-NCP-APIGW-API-KEY-ID": self.client_id,
            "X-NCP-APIGW-API-KEY": self.client_key
        }

        try:
            res = requests.get(URL, headers=self.headers, params=self.params, timeout=10)
            
            # 응답 상태 확인
            if res.status_code != 200:
                print(f"Map API Error: {res.status_code}")
                print(f"Response: {res.text}")
                return self._create_error_pixmap(f"API Error: {res.status_code}")
            
            # 이미지 파싱
            img = Image.open(BytesIO(res.content))
            pix = self.pil2pixmap(img)
            return pix
            
        except requests.exceptions.Timeout:
            print("Map API request timeout")
            return self._create_error_pixmap("Request Timeout")
        except requests.exceptions.RequestException as e:
            print(f"Map API request error: {e}")
            return self._create_error_pixmap(f"Request Error: {str(e)}")
        except Exception as e:
            print(f"Map image error: {e}")
            return self._create_error_pixmap(f"Error: {str(e)}")
    
    def _create_error_pixmap(self, message):
        """에러 발생 시 표시할 기본 이미지 생성"""
        width = self.params.get("w", 800)
        height = self.params.get("h", 600)
        
        img = Image.new('RGB', (width, height), color=(200, 200, 200))
        
        return self.pil2pixmap(img)
    
    def pil2pixmap(self,im):
        im = im.convert("RGBA")
        data = im.tobytes("raw", "RGBA")
        qimage = QImage(data, im.width, im.height, QImage.Format_RGBA8888)
        return QPixmap.fromImage(qimage)
    
    def update_markers(self, sensors, gps_data, power_status):
        self.clearMarkers()
        
        for ip, channel in sensors.items():
            pos = gps_data.get(ip)
            power = power_status.get(ip, False)
            
            if pos is None:
                continue
            
            color = "green" if power else "red"
            lng, lat = pos
            
            self.addMarker(
                lng=lng,
                lat=lat,
                marker="t",
                size="mid",
                color=color,
                label=channel
            )



class MapViewController:
    
    def __init__(self, map_widget, static_map, update_callback=None):
        self.map_widget = map_widget
        self.static_map = static_map
        self.last_pos = None
        self.is_dragging = False
        self.is_zooming = False
        self._update_callback = update_callback
        self._zoom_timer = QTimer()
        self._zoom_timer.setSingleShot(True)
        self._zoom_timer.timeout.connect(self._on_zoom_finished)
    
    def set_update_callback(self, callback):
        self._update_callback = callback
    
    def handle_wheel_event(self, event):
        delta = event.angleDelta().y()
        current_zoom = self.static_map.getZoom()
        
        if delta > 0:
            new_zoom = min(current_zoom + 1, 20)
        else:
            new_zoom = max(current_zoom - 1, 1)

        self.static_map.setZoom(new_zoom)
        
        self.is_zooming = True
        self._zoom_timer.start(100)
        
        self._trigger_update()
    
    def _on_zoom_finished(self):
        self.is_zooming = False
    
    def handle_mouse_press(self, event):
        if event.button() == Qt.LeftButton:
            self.last_pos = event.pos()
            self.is_dragging = True
    
    def handle_mouse_move(self, event):
        if self.last_pos is not None:
            dx = event.x() - self.last_pos.x()
            dy = event.y() - self.last_pos.y()
            
            lon, lat = map(float, self.static_map.getCenter().split(","))
            scale = 0.3 / (2 ** (self.static_map.getZoom() - 1))
            
            lon -= dx * scale
            lat += dy * scale
            
            self.static_map.setCenter(lon, lat)
            self.last_pos = event.pos()
    
    def handle_mouse_release(self, event):
        if event.button() == Qt.LeftButton:
            self.is_dragging = False
            self.last_pos = None
            self._trigger_update()
    
    def _trigger_update(self):
        if self._update_callback:
            self._update_callback()