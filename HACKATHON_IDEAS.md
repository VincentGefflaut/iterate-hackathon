# Source Hackathon - AI for Retail Operations
## Ideas & Strategy Document

---

## Challenge Summary

**The Problem**: Retail operations teams at a 20,000+ product pharmacy manually work with:
- Messy operational data (duplicates, typos, inconsistent formats)
- Spreadsheet-based workflows
- LLMs that hallucinate on financial/inventory data
- No integration between systems (ERP, Shopify, POS)

**The Data**:
- 2 years of sales data (Sept 2023 - Oct 2025)
- 1.3M+ retail transactions across 10+ locations
- 1.1M+ online orders (Shopify)
- 20,000+ products
- Inventory snapshots

**The Goal**: Build AI agents that automate retail operations with proper guardrails against hallucination

---

## Key Problems Identified from Data Analysis

### 1. Data Quality Nightmares
- **Duplicate SKUs**: Same barcode, multiple product names (inconsistent naming)
- **Negative Margins**: Transactions selling below cost
- **Heavy Discounting**: Uncontrolled discounts eating profit
- **Missing Data**: Incomplete records across multiple columns
- **Format Inconsistency**: Scientific notation in barcodes, spacing issues

### 2. Inventory Management Chaos
- Products with <7 days of stock (stockout risk on top sellers)
- Massive dead stock (>60 days inventory tying up capital)
- No automated reordering system
- Products with zero sales still in inventory

### 3. Manual Reporting Hell
- Daily sales reports compiled manually
- Product performance analysis done in Excel
- No cross-channel visibility (online vs retail)
- Hours spent aggregating data instead of acting on insights

### 4. Lost Revenue Opportunities
- No trend detection or seasonality analysis
- No automated markdown strategies for slow movers
- No cross-sell/upsell recommendations
- No predictive analytics

---

## Solution Ideas (Ranked by Impact)

### 🏆 IDEA #1: Smart Inventory Optimization Agent
**Impact**: HIGH | **Feasibility**: HIGH | **Differentiation**: MEDIUM

**The Problem It Solves**:
Buyers currently spend hours each week:
- Analyzing the "Product Performance Report" manually
- Identifying products at risk of stockout
- Finding slow movers to discount
- Calculating reorder quantities
- Generating purchase orders

**What It Does**:
An AI agent that analyzes sales velocity, seasonality, and stock levels to:
1. **Auto-detect urgent reorders** (products with <7 days stock)
2. **Generate optimized purchase orders** with proper quantities
3. **Identify slow movers** for markdown campaigns
4. **Calculate dead stock** locked capital and recommend actions
5. **Predict future demand** using historical patterns

**Guardrails Against Hallucination**:
- Hard constraints: Never order more than 90 days of historical velocity
- Confidence scores: Flag low-confidence predictions for human review
- Rule-based validation: Check if suggested order quantity is within 2x of historical patterns
- Multi-step verification: Agent shows calculations before generating order
- Human-in-the-loop: Require approval for orders >€5,000

**Technical Approach**:
```python
# Structured output using Pydantic models
class PurchaseOrder(BaseModel):
    product_name: str
    supplier: str
    current_stock: int
    daily_velocity: float
    days_of_stock: float
    recommended_order_qty: int
    order_value_euros: float
    reasoning: str
    confidence_score: float  # 0-1

# Agent workflow:
1. Calculate sales velocity (last 7, 30, 90 days)
2. Detect seasonality patterns
3. Calculate optimal reorder point
4. Generate structured PurchaseOrder objects
5. Validate against business rules
6. Format as Excel for buyer review
```

**Demo Flow**:
1. Input: Current inventory snapshot + sales data
2. Agent analyzes and outputs: "Found 47 products needing urgent reorder"
3. Shows top 10 with calculations visible
4. Generates Excel purchase order template
5. Highlights products flagged for human review (low confidence)

---

### 🏆 IDEA #2: Data Quality Guardian
**Impact**: HIGH | **Feasibility**: HIGH | **Differentiation**: MEDIUM-HIGH

