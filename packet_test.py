import socket
import threading
import time

# ----------------------------------------
# 23번 포트: 전원 상태 STX/ETX 패킷 송신
# ----------------------------------------
def power_sensor():
    server = socket.socket()
    server.bind(("127.0.0.1", 23))
    server.listen(1)

    print("[PORT 23] Waiting for connection...")
    conn, addr = server.accept()
    print("[PORT 23] Connected:", addr)

    toggle = False

    while True:
        if toggle:
            packet = b'\x02' + b'01' + b'\x03\r\n'
        else:
            packet = b'\x02' + b'00' + b'\x03\r\n'

        conn.send(packet)
        print("[23] Sent:", packet)

        toggle = not toggle
        time.sleep(1)


# ----------------------------------------
# 24번 포트: GPS NMEA GPGGA 문장 송신
# ----------------------------------------
def gps_sensor():
    server = socket.socket()
    server.bind(("127.0.0.1", 24))
    server.listen(1)

    print("[PORT 24] Waiting for connection...")
    conn, addr = server.accept()
    print("[PORT 24] Connected:", addr)

    gpgga = b"$GPGGA,114455.532,3735.0079,N,12701.6446,E,1,03,7.9,48.8,M,19.6,M,0.0,0000*48\r\n"

    while True:
        conn.send(gpgga)
        print("[24] Sent:", gpgga)
        time.sleep(1)

if __name__ == "__main__":
    t1 = threading.Thread(target=power_sensor)
    t2 = threading.Thread(target=gps_sensor)

    t1.start()
    t2.start()

    t1.join()
    t2.join()
