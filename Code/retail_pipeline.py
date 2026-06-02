import pandas as pd

# -------------------------
# LOAD DATA
# -------------------------

file_path = "Data/USECASE - Data Engineering (2).xlsx"

product_df = pd.read_excel(
    file_path,
    sheet_name="product_details"
)

retail1_df = pd.read_excel(
    file_path,
    sheet_name="retail_data1"
)

retail2_df = pd.read_excel(
    file_path,
    sheet_name="retail_data2"
)

# -------------------------
# COMBINE DATASETS
# -------------------------

retail_df = pd.concat(
    [retail1_df, retail2_df],
    ignore_index=True
)

print("Original Records:", len(retail_df))

# -------------------------
# REMOVE FAILED TRANSACTIONS
# -------------------------

retail_df = retail_df[
    retail_df["payment_status"] == "successful"
]

# -------------------------
# REMOVE INVALID QUANTITIES
# -------------------------

retail_df = retail_df[
    retail_df["quantity"] > 0
]

# -------------------------
# STANDARDIZE CATEGORIES
# -------------------------

category_map = {
    "ELEC": "Electronics",
    "electronics": "Electronics",

    "CLOTH": "Clothing",
    "clothing": "Clothing",

    "FURN": "Furniture",
    "furniture": "Furniture",

    "HOME": "Home Appliances",
    "home appliances": "Home Appliances"
}

retail_df["category"] = retail_df["category"].replace(category_map)

# -------------------------
# STANDARDIZE PRODUCT NAMES
# -------------------------

retail_df["product_name"] = (
    retail_df["product_name"]
    .str.strip()
    .str.title()
)

# -------------------------
# FIX MISSING PRICES
# -------------------------

price_lookup = dict(
    zip(
        product_df["product_id"],
        product_df["price"]
    )
)

retail_df["price"] = retail_df.apply(
    lambda row:
    price_lookup[row["product_id"]]
    if pd.isnull(row["price"])
    else row["price"],
    axis=1
)

# -------------------------
# STANDARDIZE DATE
# -------------------------

retail_df["transaction_date"] = pd.to_datetime(
    retail_df["transaction_date"],
    errors="coerce"
)

# -------------------------
# PII MASKING
# -------------------------

def mask_email(email):
    if pd.isnull(email):
        return email

    username, domain = str(email).split("@")
    return username[0] + "*****@" + domain


def mask_phone(phone):
    phone = str(phone)
    return "******" + phone[-4:]


def mask_name(name):
    parts = str(name).split()

    masked = []

    for p in parts:
        masked.append(p[0] + "*" * (len(p) - 1))

    return " ".join(masked)


retail_df["email"] = retail_df["email"].apply(mask_email)

retail_df["phone"] = retail_df["phone"].apply(mask_phone)

retail_df["customer_name"] = retail_df["customer_name"].apply(mask_name)

# -------------------------
# REVENUE CALCULATION
# -------------------------

retail_df["Revenue"] = (
    retail_df["price"]
    * retail_df["quantity"]
    * (1 - retail_df["discount"])
)

# -------------------------
# KPI CALCULATIONS
# -------------------------

total_revenue = retail_df["Revenue"].sum()

total_orders = retail_df["transaction_id"].nunique()

total_customers = retail_df["customer_id"].nunique()

average_order_value = total_revenue / total_orders

print("\n===== KPI REPORT =====\n")

print(f"Total Revenue : {total_revenue:,.2f}")
print(f"Total Orders : {total_orders}")
print(f"Total Customers : {total_customers}")
print(f"Average Order Value : {average_order_value:,.2f}")


# -------------------------
# MONTH COLUMN
# -------------------------

retail_df["Month"] = (
    retail_df["transaction_date"]
    .dt.strftime("%Y-%m")
)

# -------------------------
# MONTHLY REVENUE
# -------------------------

monthly_revenue = (
    retail_df
    .groupby("Month")["Revenue"]
    .sum()
    .reset_index()
)

print("\nMonthly Revenue\n")
print(monthly_revenue)

# -------------------------
# REVENUE BY CATEGORY
# -------------------------

revenue_by_category = (
    retail_df
    .groupby("category")["Revenue"]
    .sum()
    .reset_index()
)

print("\nRevenue By Category\n")
print(revenue_by_category)

# -------------------------
# REVENUE BY CITY
# -------------------------

revenue_by_city = (
    retail_df
    .groupby("city")["Revenue"]
    .sum()
    .reset_index()
)

print("\nTop Cities By Revenue\n")

print(
    revenue_by_city
    .sort_values(
        by="Revenue",
        ascending=False
    )
)

# -------------------------
# TOP PRODUCTS
# -------------------------

top_products = (
    retail_df
    .groupby("product_name")["Revenue"]
    .sum()
    .reset_index()
)

print("\nTop Products\n")

print(
    top_products
    .sort_values(
        by="Revenue",
        ascending=False
    )
)

# -------------------------
# EXPORT FILES
# -------------------------

retail_df.to_csv(
    "Output/cleaned_retail_data.csv",
    index=False
)

revenue_by_category.to_csv(
    "Output/revenue_by_category.csv",
    index=False
)

revenue_by_city.to_csv(
    "Output/revenue_by_city.csv",
    index=False
)

top_products.to_csv(
    "Output/top_products.csv",
    index=False
)

monthly_revenue.to_csv(
    "Output/monthly_revenue.csv",
    index=False
)

print("\n================================")
print("FILES EXPORTED SUCCESSFULLY")
print("================================")

print("\nGenerated Files:")

print("1. cleaned_retail_data.csv")
print("2. revenue_by_category.csv")
print("3. revenue_by_city.csv")
print("4. top_products.csv")
print("5. monthly_revenue.csv")