**The Problem It Solves**:
Messy data causes:
- Lost sales (can't find products due to naming inconsistencies)
- Profit leaks (negative margin transactions)
- Inventory errors (duplicate SKUs)
- Wrong decisions (garbage in, garbage out)

**What It Does**:
Autonomous data cleaning agent that:
1. **Detects duplicate products** (same barcode, different names)
2. **Suggests canonical names** using product clustering
3. **Flags pricing anomalies** (selling below cost, massive discounts)
4. **Identifies missing data** and suggests fills using context
5. **Normalizes formats** (barcodes, pack sizes, product names)
6. **Generates cleanup reports** with proposed fixes

**Key Innovation - Smart Reconciliation**:
Instead of blindly fixing data, the agent:
- Shows evidence: "Barcode 5060135230562 has 3 names: 'MacuSave 30s', 'MacuSave Eye Food 30s', 'Macusave Eye Supplement'"
- Suggests fix with reasoning: "Recommend: 'MacuSave Eye Food Supplement 30s' (appears in 78% of transactions, matches supplier catalog)"
- Calculates impact: "Fixing this will unify 1,247 transaction records worth €24,567"

**Guardrails**:
- Never auto-update source data without approval
- Show all proposed changes in diff format
- Confidence threshold: Only auto-fix >95% confidence issues
- Audit trail: Log all changes with timestamp and reasoning

**Demo Flow**:
1. Agent scans sales data
2. Reports: "Found 156 data quality issues"
3. Groups by severity: Critical (23), High (67), Medium (66)
4. Shows top critical issue with evidence
5. User approves batch fix
6. Agent generates cleaned CSV + audit log

---

### 🏆 IDEA #3: Multi-Channel Performance Dashboard Builder
**Impact**: MEDIUM-HIGH | **Feasibility**: MEDIUM | **Differentiation**: HIGH

**The Problem It Solves**:
Operations teams manually:
- Pull data from retail POS system
- Pull data from Shopify
- Combine in Excel to see full picture
- Rebuild reports daily/weekly from scratch

**What It Does**:
An AI agent that:
1. **Unifies online + retail sales** into single view
2. **Auto-generates the manual reports** (Daily Sales, Product Performance, Weekly Dashboard)
3. **Detects anomalies** and highlights them automatically
4. **Explains insights** in plain English
5. **Adapts to user questions** ("Show me pain relief category performance last month")

**Key Innovation - Self-Configuring ERP**:
Unlike traditional BI tools that require configuration, this agent:
- **Learns the schema** by reading the CSVs
- **Infers relationships** (products, locations, departments)
- **Generates SQL/Pandas code** to answer questions
- **Validates outputs** against business rules
- **Remembers preferences** (save commonly used reports)

**Example Interaction**:
```
User: "Generate the Daily Sales Report for yesterday across all locations"

Agent:
1. Analyzing sales data for 2025-11-14...
2. Calculating metrics for 10 locations + online...
3. Comparing to prior year (2024-11-14)...
4. Validating totals (sum of locations matches grand total ✓)

Here's your report: [generates Excel matching the template]

🚨 ALERT: Kinvara location down 23% YoY - investigate?
✨ INSIGHT: Online sales up 34% vs last Wednesday - promotion impact?
```

**Guardrails**:
- Cross-validation: Verify totals add up correctly
- Anomaly detection: Flag unusual numbers for review
- Template matching: Ensure output format matches human examples
- Calculation transparency: Show SQL/formulas used

---

### 🏆 IDEA #4: Sales Trend & Anomaly Detection Agent
**Impact**: MEDIUM | **Feasibility**: MEDIUM-HIGH | **Differentiation**: MEDIUM

**The Problem It Solves**:
Nobody is actively monitoring for:
- Emerging product trends
- Sudden sales drops (competitive threat? quality issue?)
- Seasonal patterns
- Cross-sell opportunities

**What It Does**:
A monitoring agent that:
1. **Runs daily analysis** on sales data
2. **Detects unusual patterns** (sudden spike/drop)
3. **Identifies trends** (this product growing 20% month-over-month)
4. **Suggests actions** (capitalize on trend, investigate drop)
5. **Sends alerts** to operations team

**Example Alerts**:
```
🔥 TRENDING UP: "Symprove Gut Health 4-Week Pack"
   - Sales up 127% vs last month
   - High margin product (55%)
   - ACTION: Increase stock, feature in newsletter

⚠️ SUDDEN DROP: "Nurofen Rapid Relief 20s"
   - Usually #1 seller, down 45% this week
   - Possible stockout at some locations?
   - ACTION: Check inventory across branches

💡 SEASONAL PATTERN: "La Roche Posay Sunscreen"
   - April-July peak season approaching
   - Last year sales grew 340% in this period
   - ACTION: Place advance orders now

🤝 CROSS-SELL OPPORTUNITY:
   - 67% of customers buying "Revive Active" also buy "Symprove"
   - Current display has them in different aisles
   - ACTION: Create combo display, test bundle pricing
```

**Guardrails**:
- Statistical significance testing (avoid false positives from noise)
- Contextual awareness (don't alert on known events like promotions)
- Adjustable thresholds (user sets sensitivity)

---

### 🏆 IDEA #5: Auto-Purchase Order Generator
**Impact**: HIGH | **Feasibility**: MEDIUM | **Differentiation**: HIGH

**The Problem It Solves**:
Creating purchase orders requires:
- Identifying what to order (from inventory analysis)
- Looking up supplier info
- Calculating quantities
- Formatting as Excel/CSV for supplier
- Following up on order status

**What It Does**:
End-to-end purchase order automation:

1. **Intake**: "I need to order pain relief products for Baggot St location"

2. **Agent Analysis**:
   - Filters to pain relief category + Baggot St
   - Calculates stock levels vs velocity
   - Groups by supplier (since you order per supplier)
   - Generates optimal order quantities

3. **Output**: Excel PO ready to send:
   ```
   PURCHASE ORDER - Pharmax
   Date: 2025-11-15
   Location: Baggot St

   SKU       | Product              | Current | Daily | Recommended | Unit Cost | Total
   ---------|----------------------|---------|-------|-------------|-----------|-------
   2371      | Solpadeine 24s       | 12      | 8.3   | 250         | €8.36     | €2,090
   26795     | Nurofen Plus 24s     | 23      | 5.1   | 150         | €10.74    | €1,611
   ...

   TOTAL ORDER VALUE: €15,847.50
   ESTIMATED DAYS COVERAGE: 30 days
   ```

4. **Guardrails**:
   - Maximum order value per supplier without approval: €10,000
   - Flag if order >2x normal order size
   - Verify supplier names against master list
   - Calculate expected delivery date based on lead times

**Advanced Feature - Negotiation Assistant**:
- "Supplier quoted €8.50/unit but historical cost is €8.36"
- "ALERT: 1.7% price increase - negotiate or accept?"
- Tracks price changes over time

---

## Recommended Approach for Hackathon

### 🎯 Best Demo Strategy: **Combine Ideas #1 + #2**

**Why This Combo Wins**:
1. **Complete narrative**: "Your data is messy → We clean it → Now we can optimize inventory"
2. **Clear before/after**: Show the mess, show the fix, show the value
3. **Addresses both challenge points**: Messy data + LLM guardrails
4. **Tangible business impact**: €€€ saved from avoiding stockouts + freeing dead stock capital

### Demo Flow (10 minutes):

**Act 1: The Problem (2 min)**
- Show the messy data (duplicates, negative margins, inconsistent names)
- Show the manual Excel workflow (painful)
- "Operations teams spend 10+ hours/week on this"

**Act 2: Data Quality Guardian (3 min)**
- Run the agent: "Analyzing 1.3M transactions..."
- Output: "Found 156 critical data quality issues"
- Show top 5 issues with evidence + suggested fixes
- User approves → Agent generates clean dataset
- "Unified 1,247 duplicate product records, recovered €12,450 in pricing errors"

**Act 3: Smart Inventory Agent (4 min)**
- Feed cleaned data to inventory agent
- Agent: "Analyzing stock levels across 10 locations for 20,000 products..."
- Output dashboard:
  - 🚨 47 products need urgent reorder (avoid stockouts)
  - 💰 €125,000 locked in slow-moving inventory (markdown candidates)
  - 📊 Auto-generated purchase order for top supplier
- Show the Excel PO ready to send
- "Recommended orders will prevent €50,000 in lost sales from stockouts"

**Act 4: The Vision (1 min)**
- "This is just the beginning - imagine this running automatically every day"
- "Zero manual Excel work, proactive alerts, optimized inventory"
- "From 10 hours/week → 10 minutes/week"

---

## Technical Architecture

### Stack Recommendation:
```
Frontend: Streamlit (fast to build, good for demos)
Backend: Python + FastAPI
LLM: Claude 3.5 Sonnet via Anthropic API
Data: Pandas + DuckDB (for fast SQL on CSVs)
Validation: Pydantic for structured outputs
Orchestration: LangGraph for multi-agent workflows
```

### Key Technical Patterns:

**1. Structured Outputs (Critical for Guardrails)**:
```python
from pydantic import BaseModel, Field, validator

class DataQualityIssue(BaseModel):
    issue_type: Literal["duplicate", "pricing_error", "missing_data", "format_error"]
    severity: Literal["critical", "high", "medium", "low"]
    affected_records: int
    evidence: str
    suggested_fix: str
    confidence: float = Field(ge=0, le=1)

    @validator('confidence')
    def confidence_threshold(cls, v):
        if v < 0.7:
            raise ValueError('Low confidence fixes require human review')
        return v
```

**2. Multi-Step Reasoning with Validation**:
```python
def generate_purchase_order(product_data, inventory_data):
    # Step 1: Calculate metrics
    metrics = agent.calculate_velocity(product_data)

    # Step 2: Validate calculations
    assert metrics['daily_velocity'] >= 0, "Velocity cannot be negative"
    assert metrics['current_stock'] >= 0, "Stock cannot be negative"

    # Step 3: Generate recommendation
    recommendation = agent.recommend_order_qty(metrics)

    # Step 4: Business rule validation
    if recommendation['order_value'] > 10000:
        recommendation['requires_approval'] = True

    # Step 5: Structured output
    return PurchaseOrder(**recommendation)
```

**3. Confidence Scoring**:
```python
def calculate_confidence(historical_data, prediction):
    factors = {
        'data_completeness': len(historical_data) / expected_days,
        'consistency': 1 - cv(historical_data.velocity),  # coefficient of variation
        'recency': exponential_decay(days_since_last_sale),
    }
    return weighted_average(factors)
```

---

## Data Analysis Preview

Based on the exploration notebook, here are some real insights to showcase:

### Real Issues Found:
1. **Duplicate Products**: Hundreds of barcodes with multiple names
2. **Negative Margins**: Transactions losing money
3. **Dead Stock**: Products with >100 days of inventory
4. **Heavy Discounting**: Products discounted >25% off RRP

### Real Opportunities:
1. **Top Products**: Show actual top 20 by revenue + margin
2. **Urgent Reorders**: Real products at <7 days stock
3. **Slow Movers**: Real products with €€€ locked up
4. **Department Performance**: Which categories are most profitable

---

## Judging Criteria Alignment

**1. Innovation & Creativity**:
- ✅ Multi-agent system (data cleaning → analysis → action)
- ✅ Self-configuring approach (learns schema from CSVs)
- ✅ Confidence-scored outputs (novel guardrail approach)

**2. Technical Excellence**:
- ✅ Structured outputs (Pydantic models)
- ✅ Multi-step validation
- ✅ Handles real messy data (not toy examples)

**3. Business Impact**:
- ✅ Quantified value (€€€ saved from stockouts + freed capital)
- ✅ Time savings (10 hours/week → 10 min/week)
- ✅ Addresses real pain points from the example reports

**4. Addressing the Challenge**:
- ✅ Messy data handling (Data Quality Guardian)
- ✅ LLM guardrails (structured outputs, validation, confidence scores)
- ✅ Format consistency (template matching)
- ✅ Uses the actual datasets provided

---

## Next Steps

1. **Run the exploration notebook** to get real numbers
2. **Build Data Quality Guardian agent** first (foundation)
3. **Build Inventory Optimization agent** second (showcase)
4. **Create Streamlit demo UI** for presentation
5. **Practice the narrative** (problem → solution → impact)

Good luck! 🚀
