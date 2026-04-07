from models import Base
from db import ENGINE
import sys

#Make the table
def create():
    Base.metadata.create_all(ENGINE)
    
#Remove table
def drop():
    Base.metadata.drop_all(ENGINE)

#Start session code
if __name__ == "__main__":
        if len(sys.argv) > 0:
            for arg in sys.argv:
                match arg:
                    case "create":
                        create()
                    case "drop":
                        drop()
                    case "start":
                        drop()
                        create()

        else:
            # Else for the if statment checking sys.argv length
            print("Please inlude 1 or more arguments")