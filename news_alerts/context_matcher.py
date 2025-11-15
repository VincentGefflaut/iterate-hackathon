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

            # Locations (stores) with coordinates for distance calculation
            "store_locations": [
                {"name": "Baggot St", "lat": 53.3314, "lon": -6.2462},
                {"name": "Grafton St", "lat": 53.3424, "lon": -6.2597},
                {"name": "O'Connell St", "lat": 53.3498, "lon": -6.2603},
                {"name": "Dame St", "lat": 53.3445, "lon": -6.2667},
                {"name": "Capel St", "lat": 53.3475, "lon": -6.2678},
                {"name": "Talbot St", "lat": 53.3505, "lon": -6.2536},
                {"name": "Thomas St", "lat": 53.3428, "lon": -6.2834},
                {"name": "Rathmines", "lat": 53.3238, "lon": -6.2648},
                {"name": "Ranelagh", "lat": 53.3257, "lon": -6.2555},
                {"name": "Ballsbridge", "lat": 53.3327, "lon": -6.2297}
            ],

            # Dublin venue coordinates for proximity calculations
            "dublin_venues": {
                "3arena": {"lat": 53.3486, "lon": -6.2294},
                "croke park": {"lat": 53.3606, "lon": -6.2513},
                "aviva stadium": {"lat": 53.3356, "lon": -6.2284},
                "convention centre": {"lat": 53.3476, "lon": -6.2397},
                "rds": {"lat": 53.3293, "lon": -6.2317},
                "st stephens green": {"lat": 53.3381, "lon": -6.2595},
                "temple bar": {"lat": 53.3456, "lon": -6.2647},
                "trinity college": {"lat": 53.3438, "lon": -6.2546}
            },

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

    @staticmethod
    def _calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Calculate distance between two coordinates using Haversine formula

        Args:
            lat1, lon1: First coordinate
            lat2, lon2: Second coordinate

        Returns:
            Distance in kilometers
        """
        import math

        # Earth's radius in kilometers
        R = 6371.0

        # Convert to radians
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        dlon = math.radians(lon2 - lon1)
        dlat = math.radians(lat2 - lat1)

        # Haversine formula
        a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        distance = R * c
        return distance

    def _find_nearby_stores(self, event_lat: float, event_lon: float, max_distance_km: float = 10.0) -> List[Tuple[str, float]]:
        """
        Find stores within a certain distance of an event location

        Args:
            event_lat, event_lon: Event coordinates
            max_distance_km: Maximum distance in km

        Returns:
            List of tuples (store_name, distance_km) sorted by distance
        """
        nearby_stores = []

        for store in self.config["store_locations"]:
            distance = self._calculate_distance(
                event_lat, event_lon,
                store["lat"], store["lon"]
            )

            if distance <= max_distance_km:
                nearby_stores.append((store["name"], distance))

        # Sort by distance
        nearby_stores.sort(key=lambda x: x[1])

        return nearby_stores

    def _get_venue_coordinates(self, location_text: str) -> Optional[Tuple[float, float]]:
        """
        Try to extract coordinates from location text by matching known venues

        Args:
            location_text: Location description from event

        Returns:
            Tuple of (lat, lon) if found, None otherwise
        """
        if not location_text:
            return None

        location_lower = location_text.lower()

        # Check known venues
        for venue_name, coords in self.config["dublin_venues"].items():
            if venue_name in location_lower:
                return (coords["lat"], coords["lon"])

        return None

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
        elif event.event_type == "weather_extreme":
            alert = self._evaluate_weather_extreme(event)
        elif event.event_type == "supply_disruption":
            alert = self._evaluate_supply_disruption(event)
        elif event.event_type == "viral_trend":
            alert = self._evaluate_viral_trend(event)
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
        """Build enhanced prompt for LLM with historical context and data insights"""

        # Extract key metrics for context
        key_metrics_str = ""
        if alert.decision.key_metrics:
            key_metrics_str = "\n\nDATA INSIGHTS:"
            for key, value in alert.decision.key_metrics.items():
                key_metrics_str += f"\n  • {key}: {value}"

        # Build historical context section
        historical_context = ""
        if self.use_real_data:
            historical_context = "\n\nHISTORICAL CONTEXT:"
            historical_context += "\n  This alert was generated using real sales and inventory data."
            historical_context += "\n  The reasoning above includes actual stock levels, consumption rates, and traffic patterns."
            historical_context += "\n  Use these data points to provide specific, quantitative recommendations."

        # Add confidence level interpretation
        confidence_str = f"\nDecision Confidence: {alert.decision.confidence:.0%}"
        if alert.decision.confidence >= 0.90:
            confidence_str += " (VERY HIGH - backed by real data)"
        elif alert.decision.confidence >= 0.75:
            confidence_str += " (HIGH - strong indicators)"
        elif alert.decision.confidence >= 0.60:
            confidence_str += " (MODERATE - some uncertainty)"
        else:
            confidence_str += " (LOW - requires validation)"

        prompt = f"""You are a business analyst for a retail pharmacy chain in Dublin, Ireland.

