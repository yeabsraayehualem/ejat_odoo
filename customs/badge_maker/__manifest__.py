{
    "name":"Badge Maker",
    "version":"1.0",
    "category":"Human Resources",
    "summary":"Badge Maker",
    "description":"Badge Maker",
    "author":"Jan Elias",
    "depends":["base","hr"],
    "data":[
        "views/hr_employee.xml",
        "views/badge_report.xml",
    ],
    "assets":{
        "web.assets_backend": [
            "badge_maker/static/css/badge.css",
            "badge_maker/static/img/idfront.png",
            "badge_maker/static/img/idback.png",
        ],
    },
    "installable":True,
    "application":True,
}