import streamlit as st
import pandas as pd
import datetime
import os

DATA_PATH = 'data/inventory.csv'
ORDER_PATH = 'data/orders.csv'

st.set_page_config(page_title="Store Management", layout="wide")
st.title("New Footwear & Rice Merchants, Ambedkhar Centre, Velair - Inventory Management System")

# Load inventory
if os.path.exists(DATA_PATH):
    df_inventory = pd.read_csv(DATA_PATH)
else:
    st.error("Missing inventory.csv file!")

# Load orders
if os.path.exists(ORDER_PATH):
    df_orders = pd.read_csv(ORDER_PATH)
else:
    df_orders = pd.DataFrame(columns=["Date", "Item", "Quantity", "Total"])

tab1, tab2, tab3 = st.tabs([" Inventory", " New Order", " Order History"])

with tab1:
    st.subheader(" Current Inventory")
    st.dataframe(df_inventory, use_container_width=True)

    st.subheader(" Update Stock")
    with st.form("update_stock_form"):
        item = st.selectbox("Select Item", df_inventory['Item'])
        add_qty = st.number_input("Quantity to Add", min_value=0)
        submit = st.form_submit_button("Update Stock")

        if submit and add_qty > 0:
            df_inventory.loc[df_inventory['Item'] == item, 'Stock'] += add_qty
            df_inventory.to_csv(DATA_PATH, index=False)
            st.success(f"{add_qty} units added to {item}.")

with tab2:
    st.subheader(" Place New Order")

    with st.form("order_form"):
        item = st.selectbox("Item", df_inventory['Item'])
        qty = st.number_input("Quantity", min_value=1)
        order_submit = st.form_submit_button("Submit Order")

        if order_submit:
            stock = int(df_inventory[df_inventory['Item'] == item]['Stock'])
            price = float(df_inventory[df_inventory['Item'] == item]['Price'])

            if qty > stock:
                st.error("Insufficient stock.")
            else:
                total = qty * price
                df_inventory.loc[df_inventory['Item'] == item, 'Stock'] -= qty
                df_orders = pd.concat([df_orders, pd.DataFrame([{
                    "Date": datetime.date.today(),
                    "Item": item,
                    "Quantity": qty,
                    "Total": total
                }])], ignore_index=True)

                df_inventory.to_csv(DATA_PATH, index=False)
                df_orders.to_csv(ORDER_PATH, index=False)
                st.success(f"Order placed: {item} x {qty} = ₹{total:.2f}")

with tab3:
    st.subheader(" Order History")
    st.dataframe(df_orders, use_container_width=True)

    st.download_button(" Download Order History", df_orders.to_csv(index=False), file_name="orders.csv")
