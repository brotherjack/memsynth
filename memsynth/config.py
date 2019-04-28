import os

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEST_DIR = os.path.join(ROOT_DIR, 'tests')

EXPECTED_FORMAT_MEM_LIST = {
    "columns": [
        "AK_ID",
        "DSA_ID",
        "first_name",
        "middle_name",
        "last_name",
        "suffix",
        "Family_first_name",
        "Family_last_name",
        "Organization",
        "Address_Line_1",
        "Address_Line_2",
        "City",
        "State",
        "Zip",
        "Country",
        "Mobile_Phone",
        "Home_Phone",
        "Work_Phone",
        "Email",
        "Mail_preference",
        "Do_Not_Call",
        "Join_Date",
        "Xdate",
        "Memb_status",
        "membership_type",
        "monthly_status"
    ]
}

EXPECTATIONS = {
    "AK_ID": {
        "data_type": "integer",
        "regex": "[0-9]+",
        "nullable": False
        },
    "DSA_ID": {
        "data_type": "integer",
        "regex": "[0-9]+",
        "nullable": True
    },
}