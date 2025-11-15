"""
Quick Analysis: Order Fulfillments & Order Tags
"""

import pandas as pd
import numpy as np
from collections import Counter

print("="*80)
print("ONLINE ORDER DATA ANALYSIS - FULFILLMENTS & TAGS")
print("="*80)

# ============================================================================
# 1. ORDER FULFILLMENTS
# ============================================================================
print("\n" + "="*80)
print("1. ORDER FULFILLMENTS ANALYSIS")
print("="*80)

try:
    fulfillments = pd.read_csv('data/input/Online/order_fulfillments.csv',
                               encoding='utf-8-sig',
                               low_memory=False)

    print(f"\n✓ Loaded {len(fulfillments):,} fulfillment records")
    print(f"  Columns ({fulfillments.shape[1]}): {fulfillments.columns.tolist()}")

    # Show sample
    print("\nFirst 5 records:")
    print(fulfillments.head())

    # Analyze columns
    print("\n" + "-"*80)
    print("Column Analysis:")
    for col in fulfillments.columns:
        non_null = fulfillments[col].notna().sum()
        unique = fulfillments[col].nunique()
        print(f"  • {col:30s}: {non_null:>8,} non-null ({unique:>8,} unique)")

    # Status analysis if available
    if 'status' in fulfillments.columns:
        print("\n" + "-"*80)
        print("Fulfillment Status:")
        for status, count in fulfillments['status'].value_counts().items():
            pct = 100 * count / len(fulfillments)
            print(f"  • {str(status):20s}: {count:>8,} ({pct:>5.1f}%)")

    # Shipment status if available
    if 'shipmentStatus' in fulfillments.columns:
        print("\n" + "-"*80)
        print("Shipment Status:")
        for status, count in fulfillments['shipmentStatus'].value_counts().items():
            pct = 100 * count / len(fulfillments)
            print(f"  • {str(status):20s}: {count:>8,} ({pct:>5.1f}%)")

    # Date analysis
    date_cols = [col for col in fulfillments.columns if 'At' in col or 'date' in col.lower()]
    if date_cols:
        print("\n" + "-"*80)
        print("Date Range:")
        for col in date_cols:
            try:
                fulfillments[col] = pd.to_datetime(fulfillments[col], errors='coerce')
                min_date = fulfillments[col].min()
                max_date = fulfillments[col].max()
                print(f"  • {col:30s}: {min_date} to {max_date}")
            except:
                pass

    # Tracking info
    tracking_cols = [col for col in fulfillments.columns if 'tracking' in col.lower()]
    if tracking_cols:
        print("\n" + "-"*80)
        print("Tracking Information:")
        for col in tracking_cols:
            has_tracking = fulfillments[col].notna().sum()
            pct = 100 * has_tracking / len(fulfillments)
            print(f"  • {col:30s}: {has_tracking:>8,} ({pct:>5.1f}%) have tracking")

except FileNotFoundError:
    print("\n✗ order_fulfillments.csv not found")
except Exception as e:
    print(f"\n✗ Error loading fulfillments: {e}")

# ============================================================================
# 2. ORDER TAGS
# ============================================================================
print("\n" + "="*80)
print("2. ORDER TAGS ANALYSIS")
print("="*80)