A data-driven alert system has generated a business alert based on a detected event. Your job is to translate technical insights into actionable business recommendations.

========================
EVENT DETECTED
========================
Title: {event.title}
Description: {event.description}
Type: {event.event_type}
Severity: {event.severity}
Location: {event.location or 'Not specified'}
Date: {event.event_date or 'Ongoing'}

========================
ALERT DECISION
========================
Alert Type: {alert.alert_type}
Severity: {alert.severity}
Urgency: {alert.urgency}
Affected Categories: {', '.join(alert.affected_categories) if alert.affected_categories else 'All product categories'}
Affected Stores: {', '.join(alert.affected_locations) if alert.affected_locations else 'All stores'}{confidence_str}{key_metrics_str}{historical_context}

========================
DECISION REASONING
========================
{chr(10).join(f"  • {reason}" for reason in alert.decision.reasoning)}

========================
RECOMMENDED ACTIONS
========================
IMMEDIATE (Next 24 hours):
{chr(10).join(f"  {i}. {action}" for i, action in enumerate(alert.immediate_actions, 1)) if alert.immediate_actions else "  None specified"}

SHORT-TERM (Next 2-7 days):
{chr(10).join(f"  {i}. {action}" for i, action in enumerate(alert.short_term_actions, 1)) if alert.short_term_actions else "  None specified"}

========================
YOUR TASK
========================

Provide a comprehensive business analysis with these sections:

1. EXECUTIVE SUMMARY (2-3 sentences):
   Translate the technical alert into a clear business narrative. What's happening, why it matters, and what we should do.

2. FINANCIAL IMPACT:
   - Estimated revenue opportunity or risk (be specific if data provided)
   - Cost of action vs. cost of inaction
   - ROI considerations

3. DETAILED ACTION PLAN:
   For each recommended action, provide:
   - WHAT: Specific products/SKUs to focus on (use category names from above)
   - HOW: Practical execution steps
   - WHO: Specific roles responsible
   - WHEN: Precise timeline
   - WHY: Business rationale

4. RISK ANALYSIS:
   - Primary risks if we don't act (quantify where possible)
   - Secondary risks from acting (overcorrection, opportunity cost)
   - Mitigation strategies
   - Timeline pressure (how fast must we move?)

5. COMPETITIVE INTELLIGENCE:
   - How competitors might respond
   - First-mover advantages
   - Market positioning opportunities

6. CUSTOMER IMPACT:
   - How customers will be affected
   - Messaging guidelines for store staff
   - Service level expectations

7. MANAGER BRIEFING POINTS (5-7 bullets):
   Clear, confident talking points for managers to deliver to their teams.
   Focus on: what's happening, what we're doing, what success looks like.

CONTEXT NOTES:
- You operate 10 retail pharmacy stores across Dublin
- Average transaction value: €12
- Peak traffic times: lunch (12-2pm) and evening (5-7pm)
- 80+ product categories, 18,000+ SKUs
- You compete with Boots, LloydsPharmacy, and independent pharmacies
- Irish customers value personal service and expert advice

Be specific. Use data from the reasoning section. If days of supply is mentioned, use it. If traffic patterns are shown, reference them. Make this analysis tactical and immediately actionable.

