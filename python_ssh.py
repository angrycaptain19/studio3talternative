import paramiko
import sys
from scp import SCPClient
from zipfile import ZipFile
from getpass import getpass
import subprocess



def unzip_folder(zip_folder, destination, pwd):
        """
        Args:
            zip_folder (string): zip folder to be unzipped
            destination (string): path of destination folder
            pwd(string): zip folder password

        """
        with ZipFile(zip_folder) as zf:
            zf.extractall(destination, pwd=pwd.encode())


def progress4(filename, size, sent, peername):
    sys.stdout.write("(%s:%s) %s's progress: %.2f%%   \r" % (peername[0], peername[1], filename, float(sent)/float(size)*100) )


def install_zip():
    try:
        command = "sudo apt install zip -y"
        stdin , stdout, stderr = c.exec_command("sudo apt install zip -y")
        error_output=stderr.read()
        print(result_output)
        if error_output:
            print("Error {}".format(error_output))
    except:
        print("Zip installation failed or already installed") 


def ssh_connection():
    try:
        pemFilePath=input("Please enter server pem file absolute path : ");
        hostName=input("Please enter host/ip address : ");
        userName=input("Please enter server username : ");
        print(pemFilePath)
        k = paramiko.RSAKey.from_private_key_file(pemFilePath)
        c = paramiko.SSHClient()
        c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        print("connecting")
        c.connect(hostname = hostName, username = userName, pkey = k )

        print("connected")

        install_zip()

        mongodb_username=input("Enter mongodb username : ");
        mongodb_password=input("Enter mongodb password : ");
        mongodb_database=input("Enter mongodb database : ");
        mongodb_host=input("Enter mongodb host : ");
        mongodb_port=input("Enter mongodb port : ")

        commands = [
            "mongodump --uri=mongodb://{}:{}@{}:{}/{}".format(mongodb_username,mongodb_password,mongodb_host,mongodb_port,mongodb_database),
            "ls"
            # "sudo zip -r dump.zip dump"
        ]

        for command in commands:
            print("Executing {}".format(str(command)))
            stdin , stdout, stderr = c.exec_command(command)
            result_output = stdout.read()
            error_output=stderr.read()
            print(result_output)
            if error_output:
                print("Error {}".format(error_output))

        scp = SCPClient(c.get_transport(), progress4=progress4)
        scp.get('dump.zip')  
        print("\n")
        print("Enter your password")
        pwd = getpass()
        unzip_folder("dump.zip","dump",pwd)

        db_command="mongorestore --db {} --verbose dump/dump/{}".format(mongodb_database,mongodb_database)
        # c.exec_command(db_command)

        os.system(db_command)


        
    except Exception as e :
        print("Something goes wrong {}".format(str(e)))
    finally:
        c.close()
       


ssh_connection()
