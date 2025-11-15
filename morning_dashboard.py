#!/usr/bin/env python3
"""
Morning Dashboard Generator

Generates a beautiful, animated HTML dashboard showing business alerts.
Designed to run every morning and display the latest alerts.

Usage:
    python morning_dashboard.py                    # Show today's alerts
    python morning_dashboard.py --days 7           # Show last 7 days
    python morning_dashboard.py --auto-open        # Auto-open in browser
    python morning_dashboard.py --watch            # Auto-refresh mode
"""

import json
import argparse
from pathlib import Path
from datetime import datetime, timedelta, date
from typing import List, Dict, Any
from collections import Counter
import webbrowser


class MorningDashboard:
    """Generates beautiful HTML dashboard for business alerts"""

    def __init__(self, alerts_dir: Path = None):
        self.alerts_dir = alerts_dir or Path("data/alerts")

    def load_alerts(self, days: int = 1) -> List[Dict[str, Any]]:
        """Load alerts from the last N days"""
        cutoff_date = datetime.now() - timedelta(days=days)
        alerts = []

        if not self.alerts_dir.exists():
            return alerts

        for alert_file in sorted(self.alerts_dir.glob("alert_*.json")):
            try:
                with open(alert_file, 'r', encoding='utf-8') as f:
                    alert = json.load(f)

                # Parse generated_at timestamp
                generated_at = datetime.fromisoformat(alert.get("generated_at", ""))

                if generated_at >= cutoff_date:
                    alerts.append(alert)
            except Exception as e:
                print(f"⚠️  Error loading {alert_file.name}: {e}")

        # Sort by generated_at descending (newest first)
        alerts.sort(key=lambda x: x.get("generated_at", ""), reverse=True)
        return alerts

    def generate_html(self, alerts: List[Dict[str, Any]], auto_refresh: bool = False) -> str:
        """Generate beautiful HTML dashboard"""

        # Calculate statistics
        total_alerts = len(alerts)
        critical_count = sum(1 for a in alerts if a.get("severity") == "critical")
        high_count = sum(1 for a in alerts if a.get("severity") == "high")
        moderate_count = sum(1 for a in alerts if a.get("severity") == "moderate")

        event_types = Counter(a.get("alert_type", "unknown") for a in alerts)
        avg_confidence = sum(a.get("decision", {}).get("confidence", 0) for a in alerts) / total_alerts if total_alerts > 0 else 0

        # Get unique locations
        locations = set()
        for alert in alerts:
            locations.update(alert.get("decision", {}).get("affected_locations", []))

        # Generate alert cards HTML
        alert_cards_html = self._generate_alert_cards(alerts)

        # Auto-refresh meta tag
        refresh_meta = '<meta http-equiv="refresh" content="300">' if auto_refresh else ''

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Morning Alerts Dashboard - {datetime.now().strftime('%B %d, %Y')}</title>
    {refresh_meta}
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        :root {{
            --bg-primary: #0f172a;
            --bg-secondary: #1e293b;
            --bg-card: #334155;
            --text-primary: #f1f5f9;
            --text-secondary: #cbd5e1;
            --text-muted: #94a3b8;
            --accent: #3b82f6;
            --critical: #ef4444;
            --high: #f97316;
            --moderate: #3b82f6;
            --low: #10b981;
            --border: #475569;
            --shadow: rgba(0, 0, 0, 0.3);
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: linear-gradient(135deg, var(--bg-primary) 0%, #1a2332 100%);
            color: var(--text-primary);
            min-height: 100vh;
            padding: 2rem;
            line-height: 1.6;
        }}

        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}

        /* Header */
        .header {{
            text-align: center;
            margin-bottom: 3rem;
            animation: fadeInDown 0.6s ease-out;
        }}

        .header h1 {{
            font-size: 3rem;
            font-weight: 700;
            background: linear-gradient(135deg, #60a5fa 0%, #a78bfa 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.5rem;
        }}

        .header .subtitle {{
            color: var(--text-secondary);
            font-size: 1.2rem;
        }}

        .header .date {{
            color: var(--text-muted);
            font-size: 1rem;
            margin-top: 0.5rem;
        }}

        /* Statistics Grid */
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1.5rem;
            margin-bottom: 3rem;
            animation: fadeInUp 0.6s ease-out 0.2s both;
        }}

        .stat-card {{
            background: var(--bg-card);
            border-radius: 1rem;
            padding: 1.5rem;
            border: 1px solid var(--border);
            box-shadow: 0 4px 6px var(--shadow);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }}

        .stat-card:hover {{
            transform: translateY(-4px);
            box-shadow: 0 8px 12px var(--shadow);
        }}

        .stat-card .label {{
            color: var(--text-muted);
            font-size: 0.875rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 0.5rem;
        }}

        .stat-card .value {{
            font-size: 2.5rem;
            font-weight: 700;
            color: var(--text-primary);
        }}

        .stat-card .subtext {{
            color: var(--text-secondary);
            font-size: 0.875rem;
            margin-top: 0.5rem;
        }}

        .stat-card.critical .value {{ color: var(--critical); }}
        .stat-card.high .value {{ color: var(--high); }}
        .stat-card.moderate .value {{ color: var(--moderate); }}
        .stat-card.success .value {{ color: var(--low); }}

        /* Alert Cards */
        .alerts-section {{
            margin-bottom: 3rem;
        }}

        .section-title {{
            font-size: 1.5rem;
            font-weight: 600;
            margin-bottom: 1.5rem;
            color: var(--text-primary);
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}

        .section-title::before {{
            content: '';
            width: 4px;
            height: 1.5rem;
            background: var(--accent);
            border-radius: 2px;
        }}

        .alert-card {{
            background: var(--bg-card);
            border-radius: 1rem;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
            border-left: 4px solid var(--accent);
            box-shadow: 0 4px 6px var(--shadow);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            animation: slideInLeft 0.6s ease-out both;
        }}

        .alert-card:nth-child(1) {{ animation-delay: 0.1s; }}
        .alert-card:nth-child(2) {{ animation-delay: 0.2s; }}
        .alert-card:nth-child(3) {{ animation-delay: 0.3s; }}
        .alert-card:nth-child(4) {{ animation-delay: 0.4s; }}
        .alert-card:nth-child(5) {{ animation-delay: 0.5s; }}

        .alert-card:hover {{
            transform: translateX(8px);
            box-shadow: 0 8px 12px var(--shadow);
        }}

        .alert-card.critical {{ border-left-color: var(--critical); }}
        .alert-card.high {{ border-left-color: var(--high); }}
        .alert-card.moderate {{ border-left-color: var(--moderate); }}
        .alert-card.low {{ border-left-color: var(--low); }}

        .alert-header {{
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 1rem;
            gap: 1rem;
        }}

        .alert-title {{
            font-size: 1.25rem;
            font-weight: 600;
            color: var(--text-primary);
            flex: 1;
        }}

        .alert-badges {{
            display: flex;
            gap: 0.5rem;
            flex-wrap: wrap;
        }}

        .badge {{
            padding: 0.25rem 0.75rem;
            border-radius: 9999px;
            font-size: 0.75rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}

        .badge.critical {{
            background: rgba(239, 68, 68, 0.2);
            color: var(--critical);
            border: 1px solid var(--critical);
        }}

        .badge.high {{
            background: rgba(249, 115, 22, 0.2);
            color: var(--high);
            border: 1px solid var(--high);
        }}

        .badge.moderate {{
            background: rgba(59, 130, 246, 0.2);
            color: var(--moderate);
            border: 1px solid var(--moderate);
        }}

        .badge.low {{
            background: rgba(16, 185, 129, 0.2);
            color: var(--low);
            border: 1px solid var(--low);
        }}

        .alert-meta {{
            display: flex;
            gap: 1.5rem;
            flex-wrap: wrap;
            color: var(--text-muted);
            font-size: 0.875rem;
            margin-bottom: 1rem;
        }}

        .alert-meta-item {{
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}

        .alert-description {{
            color: var(--text-secondary);
            margin-bottom: 1rem;
            line-height: 1.6;
        }}

        .alert-categories {{
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
            margin-bottom: 1rem;
        }}

        .category-tag {{
            background: var(--bg-secondary);
            color: var(--text-secondary);
            padding: 0.25rem 0.75rem;
            border-radius: 0.5rem;
            font-size: 0.875rem;
            border: 1px solid var(--border);
        }}

        .alert-locations {{
            color: var(--text-secondary);
            font-size: 0.875rem;
        }}

        .confidence-bar {{
            margin-top: 1rem;
            padding-top: 1rem;
            border-top: 1px solid var(--border);
        }}

        .confidence-label {{
            color: var(--text-muted);
            font-size: 0.875rem;
            margin-bottom: 0.5rem;
        }}

        .confidence-progress {{
            height: 8px;
            background: var(--bg-secondary);
            border-radius: 9999px;
            overflow: hidden;
        }}

        .confidence-fill {{
            height: 100%;
            background: linear-gradient(90deg, var(--accent), var(--low));
            border-radius: 9999px;
            transition: width 1s ease-out;
        }}

        /* Empty State */
        .empty-state {{
            text-align: center;
            padding: 4rem 2rem;
            color: var(--text-muted);
        }}

        .empty-state-icon {{
            font-size: 4rem;
            margin-bottom: 1rem;
            opacity: 0.5;
        }}

        .empty-state-text {{
            font-size: 1.25rem;
        }}

        /* Animations */
        @keyframes fadeInDown {{
            from {{
                opacity: 0;
                transform: translateY(-20px);
            }}
            to {{
                opacity: 1;
                transform: translateY(0);
            }}
        }}

        @keyframes fadeInUp {{
            from {{
                opacity: 0;
                transform: translateY(20px);
            }}
            to {{
                opacity: 1;
                transform: translateY(0);
            }}
        }}

        @keyframes slideInLeft {{
            from {{
                opacity: 0;
                transform: translateX(-30px);
            }}
            to {{
                opacity: 1;
                transform: translateX(0);
            }}
        }}

        /* Responsive */
        @media (max-width: 768px) {{
            body {{
                padding: 1rem;
            }}

            .header h1 {{
                font-size: 2rem;
            }}

            .stats-grid {{
                grid-template-columns: 1fr;
            }}

            .alert-header {{
                flex-direction: column;
            }}

            .alert-meta {{
                flex-direction: column;
                gap: 0.5rem;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <div class="header">
            <h1>🌅 Morning Alerts Dashboard</h1>
            <div class="subtitle">Your Daily Business Intelligence Briefing</div>
            <div class="date">{datetime.now().strftime('%A, %B %d, %Y at %H:%M')}</div>
        </div>

        <!-- Statistics -->
        <div class="stats-grid">
            <div class="stat-card">
                <div class="label">Total Alerts</div>
                <div class="value">{total_alerts}</div>
                <div class="subtext">Last 24 hours</div>
            </div>

            <div class="stat-card critical">
                <div class="label">Critical</div>
                <div class="value">{critical_count}</div>
                <div class="subtext">Immediate action required</div>
            </div>

            <div class="stat-card high">
                <div class="label">High Priority</div>
                <div class="value">{high_count}</div>
                <div class="subtext">Review today</div>
            </div>

            <div class="stat-card moderate">
                <div class="label">Moderate</div>
                <div class="value">{moderate_count}</div>
                <div class="subtext">Monitor closely</div>
            </div>

            <div class="stat-card success">
                <div class="label">Confidence</div>
                <div class="value">{avg_confidence:.0%}</div>
                <div class="subtext">Average decision confidence</div>
            </div>

            <div class="stat-card">
                <div class="label">Locations</div>
                <div class="value">{len(locations)}</div>
                <div class="subtext">Stores affected</div>
            </div>
        </div>

        <!-- Alerts Section -->
        <div class="alerts-section">
            <h2 class="section-title">Recent Alerts</h2>
            {alert_cards_html}
        </div>
    </div>

    <script>
        // Animate confidence bars on load
        document.addEventListener('DOMContentLoaded', function() {{
            const bars = document.querySelectorAll('.confidence-fill');
            bars.forEach(bar => {{
                const width = bar.style.width;
                bar.style.width = '0%';
                setTimeout(() => {{
                    bar.style.width = width;
                }}, 100);
            }});
        }});
    </script>
</body>
</html>"""

        return html

    def _generate_alert_cards(self, alerts: List[Dict[str, Any]]) -> str:
        """Generate HTML for alert cards"""
        if not alerts:
            return """
            <div class="empty-state">
                <div class="empty-state-icon">✨</div>
                <div class="empty-state-text">No alerts in the selected time period</div>
            </div>
            """

        cards_html = []

        for alert in alerts:
            severity = alert.get("severity", "low")
            alert_type = alert.get("alert_type", "unknown")
            title = alert.get("title", "Untitled Alert")
            description = alert.get("description", "")

            # Parse timestamp
            generated_at = alert.get("generated_at", "")
            try:
                dt = datetime.fromisoformat(generated_at)
                time_str = dt.strftime('%H:%M')
                date_str = dt.strftime('%b %d')
            except:
                time_str = "Unknown"
                date_str = ""

            # Get confidence
            confidence = alert.get("decision", {}).get("confidence", 0)
            confidence_pct = int(confidence * 100)

            # Get categories
            categories = alert.get("decision", {}).get("affected_categories", [])
            categories_html = ''.join([
                f'<span class="category-tag">{cat}</span>'
                for cat in categories[:5]  # Limit to 5
            ])
            if len(categories) > 5:
                categories_html += f'<span class="category-tag">+{len(categories) - 5} more</span>'

            # Get locations
            locations = alert.get("decision", {}).get("affected_locations", [])
            locations_str = ', '.join(locations[:3])
            if len(locations) > 3:
                locations_str += f' +{len(locations) - 3} more'

            # Event type emoji
            event_emoji = {
                "health_emergency": "🏥",
                "major_event": "🎉",
                "weather_extreme": "⛈️",
                "supply_disruption": "📦",
                "viral_trend": "📱"
            }.get(alert_type, "📢")

            card_html = f"""
            <div class="alert-card {severity}">
                <div class="alert-header">
                    <div class="alert-title">{event_emoji} {title}</div>
                    <div class="alert-badges">
                        <span class="badge {severity}">{severity}</span>
                    </div>
                </div>

                <div class="alert-meta">
                    <div class="alert-meta-item">
                        <span>🕐</span>
                        <span>{time_str}</span>
                    </div>
                    <div class="alert-meta-item">
                        <span>📅</span>
                        <span>{date_str}</span>
                    </div>
                    <div class="alert-meta-item">
                        <span>🏷️</span>
                        <span>{alert_type.replace('_', ' ').title()}</span>
                    </div>
                </div>

                <div class="alert-description">{description[:200]}{'...' if len(description) > 200 else ''}</div>

                {f'<div class="alert-categories">{categories_html}</div>' if categories else ''}

                {f'<div class="alert-locations">📍 Affected Stores: {locations_str}</div>' if locations else ''}

                <div class="confidence-bar">
                    <div class="confidence-label">Decision Confidence: {confidence_pct}%</div>
                    <div class="confidence-progress">
                        <div class="confidence-fill" style="width: {confidence_pct}%"></div>
                    </div>
                </div>
            </div>
            """

            cards_html.append(card_html)

        return '\n'.join(cards_html)

    def generate_and_save(self, output_file: Path, days: int = 1, auto_refresh: bool = False):
        """Generate dashboard and save to file"""
        alerts = self.load_alerts(days=days)
        html = self.generate_html(alerts, auto_refresh=auto_refresh)

        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html)

        return output_file, len(alerts)


def main():
    parser = argparse.ArgumentParser(
        description="Generate beautiful morning alerts dashboard",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python morning_dashboard.py                    # Today's alerts
  python morning_dashboard.py --days 7           # Last 7 days
  python morning_dashboard.py --auto-open        # Auto-open in browser
  python morning_dashboard.py --watch            # Auto-refresh every 5 min
  python morning_dashboard.py --output custom.html
        """
    )

    parser.add_argument(
        '--days',
        type=int,
        default=1,
        help='Number of days to include (default: 1)'
    )

    parser.add_argument(
        '--output',
        type=Path,
        default=Path('data/dashboard/morning_alerts.html'),
        help='Output HTML file path'
    )

    parser.add_argument(
        '--auto-open',
        action='store_true',
        help='Automatically open dashboard in browser'
    )

    parser.add_argument(
        '--watch',
        action='store_true',
        help='Enable auto-refresh every 5 minutes'
    )

    args = parser.parse_args()

    print("╔" + "="*78 + "╗")
    print("║" + " "*20 + "MORNING ALERTS DASHBOARD GENERATOR" + " "*24 + "║")
    print("╚" + "="*78 + "╝")
    print()

    dashboard = MorningDashboard()

    print(f"📊 Loading alerts from last {args.days} day(s)...")
    output_file, alert_count = dashboard.generate_and_save(
        output_file=args.output,
        days=args.days,
        auto_refresh=args.watch
    )

    print(f"✅ Dashboard generated: {output_file}")
    print(f"📈 Total alerts displayed: {alert_count}")

    if args.watch:
        print("🔄 Auto-refresh enabled (updates every 5 minutes)")

    if args.auto_open:
        print(f"🌐 Opening dashboard in browser...")
        webbrowser.open(f'file://{output_file.absolute()}')
    else:
        print(f"\n💡 To view the dashboard, open:")
        print(f"   file://{output_file.absolute()}")
        print(f"\n   Or run with --auto-open flag")

    print()


if __name__ == "__main__":
    main()
