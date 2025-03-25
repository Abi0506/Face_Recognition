import time
import threading
from zk import ZK
import base64

DEVICE_IP = "192.168.1.100"
PORT = 4370

def connect_to_device(reason):
    
    zk = ZK(DEVICE_IP, port=PORT, timeout=5, password=0, force_udp=False, ommit_ping=False)
    try:
        conn = zk.connect()
        print("Connected to device successfully for reason: ", reason)
        return conn
    except Exception as e:
        print(f"Connection failed: {e}")
        return None

def get_realtime_logs(conn):
    
   
    if not conn:
        return

    try:
        conn.reg_event(1)  
        print("Listening for real-time logs...")

        for attendance in conn.live_capture():
            if attendance:
                print(f"New Entry -> UserID: {attendance.user_id}, Time: {attendance.timestamp}, Status: {attendance.status}")
    except KeyboardInterrupt:
        print("Stopping real-time log listener.")
    except Exception as e:
        print(f" Real-time logging error: {e}")
    finally:
        conn.disconnect()

def set_user_credentials(user_id, name, password):
    conn = connect_to_device("setting user credentials")
    
    if not conn:
        return

    try:
        uid = int(user_id) % 65535  

        conn.set_user(
            uid=uid,                   
            user_id=str(user_id),       
            name=name,
            privilege=0,
            password=password
        )
        print(f"User '{name}' (User ID: {user_id}, Internal UID: {uid}) added successfully!")
    except Exception as e:
        print(f"Error setting user credentials: {e}")
    finally:
        conn.disconnect()
    



def delete_user(user_id):
    conn = connect_to_device("deleting user")
    if not conn:
        return

    try:
        uid = int(user_id) % 65535
        if uid > 32767:
            uid -= 65536  
        conn.delete_user(uid=uid)
        print(f" User with ID {user_id} deleted successfully!")
    except Exception as e:
        print(f" Error deleting user: {e}")
    finally:
        conn.disconnect()
    

def image_to_base64(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode("utf-8")

def upload_user_photo(user_id, image):
    conn = connect_to_device("uploading user photo")
    if not conn:
        return

    try:
        uid = int(user_id) % 65535
        if uid > 32767:
            uid -= 65536  
        conn.set_user_photo(uid=uid, fid=50,template=image)
        print(f"Photo uploaded successfully for user ID {user_id}")
    except Exception as e:
        print(f"Error uploading user photo: {e}")
    finally:
        conn.disconnect()

def main():
    conn_log = connect_to_device("real-time logs")
   
    log_thread = threading.Thread(target=get_realtime_logs, args=(conn_log,))
    log_thread.start()

    
    # time.sleep(2)
    # set_user_credentials(user_id=715524104021, name="Arya A", password="")
    # time.sleep(2)
    # delete_user(user_id=715524104021)

    # image = image_to_base64("face_image.png.jpg")
    # upload_user_photo(user_id=715524104021, image=image)
    
    log_thread.join()
    

if __name__ == "__main__":
    main()
