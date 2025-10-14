Remainder Module (Odoo Module)

Overview

The Remainder Module is a focused Odoo application designed to track and manage critical deadlines for recurring purchases, licenses, or any product/service with an expiration or renewal date.

Its core functionality lies in automated, customizable email reminders and activity scheduling, ensuring that key personnel are notified a configurable number of days before a deadline is reached. It serves as a centralized tracking tool to prevent missed renewals and maintain proactive client relationships.

Key Features

Automated Reminder System

Daily Cron Job: A daily scheduled action automatically checks all Confirmed records against the current date to determine if a reminder should be triggered.

Configurable Timing: Users can specify when the reminder should be sent relative to the deadline, choosing from options like 7, 15, 30, 60, or 90 days before the Purchase Deadline.

Custom Email Recipient: The reminder email is sent to a customizable field, Reminder Email To, allowing flexibility to notify external parties or specific non-Odoo users.

Internal Activity Creation: When an external reminder email is sent, the module automatically schedules a To-Do activity for the Responsible Odoo user for internal follow-up.

Data & Workflow Tracking
Financial Tracking: Each record tracks Quantity, Price (Monetary field), and automatically calculates the Total Value (Quantity × Price).

Days Remaining: A computed field, Days Remaining, gives an at-a-glance view of the time left until the deadline.

Uniqueness Constraint: Prevents duplicate reminders by enforcing a unique combination of Partner Number and Product Name.

Workflow States: Simple workflow to manage records: Draft, Confirmed (active), and Cancelled.

User Interface & Analytics

Color-Coded Status: The List and Kanban views provide immediate visual feedback using color-coding based on status and deadline urgency:

Red: Overdue or Cancelled.

Orange: Urgent (7 days or less remaining).

Green: Confirmed and on track.

Blue: Draft/New.

Urgent Dashboard: A dedicated menu action for My Dashboard (Urgent) filters all records due in 7 days or less.

Comprehensive Views: Supports multiple views for analysis, including List, Kanban, Pivot, Calendar (based on Purchase Deadline), and Graph (analyzing total value and quantity).

Usage Guide

Create a Record: Navigate to Reminders > Remainder Records and create a new record.

Fill Mandatory Fields: Provide the Partner Number, Product Name, Purchase Deadline, and Price.

Configure Reminder: Set the Reminder Timing (e.g., 30 Days Before Deadline) and the Reminder Email To recipient.

Activate Automation: Records start in Draft state. Click the Confirm button on the form to move the record to Confirmed status and enable the daily reminder check.

Monitor:

Check the My Dashboard (Urgent) menu for immediate priorities.

Check your Odoo activities for follow-up tasks created by the automation system.

Use the Pivot and Graph views to analyze quantities and total value by deadline or status.

Reporting: Generates a standard PDF Remainder Report for printing or documentation.

