import time
import threading
from zk import ZK
import base64
import mysql.connector
import pandas as pd


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

def get_attendence_list():
    conn = connect_to_device("getting attendance list")
    if not conn:
        return "connection failed"
    try :
        conn.disable_device()
        logs = conn.get_attendance()
        conn.enable_device()
        for log in logs:
            print(f"User ID: {log.user_id}, Timestamp: {log.timestamp}, Status: {log.status}")
    except Exception as e:
        print(f"Error getting attendance logs: {e}")
    finally:    
        conn.disconnect()        

    

def get_realtime_logs(conn):
    
   
    if not conn:
        return

    try:
        conn.reg_event(1)  
        mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            password="redwolf_8324",
            database="faculty",
            use_pure=True   
        )
        
        cursor = mydb.cursor()
        print("Listening for real-time logs...")

        for attendance in conn.live_capture():
            if attendance:
                print(f"New Entry -> UserID: {attendance.user_id}, Time: {attendance.timestamp}, Status: {attendance.status}")
                sql = f"INSERT INTO logs (user_id, timestamp) VALUES ('{attendance.user_id}', '{attendance.timestamp}')"
                cursor.execute(sql)
                mydb.commit()
    except KeyboardInterrupt:
        print("Stopping real-time log listener.")
    except Exception as e:
        print(f" Real-time logging error: {e}")
    finally:
        mydb.close90
        conn.disconnect()
def set_user_credentials(user_id, name, password):
    conn = connect_to_device("setting user credentials")
    
    if not conn:
        return

    try:
        uid = int(user_id[1:])
        df = pd.read_excel("Faculty.xlsx")

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
    
def get_user_credentials():
    conn = connect_to_device("getting user credentials")
    
    if not conn:
        return

    try:
        if conn:
            print("✅ Connected to Biometric Device!")

            users = conn.get_users()
    
            for user in users:
                print(f"User ID: {user.user_id}, Name: {user.name}, Card: {user.card} Privilege: {user.privilege}, Password: {user.password}")

    

    
    except Exception as e:
        print(f"Error getting user credentials: {e}")
    finally:
        conn.disconnect()


def delete_user(user_id):
    conn = connect_to_device("deleting user")
    if not conn:
        return

    try:
        uid = int(user_id[1:])
        conn.delete_user(uid=uid)
        print(f" User with ID {user_id} deleted successfully!")
    except Exception as e:
        print(f" Error deleting user: {e}")
    finally:
        conn.disconnect()
    
def delete_logs():
    conn = connect_to_device("deleting logs")
    if not conn:
        return

    try:
        conn.clear_attendance()
        print("All attendance logs deleted successfully!")
    except Exception as e:
        print(f"Error deleting logs: {e}")
    finally:
        conn.disconnect()



def migrate():
    df = pd.read_excel("Faculty.xlsx")
    filtered_df = df[df["department"] == "CSE" ]  
    dicts = filtered_df.to_dict(orient="records")
    
    try:    
            
        for record in dicts:
            user_id = record["fac_id"]
            name = record["name"]
            set_user_credentials(user_id=user_id, name=name ,password='')
            time.sleep(1)

            
    except Exception as e:
        print(f"Error during migration: {e}")
    finally:
        
        print("Migration completed successfully!")        

def main():
    conn_log = connect_to_device("real-time logs")
   
    log_thread = threading.Thread(target=get_realtime_logs, args=(conn_log,))
    log_thread.start()

    time.sleep(2)
    # print("Getting attendance list...")
    # get_attendence_list()
    # time.sleep(2)
    # print("Deleting logs...")
    # delete_logs()
    # print("Getting attendance logs...")
    
    get_attendence_list()
    # time.sleep(2)
    # set_user_credentials(user_id="I0299", name="Arya A", password="1234",)
    # time.sleep(2)
    # delete_user(user_id="I0200")
    # time.sleep(2)
    # get_user_credentials()
    # time.sleep(2)
    # migrate()
    
    
    log_thread.join()
    

if __name__ == "__main__":
    main()