Format your response with clear markdown headings (## for sections)."""

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

        # Rule 2: Location proximity with intelligent distance calculations
        affected_locations = []
        if event.location:
            # Try to get coordinates for the event
            event_coords = self._get_venue_coordinates(event.location)

            if event_coords:
                event_lat, event_lon = event_coords
                decision_reasons.append(f"Event location identified: {event.location}")

                # Find nearby stores using distance calculations
                nearby_stores = self._find_nearby_stores(event_lat, event_lon, max_distance_km=5.0)

                if nearby_stores:
                    # Categorize by impact zone
                    high_impact_stores = [name for name, dist in nearby_stores if dist <= self.config["proximity_thresholds"]["high_impact"]]
                    moderate_impact_stores = [name for name, dist in nearby_stores if self.config["proximity_thresholds"]["high_impact"] < dist <= self.config["proximity_thresholds"]["moderate_impact"]]

                    if high_impact_stores:
                        affected_locations = high_impact_stores
                        decision_reasons.append(
                            f"🎯 {len(high_impact_stores)} store(s) within {self.config['proximity_thresholds']['high_impact']}km: {', '.join(high_impact_stores)}"
                        )
                        alert_needed = True
                        confidence += 0.15
                    elif moderate_impact_stores:
                        affected_locations = moderate_impact_stores
                        decision_reasons.append(
                            f"📍 {len(moderate_impact_stores)} store(s) within {self.config['proximity_thresholds']['moderate_impact']}km: {', '.join(moderate_impact_stores)}"
                        )
                        alert_needed = True
                        confidence += 0.10

                    # Add distance details for closest stores
                    for store_name, distance in nearby_stores[:3]:
                        decision_reasons.append(f"  • {store_name}: {distance:.2f}km from event")
                else:
                    decision_reasons.append("No stores within 5km of event location")

            elif "dublin" in event.location.lower():
                # Generic Dublin event - all stores potentially affected
                affected_locations = [store["name"] for store in self.config["store_locations"]]
                decision_reasons.append("Dublin-wide event - all stores may see impact")
                alert_needed = True
                confidence += 0.05

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

    def _evaluate_weather_extreme(self, event: DetectedEvent) -> Optional[BusinessAlert]:
        """
        Evaluate weather extreme event (heatwave, cold snap, flooding, storm)

        Business Rules:
        1. Identify weather type from event description
        2. Map to weather-sensitive product categories
        3. Check seasonal patterns and current stock
        4. (Data-driven): Use actual seasonal sales data and inventory
        """
        decision_reasons = []
        alert_needed = False
        confidence = 0.6

        # Identify weather type
        event_text = f"{event.title} {event.description}".lower()
        weather_type = None

        if any(keyword in event_text for keyword in ["heatwave", "heat", "hot", "temperature soaring"]):
            weather_type = "heatwave"
        elif any(keyword in event_text for keyword in ["cold snap", "freeze", "frost", "arctic"]):
            weather_type = "cold_snap"
        elif any(keyword in event_text for keyword in ["flood", "flooding", "storm", "heavy rain"]):
            weather_type = "flooding"

        if not weather_type:
            decision_reasons.append("Could not identify specific weather type")
            return None

        decision_reasons.append(f"Weather type identified: {weather_type}")

        # Map to categories
        weather_category_map = {
            "heatwave": ["Skincare", "OTC : Allergy", "Nutritional Supplements"],
            "cold_snap": ["OTC : Cold & Flu", "Vitamins"],
            "flooding": ["OTC : First Aid", "Female Toiletries : Hygiene"],
        }

        affected_categories = weather_category_map.get(weather_type, [])

        # DATA-DRIVEN ENHANCEMENT
        if self.use_real_data and self.feature_calculator:
            try:
                features = self.feature_calculator.get_weather_features(
                    weather_type=weather_type,
                    as_of_date=date.today()
                )

                if features and 'category_patterns' in features:
                    for category, pattern in features['category_patterns'].items():
                        decision_reasons.append(
                            f"📊 DATA: {category} current stock = {pattern.get('current_stock', 0):.0f} units"
                        )

                        if 'days_of_supply_peak' in pattern:
                            days_supply = pattern['days_of_supply_peak']
                            decision_reasons.append(
                                f"📊 DATA: Days of supply at seasonal peak = {days_supply:.1f} days"
                            )

                            if days_supply < 7:
                                alert_needed = True
                                confidence = 0.85
                                decision_reasons.append(
                                    f"⚠️  LOW STOCK: Only {days_supply:.1f} days at peak seasonal demand"
                                )
                            elif days_supply < 14:
                                alert_needed = True
                                confidence = 0.75
                                decision_reasons.append(
                                    f"⚠️  MODERATE: {days_supply:.1f} days supply - monitor closely"
                                )

            except Exception as e:
                decision_reasons.append(f"⚠️  Could not load weather features: {e}")

        # Heuristic fallback
        if event.severity in ["high", "critical"]:
            alert_needed = True
            confidence += 0.1
            decision_reasons.append(f"High severity weather event: {event.severity}")

        if not alert_needed:
            return None

        # Create alert
        playbook = get_playbook("weather_extreme", "moderate")
        immediate, short_term, monitoring = convert_playbook_to_actions(playbook)

        decision = AlertDecision(
            alert_needed=alert_needed,
            confidence=min(confidence, 1.0),
            reasoning=decision_reasons,
            key_metrics={
                "weather_type": weather_type,
                "affected_categories": affected_categories,
            }
        )

        severity_level = "high" if event.severity in ["high", "critical"] else "moderate"

        alert = BusinessAlert(
            alert_id=str(uuid.uuid4()),
            generated_at=datetime.now().isoformat(),
            event_id=event.source_url,
            alert_type="weather_extreme",
            severity=severity_level,
            urgency="within_24h" if event.severity == "critical" else "within_week",
            event_title=event.title,
            event_description=event.description,
            event_date=event.event_date,
            event_location=event.location,
            affected_categories=affected_categories,
            affected_locations=[store["name"] for store in self.config["store_locations"]],
            estimated_impact="moderate",
            decision=decision,
            playbook_name=playbook.name,
            immediate_actions=immediate,
            short_term_actions=short_term,
            monitoring_plan=monitoring,
            escalation_criteria=[
                f"Stock levels for {weather_type} products drop below 5 days supply",
                "Customer demand exceeds 150% of seasonal peak",
                "Supplier delivery delays occur"
            ]
        )

        return alert

    def _evaluate_supply_disruption(self, event: DetectedEvent) -> Optional[BusinessAlert]:
        """
        Evaluate supply disruption event (supplier issues, shipping delays, port strikes)

        Business Rules:
        1. Identify affected supplier (if mentioned)
        2. Check supplier criticality
        3. Assess impact on product availability
        4. (Data-driven): Use actual supplier dependency data
        """
        decision_reasons = []
        alert_needed = False
        confidence = 0.6

        # Try to identify supplier
        event_text = f"{event.title} {event.description}".lower()
        affected_supplier = None

        # Check if supplier mentioned in event
        # (In production, would use NER or entity extraction)
        if "supplier" in event_text or "manufacturer" in event_text:
            decision_reasons.append("Supplier-related disruption detected")
            alert_needed = True
            confidence += 0.2

        # DATA-DRIVEN ENHANCEMENT
        if self.use_real_data and self.feature_calculator:
            try:
                features = self.feature_calculator.get_supply_disruption_features(
                    as_of_date=date.today()
                )

                if features and 'supplier_criticality' in features:
                    critical_suppliers = {
                        name: info for name, info in features['supplier_criticality'].items()
                        if info['criticality_rank'] in ['CRITICAL', 'HIGH']
                    }

                    decision_reasons.append(
                        f"📊 DATA: {len(critical_suppliers)} critical/high suppliers identified"
                    )

                    # If event mentions supplier impact
                    if alert_needed:
                        for supplier, info in list(critical_suppliers.items())[:3]:
                            decision_reasons.append(
                                f"  • {supplier}: {info['revenue_dependency']*100:.1f}% revenue dependency"
                            )

                        alert_needed = True
                        confidence = 0.90
                        decision_reasons.append(
                            "🚨 CRITICAL: Supply disruption could affect major suppliers"
                        )

            except Exception as e:
                decision_reasons.append(f"⚠️  Could not load supply disruption features: {e}")

        # Heuristic: High severity supply issues always alert
        if event.severity in ["high", "critical"]:
            alert_needed = True
            confidence += 0.1
            decision_reasons.append(f"High severity supply disruption: {event.severity}")

        if not alert_needed:
            return None

        # Create alert
        playbook = get_playbook("supply_disruption", "critical")
        immediate, short_term, monitoring = convert_playbook_to_actions(playbook)

        decision = AlertDecision(
            alert_needed=alert_needed,
            confidence=min(confidence, 1.0),
            reasoning=decision_reasons,
            key_metrics={
                "event_severity": event.severity,
            }
        )

        alert = BusinessAlert(
            alert_id=str(uuid.uuid4()),
            generated_at=datetime.now().isoformat(),
            event_id=event.source_url,
            alert_type="supply_disruption",
            severity="critical" if event.severity in ["high", "critical"] else "high",
            urgency="immediate",
            event_title=event.title,
            event_description=event.description,
            event_date=event.event_date,
            event_location=event.location,
            affected_categories=[],
            affected_locations=[store["name"] for store in self.config["store_locations"]],
            estimated_impact="high",
            decision=decision,
            playbook_name=playbook.name,
            immediate_actions=immediate,
            short_term_actions=short_term,
            monitoring_plan=monitoring,
            escalation_criteria=[
                "Critical suppliers confirm delayed deliveries",
                "Stock levels for key products drop below 10 days",
                "No alternative suppliers available"
            ]
        )

        return alert

    def _evaluate_viral_trend(self, event: DetectedEvent) -> Optional[BusinessAlert]:
        """
        Evaluate viral trend event (social media buzz, product trending)

        Business Rules:
        1. Identify trending product/category
        2. Check if we stock it
        3. Assess current inventory vs potential spike
        4. (Data-driven): Use product search and stock levels
        """
        decision_reasons = []
        alert_needed = False
        confidence = 0.5

        # Try to identify product keywords from event
        event_text = f"{event.title} {event.description}".lower()
        product_keyword = None

        # Common viral product patterns
        viral_keywords = ["vitamin", "supplement", "skincare", "collagen", "magnesium", "protein"]
        for keyword in viral_keywords:
            if keyword in event_text:
                product_keyword = keyword
                break

        if not product_keyword:
            decision_reasons.append("No specific product identified in viral trend")
            # Try to extract from title
            words = event.title.split()
            if len(words) > 0:
                product_keyword = words[0].lower()
                decision_reasons.append(f"Using keyword from title: {product_keyword}")

        # DATA-DRIVEN ENHANCEMENT
        if self.use_real_data and self.feature_calculator and product_keyword:
            try:
                features = self.feature_calculator.get_viral_trend_features(
                    product_keyword=product_keyword,
                    as_of_date=date.today()
                )

                if features and features.get('found'):
                    product_count = features.get('matching_products_count', 0)
                    decision_reasons.append(
                        f"📊 DATA: Found {product_count} products matching '{product_keyword}'"
                    )

                    for product in features.get('products', [])[:3]:
                        if 'can_capitalize' in product:
                            decision_reasons.append(
                                f"  • {product['product']}: {product.get('current_stock', 0):.0f} units"
                            )
                            decision_reasons.append(
                                f"    Days at 4x spike: {product.get('days_of_supply_at_4x_spike', 0):.1f} days"
                            )

                            if product.get('can_capitalize', False):
                                alert_needed = True
                                confidence = 0.80
                                decision_reasons.append(
                                    "✅ OPPORTUNITY: Sufficient stock to capitalize on viral trend"
                                )
                            else:
                                alert_needed = True
                                confidence = 0.75
                                decision_reasons.append(
                                    "⚠️  LIMITED STOCK: May sell out quickly during viral spike"
                                )
                else:
                    decision_reasons.append(f"No products found matching '{product_keyword}'")
                    return None

            except Exception as e:
                decision_reasons.append(f"⚠️  Could not load viral trend features: {e}")

        # Heuristic: High urgency trends always alert
        if event.urgency == "immediate":
            alert_needed = True
            confidence += 0.1
            decision_reasons.append("Immediate action needed for viral trend")

        if not alert_needed:
            return None

        # Create alert
        playbook = get_playbook("viral_trend", "moderate")
        immediate, short_term, monitoring = convert_playbook_to_actions(playbook)

        decision = AlertDecision(
            alert_needed=alert_needed,
            confidence=min(confidence, 1.0),
            reasoning=decision_reasons,
            key_metrics={
                "product_keyword": product_keyword,
            }
        )

        alert = BusinessAlert(
            alert_id=str(uuid.uuid4()),
            generated_at=datetime.now().isoformat(),
            event_id=event.source_url,
            alert_type="viral_trend",
            severity="moderate",
            urgency="within_24h",
            event_title=event.title,
            event_description=event.description,
            event_date=event.event_date,
            event_location=event.location,
            affected_categories=[],
            affected_locations=[store["name"] for store in self.config["store_locations"]],
            estimated_impact="moderate",
            decision=decision,
            playbook_name=playbook.name,
            immediate_actions=immediate,
            short_term_actions=short_term,
            monitoring_plan=monitoring,
            escalation_criteria=[
                "Product sells out in >50% of stores",
                "Social media mentions increase >500%",
                "Competitor stockouts reported"
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
