import csv
import argparse
from pathlib import Path
import sys
import os
import re

# My file doesn't include group permissions so this is hard coded for now
# Android considers all group permissions as dangerous:
#                                          https://developer.android.com/guide/topics/permissions/overview#perm-groups
group_permission_names = ["ACTIVITY_RECOGNITION","CALENDAR", "CALL_LOG", "CAMERA", "CONTACTS","LOCATION"
                          ,"MICROPHONE","PHONE","SENSORS", "SMS", "STORAGE"]

def parse_my_args():
    '''
    Parses program arguments
    '''
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument("methods_f", help="Must include filename of csv file of method docs")
    parser.add_argument("perms_f", help="Must include filename of csv file of Android permissions")
    args = parser.parse_args()
    # print(args.methods_f)
    # print(os.listdir())
    print(Path(args.methods_f).exists())
    print(Path(args.perms_f).exists())
    if not Path(args.methods_f).exists():
        print("First argument was not a valid filename.")
        sys.exit()

    if not Path(args.perms_f).exists():
        print("Second argument was not a valid filename.")
        sys.exit()

    return args


class Permission:
    methods_needing_perm = []

    def __init__(self, name="", protection_level="", is_group=False):
        self.name = name
        self.protection_level = protection_level
        self.is_group = is_group


class API_doc():
    def __init__(self, name='', description='', permissions = [], classes=[]):
        self.name = name
        self.description = description
        self.permissions = permissions


class API_Package(API_doc):
    def __init__(self, name='', description='', permissions = [], classes=[]):
        super().__init__(name=name, description=description, permissions=permissions)
        self.classes = classes

    def to_string(self):
        ret = self.name +"\n"
        for c in self.classes:
            ret += c.to_string()
        return ret

        
class API_Class(API_doc):
    def __init__(self, name='', description='', permissions = [], methods=[]):
        super().__init__(name=name, description=description, permissions=permissions)
        self.methods = methods

    def to_string(self):
        ret = "\t"+self.name + "\n"
        for c in self.methods:
            ret += c.to_string()

        return ret


class API_Method(API_doc):
    def __init__(self, name='', description='', permissions = []):
        super().__init__(name=name, description=description, permissions=permissions)

    def to_string(self):
        return "\t\t"+self.name+"\n"



def read_permissions(perms_f):
    '''
    Reads permissions from file csv file given by John Heaps. His file did not include group permissions though
    so those are manually encoded here :( Will update if permission extraction tool is updated to include these.

    :param perms_f: string - name of csv file
    :return: set - set of permission objects
    '''

    perm_set = set()
    with open(perms_f, newline="") as f:
        reader = csv.reader(f, dialect="excel")
        for i, row in enumerate(reader):
            # Header line
            if i == 0:
                continue
            perm = Permission()

            # Set name
            perm.name = row[0].strip()

            # Set protection level
            if re.search("dangerous", row[2].lower()):
                perm.protection_level = 'dangerous'
            elif re.search("signature", row[2].lower()):
                perm.protection_level = 'signature'
            else:
                perm.protection_level = 'normal'

            #Set group boolean
            perm.is_group = False
            perm_set.add(perm)

    for group_perm_name in group_permission_names:
        perm_set.add(Permission(group_perm_name, protection_level="dangerous", is_group=True))

    # for perm in perm_set:
    #     print("%-40s%-20s%-20s"%(perm.name, perm.protection_level, perm.is_group))
    return perm_set


def read_api_docs(methods_f):
    packages = []
    with open(methods_f, newline='', encoding='utf-8') as f:
        reader = csv.reader(f, dialect='excel')
        curr_package = curr_class = ""
        for i, row in enumerate(reader):
            # Library info
            if i ==0:
                continue

            # Package
            if len(row) > 1 and row[1] != '':
                curr_package = API_Package(name=row[1])
                if len(row) > 2:
                    curr_package.description = row[2]
                packages.append(curr_package)

            # Class
            elif  len(row) > 2 and row[2] != '':
                curr_class = API_Class(name=row[2])
                if len(row) > 3:
                    curr_class.description = row[3]
                curr_package.classes.append(curr_class)

            # Method
            elif  len(row) >3 and row[3] != '':
                method = API_Method(name=row[3])
                if len(row) > 4:
                    method.description = row[2]
                curr_class.methods.append(method)

    # for package in packages:
    #     print(package.to_string())

    return packages





def main():
    args = parse_my_args()
    perms = read_permissions(args.perms_f)
    api = read_api_docs(args.methods_f)


if __name__ == "__main__":
    main()