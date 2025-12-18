import socket
import base64


class NtripClient:
    
    def __init__(self):
        self.host_address = None
        self.host_port = None
        self.user_id = None
        self.user_pw = None
        self.mount_point = None
        self.socket = None
        self.auth = None
    
    def set_host(self, address, port):
        self.host_address = address
        self.host_port = port
    
    def set_login_info(self, user_id, password):
        self.user_id = user_id
        self.user_pw = password
    
    def set_mountpoint(self, mountpoint):
        self.mount_point = mountpoint
        self.auth = base64.b64encode(f"{self.user_id}:{self.user_pw}".encode()).decode()
    
    def connect(self):
        self.socket = socket.socket()
        self.socket.connect((self.host_address, self.host_port))
        
        msg = f"GET /{self.mount_point} HTTP/1.1\r\n"
        msg += "User-Agent: NTRIP ntripclient\r\n"
        msg += "Authorization: Basic " + self.auth + "\r\n"
        msg += "Accept: */*\r\nConnection: close\r\n"
        msg += "\r\n"
        
        self.socket.send(msg.encode())
        
        buffer = self.socket.recv(4096)
        result = buffer.decode("utf-8")
        
        print("NTRIP Server Response:")
        print(result)
        
        if "ICY 200 OK" in result:
            print("Connected to NTRIP Server")
            return True
        else:
            print("Failed to connect to NTRIP Server")
            return False
    
    def send_nmea(self, nmea_message):
        nmea = nmea_message + "\r\n"
        self.socket.send(nmea.encode())
    
    def receive_rtcm(self):
        return self.socket.recv(8192)
    
    def close(self):
        if self.socket:
            self.socket.close()


if __name__ == "__main__":
    HOST_ADDRESS = "RTS1.ngii.go.kr"
    HOST_PORT = 2101
    USER_ID = "ohsh8080"
    USER_PW = "ngii"
    MOUNT_POINT = "RTK-RTCM32"
    NMEA_MESSAGE = "$GPGGA,123519,3735.0079,N,12701.6446,E,1,12,0.8,45.0,M,19.6,M,,*72"
    
    client = NtripClient()
    client.set_host(HOST_ADDRESS, HOST_PORT)
    client.set_login_info(USER_ID, USER_PW)
    client.set_mountpoint(MOUNT_POINT)
    
    if client.connect():
        client.send_nmea(NMEA_MESSAGE)
        rtcm_data = client.receive_rtcm()
        result = base64.b64encode(rtcm_data).decode()
        print("Received RTCM data (base64):", result)
        client.close()
