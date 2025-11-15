# Demo Examples - Real Cases from the Data

These are ACTUAL examples from the dataset that make perfect demo material.

---

## 🔥 DATA QUALITY GUARDIAN - Example Cases

### Case 1: The Cutex Chaos
**Barcode**: 309971000000

**The Problem**:
One barcode mapped to 8 different product names across 146 transactions:

```
Current State (Messy):
├─ "Cutex Acetone Free Nail Polish Remover 100ml" (24 transactions)
├─ "Cutex Moisture Rich 100Ml" (19 transactions)
├─ "Cutex Moisture Rich Nail Varnish Remover 200Ml" (8 transactions)
├─ "Cutex Nourish Nail Polish Remover 200ml" (14 transactions)
├─ "Cutex Nourishing 100Ml" (19 transactions)
├─ "Cutex Ultra Powerful Nail Polish Remover 100ml" (42 transactions)
├─ "Cutex Non Acetone Nail Varnish Remover 200ml" (12 transactions)
└─ "Cutex Ultra-Powerful Nail Varnish Remover 200Ml" (8 transactions)
```

**AI Agent Output**:
```
🔍 DUPLICATE DETECTED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Issue Type: Product Name Inconsistency
Severity: HIGH
Affected Records: 146 transactions
Barcode: 309971000000

Evidence:
• 8 different names for the same barcode
• Names vary by:
  - Capitalization ("100Ml" vs "100ml")
  - Spelling ("Varnish" vs "Polish")
  - Abbreviation ("Nail Polish" vs just product name)

Analysis:
• Most common: "Cutex Ultra Powerful..." (42 transactions, 28.8%)
• Most recent: "Cutex Acetone Free..." (last 30 days)
• Supplier catalog says: "Cutex Nail Polish Remover - Multiple Variants"

Recommended Fix:
Create 4 distinct products (these ARE different products):
├─ Cutex Acetone Free 100ml (Barcode: 309971000001)
├─ Cutex Moisture Rich 100ml (Barcode: 309971000002)
├─ Cutex Nourishing 100ml (Barcode: 309971000003)
└─ Cutex Ultra Powerful 100ml (Barcode: 309971000004)

Impact:
✓ Clears 146 transaction records
✓ Enables accurate inventory tracking per variant
✓ Prevents future barcode collisions

Confidence: 95% (requires barcode verification with supplier)
```

**Human Approval Workflow**:
```
[ Approve All ] [ Review Individually ] [ Reject ]
```

---

### Case 2: The Benefit Barcode Nightmare
**Barcode**: 602004000000

**The Problem**:
**66 different Benefit makeup products** mapped to ONE barcode!

Examples:
- "Benefit Benetint Mini IB290"
- "Benefit Boi-ing Concealer Shade 03"
- "Benefit Boi-ing Concealer Shade 04"
- "Benefit Brow Contour Pro Shade 1"
- "Benefit Gimme Brow Shade 03"
- ... (61 more)

**This is CLEARLY a data entry error** - someone used a placeholder barcode for all Benefit products.

**AI Agent Output**:
```
🚨 CRITICAL DATA ERROR
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Issue Type: Barcode Collision (Extreme)
Severity: CRITICAL
Affected Records: 308 transactions across 66 products
Barcode: 602004000000

Evidence:
• 66 unique products mapped to same barcode
• All from "Benefit" brand
• Products range from:
  - Mascaras (different formulas)
  - Concealers (different shades)
  - Brow products (different shades)
  - Gift sets

Root Cause Analysis:
• Barcode "602004000000" appears to be a placeholder/dummy code
• Likely used when actual barcodes were unavailable during data entry
• Each product needs unique barcode

Recommended Action:
URGENT: Contact Benefit supplier for accurate barcode list

Temporary Fix:
Create internal SKU codes:
• BENEFIT-BENETINT-MINI → Auto-assign: 602004000001
• BENEFIT-BOIING-03 → Auto-assign: 602004000002
• ... (continues for all 66 products)

Impact:
⚠️  Impossible to track inventory for any Benefit product
⚠️  Cannot reorder accurately
⚠️  Cannot generate sales reports per product
⚠️  High theft risk (all scan as same price)

Priority: IMMEDIATE ACTION REQUIRED

Confidence: 99.9% (this is definitively an error)
```

---

