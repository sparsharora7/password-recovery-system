import mysql.connector
import re


class TreeNode:
    def __init__(self, key, user_id):
        self.key = key
        self.user_id = user_id
        self.left = None
        self.right = None


class UserDatabase:
    def __init__(self, host, user, password, database):
        self.conn = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        self.create_table()

    def create_table(self):
        cursor = self.conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS users1
                          (id INT AUTO_INCREMENT PRIMARY KEY, 
                          username VARCHAR(255) NOT NULL UNIQUE, 
                          password VARCHAR(255) NOT NULL, 
                          email VARCHAR(255))''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS old_passwords
                          (user_id INT, 
                          password VARCHAR(255),
                          FOREIGN KEY(user_id) REFERENCES users1(id))''')
        self.conn.commit()

    def insert_user(self, username, password, email):
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO users1 (username, password, email) VALUES (%s, %s, %s)", (username, password, email))
        self.conn.commit()

    def find_user_by_username(self, username):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM users1 WHERE username=%s", (username,))
        return cursor.fetchone()

    def reset_password(self, username, new_password):
        user = self.find_user_by_username(username)
        if user:
            old_password = user[2]  # Fetch current password
            cursor = self.conn.cursor()
            cursor.execute("UPDATE users1 SET password=%s WHERE username=%s", (new_password, username))
            cursor.execute("INSERT INTO old_passwords (user_id, password) VALUES (%s, %s)", (user[0], old_password))
            self.conn.commit()
            print("Password reset successful for user:", username)
            print("Old Password:", old_password)
            print("New Password:", new_password)
            return True
        else:
            print("User not found!")
            return False

    def print_tree(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM users1")
        for row in cursor.fetchall():
            print("Username:", row[1])
            print("Password:", row[2])
            cursor.execute("SELECT password FROM old_passwords WHERE user_id=%s", (row[0],))
            old_passwords = [old_password[0] for old_password in cursor.fetchall()]
            print("Old Passwords:", old_passwords)
            print("Email:", row[3])
            print()


def main():
    host = "localhost"
    user = "root"
    password = "2796"
    database = "pws"

    user_db = UserDatabase(host, user, password, database)

    # Adding users based on user input
    while True:
        username = input("Enter username (or 'quit' to exit): ")
        if username.lower() == 'quit':
            break
        password = input("Enter password: ")
        if len(password) < 8 or password.isspace():
            print("Password must be minimum 8 characters long")
        else:
            email = input("Enter email address: ")
            user_db.insert_user(username, password, email)

    # Continuous password reset process
    while True:
        username = input("Enter username for password reset (or 'quit' to exit): ")
        if username.lower() == 'quit':
            break
        new_password = input("Enter new password: ")  # Added line to get new password
        if user_db.reset_password(username, new_password):
            user_db.print_tree()  # Print the tree after password reset


if __name__ == "__main__":
    main()
