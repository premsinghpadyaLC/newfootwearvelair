import streamlit as st
import pandas as pd
import datetime
import os
from fpdf import FPDF
import urllib.request

FONT_PATH = 'DejaVuSans.ttf'

def download_font():
    url = 'https://github.com/dejavu-fonts/dejavu-fonts/raw/master/ttf/DejaVuSans.ttf'
    if not os.path.exists(FONT_PATH):
        st.info("Downloading font file for Unicode support...")
        try:
            urllib.request.urlretrieve(url, FONT_PATH)
            st.success("Font downloaded successfully.")
        except Exception as e:
            st.error(f"Failed to download font file: {e}")

download_font()

# CONFIGURATION
DATA_PATH = 'data/inventory.csv'
ORDER_PATH = 'data/orders.csv'
INVOICE_PATH = 'invoices/'
FONT_PATH = 'DejaVuSans.ttf'  # Update if you put the font elsewhere

# STREAMLIT SETTINGS
st.set_page_config(page_title="Store Management", layout="wide")
st.title("New Footwear & Rice Store, Ambedkhar Centre, Velair - Inventory System with Invoice Download")

# LOAD INVENTORY
if os.path.exists(DATA_PATH):
    df_inventory = pd.read_csv(DATA_PATH)
else:
    st.error("Missing inventory.csv file!")

# LOAD ORDERS
if os.path.exists(ORDER_PATH):
    df_orders = pd.read_csv(ORDER_PATH)
else:
    df_orders = pd.DataFrame(columns=["Invoice", "Date", "Customer", "Email", "Item", "Quantity", "Total"])

# Ensure invoice folder exists
os.makedirs(INVOICE_PATH, exist_ok=True)

# TABS
tab1, tab2, tab3 = st.tabs([" Inventory", " New Order", " Order History"])

# ---------------------------- TAB 1: INVENTORY ----------------------------
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

# ---------------------------- TAB 2: NEW ORDER ----------------------------
with tab2:
    st.subheader("Place New Order")

    with st.form("order_form"):
        customer = st.text_input("Customer Name")
        email = st.text_input("Customer Email")
        item = st.selectbox("Item", df_inventory['Item'])
        qty = st.number_input("Quantity", min_value=1)
        order_submit = st.form_submit_button("Submit Order")

        if order_submit:
            if not customer or not email:
                st.warning("Please enter customer name and email.")
            else:
                stock = int(df_inventory[df_inventory['Item'] == item]['Stock'])
                price = float(df_inventory[df_inventory['Item'] == item]['Price'])

                if qty > stock:
                    st.error("Insufficient stock.")
                else:
                    total = qty * price
                    invoice_num = f"INV{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
                    date = datetime.date.today()

                    # Update inventory
                    df_inventory.loc[df_inventory['Item'] == item, 'Stock'] -= qty
                    df_inventory.to_csv(DATA_PATH, index=False)

                    # Add order
                    df_orders = pd.concat([df_orders, pd.DataFrame([{
                        "Invoice": invoice_num,
                        "Date": date,
                        "Customer": customer,
                        "Email": email,
                        "Item": item,
                        "Quantity": qty,
                        "Total": total
                    }])], ignore_index=True)
                    df_orders.to_csv(ORDER_PATH, index=False)

                    # Create PDF Invoice using fpdf2 with Unicode font
                    pdf_path = os.path.join(INVOICE_PATH, f"{invoice_num}.pdf")
                    pdf = FPDF()
                    pdf.add_page()

                    # Add Unicode font (DejaVuSans)
                    pdf.add_font('DejaVu', '', FONT_PATH, uni=True)
                    pdf.set_font('DejaVu', 'B', 14)
                    pdf.set_fill_color(230, 230, 250)
                    pdf.cell(0, 10, "Footwear & Rice Store - Customer Invoice", ln=True, align='C', fill=True)
                    pdf.ln(8)

                    pdf.set_font('DejaVu', '', 12)
                    pdf.cell(0, 8, f"Invoice No: {invoice_num}", ln=True)
                    pdf.cell(0, 8, f"Date: {date}", ln=True)
                    pdf.cell(0, 8, f"Customer Name: {customer}", ln=True)
                    pdf.cell(0, 8, f"Email: {email}", ln=True)
                    pdf.ln(10)

                    pdf.set_fill_color(220, 220, 220)
                    pdf.set_font('DejaVu', 'B', 12)
                    pdf.cell(60, 10, "Item", 1, 0, 'C', 1)
                    pdf.cell(40, 10, "Quantity", 1, 0, 'C', 1)
                    pdf.cell(40, 10, "Unit Price", 1, 0, 'C', 1)
                    pdf.cell(40, 10, "Total", 1, 1, 'C', 1)

                    pdf.set_font('DejaVu', '', 12)
                    pdf.cell(60, 10, item, 1)
                    pdf.cell(40, 10, str(qty), 1)
                    pdf.cell(40, 10, f"₹{price:.2f}", 1)
                    pdf.cell(40, 10, f"₹{total:.2f}", 1)
                    pdf.output(pdf_path)

                    with open(pdf_path, "rb") as file:
                        st.download_button(label=" Download Invoice PDF", data=file, file_name=f"{invoice_num}.pdf")

                    st.success(f"Order placed and invoice generated for {customer}.")

# ---------------------------- TAB 3: ORDER HISTORY ----------------------------
with tab3:
    st.subheader(" Order History")
    st.dataframe(df_orders, use_container_width=True)
    st.download_button(" Download Order History CSV", df_orders.to_csv(index=False), file_name="orders.csv")
