"""Mock School Analytics API for Principal / Management queries."""

from typing import Dict, Any, List


class MockAnalyticsService:
    """Mock school-wide analytics service."""

    def get_school_attendance_summary(self) -> Dict[str, Any]:
        return {
            "overall_attendance_pct": 92.4,
            "total_students": 450,
            "present_today": 416,
            "absent_today": 34,
            "by_class": [
                {"class_name": "Class 10-A", "attendance_pct": 94.2, "present": 28, "total": 30},
                {"class_name": "Class 10-B", "attendance_pct": 90.0, "present": 27, "total": 30},
                {"class_name": "Class 9-A", "attendance_pct": 93.3, "present": 28, "total": 30},
                {"class_name": "Class 9-B", "attendance_pct": 91.5, "present": 27, "total": 30},
            ],
            "flagged_students": [
                {"student_id": "S002", "name": "Priya Sharma", "class": "10-A", "attendance_pct": 74.5, "reason": "Consecutive 3-day absence"},
                {"student_id": "S007", "name": "Vikas Rao", "class": "9-B", "attendance_pct": 68.0, "reason": "Low monthly aggregate"}
            ]
        }


analytics_service = MockAnalyticsService()
