"""
Deep Data Analysis for Source Hackathon
Comprehensive exploration of retail + online data
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

print("="*80)
print("DEEP DATA ANALYSIS - SOURCE HACKATHON")
print("="*80)

# ============================================================================
# 1. LOAD RETAIL SALES DATA
# ============================================================================
print("\n" + "="*80)
print("1. LOADING RETAIL SALES DATA")
print("="*80)

retail_sales = pd.read_csv('data/input/Retail/retail_sales_data_01_09_2023_to_31_10_2025.csv',
                           encoding='utf-8-sig',
                           low_memory=False)

print(f"✓ Loaded {len(retail_sales):,} transaction lines")
print(f"✓ Date range: {retail_sales['Sale Date'].min()} to {retail_sales['Sale Date'].max()}")
print(f"✓ Columns: {retail_sales.shape[1]}")

# Parse dates with mixed format
retail_sales['Sale Date'] = pd.to_datetime(retail_sales['Sale Date'], format='mixed', dayfirst=True)

print(f"\nBasic Stats:")
print(f"  - Unique Products: {retail_sales['Product'].nunique():,}")
print(f"  - Unique Branches: {retail_sales['Branch Name'].nunique()}")
print(f"  - Unique Departments: {retail_sales['Dept Fullname'].nunique()}")
print(f"  - Total Revenue: €{retail_sales['Turnover'].sum():,.2f}")
print(f"  - Total Profit: €{retail_sales['Profit'].sum():,.2f}")
print(f"  - Overall Margin: {100*retail_sales['Profit'].sum()/retail_sales['Turnover'].sum():.2f}%")

# ============================================================================
# 2. DATA QUALITY DEEP DIVE
# ============================================================================
print("\n" + "="*80)
print("2. DATA QUALITY ANALYSIS - THE MESSY REALITY")
print("="*80)

# Missing data
print("\n📋 MISSING DATA:")
missing = retail_sales.isnull().sum()
missing_pct = 100 * missing / len(retail_sales)
for col in retail_sales.columns:
    if missing[col] > 0:
        print(f"  - {col}: {missing[col]:,} ({missing_pct[col]:.2f}%)")

# Duplicates by barcode
print("\n🔍 DUPLICATE PRODUCT NAMES (Same Barcode, Different Names):")
barcode_groups = retail_sales.groupby('Barcode')['Product'].unique()
duplicates = barcode_groups[barcode_groups.apply(len) > 1]
print(f"  - Found {len(duplicates):,} barcodes with multiple product names")
print(f"\n  Top 10 Examples:")
for i, (barcode, names) in enumerate(list(duplicates.items())[:10], 1):
    sales_count = retail_sales[retail_sales['Barcode'] == barcode].groupby('Product')['Sale ID'].count()
    print(f"\n  {i}. Barcode: {barcode}")
    for name in names:
        count = sales_count.get(name, 0)
        print(f"     → \"{name}\" ({count:,} transactions)")

# Negative margins
print("\n💸 NEGATIVE MARGIN ANALYSIS:")
negative_margin = retail_sales[retail_sales['Profit'] < 0].copy()
print(f"  - Transactions with negative profit: {len(negative_margin):,} ({100*len(negative_margin)/len(retail_sales):.2f}%)")
print(f"  - Total loss: €{negative_margin['Profit'].sum():,.2f}")
print(f"\n  Top 10 Loss-Making Products:")
neg_by_product = negative_margin.groupby('Product').agg({
    'Profit': 'sum',
    'Qty Sold': 'sum',
    'Turnover': 'sum',
    'Trade Price': 'mean'
}).sort_values('Profit')
for i, (product, row) in enumerate(neg_by_product.head(10).iterrows(), 1):
    print(f"  {i}. {product[:60]}")
    print(f"     Loss: €{row['Profit']:.2f} | Units: {row['Qty Sold']:.0f} | Revenue: €{row['Turnover']:.2f}")

# Heavy discounting
print("\n🎁 HEAVY DISCOUNTING ANALYSIS:")
retail_sales['Discount %'] = np.where(
    (retail_sales['Turnover'] + retail_sales['Disc Amount']) > 0,
    100 * retail_sales['Disc Amount'] / (retail_sales['Turnover'] + retail_sales['Disc Amount']),
    0
)
heavy_discount = retail_sales[retail_sales['Discount %'] > 25].copy()
print(f"  - Transactions with >25% discount: {len(heavy_discount):,} ({100*len(heavy_discount)/len(retail_sales):.2f}%)")
print(f"  - Total discounts given: €{retail_sales['Disc Amount'].sum():,.2f}")
print(f"  - Average discount rate: {retail_sales['Discount %'].mean():.2f}%")

discount_by_product = heavy_discount.groupby('Product').agg({
    'Discount %': 'mean',
    'Disc Amount': 'sum',
    'Qty Sold': 'sum'
}).sort_values('Disc Amount', ascending=False)
print(f"\n  Top 10 Most Discounted Products (by total € discounted):")
for i, (product, row) in enumerate(discount_by_product.head(10).iterrows(), 1):
    print(f"  {i}. {product[:60]}")
    print(f"     Avg Discount: {row['Discount %']:.1f}% | Total Discounted: €{row['Disc Amount']:,.2f}")

# ============================================================================
# 3. SALES PERFORMANCE ANALYSIS
# ============================================================================
print("\n" + "="*80)
print("3. SALES PERFORMANCE DEEP DIVE")
print("="*80)

# Top products
print("\n🏆 TOP 20 PRODUCTS BY REVENUE:")
top_products = retail_sales.groupby('Product').agg({
    'Turnover': 'sum',
    'Profit': 'sum',
    'Qty Sold': 'sum',
    'Trade Price': 'mean',
    'RRP': 'mean',
    'Sale ID': 'nunique'
}).copy()
top_products['Margin %'] = 100 * top_products['Profit'] / top_products['Turnover']
top_products['Avg Price'] = top_products['Turnover'] / top_products['Qty Sold']
top_products = top_products.sort_values('Turnover', ascending=False)

for i, (product, row) in enumerate(top_products.head(20).iterrows(), 1):
    print(f"\n{i}. {product[:70]}")
    print(f"   Revenue: €{row['Turnover']:,.2f} | Profit: €{row['Profit']:,.2f} | Margin: {row['Margin %']:.1f}%")
    print(f"   Units: {row['Qty Sold']:,.0f} | Avg Price: €{row['Avg Price']:.2f} | Transactions: {row['Sale ID']:,.0f}")

# Branch performance
print("\n🏪 BRANCH PERFORMANCE:")
branch_perf = retail_sales.groupby('Branch Name').agg({
    'Turnover': 'sum',
    'Profit': 'sum',
    'Qty Sold': 'sum',
    'Sale ID': 'nunique'
}).copy()
branch_perf['Margin %'] = 100 * branch_perf['Profit'] / branch_perf['Turnover']
branch_perf['Avg Transaction'] = branch_perf['Turnover'] / branch_perf['Sale ID']
branch_perf = branch_perf.sort_values('Turnover', ascending=False)

for branch, row in branch_perf.iterrows():
    print(f"\n  {branch}:")
    print(f"    Revenue: €{row['Turnover']:,.2f} | Profit: €{row['Profit']:,.2f} | Margin: {row['Margin %']:.1f}%")
    print(f"    Transactions: {row['Sale ID']:,.0f} | Avg Trans: €{row['Avg Transaction']:.2f} | Units: {row['Qty Sold']:,.0f}")

# Department performance
print("\n📊 TOP 15 DEPARTMENTS BY REVENUE:")
dept_perf = retail_sales.groupby('Dept Fullname').agg({
    'Turnover': 'sum',
    'Profit': 'sum',
    'Qty Sold': 'sum'
}).copy()
dept_perf['Margin %'] = 100 * dept_perf['Profit'] / dept_perf['Turnover']
dept_perf = dept_perf.sort_values('Turnover', ascending=False)

for i, (dept, row) in enumerate(dept_perf.head(15).iterrows(), 1):
    print(f"{i:2d}. {dept[:50]:50s} | Rev: €{row['Turnover']:>12,.2f} | Margin: {row['Margin %']:5.1f}%")

# ============================================================================
# 4. TEMPORAL ANALYSIS
# ============================================================================
print("\n" + "="*80)
print("4. TEMPORAL PATTERNS & TRENDS")
print("="*80)

# Monthly trends
monthly = retail_sales.groupby(retail_sales['Sale Date'].dt.to_period('M')).agg({
    'Turnover': 'sum',
    'Profit': 'sum',
    'Sale ID': 'nunique'
}).copy()
monthly['Margin %'] = 100 * monthly['Profit'] / monthly['Turnover']

print("\n📅 MONTHLY SALES TRENDS:")
print(f"\n{'Month':15s} {'Revenue':>15s} {'Profit':>15s} {'Margin %':>10s} {'Trans':>10s}")
print("-" * 70)
for month, row in monthly.iterrows():
    print(f"{str(month):15s} €{row['Turnover']:>14,.2f} €{row['Profit']:>14,.2f} {row['Margin %']:>9.1f}% {row['Sale ID']:>10,.0f}")

# Best and worst months
best_month = monthly['Turnover'].idxmax()
worst_month = monthly['Turnover'].idxmin()
print(f"\n  🎯 Best Month: {best_month} (€{monthly.loc[best_month, 'Turnover']:,.2f})")
print(f"  📉 Worst Month: {worst_month} (€{monthly.loc[worst_month, 'Turnover']:,.2f})")
print(f"  📈 Growth: {100*(monthly['Turnover'].iloc[-1]/monthly['Turnover'].iloc[0] - 1):.1f}% from first to last month")

# Day of week analysis
retail_sales['Day of Week'] = retail_sales['Sale Date'].dt.day_name()
dow_perf = retail_sales.groupby('Day of Week').agg({
    'Turnover': 'mean',
    'Sale ID': 'nunique'
}).reindex(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'])

print("\n📆 AVERAGE DAILY SALES BY DAY OF WEEK:")
for day, row in dow_perf.iterrows():
    print(f"  {day:10s}: €{row['Turnover']:>10,.2f} avg revenue | {row['Sale ID']:>6,.0f} transactions")

# ============================================================================
# 5. INVENTORY ANALYSIS
# ============================================================================
print("\n" + "="*80)
print("5. INVENTORY OPTIMIZATION ANALYSIS")
print("="*80)

# Load inventory
inventory = pd.read_csv('data/input/Retail/retail_inventory_snapshot_30_10_25.csv',
                        encoding='utf-8-sig',
                        low_memory=False)

print(f"✓ Loaded inventory snapshot (30 Oct 2025)")
print(f"  - Total SKU-Location records: {len(inventory):,}")
print(f"  - Unique products: {inventory['Product'].nunique():,}")

# Calculate total inventory value
inventory['Stock Value'] = inventory['Branch Stock Level'] * inventory['Trade Price']
total_inventory_value = inventory['Stock Value'].sum()
print(f"  - Total inventory value: €{total_inventory_value:,.2f}")

# Inventory by branch
inv_by_branch = inventory.groupby('Branch Name').agg({
    'Branch Stock Level': 'sum',
    'Stock Value': 'sum',
    'Product': 'count'
})
inv_by_branch.columns = ['Units', 'Value €', 'SKUs']
inv_by_branch = inv_by_branch.sort_values('Value €', ascending=False)

print("\n📦 INVENTORY BY BRANCH:")
for branch, row in inv_by_branch.iterrows():
    print(f"  {branch:20s}: €{row['Value €']:>12,.2f} | {row['Units']:>8,.0f} units | {row['SKUs']:>6,.0f} SKUs")

# Calculate velocity (last 30 days)
last_date = retail_sales['Sale Date'].max()
recent_sales = retail_sales[retail_sales['Sale Date'] >= last_date - pd.Timedelta(days=30)].copy()

velocity = recent_sales.groupby('Product').agg({
    'Qty Sold': 'sum',
    'Turnover': 'sum',
    'Profit': 'sum'
}).copy()
velocity.columns = ['Units_30d', 'Revenue_30d', 'Profit_30d']
velocity['Daily_Velocity'] = velocity['Units_30d'] / 30

# Aggregate inventory by product
inv_by_product = inventory.groupby('Product').agg({
    'Branch Stock Level': 'sum',
    'Trade Price': 'first',
    'RRP': 'first'
}).copy()
inv_by_product.columns = ['Stock', 'Cost', 'RRP']

# Merge with velocity
stock_analysis = inv_by_product.join(velocity, how='left').fillna(0)
stock_analysis['Days_Stock'] = np.where(
    stock_analysis['Daily_Velocity'] > 0,
    stock_analysis['Stock'] / stock_analysis['Daily_Velocity'],
    999
)
stock_analysis['Stock_Value'] = stock_analysis['Stock'] * stock_analysis['Cost']

print("\n🎯 STOCK COVERAGE SEGMENTATION:")
urgent = stock_analysis[(stock_analysis['Days_Stock'] < 7) & (stock_analysis['Daily_Velocity'] > 0)]
optimal = stock_analysis[(stock_analysis['Days_Stock'] >= 7) & (stock_analysis['Days_Stock'] <= 21)]
overstocked = stock_analysis[(stock_analysis['Days_Stock'] > 60) & (stock_analysis['Stock'] > 0)]
dead_stock = stock_analysis[(stock_analysis['Units_30d'] == 0) & (stock_analysis['Stock'] > 0)]

print(f"  🚨 URGENT (<7 days): {len(urgent):,} products - REORDER NOW")
print(f"  ✅ OPTIMAL (7-21 days): {len(optimal):,} products")
print(f"  ⚠️  OVERSTOCKED (>60 days): {len(overstocked):,} products")
print(f"  💀 DEAD STOCK (no sales in 30d): {len(dead_stock):,} products")

# Urgent reorders
print("\n🚨 TOP 20 URGENT REORDERS (<7 days stock, sorted by revenue impact):")
urgent_sorted = urgent.sort_values('Revenue_30d', ascending=False).head(20)
for i, (product, row) in enumerate(urgent_sorted.iterrows(), 1):
    print(f"\n{i}. {product[:65]}")
    print(f"   Stock: {row['Stock']:.0f} units | Daily Sales: {row['Daily_Velocity']:.1f} | Days Left: {row['Days_Stock']:.1f}")
    print(f"   30d Revenue: €{row['Revenue_30d']:,.2f} | Profit: €{row['Profit_30d']:,.2f}")

# Dead stock
print("\n💀 TOP 20 DEAD STOCK (No sales in 30 days, sorted by locked capital):")
dead_sorted = dead_stock.sort_values('Stock_Value', ascending=False).head(20)
for i, (product, row) in enumerate(dead_sorted.iterrows(), 1):
    print(f"\n{i}. {product[:65]}")
    print(f"   Stock: {row['Stock']:.0f} units @ €{row['Cost']:.2f} = €{row['Stock_Value']:,.2f} locked")
    print(f"   RRP: €{row['RRP']:.2f} | No sales in last 30 days")

print(f"\n💰 TOTAL CAPITAL LOCKED IN DEAD STOCK: €{dead_stock['Stock_Value'].sum():,.2f}")

# Slow movers
print("\n⚠️  TOP 20 SLOW MOVERS (>60 days stock, sorted by locked capital):")
slow_sorted = overstocked.sort_values('Stock_Value', ascending=False).head(20)
for i, (product, row) in enumerate(slow_sorted.iterrows(), 1):
    print(f"\n{i}. {product[:65]}")
    print(f"   Stock: {row['Stock']:.0f} units | Daily Sales: {row['Daily_Velocity']:.2f} | Days Stock: {row['Days_Stock']:.0f}")
    print(f"   Locked Capital: €{row['Stock_Value']:,.2f}")

print(f"\n💰 TOTAL CAPITAL LOCKED IN SLOW MOVERS: €{overstocked['Stock_Value'].sum():,.2f}")

# ============================================================================
# 6. SUPPLIER ANALYSIS
# ============================================================================
print("\n" + "="*80)
print("6. SUPPLIER ANALYSIS")
print("="*80)

supplier_perf = retail_sales.groupby('OrderList').agg({
    'Turnover': 'sum',
    'Profit': 'sum',
    'Product': 'nunique'
}).copy()
supplier_perf['Margin %'] = 100 * supplier_perf['Profit'] / supplier_perf['Turnover']
supplier_perf = supplier_perf.sort_values('Turnover', ascending=False)

print("\n📦 TOP 20 SUPPLIERS BY REVENUE:")
for i, (supplier, row) in enumerate(supplier_perf.head(20).iterrows(), 1):
    print(f"{i:2d}. {supplier[:45]:45s} | Rev: €{row['Turnover']:>12,.2f} | Margin: {row['Margin %']:5.1f}% | SKUs: {row['Product']:>5.0f}")

# ============================================================================
# 7. PRICING ANALYSIS
# ============================================================================
print("\n" + "="*80)
print("7. PRICING & PROFITABILITY ANALYSIS")
print("="*80)

# Calculate actual selling price vs RRP
retail_sales['Actual Price'] = retail_sales['Turnover'] / retail_sales['Qty Sold']
retail_sales['Price vs RRP %'] = 100 * (retail_sales['Actual Price'] / retail_sales['RRP'] - 1)

# Products sold significantly below RRP
underpriced = retail_sales[retail_sales['Price vs RRP %'] < -10].copy()
print(f"\n💸 UNDERPRICING ANALYSIS:")
print(f"  - Transactions sold >10% below RRP: {len(underpriced):,} ({100*len(underpriced)/len(retail_sales):.2f}%)")

underprice_impact = underpriced.groupby('Product').agg({
    'Turnover': 'sum',
    'Qty Sold': 'sum',
    'RRP': 'mean',
    'Actual Price': 'mean'
}).copy()
underprice_impact['Lost Revenue'] = underprice_impact['Qty Sold'] * (underprice_impact['RRP'] - underprice_impact['Actual Price'])
underprice_impact = underprice_impact.sort_values('Lost Revenue', ascending=False)

print(f"\n  TOP 10 PRODUCTS WITH HIGHEST PRICING OPPORTUNITY:")
for i, (product, row) in enumerate(underprice_impact.head(10).iterrows(), 1):
    print(f"\n  {i}. {product[:65]}")
    print(f"     RRP: €{row['RRP']:.2f} | Avg Actual: €{row['Actual Price']:.2f} | Gap: €{row['RRP']-row['Actual Price']:.2f}")
    print(f"     Potential Revenue Recovery: €{row['Lost Revenue']:,.2f}")

# ============================================================================
# 8. KEY INSIGHTS SUMMARY
# ============================================================================
print("\n" + "="*80)
print("8. KEY INSIGHTS & HACKATHON OPPORTUNITIES")
print("="*80)

print(f"""
🎯 BUSINESS SCALE:
  - Total Revenue (2 years): €{retail_sales['Turnover'].sum():,.2f}
  - Total Profit: €{retail_sales['Profit'].sum():,.2f}
  - Average Margin: {100*retail_sales['Profit'].sum()/retail_sales['Turnover'].sum():.2f}%
  - Unique Products: {retail_sales['Product'].nunique():,}
  - Total Transactions: {retail_sales['Sale ID'].nunique():,}
  - Locations: {retail_sales['Branch Name'].nunique()}

