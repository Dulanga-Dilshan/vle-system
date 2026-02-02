SETTINGS_SCHEMA = {
    # -------- System --------
    "SYSTEM_NAME": {
        "default": "UOV VLE",
        "type": "str",
        "rules": {
            "min_length": 1,
            "max_length": 50,
            "strip": True,
        },
    },
    "SYSTEM_TAGLINE": {
        "default": "",
        "type": "str",
        "rules": {
            "max_length": 120,
            "allow_empty": True,
            "strip": True,
        },
    },
    "SYSTEM_LOGO_URL": {
        "default": "",
        "type": "str",
        "rules": {
            "format": "url",
            "max_length": 500,
            "allow_empty": True,
        },
    },

    # -------- Pagination --------
    "USERS_PER_PAGE": {
        "default": 50,
        "type": "int",
        "rules": {
            "min": 5,
            "max": 500,
        },
    },

    # -------- Maintenance --------
    "MAINTENANCE_MODE": {
        "default": False,
        "type": "bool",
        "rules": {},
    },
    "MAINTENANCE_MESSAGE": {
        "default": "System is under maintenance. Try again later.",
        "type": "str",
        "rules": {
            "max_length": 300,
            "strip": True,
        },
    },
    "MAINTENANCE_ALLOWED_ROLES": {
        "default": ["admin"],
        "type": "list",
        "rules": {
            "item_type": "str",
            "choices": ["admin", "staff", "lecturer"],
            "unique_items": True,
            "min_items": 0,
            "max_items": 10,
        },
    },

    # -------- Uploads --------
    "MAX_UPLOAD_MB": {
        "default": 10,
        "type": "int",
        "rules": {
            "min": 1,
            "max": 200,
        },
    },
    "ALLOWED_FILE_EXTENSIONS": {
        "default": ".pdf,.doc,.docx,.jpg,.jpeg,.png",
        "type": "str",
        "rules": {
            "format": "csv_extensions",
            "max_length": 300,
        },
    },
    "BLOCK_EXECUTABLE_UPLOADS": {
        "default": True,
        "type": "bool",
        "rules": {},
    },

    # -------- Email --------
    "EMAIL_ENABLED": {
        "default": False,
        "type": "bool",
        "rules": {},
    },
    "EMAIL_PROVIDER": {
        "default": "none",
        "type": "str",
        "rules": {
            "choices": ["none", "smtp", "sendgrid", "mailgun", "ses"],
        },
    },
    "EMAIL_FROM_NAME": {
        "default": "UOV VLE",
        "type": "str",
        "rules": {
            "max_length": 60,
            "strip": True,
        },
    },
    "EMAIL_FROM_ADDRESS": {
        "default": "noreply@university.edu",
        "type": "str",
        "rules": {
            "format": "email",
            "max_length": 254,
        },
    },
    "EMAIL_REPLY_TO": {
        "default": "",
        "type": "str",
        "rules": {
            "format": "email",
            "allow_empty": True,
            "max_length": 254,
        },
    },
    "EMAIL_FOOTER_TEXT": {
        "default": "",
        "type": "str",
        "rules": {
            "max_length": 500,
            "allow_empty": True,
        },
    },

    # -------- Security --------
    "PASSWORD_RESET_ENABLED": {
        "default": False,
        "type": "bool",
        "rules": {},
    },
    "RESET_TOKEN_EXPIRY_MIN": {
        "default": 30,
        "type": "int",
        "rules": {
            "min": 5,
            "max": 1440,
        },
    },
    "RESET_LINK_BASE_URL": {
        "default": "",
        "type": "str",
        "rules": {
            "format": "url",
            "allow_empty": True,
            "max_length": 500,
        },
    },
    "FORCE_PASSWORD_CHANGE_ON_FIRST_LOGIN": {
        "default": True,
        "type": "bool",
        "rules": {},
    },

    "INACTIVITY_LOGOUT_TIME":{
        "default":21600, #6 HOURS
        "type":'int',
        "rules": {
            "min": 3600, #1 hour
            "max": 2592000,#30 day
        },
    },

    "SESSION_EXPIRE":{
        "default":172800,#2 days
        "type":'int',
        "rules": {
            "min": 86400,# day
            "max": 7776000,#3 months
        },
    },

    "ALLOW_REGISTRATION": {
        "default": True,
        "type": "bool",
        "rules": {},
    },

    "CONTACT_EMAIL": {
        "default": "contact@university.edu",
        "type": "str",
        "rules": {
            "min_length": 5,
            "max_length": 254,
            "format": "email",
        },
    },


    
}

TYPE_MAP = {
    "str": str,
    "int": int,
    "bool": bool,
    "float": float,
    "list": list,
    "dict": dict,
}
