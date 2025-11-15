"""
Alert models for Context Matcher output.

These represent actionable business alerts generated from detected events
matched against business context.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from .playbooks import Playbook, PlaybookAction


class AlertDecision(BaseModel):
    """Binary YES/NO decision on whether to generate an alert"""

    alert_needed: bool
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence in decision (0-1)")
    reasoning: List[str] = Field(default_factory=list, description="Business logic reasoning steps")

    # Business metrics that informed the decision
    key_metrics: Dict[str, Any] = Field(default_factory=dict)


class BusinessAlert(BaseModel):
    """Complete business alert with recommended actions"""

    # Alert metadata
    alert_id: str
    generated_at: str
    event_id: str  # Links back to detected event

    # Alert classification
    alert_type: str  # "health_emergency", "major_event", etc.
    severity: str  # "critical", "high", "moderate", "low"
    urgency: str  # "immediate", "within_24h", "within_week"

    # Event details
    event_title: str
    event_description: str
    event_date: Optional[str] = None
    event_location: Optional[str] = None

    # Business impact assessment
    affected_categories: List[str] = Field(default_factory=list)
    affected_locations: List[str] = Field(default_factory=list)
    estimated_impact: str  # "high", "moderate", "low"

    # Decision rationale
    decision: AlertDecision

    # Recommended actions (from playbook)
    playbook_name: str
    immediate_actions: List[str] = Field(default_factory=list)
    short_term_actions: List[str] = Field(default_factory=list)
    monitoring_plan: List[str] = Field(default_factory=list)

    # Business context (snapshot of relevant data)
    current_inventory: Optional[Dict[str, Any]] = None
    recent_sales_trends: Optional[Dict[str, Any]] = None
    supply_chain_status: Optional[Dict[str, Any]] = None

    # Follow-up
    review_date: Optional[str] = None
    escalation_criteria: List[str] = Field(default_factory=list)


class DailyAlertReport(BaseModel):
    """Daily summary of all alerts generated"""

    report_date: str
    total_events_evaluated: int
    alerts_generated: int
    alerts_by_severity: Dict[str, int] = Field(default_factory=dict)
    alerts_by_type: Dict[str, int] = Field(default_factory=dict)

    alerts: List[BusinessAlert]

    summary: str
    recommended_priorities: List[str] = Field(default_factory=list)


def convert_playbook_to_actions(playbook: Playbook) -> tuple:
    """
    Convert a Playbook object to action lists for BusinessAlert

    Returns:
        (immediate_actions, short_term_actions, monitoring_plan)
    """
    immediate = []
    short_term = []
    monitoring = playbook.monitoring_metrics.copy()

    for action in playbook.actions:
        action_text = f"{action.action} (Est. time: {action.estimated_time}, Owner: {action.responsible})"

        if action.priority == "immediate":
            immediate.append(action_text)
        elif action.priority in ["today", "this_week"]:
            short_term.append(action_text)

    return immediate, short_term, monitoring


def format_alert_for_display(alert: BusinessAlert) -> str:
    """Format alert for human-readable display"""

    lines = []
    lines.append("=" * 80)
    lines.append(f"ALERT: {alert.event_title}")
    lines.append("=" * 80)
    lines.append(f"Type: {alert.alert_type.upper()} | Severity: {alert.severity.upper()} | Urgency: {alert.urgency}")
    lines.append(f"Generated: {alert.generated_at}")
    lines.append("")

    lines.append("EVENT DETAILS:")
    lines.append(f"  {alert.event_description}")
    if alert.event_location:
        lines.append(f"  Location: {alert.event_location}")
    if alert.event_date:
        lines.append(f"  Date: {alert.event_date}")
    lines.append("")

    lines.append("BUSINESS IMPACT:")
    lines.append(f"  Estimated Impact: {alert.estimated_impact.upper()}")
    if alert.affected_categories:
        lines.append(f"  Affected Categories: {', '.join(alert.affected_categories)}")
    if alert.affected_locations:
        lines.append(f"  Affected Locations: {', '.join(alert.affected_locations)}")
    lines.append("")

    lines.append("DECISION RATIONALE:")
    for reason in alert.decision.reasoning:
        lines.append(f"  • {reason}")
    lines.append(f"  Confidence: {alert.decision.confidence:.0%}")
    lines.append("")

    if alert.immediate_actions:
        lines.append("IMMEDIATE ACTIONS:")
        for i, action in enumerate(alert.immediate_actions, 1):
            lines.append(f"  {i}. {action}")
        lines.append("")

    if alert.short_term_actions:
        lines.append("SHORT-TERM ACTIONS:")
        for i, action in enumerate(alert.short_term_actions, 1):
            lines.append(f"  {i}. {action}")
        lines.append("")

    if alert.monitoring_plan:
        lines.append("MONITORING PLAN:")
        for metric in alert.monitoring_plan:
            lines.append(f"  • {metric}")
        lines.append("")

    lines.append(f"Playbook: {alert.playbook_name}")
    lines.append(f"Alert ID: {alert.alert_id}")
    lines.append("=" * 80)

    return "\n".join(lines)


def format_daily_report(report: DailyAlertReport) -> str:
    """Format daily alert report for human-readable display"""

    lines = []
    lines.append("=" * 80)
    lines.append(f"DAILY ALERT REPORT - {report.report_date}")
    lines.append("=" * 80)
    lines.append("")

    lines.append("SUMMARY:")
    lines.append(f"  Events Evaluated: {report.total_events_evaluated}")
    lines.append(f"  Alerts Generated: {report.alerts_generated}")
    lines.append("")

    if report.alerts_by_severity:
        lines.append("Alerts by Severity:")
        for severity, count in sorted(report.alerts_by_severity.items()):
            lines.append(f"  {severity}: {count}")
        lines.append("")

    if report.alerts_by_type:
        lines.append("Alerts by Type:")
        for alert_type, count in sorted(report.alerts_by_type.items()):
            lines.append(f"  {alert_type}: {count}")
        lines.append("")

    lines.append(report.summary)
    lines.append("")

    if report.recommended_priorities:
        lines.append("RECOMMENDED PRIORITIES:")
        for i, priority in enumerate(report.recommended_priorities, 1):
            lines.append(f"  {i}. {priority}")
        lines.append("")

    lines.append("=" * 80)
    lines.append("")

    # List each alert briefly
    if report.alerts:
        lines.append("ALERTS:")
        lines.append("")
        for alert in report.alerts:
            lines.append(f"  [{alert.severity.upper()}] {alert.event_title}")
            lines.append(f"    Type: {alert.alert_type} | Urgency: {alert.urgency}")
            lines.append(f"    Impact: {alert.estimated_impact} | ID: {alert.alert_id}")
            lines.append("")

    return "\n".join(lines)
