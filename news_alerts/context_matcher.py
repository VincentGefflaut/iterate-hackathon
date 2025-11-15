"""
Context Matcher - Matches detected events against business context to generate alerts.

This is Agent 2 in the two-agent architecture:
- Agent 1 (Event Detector): Extracts facts from news → DetectedEvent
- Agent 2 (Context Matcher): Matches events to business → BusinessAlert

Uses business rules for binary YES/NO decisions, with optional LLM enhancements for:
- Natural language explanations
- Business impact analysis
- Enhanced recommendations
- Manager talking points
"""

import os
import anthropic
import pandas as pd
from datetime import date, datetime
from typing import List, Optional, Dict, Any, Tuple
from pathlib import Path
import uuid

# Load environment variables
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent.parent / '.env'
    load_dotenv(dotenv_path=env_path)
except ImportError:
    pass

from .models import DetectedEvent
from .alert_models import BusinessAlert, AlertDecision, convert_playbook_to_actions
from .playbooks import get_playbook
from .event_storage import EventStorage

# Import alert_features for data-driven matching
try:
    from alert_features import AlertFeatureCalculator
    ALERT_FEATURES_AVAILABLE = True
except ImportError:
    ALERT_FEATURES_AVAILABLE = False
    print("Warning: alert_features package not available. Data-driven matching disabled.")