try:
    order_tags = pd.read_csv('data/input/Online/order_tags.csv',
                             encoding='utf-8-sig',
                             low_memory=False)

    print(f"\n✓ Loaded {len(order_tags):,} tag records")
    print(f"  Columns ({order_tags.shape[1]}): {order_tags.columns.tolist()}")

    # Show sample
    print("\nFirst 10 records:")
    print(order_tags.head(10))

    # Find tag column
    tag_col = None
    for col in order_tags.columns:
        if 'tag' in col.lower() and col.lower() not in ['id', 'orderid', 'order_id']:
            tag_col = col
            break

    if tag_col:
        print(f"\n" + "-"*80)
        print(f"Tag Column: '{tag_col}'")
        print(f"  • Unique tags: {order_tags[tag_col].nunique():,}")
        print(f"  • Total tagged orders: {len(order_tags):,}")

        # Top tags
        print("\n" + "-"*80)
        print("TOP 50 MOST COMMON TAGS:")
        print("-"*80)
        tag_counts = order_tags[tag_col].value_counts().head(50)
        for i, (tag, count) in enumerate(tag_counts.items(), 1):
            pct = 100 * count / len(order_tags)
            print(f"{i:3d}. {str(tag):60s} | {count:>8,} ({pct:>5.2f}%)")

        # Categorize tags
        print("\n" + "-"*80)
        print("TAG CATEGORIZATION:")
        print("-"*80)

        all_tags = order_tags[tag_col].dropna().unique()

        categories = {
            'Marketing/Campaign': ['campaign', 'promo', 'sale', 'discount', 'offer', 'newsletter', 'email', 'ad', 'facebook', 'google', 'instagram'],
            'Customer Type': ['vip', 'new', 'returning', 'wholesale', 'member', 'subscriber', 'loyalty'],
            'Fulfillment': ['ship', 'delivery', 'pickup', 'express', 'standard', 'courier', 'click', 'collect'],
            'Payment': ['cod', 'prepaid', 'payment', 'paid'],
            'Product': ['prescription', 'otc', 'vitamin', 'skincare', 'supplement', 'fragrance'],
            'Special': ['gift', 'urgent', 'priority', 'sample', 'bundle', 'subscription'],
            'Status': ['cancel', 'return', 'refund', 'problem', 'issue', 'pending', 'hold']
        }

        categorized = {cat: [] for cat in categories}
        categorized['Other'] = []

        for tag in all_tags:
            tag_lower = str(tag).lower()
            matched = False

            for category, keywords in categories.items():
                if any(kw in tag_lower for kw in keywords):
                    categorized[category].append(tag)
                    matched = True
                    break

            if not matched:
                categorized['Other'].append(tag)

        for category, tags in categorized.items():
            if tags:
                print(f"\n{category} ({len(tags)} tags):")
                # Show top 10 by frequency
                tag_freq = order_tags[order_tags[tag_col].isin(tags)][tag_col].value_counts()
                for tag, count in list(tag_freq.items())[:10]:
                    print(f"  • {str(tag):50s} ({count:,} orders)")
                if len(tags) > 10:
                    print(f"  ... and {len(tags) - 10} more")

    else:
        print(f"\n✗ Could not identify tag column")
        print(f"  Available columns: {order_tags.columns.tolist()}")

except FileNotFoundError:
    print("\n✗ order_tags.csv not found")
except Exception as e:
    print(f"\n✗ Error loading tags: {e}")

# ============================================================================
# 3. CROSS-ANALYSIS
# ============================================================================
print("\n" + "="*80)
print("3. CROSS-ANALYSIS OPPORTUNITIES")
print("="*80)

try:
    if 'fulfillments' in locals() and 'order_tags' in locals():
        # Find common order IDs
        fulfillment_id_cols = [col for col in fulfillments.columns if 'order' in col.lower() and 'id' in col.lower()]
        tag_id_cols = [col for col in order_tags.columns if 'order' in col.lower()]

        print(f"\nPotential join columns:")
        print(f"  Fulfillments: {fulfillment_id_cols}")
        print(f"  Tags: {tag_id_cols}")

        if fulfillment_id_cols and tag_id_cols:
            # Try to find overlapping orders
            fulfillment_orders = set(fulfillments[fulfillment_id_cols[0]].dropna().unique())
            tag_orders = set(order_tags[tag_id_cols[0]].dropna().unique())
            overlap = fulfillment_orders & tag_orders

            print(f"\n  Orders with fulfillment data: {len(fulfillment_orders):,}")
            print(f"  Orders with tag data: {len(tag_orders):,}")
            print(f"  Overlapping orders: {len(overlap):,}")

            if overlap:
                print("\n✓ Can join fulfillment and tag data for advanced analysis")
                print("  Opportunities:")
                print("    • Analyze fulfillment speed by customer segment (VIP vs regular)")
                print("    • Track campaign effectiveness (tags) vs delivery performance")
                print("    • Identify which product types (tags) have slower fulfillment")
except:
    pass

print("\n" + "="*80)
print("ANALYSIS COMPLETE")
print("="*80)
print("\nNext steps:")
print("  1. Run online_data_exploration.ipynb for detailed visualizations")
print("  2. Build predictive models for fulfillment time")
print("  3. Create auto-tagging agent for new orders")
print("="*80)
