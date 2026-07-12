app_name = "cryo_onboarding"
app_title = "Cryo Onboarding"
app_publisher = "Laida L"
app_description = "Cryo storage onboarding"
app_email = "laidalavenia123@gmail.com"
app_license = "mit"

# Apps
# ------------------

fixtures = [
    {"dt": "Workflow", "filters": [["name", "=", "Storage Onboarding Workflow"]]},
    {
        "dt": "Workflow State",
        "filters": [
            [
                "name",
                "in",
                [
                    "Draft",
                    "Pending Approval",
                    "Approved",
                    "Rejected",
                    "Ready for Agreement",
                    "Closed",
                ],
            ]
        ],
    },
    {
        "dt": "Workflow Action Master",
        "filters": [
            [
                "name",
                "in",
                [
                    "Submit for Approval",
                    "Approve",
                    "Reject",
                    "Revise",
                    "Ready for Agreement",
                    "Close",
                ],
            ]
        ],
    },
    {"dt": "Custom Field", "filters": [["dt", "=", "Storage Onboarding Case"]]},
]

# required_apps = []

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "cryo_onboarding",
# 		"logo": "/assets/cryo_onboarding/logo.png",
# 		"title": "Cryo Onboarding",
# 		"route": "/cryo_onboarding",
# 		"has_permission": "cryo_onboarding.api.permission.has_app_permission"
# 	}
# ]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/cryo_onboarding/css/cryo_onboarding.css"
# app_include_js = "/assets/cryo_onboarding/js/cryo_onboarding.js"

# include js, css files in header of web template
# web_include_css = "/assets/cryo_onboarding/css/cryo_onboarding.css"
# web_include_js = "/assets/cryo_onboarding/js/cryo_onboarding.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "cryo_onboarding/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "cryo_onboarding/public/icons.svg"

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
# 	"methods": "cryo_onboarding.utils.jinja_methods",
# 	"filters": "cryo_onboarding.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "cryo_onboarding.install.before_install"
# after_install = "cryo_onboarding.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "cryo_onboarding.uninstall.before_uninstall"
# after_uninstall = "cryo_onboarding.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "cryo_onboarding.utils.before_app_install"
# after_app_install = "cryo_onboarding.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "cryo_onboarding.utils.before_app_uninstall"
# after_app_uninstall = "cryo_onboarding.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "cryo_onboarding.notifications.get_notification_config"

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
# 		"cryo_onboarding.tasks.all"
# 	],
# 	"daily": [
# 		"cryo_onboarding.tasks.daily"
# 	],
# 	"hourly": [
# 		"cryo_onboarding.tasks.hourly"
# 	],
# 	"weekly": [
# 		"cryo_onboarding.tasks.weekly"
# 	],
# 	"monthly": [
# 		"cryo_onboarding.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "cryo_onboarding.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "cryo_onboarding.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "cryo_onboarding.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["cryo_onboarding.utils.before_request"]
# after_request = ["cryo_onboarding.utils.after_request"]

# Job Events
# ----------
# before_job = ["cryo_onboarding.utils.before_job"]
# after_job = ["cryo_onboarding.utils.after_job"]

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
# 	"cryo_onboarding.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

# Translation
# ------------
# List of apps whose translatable strings should be excluded from this app's translations.
# ignore_translatable_strings_from = []
