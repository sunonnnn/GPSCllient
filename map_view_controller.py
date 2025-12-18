from PyQt5.QtWidgets import QLabel
from PyQt5.QtCore import Qt, QTimer


class MapViewController:
    
    def __init__(self, map_widget, static_map):
        self.map_widget = map_widget
        self.static_map = static_map
        self.last_pos = None
        self.is_dragging = False
        self.is_zooming = False
        self._update_callback = None
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
        self._zoom_timer.start(300)
        
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
            scale = 0.5 / (2 ** (self.static_map.getZoom() - 1))
            
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
