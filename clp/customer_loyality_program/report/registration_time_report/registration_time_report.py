import frappe
from frappe import _
from clp.customer_loyality_program.report.customer_registration_time_analysis.customer_registration_time_analysis import execute as base_execute

def execute(filters=None):
    return base_execute(filters)
