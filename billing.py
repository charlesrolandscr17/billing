import pandas as pd
import datetime
import re

num_to_month = {
    "01": "Janauary",
    "02": "February",
    "03": "March",
    "04": "April",
    "05": "May",
    "06": "June",
    "07": "July",
    "08": "August",
    "09": "September",
    "10": "October",
    "11": "November",
    "12": "December",
}


def check_billable_sim_ukj(data, month, year):
    # Check for activation
    if data["Status"].lower() == "active":
        data["Billing Status"] = "Billable"
    elif data["Status"].lower() == "inactive" or data["Status"].lower() == "suspended":
        if type(data["Suspension Date (UTC)"]) != pd._libs.tslibs.nattype.NaTType:
            if (
                month == pd.to_datetime(data["Suspension Date (UTC)"]).strftime("%m")
            ) and (
                year == pd.to_datetime(data["Suspension Date (UTC)"]).strftime("%Y")
            ):
                data["Billing Status"] = "Billable"
                data["Status"] = "Active"
            else:
                data["Billing Status"] = "Not Billable"
        else:
            data["Billing Status"] = "Not Billable"
    else:
        data["Billing Status"] = "Please Manually Confirm Billing"

    return data


def check_billable_sim_ono(data, month, year):
    month = num_to_month[month]
    # Check for activation
    if data["Status"].lower() == "active":
        data["Billing Status"] = "Billable"
    elif data["Status"].lower() == "inactive" or data["Status"].lower() == "suspended":
        if type(data["Suspension Date (UTC)"]) != pd._libs.tslibs.nattype.NaTType:
            if month == data["Suspension Date (UTC)"]:
                data["Billing Status"] = "Billable"
                data["Status"] = "Active"
            else:
                data["Billing Status"] = "Not Billable"
        else:
            data["Billing Status"] = "Not Billable"
    else:
        data["Billing Status"] = "Please Manually Confirm Billing"

    return data


def change_status(data, iccid, new_value, name, activation_date, customer_id):
    if data["ICCID"] == iccid:
        data["Status"] = new_value.capitalize()
        data["Data"] = name
        data["Activation Date"] = activation_date
        data["Customer ID"] = customer_id
        data["ICCID"] = f"'{iccid}"
    return data


def update_template(df_data, df_temp, customer_id, mno, month, year):
    if mno.lower() == "ukj":
        df_data = df_data.apply(
            lambda x: check_billable_sim_ukj(x, month, year), axis=1
        )
    elif mno.lower() == "onomondo":
        df_data = df_data.apply(
            lambda x: check_billable_sim_ono(x, month, year), axis=1
        )
    df_data["Subscriber ID #"] = df_data["Subscriber ID #"].apply(
        lambda data: re.sub("'", "", f"{data}")
    )
    df_temp["ICCID"] = df_temp["ICCID"].apply(lambda data: re.sub("'", "", data))
    for index, data in df_data.iterrows():
        row = {}
        if data["Billing Status"].lower() != "billable;":
            if not (df_temp[df_temp["ICCID"] == data["Subscriber ID #"]]).empty:
                df_temp = df_temp.apply(
                    lambda x: change_status(
                        x,
                        data["Subscriber ID #"],
                        data["Status"],
                        data["Name"],
                        data["Activation Date (UTC)"],
                        customer_id,
                    ),
                    axis=1,
                )
            else:
                row["ICCID"] = f'\'{data["Subscriber ID #"]}'
                row["Data"] = data["Name"]
                row["Status"] = data["Status"].capitalize()
                row["Customer ID"] = customer_id
                row["Sn"] = df_temp.iloc[-1]["Sn"] + 1
                row["Activation Date"] = data["Activation Date (UTC)"]
                row["Voice"] = "Nil"
                row["SMS"] = "Nil"
                df_temp = df_temp._append(row, ignore_index=True)
        df_temp["ICCID"] = df_temp["ICCID"].astype(str)
    return df_temp, df_data
