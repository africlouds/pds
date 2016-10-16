# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from . import __version__ as app_version

app_name = "pds"
app_title = "Premium Delivery Services"
app_publisher = "PDS Ltd"
app_description = "Premium Delivery Services"
app_icon = "octicon octicon-file-directory"
app_color = "grey"
app_email = "arwema@gmail.com"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/pds/css/pds.css"
app_include_js = [
	"https://maps.googleapis.com/maps/api/js?key=AIzaSyClZw3R63FghnycvQVypPxOTUZyHAXilEU&libraries=geometry"
]

# include js, css files in header of web template
# web_include_css = "/assets/pds/css/pds.css"
# web_include_js = "/assets/pds/js/pds.js"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Website user home page (by function)
# get_website_user_home_page = "pds.utils.get_home_page"

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "pds.install.before_install"
# after_install = "pds.install.after_install"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "pds.notifications.get_notification_config"

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

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
 	"Delivery Request": {
 		"after_insert": "pds.api.send_fcm"
	}
}


# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"pds.tasks.all"
# 	],
# 	"daily": [
# 		"pds.tasks.daily"
# 	],
# 	"hourly": [
# 		"pds.tasks.hourly"
# 	],
# 	"weekly": [
# 		"pds.tasks.weekly"
# 	]
# 	"monthly": [
# 		"pds.tasks.monthly"
# 	]
# }

# Testing
# -------

# before_tests = "pds.install.before_tests"

# Overriding Whitelisted Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "pds.event.get_events"
# }