### Case 3: Fisherman's Friend Fiasco
**Product**: Fisherman's Friend Original 25g

**The Problem**:
Selling product at **massive loss**
- Sold 188 units
- Revenue: €406.74 (€2.16 per unit)
- Cost in system: €23.89 per unit
- **Total loss: €3,898.24**

**AI Agent Output**:
```
💸 NEGATIVE MARGIN ALERT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Product: Fisherman's Friend Original 25g
Barcode: [various]
Transactions: 188
Loss: €3,898.24

Analysis:
┌─────────────────┬──────────┬──────────┬─────────┐
│ Metric          │ Current  │ Expected │ Delta   │
├─────────────────┼──────────┼──────────┼─────────┤
│ Selling Price   │ €2.16    │ €2.50    │ -14%    │
│ Cost Price      │ €23.89   │ €0.85    │ +2709%  │
│ Margin          │ -1005%   │ 66%      │ ERROR   │
└─────────────────┴──────────┴──────────┴─────────┘

Root Cause:
• Cost price is clearly WRONG in master data
• €23.89 for a candy mint is impossible
• Likely decimal point error: Should be €0.85 or €2.39

Similar Products (for validation):
• Fisherman's Friend Blackcurrant: €0.87 cost, €2.50 RRP
• Fisherman's Friend Aniseed: €0.83 cost, €2.50 RRP

Recommended Fix:
Update cost price to €0.85 (matches other variants)

If corrected:
• Actual profit: +€311.20 (not -€3,898)
• Margin: 60.9% (healthy candy margin)

Priority: HIGH (update master data immediately)
Next Action: Audit all "Fisherman's Friend" SKU costs

Confidence: 99% (cost is definitively wrong)
```

---

## 🎯 SMART INVENTORY AGENT - Example Cases

### Case 1: Critical Stockout Risk - Benylin
**Product**: Benylin Day & Night Tablets 16s
**Category**: OTC Cold & Flu (high margin, essential category)

**Current State**:
- Stock: 91 units across all locations
- Daily sales velocity: 13.7 units/day
- Days of stock remaining: **6.7 days**
- Last 30 days revenue: €4,778.80
- Last 30 days profit: €2,499.20

**AI Agent Output**:
```
🚨 URGENT REORDER REQUIRED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Product: Benylin Day & Night Tablets 16s
Status: CRITICAL - Will stock out in 6.7 days
Category: OTC Cold & Flu
Supplier: [Supplier name]

Current Situation:
┌──────────────────────┬─────────────┐
│ Metric               │ Value       │
├──────────────────────┼─────────────┤
│ Current Stock        │ 91 units    │
│ Daily Sales Velocity │ 13.7/day    │
│ Days Remaining       │ 6.7 days    │
│ Stockout Date        │ Nov 22, 2025│
└──────────────────────┴─────────────┘

Business Impact if Stockout:
• Lost revenue: €4,778/month
• Lost profit: €2,499/month
• Customer dissatisfaction: HIGH (cold/flu season essential)
• Competitor advantage: Customers will go elsewhere

Sales Pattern Analysis:
📈 Trending UP (cold/flu season starting)
• 7-day avg: 15.2 units/day (+11%)
• 30-day avg: 13.7 units/day
• 90-day avg: 11.3 units/day

Recommended Order:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Quantity: 650 units (6 cases)
Rationale:
• 45 days supply at current velocity
• Accounts for seasonal increase
• Fills to optimal stock level

Order Details:
• Unit cost: €5.39
• Total order value: €3,503.50
• Margin per unit: €6.10 (53.1%)
• Supplier: [Name]
• Lead time: 3 days
• Order by: Nov 16 (latest)

Expected Performance:
• Revenue (45 days): €7,167
• Profit (45 days): €3,965
• ROI: 113% over 45 days

Confidence: 98% (high sales consistency, clear trend)
Action: AUTO-APPROVE (under €5K threshold)
```

**Auto-Generated Purchase Order** (Excel format):
```
PURCHASE ORDER #PO-2025-1115-001
Date: November 15, 2025
Supplier: [Supplier Name]
Delivery Location: Main Warehouse (distribute to all branches)

SKU       Product                           Qty    Unit Cost   Total
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
BEN-001   Benylin Day & Night 16s          650    €5.39       €3,503.50

                                           TOTAL: €3,503.50

Expected Delivery: November 19, 2025
Payment Terms: Net 30
Approved by: [AI Agent] - Auto-approved (under threshold)

Stock Distribution Recommendation:
• Baggot St: 180 units (highest volume)
• Churchtown: 110 units
• Barrow St: 95 units
• [etc...]
```

