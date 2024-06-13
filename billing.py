import pandas as pd
import datetime
import re


def check_billable_sim(data):
    # Check for activation
    if data["Status"].lower() == "active":
        data["Billing Status"] = "Billable"
    elif data["Status"].lower() == "inactive" or data["Status"].lower() == "suspended":
        if type(data["Suspension Date (UTC)"]) != pd._libs.tslibs.nattype.NaTType:
            if (
                datetime.datetime.now().strftime("%m")
                == pd.to_datetime(data["Suspension Date (UTC)"]).strftime("%m")
            ) and (
                datetime.datetime.now().strftime("%Y")
                == pd.to_datetime(data["Suspension Date (UTC)"]).strftime("%Y")
            ):
                data["Billing Status"] = "Billable"
                data["Status"] = "active"
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
    return data


def update_template(df_data, df_temp, customer_id):
    df_data = df_data.apply(check_billable_sim, axis=1)
    df_data["Subscriber ID #"] = df_data["Subscriber ID #"].apply(
        lambda data: re.sub("'", "", data)
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
                row["ICCID"] = data["Subscriber ID #"]
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
