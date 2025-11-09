{
    "name":"EJAT Attendance Endpoint",
    "version":"1.0",
    "author":"JAN-Elias",
    "depends":['hr','project','hr_attendance','hr_holidays'],
    'data':[
        "security/ir.model.access.csv",
        "views/project_wizard.xml",
        "views/hr_attendance.xml",
        "views/hr_leave.xml",
    ],
    "application":True
}