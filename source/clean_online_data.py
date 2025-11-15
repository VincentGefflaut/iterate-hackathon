import pandas as pd

def format_online_data_full(path_orders, path_order_line_items, path_inventory_products):

    orders = pd.read_csv(path_orders)
    order_line_items_df = pd.read_csv(path_order_line_items)
    inventory_products_df = pd.read_csv(path_inventory_products)

    merged_df = (
        orders[["order_id", "shipping_province", "shipping_country"]]
        .merge(order_line_items_df[["order_id", "product_id"]],
               on="order_id", how="left")
        .drop(columns=["order_id"])
    )

    merged_df_2 = (
        merged_df
        .merge(
            inventory_products_df[["inventory_id", "inventory_productType"]],
            left_on="product_id", right_on="inventory_id", how="left"
        )[["inventory_productType", "shipping_country", "shipping_province"]]
    )

    # Counts per product type
    counts = (
        merged_df_2
        .groupby(["shipping_country", "shipping_province", "inventory_productType"])
        .size()
        .reset_index(name="n_sold")
    )

    # Top-3 per location
    top3 = (
        counts
        .sort_values(["shipping_country", "shipping_province", "n_sold"],
                     ascending=[True, True, False])
        .groupby(["shipping_country", "shipping_province"])
        .head(3)
    )

    top3["rank"] = (
        top3
        .groupby(["shipping_country", "shipping_province"])["n_sold"]
        .rank(method="first", ascending=False)
        .astype(int)
    )

    # Pivot to wide format
    wide = (
        top3
        .pivot(index=["shipping_country", "shipping_province"],
               columns="rank",
               values="inventory_productType")
        .reset_index()
        .rename(columns={
            1: "top1_productType",
            2: "top2_productType",
            3: "top3_productType"
        })
    )

    # Total sold per location
    totals = (
        counts
        .groupby(["shipping_country", "shipping_province"])["n_sold"]
        .sum()
        .reset_index(name="total_n_sold")
    )

    # Merge totals + top3
    full_df = (
        totals
        .merge(wide, on=["shipping_country", "shipping_province"], how="left")
        .sort_values("total_n_sold", ascending=False)
        .reset_index(drop=True)
    )

    return full_df


def format_online_data_top20(full_df):
    return full_df.head(20)

####Example usecase:

# path_orders = r"C:\Users\titou\Desktop\paris_hack\input_data\Online\orders.csv"
# path_order_line_items= r"C:\Users\titou\Desktop\paris_hack\input_data\Online\order_line_items.csv"
# path_inventory_products = r"C:\Users\titou\Desktop\paris_hack\input_data\Online\inventory_products.csv"

# full = format_online_data_full(path_orders, path_order_line_items, path_inventory_products)
# top20 = format_online_data_top20(full)
