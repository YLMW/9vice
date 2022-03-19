import psycopg2
from dotenv import load_dotenv
import os


class Requester:

    def __init__(self):
        env_path = os.getcwd() + "/9vice-FlaskServer/requester/.env"
        load_dotenv(dotenv_path=env_path)
        USERNAME = os.getenv("DB_USERNAME")
        PASSWORD = os.getenv("DB_PASSWORD")
        self.connection = self.db_connect(USERNAME, PASSWORD)
        self.cursor = self.connection.cursor()

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
                database="vice"
            )
            return connection
        except:
            print("[CRITICAL] Connection can not be established with database.")
            return None

    # Ferme la connexion avec la base de données
    def db_close(self):
        self.cursor.close()
        self.connection.close()

    ## =================================
    ##      USER
    ## =================================

    # Insert un nouvel utilisateur dans la base de données
    # RAJOUTER UN RETOUR
    def insert_user(self, username: str, mail: str, hash: str) -> bool:
        try:
            sql = "INSERT INTO device.users (username, mail, password) VALUES (%s, %s, %s)"
            self.cursor.execute(sql, (username, mail, hash))
            self.connection.commit()
            return True
        except:
            self.connection.commit()
            return False

    # Supprime un utilisateur dans la base de données
    # RAJOUTER UN RETOUR 
    def del_user(self, id_user: int) -> bool:
        try:
            sql = "DELETE FROM device.users WHERE id_user=%s"
            self.cursor.execute(sql, (id_user,))
            self.connection.commit()
            return True
        except:
            self.connection.commit()
            return False

    # Log in an user
    # return tuple with user's informations
    def login_user(self, login: str, type: str, hash: str) -> tuple:
        try:
            sql_name = """SELECT * FROM device.users WHERE username= %s AND password=%s"""
            sql_mail = """SELECT * FROM device.users WHERE mail= %s AND password=%s"""
            if (type == "mail"):
                self.cursor.execute(sql_mail, (login, hash))
            elif (type == "username"):
                self.cursor.execute(sql_name, (login, hash))

            return self.cursor.fetchone()
        except:
            return ()

    # Récupére la list des utilisateurs dans la base de données 
    def list_users(self) -> list:
        try:
            sql = """SELECT * FROM device.users"""
            self.cursor.execute(sql)
            return self.cursor.fetchall()
        except:
            return []

    def user_info(self, id_user: int) -> tuple:
        try:
            sql = """SELECT * FROM device.users WHERE id_user=%s"""
            self.cursor.execute(sql, (id_user,))
            ret = self.cursor.fetchone()
            return ret
        except Exception as e:
            print(e)
            return ()

    ## ================================
    ##      DEVICE
    ## ================================

    # Supprime un device dans la base de données
    def del_device(self, id: int) -> bool:
        try:
            sql = """DELETE FROM device.devices WHERE id_device = %s"""
            self.cursor.execute(sql, (id,))
            self.connection.commit()
            return True
        except:
            self.connection.commit()
            return False

    # Insert un nouveau device dans la base de données
    def insert_device(self, user_id: int, name: str, isCamera: bool, isMicro: bool, isFolder: bool,
                      pb_key: str) -> bool:

        try:
            sql = """INSERT INTO device.devices (name, id_user, camera, micro, folder, public_key) 
                    VALUES (%s, %s, %s, %s, %s, %s)"""
            self.cursor.execute(sql, (name, user_id, str(isCamera), str(isMicro), str(isFolder), pb_key))
            self.connection.commit()
            return True
        except:
            self.connection.commit()
            return False

    # Compte le nombre de devices pour un utilisateur
    def count_devices(self, id: int) -> int:
        try:
            sql = """SELECT COUNT(id_device) FROM device.devices WHERE id_user = %s """
            self.cursor.execute(sql, (id,))
            return self.cursor.fetchone()[0]
        except:
            return 0

    # Récupére la liste des devices associés à un utilisateur donnée
    def list_devices(self, id_user: int) -> list:
        try:
            sql = """SELECT devices.id_device, devices.name, devices.camera, devices.micro, devices.folder, devices.public_key
                     FROM device.devices
                     WHERE devices.id_user = %s"""
            self.cursor.execute(sql, (id_user,))
            return self.cursor.fetchall()
        except:
            return []

    # Recupere un device (ou non) en fct de lid user et id device (pour la suppression de device dans le profile)
    def is_user_device(self, user_id: int, device_id: int) -> bool:
        try:
            sql = """SELECT * FROM device.devices WHERE id_device=%s AND id_user=%s"""
            self.cursor.execute(sql, (device_id, user_id))
            ret = self.cursor.fetchone()
            if ret:
                return True
            else:
                return False
        except Exception as e:
            print("[CRITICAL] " + str(e))
            return False
    ## ================================
    ##      HISTORY
    ## ================================

    # Récupére l'historique pour un utilisateur donnée
    def get_historique(self, id: int) -> list:
        try:
            sql = """SELECT * FROM device.history WHERE id_user = %s"""
            self.cursor.execute(sql, (id,))
            return self.cursor.fetchall()
        except:
            return []

    # Récupére la dernière connexion d'un device donné d'un utilisateur
    def get_latest_con(self, login: str, name: str):
        pass
