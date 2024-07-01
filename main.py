import pandas as pd
import streamlit as st
from billing import update_template

st.set_page_config(
    page_title="Billing",
    layout="wide",
    initial_sidebar_state="auto",
    menu_items=None,
)

mno = st.text_input("Provider: ")

st.write("Provider: " + mno)

col1, col2 = st.columns(2)

with col1:
    month = st.text_input("Billing Month: ")

with col2:
    year = st.text_input("Billing Year: ")


def update():
    try:
        st.session_state.summary = {}
        st.session_state.new_template, st.session_state.new_tech = update_template(
            st.session_state.df_tech,
            st.session_state.df_template,
            customer_id,
            mno,
            year=year,
            month=month,
        )

        st.session_state.df_template, st.session_state.df_tech = update_template(
            st.session_state.df_tech,
            st.session_state.df_template,
            customer_id,
            mno,
            year=year,
            month=month,
        )
        st.session_state.bill = True
    # except KeyError:
    #     st.write("*`Check if you have uploaded the files and refresh the page`*")
    except Exception as error:
        st.write(f"`{error = }`")


try:
    tech_file = st.file_uploader("Add Technical Team Excel File:")
    temp_file = st.file_uploader("Add Template Excel File:")

    tech_team_sheet_name = st.text_input(
        "Enter the tech team sheet name", placeholder="Default: Cargo"
    )
    template_sheet_name = st.text_input(
        "Enter the template sheet name", placeholder="Default: CARGO TRANS DRC"
    )

    if tech_team_sheet_name == "":
        tech_team_sheet_name = "Cargo"
    elif template_sheet_name == "":
        template_sheet_name = "CARGO TRANS DRC"

    customer_id = int(st.number_input("Customer ID", min_value=0))

    if tech_file and temp_file and tech_team_sheet_name and template_sheet_name:
        st.session_state.df_tech = pd.read_excel(
            tech_file,
            sheet_name=tech_team_sheet_name,
            dtype={
                "Subscriber ID #": str,
            },
        )
        st.session_state.df_tech["Subscriber ID #"] = st.session_state.df_tech[
            "Subscriber ID #"
        ].astype(str)
        st.session_state.df_template = pd.read_excel(
            temp_file, sheet_name=template_sheet_name
        )
    else:
        st.info("File not loaded. Add the sheet names.", icon="ℹ️")
        st.session_state.df_tech = pd.DataFrame()
        st.session_state.df_template = pd.DataFrame()

    bill = st.button("Check Billable Sim", on_click=update)

    try:
        if not st.session_state.new_tech.empty:
            st.write(
                "### Technical",
            )
            st.dataframe(
                st.session_state.new_tech,
                use_container_width=True,
                hide_index=True,
            )
    except AttributeError:
        if tech_file:
            st.write(
                "### Technical",
            )
            st.dataframe(
                st.session_state.df_tech,
                use_container_width=True,
                hide_index=True,
            )

    try:
        if not st.session_state.new_template.empty:
            st.write(
                "### Template",
            )
            st.dataframe(
                st.session_state.new_template,
                use_container_width=True,
                hide_index=True,
            )
    except AttributeError:
        if temp_file:
            st.write(
                "### Template",
            )
            st.dataframe(
                st.session_state.df_template,
                use_container_width=True,
                hide_index=True,
            )

    try:
        if not st.session_state.new_tech.empty:
            st.write(
                "### Summary",
            )
            st.dataframe(
                st.session_state.new_tech[["Name", "Billing Status"]].value_counts(),
                use_container_width=True,
            )
    except AttributeError:
        pass
except Exception as error:
    st.write(f"*There was an error: `{error = }`*")
