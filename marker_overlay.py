from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QPainter, QColor, QPen, QFont
import math

# WGS84 타원체 상수
WGS84_A = 6378137.0  # 장반경 (m)
WGS84_E2 = 0.00669437999014  # 이심률^2

def geodetic_to_ecef(lat, lon, alt=0.0):
    lat_rad = math.radians(lat)
    lon_rad = math.radians(lon)
    
    N = WGS84_A / math.sqrt(1 - WGS84_E2 * math.sin(lat_rad)**2)
    
    x = (N + alt) * math.cos(lat_rad) * math.cos(lon_rad)
    y = (N + alt) * math.cos(lat_rad) * math.sin(lon_rad)
    z = (N * (1 - WGS84_E2) + alt) * math.sin(lat_rad)
    
    return x, y, z

def ecef_to_enu(x, y, z, ref_lat, ref_lon, ref_alt=0.0):
    ref_x, ref_y, ref_z = geodetic_to_ecef(ref_lat, ref_lon, ref_alt)
    
    dx = x - ref_x
    dy = y - ref_y
    dz = z - ref_z
    
    lat_rad = math.radians(ref_lat)
    lon_rad = math.radians(ref_lon)
    
    sin_lat = math.sin(lat_rad)
    cos_lat = math.cos(lat_rad)
    sin_lon = math.sin(lon_rad)
    cos_lon = math.cos(lon_rad)
    
    e = -sin_lon * dx + cos_lon * dy
    n = -sin_lat * cos_lon * dx - sin_lat * sin_lon * dy + cos_lat * dz
    u = cos_lat * cos_lon * dx + cos_lat * sin_lon * dy + sin_lat * dz
    
    return e, n, u

def geodetic_to_enu(lat, lon, alt, ref_lat, ref_lon, ref_alt=0.0):
    x, y, z = geodetic_to_ecef(lat, lon, alt)
    return ecef_to_enu(x, y, z, ref_lat, ref_lon, ref_alt)

def cal_meters_per_pixel(lat, zoom):
    zoom += 1  # Naver Maps zoom level adjustment
    return (
        156543.03392
        * math.cos(math.radians(lat))
        / (2 ** zoom)
    )

class MarkerOverlay(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setStyleSheet("background: transparent;")
        
        self.markers = []  # [(screen_x, screen_y, color, label), ...]
        self.map_center = (127.1054328, 37.3595963)  # (lng, lat)
        self.map_zoom = 10
        self.map_size = (800, 600)
        
        self.show()
        self.raise_()
    
    def set_map_params(self, center_lng, center_lat, zoom, width, height):
        self.map_center = (center_lng, center_lat)
        self.map_zoom = zoom
        self.map_size = (width, height)
    
    def update_markers(self, sensors, gps_data, power_status):
        self.markers = []
        
        for ip, channel in sensors.items():
            pos = gps_data.get(ip)
            power = power_status.get(ip)
            
            if pos is None:
                continue
            
            lng, lat = pos
            
            screen_x, screen_y = self._gps_to_screen(lng, lat)
            
            # 화면 범위 내에 있는지 확인
            if 0 <= screen_x <= self.map_size[0] and 0 <= screen_y <= self.map_size[1]:
                if power is None:
                    color = QColor(150, 150, 150)
                elif power:
                    color = QColor(0, 200, 0)
                else:
                    color = QColor(200, 0, 0)
                
                self.markers.append((screen_x, screen_y, color, channel))
        
        if self.isVisible():
            self.update()
    
    def _gps_to_screen(self, lng, lat):
        center_lng, center_lat = self.map_center
        width, height = self.map_size
        zoom = self.map_zoom
        
        meters_per_pixel = cal_meters_per_pixel(center_lat, zoom)
        
        # e = East (동쪽, 미터), n = North (북쪽, 미터), u = Up (고도, 미터)
        e, n, u = geodetic_to_enu(lat, lng, 0.0, center_lat, center_lng, 0.0)
        
        # ENU 좌표를 화면 픽셀로 변환
        # e는 x축 (동쪽이 양수), n은 y축 (북쪽이 양수)
        screen_x = (width / 2) + (e / meters_per_pixel)
        screen_y = (height / 2) - (n / meters_per_pixel)  # 화면 y축은 아래가 양수
        
        return int(screen_x), int(screen_y)
    
    def paintEvent(self, event):
        if not self.markers:
            return
        
        painter = QPainter(self)
        try:
            painter.setRenderHint(QPainter.Antialiasing)
            
            for x, y, color, label in self.markers:
                painter.setBrush(color)
                painter.setPen(QPen(QColor(255, 255, 255), 3))
                painter.drawEllipse(x - 15, y - 15, 30, 30)
                
                self._draw_label(painter, x, y, label, color)
        finally:
            painter.end()
    
    def _draw_label(self, painter, x, y, text, color):
        painter.setBrush(QColor(255, 255, 255, 230))
        painter.setPen(QPen(color, 2))
        
        font = QFont("Arial", 10, QFont.Bold)
        painter.setFont(font)
        metrics = painter.fontMetrics()

        text_width = metrics.horizontalAdvance(text)
        text_height = metrics.height()
        
        padding = 6
        rect_x = x - text_width // 2 - padding
        rect_y = y - 30 - text_height - padding 
        rect_width = text_width + padding * 2
        rect_height = text_height + padding * 2
        
        painter.drawRoundedRect(rect_x, rect_y, rect_width, rect_height, 4, 4)
        
        painter.setPen(QColor(0, 0, 0))
        painter.drawText(rect_x + padding, rect_y + padding + metrics.ascent(), text)