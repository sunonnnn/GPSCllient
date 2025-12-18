class MarkerManager:
    
    def __init__(self, static_map):
        self.static_map = static_map
    
    def update_markers(self, sensors, gps_data, power_status):
        self.static_map.clearMarkers()
        
        for ip, channel in sensors.items():
            pos = gps_data.get(ip)
            power = power_status.get(ip, False)
            
            if pos is None:
                continue
            
            color = "green" if power else "red"
            lng, lat = pos
            
            self.static_map.addMarker(
                lng=lng,
                lat=lat,
                marker="t",
                size="mid",
                color=color,
                label=channel
            )
