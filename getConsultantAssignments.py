import requests
import json
import pandas as pd
from datetime import datetime
import numpy as np
# from pandasgui import show
from requests.structures import CaseInsensitiveDict


def get_account_assignments_for_consultant(emp_id):
    url = "https://jigsaw.thoughtworks.net/webapi/consultant_assignments?employeeId=" + str(emp_id)
    my_cookie = ''
    headers = CaseInsensitiveDict()
    headers["authority"] = "jigsaw.thoughtworks.net"
    headers["content-type"] = "application/json"
    headers["cookie"] = my_cookie

    resp = requests.get(url, headers=headers)
    con_assignment_json = json.loads('{ "assignments": ' + resp.text + '}')
    ca_df = pd.json_normalize(con_assignment_json, record_path='assignments')
    if len(ca_df):
        ca_df['startDate'] = pd.to_datetime(ca_df['startDate'], format='%Y-%m-%d')
        ca_df['endDate'] = pd.to_datetime(ca_df['endDate'], format='%Y-%m-%d')

        ca_df.sort_values(["endDate"], ascending=[False], inplace=True)
        ca_df["accountNameX"] = ca_df["accountName"].shift()
        ca_df["cumsum"] = (ca_df["accountName"] != ca_df["accountNameX"]).cumsum()

        ca_df = ca_df.groupby((ca_df["accountName"] != ca_df["accountName"].shift()).cumsum()).\
            agg({'startDate': ['min'],
                 'endDate': ['max'],
                 'accountName': ['first']})

        ca_df.columns = ['startDate', 'endDate', 'accountName']
        return ca_df.loc[ca_df['endDate'].idxmax()]

    else:
        ca_df = pd.DataFrame(np.NaN, index=[0], columns=['accountName', 'startDate', 'endDate'])
        return ca_df.loc[0]


if __name__ == '__main__':
    input_file_name = 'data/assignments/people_search.csv'
    emp_df = pd.read_csv(input_file_name)
    emp_df.rename(columns={'Employee ID': 'emp_id'}, inplace=True)
    emp_df['emp_id'] = emp_df['emp_id'].astype("string")
    all_con_accounts = []
    for emp_id in emp_df['emp_id']:
        print(emp_id)
        emp_acc = get_account_assignments_for_consultant(emp_id)
        emp_acc['emp_id'] = str(emp_id)
        all_con_accounts.append(emp_acc)
    all_con_accounts_df = pd.DataFrame(data=all_con_accounts).reset_index(drop=True)

    all_con_accounts_df['today'] = datetime.today()
    all_con_accounts_df.loc[all_con_accounts_df['endDate'] > all_con_accounts_df['today'], 'auto_duration'] = \
        (all_con_accounts_df.today.dt.to_period('D').astype(int) -
         all_con_accounts_df.startDate.dt.to_period('D').astype(int))
    all_con_accounts_df.loc[all_con_accounts_df['endDate'] <= all_con_accounts_df['today'], 'auto_duration'] = \
        (all_con_accounts_df.endDate.dt.to_period('D').astype(int) -
         all_con_accounts_df.startDate.dt.to_period('D').astype(int))
    all_con_accounts_df.drop(columns=['today'], inplace=True)

    merged_df = emp_df.merge(all_con_accounts_df, on='emp_id')
    merged_df['auto_duration'] = merged_df['auto_duration'] / 30
    merged_df.to_csv('data/assignments/people_and_account.csv')
    # show(emp_df, all_con_accounts_df, merged_df)
