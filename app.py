import streamlit as st
import pandas as pd
import datetime
import os
from fpdf import FPDF

# -------------------- CONFIG --------------------
DATA_PATH = 'data/inventory.csv'
ORDER_PATH = 'data/orders.csv'
INVOICE_PATH = 'invoices/'
os.makedirs(INVOICE_PATH, exist_ok=True)

# -------------------- STREAMLIT SETTINGS --------------------
st.set_page_config(page_title="Store Management", layout="wide")
st.title("New Footwear & Rice Store, Ambedkhar Centre, Velair - Inventory System with Invoice Download")

# -------------------- LOAD DATA --------------------
if os.path.exists(DATA_PATH):
    df_inventory = pd.read_csv(DATA_PATH)
else:
    st.error("Missing inventory.csv file!")

if os.path.exists(ORDER_PATH):
    df_orders = pd.read_csv(ORDER_PATH)
else:
    df_orders = pd.DataFrame(columns=["Invoice", "Date", "Customer", "Email", "Item", "Quantity", "Price", "GST", "Total"])

# -------------------- TABS --------------------
tab1, tab2, tab3 = st.tabs([" Inventory", " New Order", " Order History"])

# -------------------- TAB 1: INVENTORY --------------------
with tab1:
    st.subheader("Current Inventory")
    st.dataframe(df_inventory, use_container_width=True)

    st.subheader("Update Stock")
    with st.form("update_stock_form"):
        item = st.selectbox("Select Item", df_inventory['Item'])
        add_qty = st.number_input("Quantity to Add", min_value=0)
        submit = st.form_submit_button("Update Stock")

        if submit and add_qty > 0:
            df_inventory.loc[df_inventory['Item'] == item, 'Stock'] += add_qty
            df_inventory.to_csv(DATA_PATH, index=False)
            st.success(f"{add_qty} units added to {item}.")

# -------------------- TAB 2: NEW ORDER --------------------
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
                gst = total * 0.13
                grand_total = total + gst
                invoice_num = f"INV{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
                date = datetime.date.today()

                # Update inventory
                df_inventory.loc[df_inventory['Item'] == item, 'Stock'] -= qty
                df_inventory.to_csv(DATA_PATH, index=False)

                # Save order
                new_order = pd.DataFrame([{
                    "Invoice": invoice_num,
                    "Date": date,
                    "Customer": customer,
                    "Email": email,
                    "Item": item,
                    "Quantity": qty,
                    "Price": price,
                    "GST": gst,
                    "Total": grand_total
                }])
                df_orders = pd.concat([df_orders, new_order], ignore_index=True)
                df_orders.to_csv(ORDER_PATH, index=False)

                # Generate invoice PDF
                class InvoicePDF(FPDF):
                    def header(self):
                        if os.path.exists("logo.png"):
                            self.image("logo.png", 10, 8, 33)
                        self.set_font("Arial", 'B', 14)
                        self.cell(0, 10, "New Footwear & Rice Store", ln=True, align='C')
                        self.set_font("Arial", 'I', 10)
                        self.cell(0, 10, "Ambedkhar Centre, Velair", ln=True, align='C')
                        self.ln(5)

                    def footer(self):
                        self.set_y(-35)
                        self.set_font("Arial", 'I', 9)
                        self.multi_cell(0, 5, "Note: Please verify your order. No returns after 7 days.\n"
                                              "Terms & Conditions apply. Prices include packaging.\n"
                                              "Proprietor: Padya Amarsingh\nThank you for shopping with us!", align='C')
                        if os.path.exists("logo.png"):
                            self.image("logo.png", x=90, y=self.get_y(), w=30)

                pdf_path = os.path.join(INVOICE_PATH, f"{invoice_num}.pdf")
                pdf = InvoicePDF()
                pdf.add_page()

                pdf.set_font("Arial", '', 12)
                pdf.cell(0, 8, f"Invoice No: {invoice_num}", ln=True)
                pdf.cell(0, 8, f"Date: {date}", ln=True)
                pdf.cell(0, 8, f"Customer Name: {customer}", ln=True)
                pdf.cell(0, 8, f"Email: {email}", ln=True)
                pdf.ln(10)

                pdf.set_font("Arial", 'B', 12)
                pdf.set_fill_color(220, 220, 220)
                pdf.cell(60, 10, "Item", 1, 0, 'C', 1)
                pdf.cell(25, 10, "Qty", 1, 0, 'C', 1)
                pdf.cell(35, 10, "Unit Price", 1, 0, 'C', 1)
                pdf.cell(30, 10, "GST (13%)", 1, 0, 'C', 1)
                pdf.cell(40, 10, "Total", 1, 1, 'C', 1)

                pdf.set_font("Arial", '', 12)
                pdf.cell(60, 10, item, 1)
                pdf.cell(25, 10, str(qty), 1)
                pdf.cell(35, 10, f"Rs. {price:.2f}", 1)
                pdf.cell(30, 10, f"Rs. {gst:.2f}", 1)
                pdf.cell(40, 10, f"Rs. {grand_total:.2f}", 1)
                pdf.output(pdf_path)

                # Display download button
                with open(pdf_path, "rb") as file:
                    st.download_button(
                        label=" Download Invoice PDF",
                        data=file,
                        file_name=f"{invoice_num}.pdf",
                        mime="application/pdf"
                    )

                st.success(f"Order placed and invoice generated for {customer}.")

# -------------------- TAB 3: ORDER HISTORY --------------------
with tab3:
    st.subheader("Order History")
    st.dataframe(df_orders, use_container_width=True)
    st.download_button(" Download Order History CSV", df_orders.to_csv(index=False), file_name="orders.csv")
