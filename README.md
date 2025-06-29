 
#  Family Store Inventory System

This is a simple inventory and order tracking system built for my small family-owned Footwear & Rice Store in India.

###  Features
- Add and update stock
- Place customer orders
- Automatically reduce stock
- Save and download order history
- Simple CSV-based data system (no database required)

###  Technology
- Python
- Streamlit
- CSV for local data persistence

###  Structure
- `inventory.csv` — initial stock
- `orders.csv` — all transactions
- `app.py` — main app logic

###  Run Locally

```bash
pip install streamlit pandas
streamlit run app.py