---

### Case 2: Dead Stock Nightmare - Joop Homme Fragrance
**Product**: Joop Homme EDT Spray 200ml
**Category**: Fragrance (luxury)

**Current State**:
- Stock: 23 units
- Cost per unit: €56.92
- Total locked capital: **€1,309.16**
- RRP: €104.50
- Sales in last 30 days: **ZERO**
- Sales in last 90 days: **41 units** (but at a LOSS!)
- Historical loss: -€970.08

**AI Agent Output**:
```
💀 DEAD STOCK - MARKDOWN REQUIRED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Product: Joop Homme EDT Spray 200ml
Status: ZERO sales in 30 days
Category: Fragrance - Men's
Current Value: €1,309.16 LOCKED

Historical Performance:
┌──────────────┬────────┬──────────┬─────────┐
│ Period       │ Units  │ Revenue  │ Profit  │
├──────────────┼────────┼──────────┼─────────┤
│ Last 30 days │ 0      │ €0       │ €0      │
│ Last 90 days │ 41     │ €1,677   │ -€970   │
│ Last 12 mos  │ 41     │ €1,677   │ -€970   │
└──────────────┴────────┴──────────┴─────────┘

Problem Analysis:
• Product consistently sold BELOW COST (€40.92 avg vs €56.92 cost)
• Seasonal? (Men's fragrance gift season Dec-Jan)
• Competitor pressure? (Check if others sell cheaper)
• Out of style? (Fragrance trends change)

Markdown Strategy:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Phase 1 (Weeks 1-2): 20% off RRP
• New price: €83.60 (still profitable if cost data is wrong)
• Target: Sell 8 units
• Revenue: €668.80
• If cost is actually €35: Profit €387.20

Phase 2 (Weeks 3-4): 40% off RRP
• New price: €62.70 (near cost if cost data correct)
• Target: Sell 10 units
• Revenue: €627.00
• Breakeven scenario

Phase 3 (Week 5+): 60% off RRP - CLEARANCE
• New price: €41.80 (accept loss to free capital)
• Target: Sell remaining 5 units
• Revenue: €209.00
• Loss: €75.60
• But: Free €284.60 capital for better products

Total Recovery:
• Revenue: €1,504.80 (vs €1,309 locked capital)
• Net: €195.80 gain (if cost data is wrong)
• OR: €75.60 loss (if cost data is correct)
• Either way: Better than holding forever

Alternative Strategy:
• Bundle with best-seller (buy €50 get free Joop)
• Gift-with-purchase promotion
• Staff incentive (free fragrance as bonus)
• Donate for tax writeoff (€1,309 × 21% = €275 tax benefit)

Recommended Action: Start Phase 1 markdown immediately
Priority: MEDIUM (not critical, but capital locked)
Confidence: 90% (clear dead stock pattern)
```

---

### Case 3: Slow Mover - MacuPrime (Eye Supplement)
**Product**: MacuPrime Original 90s
**Category**: Vitamins - Eye Health

**Current State**:
- Stock: 107 units
- Cost per unit: €23.50
- Total locked capital: **€2,514.50**
- Daily sales: 0.2 units/day (6 units/month)
- Days of stock: **535 days** (1.5 years!)