🚨 DATA QUALITY ISSUES (Agent Opportunity #1):
  - {len(duplicates):,} barcodes with multiple product names
  - {len(negative_margin):,} negative margin transactions (€{negative_margin['Profit'].sum():,.2f} loss)
  - {len(heavy_discount):,} heavily discounted transactions (>25% off)
  - €{retail_sales['Disc Amount'].sum():,.2f} total discounts given

💰 INVENTORY OPTIMIZATION (Agent Opportunity #2):
  - {len(urgent):,} products need URGENT reorder (<7 days stock)
  - {len(dead_stock):,} products with ZERO sales in 30 days
  - €{dead_stock['Stock_Value'].sum():,.2f} locked in dead stock
  - €{overstocked['Stock_Value'].sum():,.2f} locked in slow movers (>60 days)
  - Total inventory value: €{total_inventory_value:,.2f}

💸 PRICING OPPORTUNITIES (Agent Opportunity #3):
  - {len(underpriced):,} transactions sold >10% below RRP
  - Potential revenue recovery: €{underprice_impact['Lost Revenue'].sum():,.2f}
  - {len(supplier_perf)} active suppliers to negotiate with

📊 OPERATIONAL INSIGHTS:
  - Best performing location: {branch_perf.index[0]} (€{branch_perf.iloc[0]['Turnover']:,.2f})
  - Best month: {best_month} (€{monthly.loc[best_month, 'Turnover']:,.2f})
  - Top department: {dept_perf.index[0]} (€{dept_perf.iloc[0]['Turnover']:,.2f})
  - Top supplier: {supplier_perf.index[0]} (€{supplier_perf.iloc[0]['Turnover']:,.2f})
""")

print("="*80)
print("ANALYSIS COMPLETE")
print("="*80)