class ContextMatcher:
    """
    Matches detected events against business context

    Uses business rules to determine if an alert is needed and which actions to take.
    """

    def __init__(self, use_real_data: bool = False, enhance_with_llm: bool = True):
        """
        Initialize context matcher

        Args:
            use_real_data: If True, attempt to load real inventory/sales data from alert_features
                          If False, use heuristic-based decisions
            enhance_with_llm: If True, use LLM to generate rich explanations and recommendations
                             If False, use only rule-based logic (faster, cheaper)
        """
        self.use_real_data = use_real_data
        self.enhance_with_llm = enhance_with_llm
        self.storage = EventStorage()

        # Initialize data-driven components
        self.feature_calculator = None
        self.sales_df = None
        self.inventory_df = None

        if self.use_real_data:
            self._load_business_data()

        # Initialize LLM client if enhancements enabled
        if self.enhance_with_llm:
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if api_key:
                self.llm_client = anthropic.Anthropic(api_key=api_key)
                self.llm_model = os.getenv("CLAUDE_MODEL") or "claude-sonnet-4-5-20250929"
            else:
                print("Warning: ANTHROPIC_API_KEY not set. LLM enhancements disabled.")
                self.enhance_with_llm = False

        # Business configuration (would come from database/config in production)
        self.config = {
            # Product categories relevant to health emergencies
            "health_emergency_categories": [
                "OTC : Cold & Flu",
                "OTC : Analgesics",
                "OTC : GIT",
                "OTC : First Aid",
                "Hand Sanitizer",
                "Masks & PPE"
            ],

            # Locations (stores)
            "store_locations": [
                {"name": "Baggot St", "lat": 53.3314, "lon": -6.2462},
                {"name": "Grafton St", "lat": 53.3424, "lon": -6.2597},
                {"name": "O'Connell St", "lat": 53.3498, "lon": -6.2603}
            ],

            # Distance thresholds (km)
            "proximity_thresholds": {
                "high_impact": 1.0,  # Within 1km
                "moderate_impact": 3.0,  # Within 3km
                "low_impact": 10.0  # Within 10km
            },

            # Attendance thresholds for events
            "event_attendance_thresholds": {
                "high_impact": 10000,
                "moderate_impact": 5000,
                "low_impact": 1000
            },

            # Severity mapping for health emergencies
            "health_severity_mapping": {
                "critical": ["critical", "high"],
                "moderate": ["medium", "moderate", "low"]
            }
        }

    def _load_business_data(self):
        """
        Load sales and inventory data for data-driven matching

        Attempts to load:
        - Retail sales data (for historical patterns, consumption rates)
        - Inventory snapshot (for current stock levels)

        If data files not found, falls back to heuristic mode.
        """
        if not ALERT_FEATURES_AVAILABLE:
            print("⚠️  alert_features package not available. Install with: pip install -e .")
            print("   Falling back to heuristic-based matching.")
            self.use_real_data = False
            return

        try:
            print("Loading business data for data-driven matching...")

            # Define data paths
            base_path = Path(__file__).parent.parent
            sales_file = base_path / "data" / "input" / "Retail" / "retail_sales_data_01_09_2023_to_31_10_2025.csv"
            inventory_file = base_path / "data" / "input" / "Retail" / "retail_inventory_snapshot_30_10_25.csv"

            # Check if files exist
            if not sales_file.exists():
                print(f"⚠️  Sales data not found: {sales_file}")
                print("   Place your sales CSV in: data/input/Retail/retail_sales_data_*.csv")
                print("   Falling back to heuristic-based matching.")
                self.use_real_data = False
                return

            if not inventory_file.exists():
                print(f"⚠️  Inventory data not found: {inventory_file}")
                print("   Place your inventory CSV in: data/input/Retail/retail_inventory_snapshot_*.csv")
                print("   Falling back to heuristic-based matching.")
                self.use_real_data = False
                return

            # Load sales data
            print(f"  Loading sales data from {sales_file.name}...")
            self.sales_df = pd.read_csv(sales_file, encoding='utf-8-sig', low_memory=False)
            print(f"  ✓ Loaded {len(self.sales_df):,} sales records")

            # Load inventory data
            print(f"  Loading inventory data from {inventory_file.name}...")
            self.inventory_df = pd.read_csv(inventory_file, encoding='utf-8-sig', low_memory=False)
            print(f"  ✓ Loaded {len(self.inventory_df):,} inventory records")

            # Create AlertFeatureCalculator
            self.feature_calculator = AlertFeatureCalculator(self.sales_df, self.inventory_df)
            print("  ✓ AlertFeatureCalculator initialized")
            print("✅ Data-driven matching enabled\n")

        except Exception as e:
            print(f"⚠️  Error loading business data: {e}")
            print("   Falling back to heuristic-based matching.")
            self.use_real_data = False
            self.feature_calculator = None
            self.sales_df = None
            self.inventory_df = None

    def evaluate_events(self, target_date: Optional[date] = None) -> List[BusinessAlert]:
        """
        Evaluate all detected events for a given date and generate alerts

        Args:
            target_date: Date to evaluate events for (default: today)

        Returns:
            List of BusinessAlert objects
        """
        if target_date is None:
            target_date = date.today()

        # Load detected events
        events = self.storage.load_events(target_date)

        if not events:
            print(f"No events found for {target_date.isoformat()}")
            return []

        print(f"Evaluating {len(events)} detected events...")

        alerts = []
        for event in events:
            alert = self.evaluate_single_event(event)
            if alert:
                alerts.append(alert)

        return alerts

    def evaluate_single_event(self, event: DetectedEvent) -> Optional[BusinessAlert]:
        """
        Evaluate a single detected event and determine if alert is needed

        Args:
            event: DetectedEvent to evaluate

        Returns:
            BusinessAlert if alert needed, None otherwise
        """
        # Route to appropriate matcher based on event type
        if event.event_type == "health_emergency":
            alert = self._evaluate_health_emergency(event)
        elif event.event_type == "major_event":
            alert = self._evaluate_major_event(event)
        else:
            # For other event types, create basic alert
            alert = self._evaluate_generic_event(event)

        # Enhance with LLM if enabled and alert was generated
        if alert and self.enhance_with_llm:
            alert = self._enhance_alert_with_llm(alert, event)

        return alert

    def _enhance_alert_with_llm(self, alert: BusinessAlert, event: DetectedEvent) -> BusinessAlert:
        """
        Enhance an alert with LLM-generated explanations and insights

        Args:
            alert: BusinessAlert from rule-based logic
            event: Original DetectedEvent

        Returns:
            Enhanced BusinessAlert with LLM-generated content
        """
        try:
            # Build prompt with alert context
            prompt = self._build_enhancement_prompt(alert, event)

            # Call LLM
            response = self.llm_client.messages.create(
                model=self.llm_model,
                max_tokens=2000,
                temperature=0.3,  # Low temp for consistent, factual responses
                messages=[{"role": "user", "content": prompt}]
            )

            # Extract text response
            llm_response = ""
            for block in response.content:
                if hasattr(block, 'text'):
                    llm_response += block.text

            # Parse LLM response and enhance alert
            enhanced_alert = self._parse_llm_enhancements(alert, llm_response)

            return enhanced_alert

        except Exception as e:
            print(f"Warning: LLM enhancement failed: {e}")
            print("Returning original rule-based alert")
            return alert

    def _build_enhancement_prompt(self, alert: BusinessAlert, event: DetectedEvent) -> str:
        """Build prompt for LLM to enhance alert"""

        prompt = f"""You are a business analyst for a retail pharmacy chain in Dublin, Ireland.

A rule-based system has generated a business alert based on a detected event. Your job is to:
1. Provide a clear, natural language explanation of the business impact
2. Enhance the action recommendations with specific, practical details
3. Identify additional considerations and risks
4. Provide talking points for managers to brief their teams

EVENT DETECTED:
Title: {event.title}
Description: {event.description}
Type: {event.event_type}
Severity: {event.severity}
Location: {event.location or 'Not specified'}
Date: {event.event_date or 'Ongoing'}

RULE-BASED DECISION:
Alert Type: {alert.alert_type}
Severity: {alert.severity}
Urgency: {alert.urgency}
Affected Categories: {', '.join(alert.affected_categories) if alert.affected_categories else 'None'}
Affected Stores: {', '.join(alert.affected_locations) if alert.affected_locations else 'All stores'}

Decision Reasoning:
{chr(10).join(f"  • {reason}" for reason in alert.decision.reasoning)}

Current Recommended Actions:
IMMEDIATE:
{chr(10).join(f"  {i}. {action}" for i, action in enumerate(alert.immediate_actions, 1)) if alert.immediate_actions else "  None"}

SHORT-TERM:
{chr(10).join(f"  {i}. {action}" for i, action in enumerate(alert.short_term_actions, 1)) if alert.short_term_actions else "  None"}

Please provide:

1. BUSINESS IMPACT SUMMARY (2-3 sentences):
   A clear, jargon-free explanation of what this means for our business. Focus on customer needs, sales implications, and operational challenges.

2. ENHANCED ACTIONS (be specific and practical):
   - For each recommended action, add practical details like:
     * Which specific products to focus on
     * How to prioritize (what to do first)
     * Tips for execution
   - Suggest 1-2 additional actions if warranted

3. RISK ASSESSMENT:
   - What could go wrong if we don't act?
   - What are the upside opportunities?
   - Timeline considerations (how quickly must we act?)

4. MANAGER TALKING POINTS (3-5 bullet points):
   Key messages to communicate to store teams, phrased for verbal delivery.

Be specific to Dublin/Ireland market. Focus on actionable insights. Keep language professional but accessible.

Format your response with clear headings for each section."""

        return prompt

    def _parse_llm_enhancements(self, alert: BusinessAlert, llm_response: str) -> BusinessAlert:
        """
        Parse LLM response and add enhancements to alert

        For now, we'll add the LLM response as additional context
        Future: Could parse structured sections
        """
        # Store LLM insights in the alert
        # We can add this to the decision reasoning or create new fields

        # Add to decision reasoning
        alert.decision.reasoning.insert(0, "=== LLM Business Analysis ===")
        alert.decision.reasoning.insert(1, llm_response)

        return alert

    def _evaluate_health_emergency(self, event: DetectedEvent) -> Optional[BusinessAlert]:
        """
        Evaluate health emergency event

        Business Rules:
        1. Check if we stock relevant products (OTC health products)
        2. Assess severity based on event details
        3. Determine if inventory action needed
        4. (Data-driven): Check actual inventory levels and consumption rates
        """
        # Decision logic
        decision_reasons = []
        alert_needed = False
        confidence = 0.7  # Base confidence

        # Rule 1: Check product relevance (keyword matching)
        affected_categories = []
        for category in self.config["health_emergency_categories"]:
            # Check if event mentions relevant keywords
            event_text = f"{event.title} {event.description}".lower()

            if any(keyword in event_text for keyword in ["flu", "cold", "virus", "respiratory"]):
                if "cold" in category.lower() or "flu" in category.lower():
                    affected_categories.append(category)

            if any(keyword in event_text for keyword in ["pain", "fever", "headache"]):
                if "analgesic" in category.lower():
                    affected_categories.append(category)

            if any(keyword in event_text for keyword in ["stomach", "nausea", "vomit", "diarrhea", "norovirus"]):
                if "git" in category.lower():
                    affected_categories.append(category)

            if any(keyword in event_text for keyword in ["sanitizer", "hygiene", "wash"]):
                if "sanitizer" in category.lower():
                    affected_categories.append(category)

        if affected_categories:
            decision_reasons.append(f"We stock relevant products: {', '.join(affected_categories)}")
            alert_needed = True
            confidence += 0.1
        else:
            decision_reasons.append("No directly relevant product categories identified")
            return None  # No alert if we don't stock relevant products

        # DATA-DRIVEN ENHANCEMENT: Check actual inventory levels
        if self.use_real_data and self.feature_calculator:
            try:
                # Use the first affected category for detailed analysis
                primary_category = affected_categories[0]
                as_of_date = date.today()

                # Get health emergency features
                features = self.feature_calculator.get_health_emergency_features(
                    category=primary_category,
                    as_of_date=as_of_date
                )

                if features:
                    # Check inventory health
                    if 'inventory_health' in features:
                        inv_health = features['inventory_health']

                        # Critical decision point: Days of supply during outbreak
                        if inv_health.get('days_of_supply_outbreak'):
                            days_supply = inv_health['days_of_supply_outbreak']

                            decision_reasons.append(
                                f"📊 DATA: Current stock = {inv_health.get('total_current_stock', 0):.0f} units"
                            )
                            decision_reasons.append(
                                f"📊 DATA: Days of supply at outbreak rate (4.5x normal) = {days_supply:.1f} days"
                            )

                            # CRITICAL ALERT: Less than 5 days of outbreak supply
                            if days_supply < 5:
                                alert_needed = True
                                confidence = 0.95  # Very high confidence with real data
                                decision_reasons.append(
                                    f"🚨 CRITICAL: Only {days_supply:.1f} days of supply at outbreak consumption rate!"
                                )

                            # HIGH ALERT: 5-10 days
                            elif days_supply < 10:
                                alert_needed = True
                                confidence = 0.85
                                decision_reasons.append(
                                    f"⚠️  HIGH: {days_supply:.1f} days of supply - should restock soon"
                                )

                            # MODERATE ALERT: 10-20 days
                            elif days_supply < 20:
                                decision_reasons.append(
                                    f"✓ Adequate stock: {days_supply:.1f} days of supply at outbreak rate"
                                )
                            else:
                                decision_reasons.append(
                                    f"✓ Strong stock position: {days_supply:.1f} days of supply"
                                )

                        # Normal supply info
                        if inv_health.get('days_of_supply_normal'):
                            decision_reasons.append(
                                f"📊 DATA: Days of supply at normal rate = {inv_health['days_of_supply_normal']:.1f} days"
                            )

                    # Add consumption data
                    decision_reasons.append(
                        f"📊 DATA: Normal daily consumption = {features.get('daily_avg_units', 0):.1f} units/day"
                    )
                    decision_reasons.append(
                        f"📊 DATA: Outbreak estimated consumption = {features.get('outbreak_estimated_peak_units', 0):.1f} units/day"
                    )

            except Exception as e:
                decision_reasons.append(f"⚠️  Could not load data features: {e}")
                # Continue with heuristic-based decision

        # Rule 2: Assess severity
        severity_level = "moderate"
        playbook_severity = "moderate"

        if event.severity in ["high", "critical"]:
            severity_level = "critical"
            playbook_severity = "critical"
            decision_reasons.append(f"High severity event: {event.severity}")
            confidence += 0.1
            alert_needed = True
        else:
            decision_reasons.append(f"Moderate severity event: {event.severity}")

        # Rule 3: Assess urgency
        urgency = "within_24h"
        if event.urgency == "immediate":
            urgency = "immediate"
            decision_reasons.append("Immediate response required")
            confidence += 0.1
        elif event.urgency == "within_week":
            urgency = "within_week"

        # Rule 4: Location check (Ireland-focused)
        affected_locations = []
        if event.location:
            if "dublin" in event.location.lower() or "ireland" in event.location.lower():
                affected_locations = [store["name"] for store in self.config["store_locations"]]
                decision_reasons.append(f"Event in our market area: {event.location}")
                confidence += 0.1
            else:
                decision_reasons.append(f"Event outside primary market: {event.location}")
                confidence -= 0.1

        # Final decision
        if not alert_needed:
            return None

        # Create alert
        playbook = get_playbook("health_emergency", playbook_severity)
        immediate, short_term, monitoring = convert_playbook_to_actions(playbook)

        decision = AlertDecision(
            alert_needed=alert_needed,
            confidence=min(confidence, 1.0),
            reasoning=decision_reasons,
            key_metrics={
                "affected_categories": affected_categories,
                "event_severity": event.severity,
                "event_urgency": event.urgency
            }
        )

        alert = BusinessAlert(
            alert_id=str(uuid.uuid4()),
            generated_at=datetime.now().isoformat(),
            event_id=event.source_url,  # Using URL as event ID
            alert_type="health_emergency",
            severity=severity_level,
            urgency=urgency,
            event_title=event.title,
            event_description=event.description,
            event_date=event.event_date,
            event_location=event.location,
            affected_categories=affected_categories,
            affected_locations=affected_locations,
            estimated_impact="high" if severity_level == "critical" else "moderate",
            decision=decision,
            playbook_name=playbook.name,
            immediate_actions=immediate,
            short_term_actions=short_term,
            monitoring_plan=monitoring,
            escalation_criteria=[
                "Stockouts occur in any critical category",
                "Sales spike >200% vs baseline",
                "Supplier delivery delays >2 days"
            ]
        )

        return alert

    def _evaluate_major_event(self, event: DetectedEvent) -> Optional[BusinessAlert]:
        """
        Evaluate major event (concert, festival, conference, etc.)

        Business Rules:
        1. Check proximity to our stores
        2. Assess expected attendance
        3. Determine staffing and inventory needs
        """
        decision_reasons = []
        alert_needed = False
        confidence = 0.7

        # Rule 1: Assess attendance
        attendance = event.expected_attendance or 0
        impact_level = "low"
        playbook_severity = "moderate_impact"

        if attendance >= self.config["event_attendance_thresholds"]["high_impact"]:
            impact_level = "high"
            playbook_severity = "high_impact"
            decision_reasons.append(f"Large event: {attendance:,} expected attendees")
            alert_needed = True
            confidence += 0.15
        elif attendance >= self.config["event_attendance_thresholds"]["moderate_impact"]:
            impact_level = "moderate"
            playbook_severity = "moderate_impact"
            decision_reasons.append(f"Medium event: {attendance:,} expected attendees")
            alert_needed = True
            confidence += 0.1
        else:
            decision_reasons.append(f"Small event: {attendance:,} expected attendees")

        # Rule 2: Location proximity (simplified - would use real geocoding in production)
        affected_locations = []
        if event.location:
            location_lower = event.location.lower()

            # Check for specific Dublin venues
            high_traffic_venues = ["3arena", "croke park", "aviva stadium", "convention centre", "rds"]

            if any(venue in location_lower for venue in high_traffic_venues):
                decision_reasons.append(f"Major venue: {event.location}")
                alert_needed = True
                confidence += 0.1

                # Map to nearby stores (simplified)
                if "3arena" in location_lower or "north wall" in location_lower:
                    affected_locations = ["O'Connell St"]
                elif "grafton" in location_lower or "temple bar" in location_lower:
                    affected_locations = ["Grafton St"]
                else:
                    affected_locations = [store["name"] for store in self.config["store_locations"]]

        if not affected_locations and "dublin" in (event.location or "").lower():
            # General Dublin event - all stores potentially affected
            affected_locations = [store["name"] for store in self.config["store_locations"]]
            decision_reasons.append("Dublin-wide event - all stores may see impact")

        # DATA-DRIVEN ENHANCEMENT: Check location traffic and inventory
        if self.use_real_data and self.feature_calculator and affected_locations:
            try:
                # Analyze first affected location
                primary_location = affected_locations[0]
                as_of_date = date.today()

                # Get major event features
                features = self.feature_calculator.get_major_event_features(
                    location=primary_location,
                    as_of_date=as_of_date
                )

                if features:
                    # Traffic baseline data
                    avg_transactions = features.get('avg_transactions_per_day', 0)
                    peak_traffic = features.get('peak_day_traffic', 0)

                    decision_reasons.append(
                        f"📊 DATA: {primary_location} avg daily transactions = {avg_transactions:.0f}"
                    )
                    decision_reasons.append(
                        f"📊 DATA: Historical peak traffic = {peak_traffic:.0f} transactions/day"
                    )

                    # Event impact estimate (historical 80% lift)
                    if 'historical_event_lift' in features:
                        lift = features['historical_event_lift']
                        estimated_traffic = avg_transactions * lift
                        decision_reasons.append(
                            f"📊 DATA: Estimated event traffic = {estimated_traffic:.0f} transactions ({lift:.1%} lift)"
                        )

                        # Alert if event expected to exceed peak capacity
                        if estimated_traffic > peak_traffic:
                            alert_needed = True
                            confidence = 0.90
                            decision_reasons.append(
                                f"🚨 ALERT: Estimated traffic exceeds historical peak by {((estimated_traffic/peak_traffic - 1) * 100):.0f}%"
                            )

                    # Inventory status for event-relevant categories
                    if 'inventory_status' in features:
                        inv_status = features['inventory_status']
                        if inv_status:
                            decision_reasons.append(f"📊 DATA: Event-relevant inventory checked for {len(inv_status)} categories")
                            for cat, details in list(inv_status.items())[:3]:  # Show top 3
                                decision_reasons.append(
                                    f"  • {cat}: {details.get('stock_units', 0):.0f} units in stock"
                                )

            except Exception as e:
                decision_reasons.append(f"⚠️  Could not load major event features: {e}")
                # Continue with heuristic-based decision

        # Rule 3: Urgency based on event date
        urgency = "within_week"
        if event.event_date:
            # Parse event date (simplified)
            try:
                # Assume format is YYYY-MM-DD or contains date
                from datetime import datetime
                # For now, default to within_week
                urgency = "within_week"
                decision_reasons.append(f"Event scheduled for: {event.event_date}")
            except:
                pass

        if not alert_needed:
            return None

        # Create alert
        playbook = get_playbook("major_event", playbook_severity)
        immediate, short_term, monitoring = convert_playbook_to_actions(playbook)

        decision = AlertDecision(
            alert_needed=alert_needed,
            confidence=min(confidence, 1.0),
            reasoning=decision_reasons,
            key_metrics={
                "expected_attendance": attendance,
                "event_location": event.location,
                "impact_level": impact_level
            }
        )

        severity_level = "high" if impact_level == "high" else "moderate"

        alert = BusinessAlert(
            alert_id=str(uuid.uuid4()),
            generated_at=datetime.now().isoformat(),
            event_id=event.source_url,
            alert_type="major_event",
            severity=severity_level,
            urgency=urgency,
            event_title=event.title,
            event_description=event.description,
            event_date=event.event_date,
            event_location=event.location,
            affected_categories=["OTC : Analgesics", "OTC : First Aid", "Convenience Items"],
            affected_locations=affected_locations,
            estimated_impact=impact_level,
            decision=decision,
            playbook_name=playbook.name,
            immediate_actions=immediate,
            short_term_actions=short_term,
            monitoring_plan=monitoring,
            escalation_criteria=[
                "Foot traffic exceeds capacity",
                "Transaction processing times >10 minutes",
                "Stockouts of key convenience items"
            ]
        )

        return alert

    def _evaluate_generic_event(self, event: DetectedEvent) -> Optional[BusinessAlert]:
        """
        Generic evaluation for other event types

        Creates a low-priority monitoring alert
        """
        # For now, just create awareness alert for other event types
        decision = AlertDecision(
            alert_needed=True,
            confidence=0.5,
            reasoning=[
                f"Event type '{event.event_type}' detected",
                "Creating monitoring alert for awareness"
            ],
            key_metrics={"event_type": event.event_type}
        )

        playbook = get_playbook(event.event_type, "moderate")
        immediate, short_term, monitoring = convert_playbook_to_actions(playbook)

        alert = BusinessAlert(
            alert_id=str(uuid.uuid4()),
            generated_at=datetime.now().isoformat(),
            event_id=event.source_url,
            alert_type=event.event_type,
            severity="low",
            urgency="within_week",
            event_title=event.title,
            event_description=event.description,
            event_date=event.event_date,
            event_location=event.location,
            affected_categories=[],
            affected_locations=[],
            estimated_impact="low",
            decision=decision,
            playbook_name=playbook.name,
            immediate_actions=immediate,
            short_term_actions=short_term,
            monitoring_plan=monitoring
        )

        return alert