**AI Agent Output**:
```
⚠️  OVERSTOCK - REORDER POINT TOO HIGH
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Product: MacuPrime Original 90s
Status: Severely overstocked
Category: Vitamins - Eye Health
Locked Capital: €2,514.50

Inventory Metrics:
┌────────────────────┬──────────────┐
│ Metric             │ Value        │
├────────────────────┼──────────────┤
│ Current Stock      │ 107 units    │
│ Daily Velocity     │ 0.2/day      │
│ Days of Stock      │ 535 days     │
│ Optimal Stock      │ 15-20 units  │
│ Excess Stock       │ 87-92 units  │
└────────────────────┴──────────────┘

Why So Much Stock?
Historical order analysis:
• Oct 2024: Ordered 120 units (likely supplier minimum/promotion)
• Expected to sell in 90 days
• Actually selling in 600 days
• Classic overorder scenario

Financial Impact:
• €2,514 locked for 18 months
• Opportunity cost: 5% interest = €188 lost
• Expiration risk: Eye supplements typically 2-year shelf life
• May expire before selling all units

Recommendations:

Option 1: Do Nothing (Wait it out)
• Sell naturally over 18 months
• Risk: Expiration, capital locked
• NOT RECOMMENDED

Option 2: Aggressive Promotion
• "Eye Health Month" campaign
• Bundle: Buy MacuPrime + Free Eye Exam voucher
• Target: Sell 50 units in 3 months
• Promo cost: €500
• Benefit: Free €1,175 capital

Option 3: Negotiated Return
• Contact supplier: Return unused stock
• Typical restocking fee: 15-20%
• Return 87 units × €23.50 × 85% = €1,737 recovery
• Loss: €338 vs €2,045 locked

Option 4: Adjust Reorder Point
• Current: Automatically reorder at 90 units (wrong!)
• New: Reorder at 15 units (30 days supply)
• Prevents future overstock
• Set max order: 30 units

Recommended Action:
1. Immediate: Stop all reorders (set reorder point to 0)
2. Short-term: Implement Option 2 (promotion)
3. Long-term: Adjust reorder logic for all slow-movers

Category Review:
• Total Eye Health category: €15K inventory
• Monthly sales: €2.3K
• Days of stock: 196 days (6.5 months)
• RECOMMENDATION: Reduce entire category by 60%

Confidence: 95% (clear overstock, math is solid)
Priority: MEDIUM (not urgent but significant capital)
```

---

## 🎨 UI/UX Demo Mockups

### Dashboard View
```
╔══════════════════════════════════════════════════════════════════╗
║  RETAIL OPERATIONS AI AGENT - DASHBOARD                         ║
╠══════════════════════════════════════════════════════════════════╣
║                                                                  ║
║  📊 INVENTORY HEALTH SCORE: 67/100  (⚠️  Needs Attention)        ║
║                                                                  ║
║  ┌────────────────────────────────────────────────────────────┐ ║
║  │ 🚨 URGENT ALERTS (3)                                        │ ║
║  ├────────────────────────────────────────────────────────────┤ ║
║  │ • 515 products will stock out in <7 days                   │ ║
║  │   Action: Review auto-generated purchase orders            │ ║
║  │                                                             │ ║
║  │ • €375K locked in dead stock (0 sales in 30 days)          │ ║
║  │   Action: Review markdown recommendations                  │ ║
║  │                                                             │ ║
║  │ • 476 duplicate product names detected                     │ ║
║  │   Action: Review data cleanup suggestions                  │ ║
║  └────────────────────────────────────────────────────────────┘ ║
║                                                                  ║
║  ┌────────────────────────────────────────────────────────────┐ ║
║  │ 💡 INSIGHTS                                                 │ ║
║  ├────────────────────────────────────────────────────────────┤ ║
║  │ • Oct 2025 is your best month ever (€947K, +22% YoY)       │ ║
║  │ • Cold/flu season: Stock up on Benylin, Nurofen, Lemsip    │ ║
║  │ • Symprove discounting: Reduce by 10% to gain €50K margin  │ ║
║  └────────────────────────────────────────────────────────────┘ ║
║                                                                  ║
║  [ View Purchase Orders ]  [ Clean Data ]  [ Run Analysis ]    ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
```

