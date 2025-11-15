"""
Event storage system for detected events.

Stores events as JSON files organized by date.
"""

import json
import os
from datetime import date, datetime
from pathlib import Path
from typing import List, Optional
from .models import DetectedEvent, DailyEventReport, EventDetectionResult


class EventStorage:
    """Manages storage and retrieval of detected events"""

    def __init__(self, storage_dir: str = "data/events"):
        """
        Initialize event storage

        Args:
            storage_dir: Directory to store event JSON files
        """
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    def save_event(self, event: DetectedEvent, event_date: Optional[date] = None):
        """
        Save a single detected event

        Args:
            event: DetectedEvent to save
            event_date: Date to associate with event (default: today)
        """
        if event_date is None:
            event_date = date.today()

        # Load existing events for this date
        existing_events = self.load_events(event_date)

        # Check for duplicates (same URL)
        if not any(e.source_url == event.source_url for e in existing_events):
            existing_events.append(event)

            # Save back
            self._save_events_list(existing_events, event_date)

    def load_events(self, event_date: date) -> List[DetectedEvent]:
        """
        Load all events for a specific date

        Args:
            event_date: Date to load events for

        Returns:
            List of DetectedEvent objects
        """
        file_path = self._get_events_file_path(event_date)

        if not file_path.exists():
            return []

        with open(file_path, 'r') as f:
            data = json.load(f)

        # Parse events
        events = []
        for event_data in data.get("events", []):
            try:
                events.append(DetectedEvent(**event_data))
            except Exception as e:
                print(f"Error parsing event: {e}")

        return events

    def save_daily_report(self, report: DailyEventReport, report_date: Optional[date] = None):
        """
        Save a complete daily report

        Args:
            report: DailyEventReport to save
            report_date: Date for the report (default: today)
        """
        if report_date is None:
            report_date = date.today()

        file_path = self._get_report_file_path(report_date)

        with open(file_path, 'w') as f:
            json.dump(report.model_dump(), f, indent=2)

    def load_daily_report(self, report_date: date) -> Optional[DailyEventReport]:
        """
        Load daily report for a specific date

        Args:
            report_date: Date to load report for

        Returns:
            DailyEventReport or None if not found
        """
        file_path = self._get_report_file_path(report_date)

        if not file_path.exists():
            return None

        with open(file_path, 'r') as f:
            data = json.load(f)

        return DailyEventReport(**data)

    def get_recent_events(self, days: int = 7, event_type: Optional[str] = None) -> List[DetectedEvent]:
        """
        Get events from recent days

        Args:
            days: Number of days to look back
            event_type: Optional filter by event type

        Returns:
            List of DetectedEvent objects
        """
        all_events = []

        for i in range(days):
            event_date = date.today() - timedelta(days=i)
            events = self.load_events(event_date)

            if event_type:
                events = [e for e in events if e.event_type == event_type]

            all_events.extend(events)

        return all_events

    def get_storage_stats(self) -> dict:
        """
        Get statistics about stored events

        Returns:
            Dictionary with storage statistics
        """
        event_files = list(self.storage_dir.glob("events_*.json"))
        report_files = list(self.storage_dir.glob("report_*.json"))

        total_events = 0
        for file in event_files:
            with open(file, 'r') as f:
                data = json.load(f)
                total_events += len(data.get("events", []))

        return {
            "total_event_files": len(event_files),
            "total_report_files": len(report_files),
            "total_events": total_events,
            "storage_dir": str(self.storage_dir),
            "latest_date": self._get_latest_date()
        }

    def _save_events_list(self, events: List[DetectedEvent], event_date: date):
        """Save list of events to file"""
        file_path = self._get_events_file_path(event_date)

        data = {
            "date": event_date.isoformat(),
            "total_events": len(events),
            "events": [event.model_dump() for event in events]
        }

        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)

    def _get_events_file_path(self, event_date: date) -> Path:
        """Get file path for events on a specific date"""
        filename = f"events_{event_date.isoformat()}.json"
        return self.storage_dir / filename

    def _get_report_file_path(self, report_date: date) -> Path:
        """Get file path for daily report"""
        filename = f"report_{report_date.isoformat()}.json"
        return self.storage_dir / filename

    def _get_latest_date(self) -> Optional[str]:
        """Get the latest date with stored events"""
        event_files = sorted(self.storage_dir.glob("events_*.json"), reverse=True)
        if event_files:
            # Extract date from filename
            filename = event_files[0].name
            return filename.replace("events_", "").replace(".json", "")
        return None

    def print_stats(self):
        """Print storage statistics"""
        stats = self.get_storage_stats()

        print("=" * 60)
        print("Event Storage Statistics")
        print("=" * 60)
        print(f"Storage directory: {stats['storage_dir']}")
        print(f"Event files: {stats['total_event_files']}")
        print(f"Report files: {stats['total_report_files']}")
        print(f"Total events: {stats['total_events']}")
        print(f"Latest date: {stats['latest_date'] or 'None'}")
        print("=" * 60)

    def export_to_csv(self, output_file: str, days: int = 30):
        """
        Export events to CSV for analysis

        Args:
            output_file: Output CSV file path
            days: Number of days to include
        """
        import csv
        from datetime import timedelta

        events = self.get_recent_events(days=days)

        if not events:
            print("No events to export")
            return

        with open(output_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=[
                'date', 'event_type', 'title', 'severity', 'confidence',
                'urgency', 'location', 'event_date', 'source_url', 'published_at'
            ])

            writer.writeheader()

            for event in events:
                writer.writerow({
                    'date': event.published_at,
                    'event_type': event.event_type,
                    'title': event.title,
                    'severity': event.severity,
                    'confidence': event.confidence,
                    'urgency': event.urgency,
                    'location': event.location or '',
                    'event_date': event.event_date or '',
                    'source_url': event.source_url,
                    'published_at': event.published_at
                })

        print(f"Exported {len(events)} events to {output_file}")


# Example usage
if __name__ == "__main__":
    from datetime import timedelta

    storage = EventStorage()
    storage.print_stats()
