app_name = "clp"
app_title = "Customer Loyality Program"
app_publisher = "Aman Boora"
app_description = "Customer loyality program"
app_email = "800raaman@gmail.com"
app_license = "mit"

# Apps
# ------------------

# required_apps = []

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "clp",
# 		"logo": "/assets/clp/logo.png",
# 		"title": "Customer Loyality Program",
# 		"route": "/clp",
# 		"has_permission": "clp.api.permission.has_app_permission"
# 	}
# ]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
app_include_css = [
    "/assets/clp/css/clp_theme.css",
    "/assets/clp/css/clp_premium_petroleum.css"
]
app_include_js = "/assets/clp/js/clp.js"

# include js, css files in header of web template
web_include_css = [
    "/assets/clp/css/clp_theme.css",
    "/assets/clp/css/clp_premium_petroleum.css"
]
# web_include_js = "/assets/clp/js/clp.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "clp/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}
fixtures = [
    # 1. Custom Roles
    {
        "doctype": "Role",
        "filters": {
            "name": ["in", ["Pump Owner", "CLM Incharge", "Pump Manager", "CLP Stock Add", "CLP Stock Subtract", "CLP Stock Transfer", "CLP Reports Viewer", "CLP Referral Manager"]]
        }
    },

    # 2. Custom Fields in CLP module
    {
        "doctype": "Custom Field",
        "filters": {"module": "Customer Loyality Program"}
    },

    # 3. Permissions for our roles
    # ... other fixtures ...
    
    # DocPerm - ALL permissions for custom roles
    {
        "doctype": "DocPerm",
        "filters": {
            "parent": ["in", ["Bin", "UOM", "Stock Entry", "Warehouse", "Item"]],
            "role": ["in", ["Pump Owner", "CLM Incharge", "Pump Manager"]]
        }
    },



    
    # ... other fixtures ...


    # 4. Number Cards (from your workspace)
    {
        "doctype": "Number Card",
        "filters": {
            "name": ["in", [
                "Total Gifts Distributed",
                "Total Liters Sold", 
                "Total Active Customers",
                "Total Fuel Purchases"
            ]]
        }
    },

    # 5. Dashboard Charts (from your workspace)
    {
        "doctype": "Dashboard Chart",
        "filters": {
            "name": ["in", [
                "Customer Registrations",
                "Gift Redemptions", 
                "Fuel Purchases Count"
            ]]
        }
    },

    # 6. Workspace (CLP)
    {
        "doctype": "Workspace",
        "filters": {"name": "CLP"}
    },

    # 7. Reports (from your workspace shortcuts)
    {
        "doctype": "Report",
        "filters": {
            "name": ["in", [
                "Customer Loyalty Dashboard",
                "Gift Redemption Summary", 
                "Pump-wise Gift Stock"
            ]]
        }
    }
]


# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "clp/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "clp.utils.jinja_methods",
# 	"filters": "clp.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "clp.install.before_install"
# after_install = "clp.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "clp.uninstall.before_uninstall"
# after_uninstall = "clp.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "clp.utils.before_app_install"
# after_app_install = "clp.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "clp.utils.before_app_uninstall"
# after_app_uninstall = "clp.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "clp.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
# 	}
# }

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"clp.tasks.all"
# 	],
# 	"daily": [
# 		"clp.tasks.daily"
# 	],
# 	"hourly": [
# 		"clp.tasks.hourly"
# 	],
# 	"weekly": [
# 		"clp.tasks.weekly"
# 	],
# 	"monthly": [
# 		"clp.tasks.monthly"
# 	],
# }

# Testing
# -------

# At the end of hooks.py, add:



# before_tests = "clp.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "clp.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "clp.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["clp.utils.before_request"]
# after_request = ["clp.utils.after_request"]

# Job Events
# ----------
# before_job = ["clp.utils.before_job"]
# after_job = ["clp.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"clp.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }



# Owner-managed CLP role assignment from the standard User form.
doctype_js = {"User": "public/js/user_roles.js"}

# Active document event hooks for CLP activity audit records.
doc_events = {
    "Loyalty Customer": {"after_insert": "clp.audit.log_doc_event", "on_update": "clp.audit.log_doc_event"},
    "Fuel Purchase Entry": {"after_insert": "clp.audit.log_doc_event", "on_submit": "clp.audit.log_doc_event", "on_cancel": "clp.audit.log_doc_event"},
    "Gift Redemption": {"after_insert": "clp.audit.log_doc_event", "on_submit": "clp.audit.log_doc_event", "on_cancel": "clp.audit.log_doc_event"},
    "Gift Stock Request": {"after_insert": "clp.audit.log_doc_event", "on_submit": "clp.audit.log_doc_event", "on_cancel": "clp.audit.log_doc_event"},
    "User": {"on_update": "clp.audit.log_doc_event"},
    "Referral Reward Entry": {"after_insert": "clp.audit.log_doc_event", "on_update": "clp.audit.log_doc_event"}
}