### Purchase Order Review Screen
```
╔══════════════════════════════════════════════════════════════════╗
║  URGENT REORDERS - PURCHASE ORDER GENERATOR                      ║
╠══════════════════════════════════════════════════════════════════╣
║                                                                  ║
║  Showing: Top 20 products by revenue impact (515 total)         ║
║  Grouped by: Supplier                                           ║
║  Total PO value: €47,350                                        ║
║                                                                  ║
║  ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓ ║
║  ┃ SUPPLIER: Pharmax Ltd                          €15,847.50 ┃ ║
║  ┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫ ║
║  ┃                                                             ┃ ║
║  ┃ Benylin Day & Night 16s                                    ┃ ║
║  ┃ Stock: 91 | Daily: 13.7 | Days: 6.7 ⚠️                     ┃ ║
║  ┃ Order: 650 units × €5.39 = €3,503.50                       ┃ ║
║  ┃ [ Auto-Approved ] ROI: 113% over 45 days                   ┃ ║
║  ┃                                                             ┃ ║
║  ┃ ─────────────────────────────────────────────────────────  ┃ ║
║  ┃                                                             ┃ ║
║  ┃ Solpadeine Soluble 24s                                     ┃ ║
║  ┃ Stock: 145 | Daily: 18.1 | Days: 8.0 ⚠️                    ┃ ║
║  ┃ Order: 800 units × €8.36 = €6,688.00                       ┃ ║
║  ┃ [ Pending Review ] Value >€5K - requires approval          ┃ ║
║  ┃                                                             ┃ ║
║  ┃ ... (12 more products)                                     ┃ ║
║  ┃                                                             ┃ ║
║  ┃ [ Download Excel PO ] [ Email to Supplier ] [ Approve All ]┃ ║
║  ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛ ║
║                                                                  ║
║  ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓ ║
║  ┃ SUPPLIER: Haleon (GSK)                          €8,945.00 ┃ ║
║  ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛ ║
║                                                                  ║
║  ... (5 more suppliers)                                         ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
```

---

## 🎤 DEMO SCRIPT (10 minutes)

**[0:00-2:00] - The Problem**

"Let me show you the reality of retail operations today.

This is a real pharmacy with 20,000 products across 10 locations. They're doing €16M in revenue, but look at this..."

*Show Cutex duplicate example*

"Same barcode, EIGHT different names. Now look at this..."

*Show Benefit 66 products*

"66 products, ONE barcode. This is REAL data, not made up.

The result? €167K lost to pricing errors, €375K locked in dead stock they can't track, and buyers spending 10 hours a week manually creating purchase orders in Excel."

---

**[2:00-5:00] - The Solution (Data Quality Guardian)**

"Let's fix this. Here's our Data Quality Guardian agent.

*Run agent*

Watch it scan 1.3 million transactions... Found 476 data quality issues. Let's look at one."

*Show Cutex analysis*

"See how it shows EVIDENCE? It's not hallucinating - it's analyzing the data and showing its work. It suggests splitting these into 4 distinct products with new barcodes.

But here's the key - it doesn't auto-fix. It asks for approval. That's the guardrail.

*Click approve*

Done. 146 transactions cleaned, inventory tracking fixed."

---

**[5:00-8:00] - The Solution (Smart Inventory Agent)**

"Now that the data is clean, let's optimize inventory.

*Run inventory agent*

Found 515 products about to stock out. Here's the critical one - Benylin."

*Show Benylin analysis*

"Only 6.7 days of stock left. This product generates €4,778 per month. If it stocks out, that's lost revenue AND customers going to competitors.

The agent doesn't just flag it - it generates the purchase order.

*Show auto-generated Excel PO*

650 units, €3,503 order value, delivery by Nov 19. Ready to send to supplier.

But wait - how do we know it's not hallucinating the order quantity?

*Click to show calculation*

See? It shows the math. 13.7 units per day × 45 days = 617 units, rounded up to case size of 650. Transparent AI.

Now look at the other side - dead stock."

*Show Joop fragrance*

"€1,309 locked in fragrance with ZERO sales in 30 days. The agent recommends a tiered markdown strategy to free that capital."

---

**[8:00-10:00] - The Impact**

"Let me show you the numbers.

*Show summary dashboard*

€1.34 million annual profit improvement from:
- Preventing stockouts: €600K
- Fixing pricing errors: €167K
- Reducing excess discounts: €500K
- Labor savings: €75K

Plus €1.2M in freed capital from dead stock and slow movers.

And the time savings? 10 hours per week on purchase orders → 10 minutes. That's 520 hours a year.

All with proper guardrails:
- Structured outputs (no hallucinated numbers)
- Confidence scores (flags low-confidence recommendations)
- Human approval (nothing happens without review)
- Transparent calculations (always shows its work)

This isn't futuristic AI magic. This is operational AI you can deploy Monday morning."

*End*

---

## Files to Create for Demo

1. `demo_data.csv` - Top 100 products (for fast processing)
2. `agent_data_quality.py` - Data cleaning agent
3. `agent_inventory.py` - Inventory optimization agent
4. `app.py` - Streamlit interface
5. `sample_po.xlsx` - Template purchase order
6. `results/` - Folder with pre-generated results for backup

Ready to build! 🚀
