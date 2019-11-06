import datetime
from argparse import ArgumentParser
from prettytable import PrettyTable
import os
import re


def serial_date_to_string(srl_no):
    new_date = datetime.datetime.utcfromtimestamp(0) + datetime.timedelta(int(srl_no))
    return new_date.strftime("%Y-%m-%d")


def is_valid_file(parser, arg):
    if not os.path.exists(arg):
        parser.error(f"The file {arg} does not exist!")
    else:
        return open(arg, "r")


parser = ArgumentParser(description="Process HSTS databases")
parser.add_argument(
    dest="database_file",
    help="The path to the database to be processed",
    metavar="FILE",
    type=lambda x: is_valid_file(parser, x),
)
group = parser.add_mutually_exclusive_group(required=True)
group.add_argument("--firefox", action="store_true", help="Process a Firefox database")
group.add_argument("--chrome", action="store_true", help="Process a Chrome database")

args = parser.parse_args()

dirtydb = args.database_file.read()

if args.firefox:
    database = []
    dirtydb = dirtydb.split("\n")
    for i in dirtydb:
        if i != "":
            record = re.split(r"\t+", i)
            record.append(record[0][-4:])
            record[0] = re.search(r".+?(?=(\:|\^))", record[0]).group(0)
            record[2] = serial_date_to_string(record[2])
            cleaned = record[3].split(",")
            record[3] = datetime.datetime.fromtimestamp(int(cleaned[0]) / 1000)
            if int(cleaned[2]):
                record.append("Yes")
            else:
                record.append("No")
            database.append(record)
    table = PrettyTable()
    table.field_names = [
        "URL",
        "Visits",
        "Last Accessed",
        "Expiry",
        "Type",
        "Include Subdomains",
    ]
    for i in database:
        table.add_row(i)
    print(table)
