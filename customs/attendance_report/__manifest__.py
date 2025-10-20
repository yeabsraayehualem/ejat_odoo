{
    "name": "Attendance Report",
    "version": "1.0",
    "category": "Custom",
    "summary": "Custom Attendance Report",
    "description": """
        This module provides a custom attendance report feature.
    """,
    "author": "Jan-Elias",
    "depends": ["hr_attendance", "project"],
    "data": [
        "views/menu.xml",
        "views/attendance_report.xml",
        "views/attendance_report_wizard.xml",
        "security/ir.model.access.csv",
    ],
}