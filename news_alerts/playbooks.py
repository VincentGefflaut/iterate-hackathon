"""
Playbook definitions for different alert types.

Each playbook contains actionable steps for responding to detected events.
Based on business rules and best practices for retail pharmacy operations.
"""

from typing import Dict, List
from dataclasses import dataclass


@dataclass
class PlaybookAction:
    """Single action step in a playbook"""
    priority: str  # "immediate", "today", "this_week"
    action: str
    responsible: str  # "pharmacy_manager", "inventory_team", "all_staff"
    estimated_time: str  # e.g., "30 minutes", "2 hours"


@dataclass
class Playbook:
    """Complete playbook for responding to an alert"""
    name: str
    description: str
    actions: List[PlaybookAction]
    monitoring_metrics: List[str]
    success_criteria: List[str]


# Health Emergency Playbooks
HEALTH_EMERGENCY_PLAYBOOK_CRITICAL = Playbook(
    name="Health Emergency - Critical Response",
    description="Immediate response to disease outbreak or health crisis affecting relevant product categories",
    actions=[
        PlaybookAction(
            priority="immediate",
            action="Review current inventory levels for affected OTC categories (Cold & Flu, Analgesics, GIT, etc.)",
            responsible="pharmacy_manager",
            estimated_time="15 minutes"
        ),
        PlaybookAction(
            priority="immediate",
            action="Calculate days-of-supply at elevated demand (2-3x normal)",
            responsible="inventory_team",
            estimated_time="30 minutes"
        ),
        PlaybookAction(
            priority="immediate",
            action="Place emergency orders for products with <7 days supply at elevated demand",
            responsible="inventory_team",
            estimated_time="1 hour"
        ),
        PlaybookAction(
            priority="today",
            action="Contact key suppliers to confirm stock availability and expedited delivery",
            responsible="pharmacy_manager",
            estimated_time="1 hour"
        ),
        PlaybookAction(
            priority="today",
            action="Set up prominent in-store displays for relevant health products",
            responsible="all_staff",
            estimated_time="30 minutes"
        ),
        PlaybookAction(
            priority="today",
            action="Brief staff on symptoms, recommended products, and customer guidance",
            responsible="pharmacy_manager",
            estimated_time="15 minutes"
        ),
        PlaybookAction(
            priority="this_week",
            action="Monitor daily sales trends and adjust orders accordingly",
            responsible="inventory_team",
            estimated_time="ongoing"
        )
    ],
    monitoring_metrics=[
        "Daily sales by affected category",
        "Stock levels (units and days-of-supply)",
        "Supplier delivery times",
        "Customer inquiries/complaints",
        "Stockout incidents"
    ],
    success_criteria=[
        "No stockouts of critical products",
        "Maintained >5 days supply throughout crisis",
        "Positive customer feedback on product availability",
        "Sales captured vs. estimated demand >80%"
    ]
)

HEALTH_EMERGENCY_PLAYBOOK_MODERATE = Playbook(
    name="Health Emergency - Standard Response",
    description="Proactive response to health alerts with adequate current inventory",
    actions=[
        PlaybookAction(
            priority="today",
            action="Review inventory levels for potentially affected categories",
            responsible="inventory_team",
            estimated_time="30 minutes"
        ),
        PlaybookAction(
            priority="today",
            action="Increase next regular order by 25-50% for relevant products",
            responsible="inventory_team",
            estimated_time="30 minutes"
        ),
        PlaybookAction(
            priority="this_week",
            action="Monitor sales trends daily for early warning signs",
            responsible="inventory_team",
            estimated_time="15 minutes daily"
        ),
        PlaybookAction(
            priority="this_week",
            action="Ensure staff awareness of potential increased demand",
            responsible="pharmacy_manager",
            estimated_time="10 minutes"
        )
    ],
    monitoring_metrics=[
        "Daily sales by category",
        "Week-over-week growth rates",
        "Customer inquiries"
    ],
    success_criteria=[
        "Proactive inventory build-up completed",
        "No emergency orders needed",
        "Smooth handling of any demand increase"
    ]
)

