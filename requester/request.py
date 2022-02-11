import psycopg2
from dotenv import load_dotenv
import os

from pymysql import NULL
from sqlalchemy import true

load_dotenv()

class Requester:

    def __init__(self):
        connection = self.db_connect(os.environ.get("USERNAME"), os.environ.get("PASSWORD"))
        cursor = connection.cursor()

    ## =================================
    ##      DATABASE
    ## =================================

    # Établie la connexion avec la base de données
    def db_connect(self, USERNAME: str, PASSWORD: str):
        try:
            connection = psycopg2.connect(
                        user=USERNAME,
                        password=PASSWORD,
                        host="127.0.0.1",
                        port="5432",
                        database="9vice"
            )
            return connection
        except:
            print("[CRITICAL] Connection can not be established with database.")



    # Ferme la connexion avec la base de données
    def db_close(self):
        self.cursor.close()
        self.connection.close()

    ## =================================
    ##      USER
    ## =================================

    # Insert un nouvel utilisateur dans la base de données
    def insert_user(self, username: str, mail: str, hash: str):
        sql = "INSERT INTO device.users (username, mail, password) VALUES (%s, %s, %s)"
        self.cursor.execute(sql, (username, mail, hash))
        self.connection.commit()

    # Supprime un utilisateur dans la base de données
    def del_user(self, mail: str) -> bool:
        sql = "DELETE FROM device.users WHERE mail=%s"
        self.cursor.execute(sql, mail)
        self.connection.commit()

    # Vérifie si un utilisateur existe dans la base de données
    def user_exist(self, login: str, type: str) -> bool:
        sql_mail = "SELECT username, mail, password, isAdmin FROM device.users WHERE mail = %s"
        sql_name = "SELECT username, mail, password, isAdmin FROM device.users WHERE username = %s"
        
        if(type == "mail"):
            self.cursor.execute(sql_mail, login)
        else:
            self.cursor.execute(sql_name, login)

        return (not self.cursor.fetchall())

    # Récupére le password haché pour un utilisateur donné
    def get_password(self, username : str) -> str:
        pass

    # Log in an user
    # return tuple with user's informations
    def login_user(self, login : str,  type : str, hash : str) -> tuple:
        sql_name = """SELECT * FROM device.users WHERE username= %s AND password=%s"""
        sql_mail = """SELECT * FROM device.users WHERE mail= %s AND password=%s"""
        if(type=="mail"):
            self.cursor.execute(sql_mail, (login, hash))
        else:
            self.cursor.execute(sql_name, (login, hash))

        return self.cursor.fetchone()


    # Récupére la list des utilisateurs dans la base de données 
    def list_users(self) -> list:
        sql = """SELECT * FROM device.users"""
        self.cursor.execute(sql)
        return self.cursor.fetchall()

    ## ================================
    ##      DEVICE
    ## ================================

    # Supprime un device dans la base de données
    def del_device(self, id: int) -> bool:
        sql = """DELETE FROM device.devices WHERE id_device = %s"""
        self.cursor.execute(sql, (id,))
        self.connection.commit()
        print(self.cursor.statusmessage)
        return True


    # Insert un nouveau device dans la base de données
    def insert_device(self, name: str, isCamera: bool, isMicro: bool, isFolder: bool, pb_key: str) -> bool:
        sql = """INSERT INTO device.devices VALUES (%s, %s, %s, %s, %s)"""
        self.cursor.execute(sql, (name, isCamera, isMicro, isFolder, pb_key))
        self.connection.commit()
        print(self.cursor.statusmessage)
        return True

    # Vérifie si un device existe dans la base de données
    def device_exist(self, name) -> bool:
        pass

    # Compte le nombre de devices pour un utilisateur
    def count_devices(self, id: int) -> int:
        sql = """SELECT COUNT(id_device) FROM device.belong WHERE id_user = %s """
        self.cursor.execute(sql, (id,))
        return self.cursor.fetchone()[0]

    # Récupére la liste des devices associés à un utilisateur donnée
    def list_devices(self, id: int) -> list:
        sql = """SELECT device.devices.id_device, device.devices.isCamera, device.devices.isMicro, device.devices.isFolder, device.devices.pb_key
         FROM device.devices, device.belong 
         WHERE device.belong.id_user = %s 
         AND device.belong.id_device = device.devices.id_device"""

        self.cursor.execute(sql, (id,))
        return self.cursor.fetchall()


    ## ================================
    ##      HISTORY
    ## ================================

    # Récupére l'historique pour un utilisateur donnée
    def get_historique(self, id: int) -> list:
        sql = """SELECT * FROM device.history WHERE id_user = %s"""
        self.cursor.execute(sql, (id,))
        return self.cursor.fetchall()

    # Récupére la dernière connexion d'un device donné d'un utilisateur
    def get_latest_con(self, login: str, name: str):
        pass


