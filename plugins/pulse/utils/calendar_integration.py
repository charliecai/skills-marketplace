"""Calendar integration utility for pulse skill.

Generates .ics files from routine tables in annual plans.
"""

from datetime import datetime
from typing import List, Dict, Optional, Tuple
import re


class RoutineEvent:
    """Represents a single routine event."""

    def __init__(self, name: str, start_time: str, duration: str,
                 frequency: str, kr_ref: str = "", note: str = ""):
        self.name = name
        self.start_time = start_time
        self.duration = duration
        self.frequency = frequency
        self.kr_ref = kr_ref
        self.note = note


def parse_duration(duration_str: str) -> int:
    """Convert duration string to minutes."""
    match = re.search(r'(\d+)', duration_str)
    if not match:
        return 30
    num = int(match.group(1))
    return num * 60 if 'h' in duration_str.lower() else num


def parse_time_slot(time_slot: str) -> Tuple[Optional[str], Optional[str]]:
    """Extract start and end time from time slot string."""
    match = re.match(r'(\d{2}:\d{2})-(\d{2}:\d{2})', time_slot)
    if match:
        return match.group(1), match.group(2)
    match = re.match(r'(\d{2}:\d{2})', time_slot)
    if match:
        return match.group(1), None
    return None, None


def check_time_conflict(events: List[RoutineEvent]) -> List[str]:
    """Check for time conflicts in same-day events."""
    conflicts = []
    daily_events = [e for e in events if e.frequency == "daily"]

    for i, e1 in enumerate(daily_events):
        start1, _ = parse_time_slot(e1.start_time)
        if not start1:
            continue
        start1_time = datetime.strptime(start1, "%H:%M")
        end1_min = start1_time.hour * 60 + start1_time.minute + parse_duration(e1.duration)

        for e2 in daily_events[i+1:]:
            start2, _ = parse_time_slot(e2.start_time)
            if not start2:
                continue
            start2_time = datetime.strptime(start2, "%H:%M")
            start2_min = start2_time.hour * 60 + start2_time.minute

            if start2_min < end1_min:
                conflicts.append(f"Conflict: {e1.name} ({e1.start_time}) and {e2.name} ({e2.start_time})")

    return conflicts


def generate_ics(events: List[RoutineEvent], year: int, timezone: str = "Asia/Shanghai") -> str:
    """Generate .ics file content from routine events."""
    ics_lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//Life Planner//Annual Routines//EN",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        f"X-WR-TIMEZONE:{timezone}",
    ]

    for event in events:
        start_time, _ = parse_time_slot(event.start_time)
        if not start_time:
            continue

        freq_rule = ""
        if event.frequency == "daily":
            freq_rule = "FREQ=DAILY"
        elif event.frequency.startswith("weekly"):
            day = event.frequency.split(":")[1] if ":" in event.frequency else "1"
            weekdays = ["MO", "TU", "WE", "TH", "FR", "SA", "SU"]
            weekday = weekdays[int(day) - 1] if day.isdigit() and 1 <= int(day) <= 7 else "MO"
            freq_rule = f"FREQ=WEEKLY;BYDAY={weekday}"
        elif event.frequency.startswith("monthly"):
            day = event.frequency.split(":")[1] if ":" in event.frequency else "1"
            freq_rule = f"FREQ=MONTHLY;BYMONTHDAY={day}"

        dt_start = f"{year}0101T{start_time.replace(':', '')}00"
        duration_min = parse_duration(event.duration)

        description = f"KR: {event.kr_ref}\\n{event.note}" if event.kr_ref else event.note

        ics_lines.extend([
            "BEGIN:VEVENT",
            f"DTSTART;TZID={timezone}:{dt_start}",
            f"DURATION:PT{duration_min}M",
            f"RRULE:{freq_rule};UNTIL={year}1231T235959Z",
            f"SUMMARY:{event.name}",
            f"DESCRIPTION:{description}",
            "END:VEVENT",
        ])

    ics_lines.append("END:VCALENDAR")
    return "\n".join(ics_lines)


def validate_routines(events: List[RoutineEvent]) -> Dict[str, List[str]]:
    """Run all validation checks on routine events."""
    issues = {
        "conflicts": check_time_conflict(events),
        "invalid_times": [],
        "missing_data": []
    }

    for event in events:
        start_time, _ = parse_time_slot(event.start_time)
        if not start_time:
            issues["invalid_times"].append(f"{event.name}: Invalid time format '{event.start_time}'")

        if not event.name or not event.duration:
            issues["missing_data"].append(f"{event.name or 'Unknown'}: Missing required information")

    return {k: v for k, v in issues.items() if v}