# Major Events Playbooks
MAJOR_EVENT_PLAYBOOK_HIGH_IMPACT = Playbook(
    name="Major Event - High Impact Response",
    description="Response to large events near store locations (>10,000 attendance)",
    actions=[
        PlaybookAction(
            priority="today",
            action="Review proximity of event to each store location",
            responsible="pharmacy_manager",
            estimated_time="15 minutes"
        ),
        PlaybookAction(
            priority="today",
            action="Increase inventory for convenience items: analgesics, first aid, travel-size products",
            responsible="inventory_team",
            estimated_time="1 hour"
        ),
        PlaybookAction(
            priority="today",
            action="Ensure adequate staffing for event dates (especially evening/weekend events)",
            responsible="pharmacy_manager",
            estimated_time="30 minutes"
        ),
        PlaybookAction(
            priority="this_week",
            action="Set up promotional displays for event-relevant products (hangover relief, energy, snacks)",
            responsible="all_staff",
            estimated_time="1 hour"
        ),
        PlaybookAction(
            priority="this_week",
            action="Extend opening hours if event is in evening/night",
            responsible="pharmacy_manager",
            estimated_time="planning"
        ),
        PlaybookAction(
            priority="this_week",
            action="Coordinate with security if expecting large crowds",
            responsible="pharmacy_manager",
            estimated_time="30 minutes"
        )
    ],
    monitoring_metrics=[
        "Foot traffic counts",
        "Transaction volume by hour",
        "Sales lift by category",
        "Staff performance under load"
    ],
    success_criteria=[
        "No stockouts during event period",
        "Transaction processing times <5 minutes average",
        "Positive customer experience despite crowds",
        "Sales lift >20% vs. normal day"
    ]
)

MAJOR_EVENT_PLAYBOOK_MODERATE_IMPACT = Playbook(
    name="Major Event - Moderate Impact Response",
    description="Response to medium-sized events or events at moderate distance",
    actions=[
        PlaybookAction(
            priority="this_week",
            action="Slight increase in convenience product inventory (+15-20%)",
            responsible="inventory_team",
            estimated_time="30 minutes"
        ),
        PlaybookAction(
            priority="this_week",
            action="Ensure full staffing for event dates (no call-outs)",
            responsible="pharmacy_manager",
            estimated_time="15 minutes"
        ),
        PlaybookAction(
            priority="this_week",
            action="Monitor foot traffic and be prepared to extend hours if needed",
            responsible="all_staff",
            estimated_time="ongoing"
        )
    ],
    monitoring_metrics=[
        "Foot traffic patterns",
        "Sales vs. baseline"
    ],
    success_criteria=[
        "Maintained stock levels",
        "Adequate staffing coverage",
        "Captured any incremental sales opportunity"
    ]
)


# Playbook mapping
PLAYBOOK_REGISTRY: Dict[str, Dict[str, Playbook]] = {
    "health_emergency": {
        "critical": HEALTH_EMERGENCY_PLAYBOOK_CRITICAL,
        "moderate": HEALTH_EMERGENCY_PLAYBOOK_MODERATE
    },
    "major_event": {
        "high_impact": MAJOR_EVENT_PLAYBOOK_HIGH_IMPACT,
        "moderate_impact": MAJOR_EVENT_PLAYBOOK_MODERATE_IMPACT
    }
}


def get_playbook(event_type: str, severity: str) -> Playbook:
    """
    Get the appropriate playbook for an event

    Args:
        event_type: Type of event (e.g., "health_emergency", "major_event")
        severity: Severity level (e.g., "critical", "moderate", "high_impact")

    Returns:
        Playbook object with actions and guidelines
    """
    event_playbooks = PLAYBOOK_REGISTRY.get(event_type, {})
    playbook = event_playbooks.get(severity)

    if not playbook:
        # Return a generic playbook
        return Playbook(
            name=f"{event_type} - Generic Response",
            description="Generic response playbook - customize based on event specifics",
            actions=[
                PlaybookAction(
                    priority="today",
                    action="Assess potential business impact",
                    responsible="pharmacy_manager",
                    estimated_time="30 minutes"
                ),
                PlaybookAction(
                    priority="today",
                    action="Monitor relevant metrics daily",
                    responsible="inventory_team",
                    estimated_time="15 minutes daily"
                )
            ],
            monitoring_metrics=["Sales trends", "Inventory levels"],
            success_criteria=["Proactive monitoring established"]
        )

    return playbook
