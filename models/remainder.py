from odoo import models, fields, api
from datetime import date, timedelta
from odoo.exceptions import UserError


class RemainderRecord(models.Model):
    _name = 'remainder.record'
    _description = 'Remainder Record'
    _inherit = ['mail.thread', 'mail.activity.mixin']  # Enables chatter + activity scheduling

    def name_get(self):
        """
        Override display name:
        Shows records as "<Product Name> (<Partner Number>)"
        instead of default 'Record ID'.
        """
        result = []
        for record in self:
            name = f'{record.product_name} ({record.partner_number})'
            result.append((record.id, name))
        return result

    # Database-level uniqueness constraint to avoid duplicates
    _sql_constraints = [
        (
            'product_partner_unique',
            'unique(partner_number, product_name)',
            'A reminder already exists for this Partner Number and Product Name combination. '
            'Please check your existing records.'
        )
    ]

    # ==========================
    # Business Data Fields
    # ==========================
    partner_number = fields.Char(
        string='Partner Number',
        required=True,
        copy=False,  # Prevents accidental duplication in "Duplicate" action
        help="Unique identifier for the partner/customer."
    )
    product_name = fields.Char(string='Product Name', required=True)
    quantity = fields.Float(string='Quantity', default=1.0)
    price = fields.Monetary(string='Price', currency_field='currency_id', required=True)

    # Key date used for reminders
    purchase_deadline = fields.Date(string='Purchase Deadline', required=True, tracking=True)

    # Email recipient (can be customized per record)
    reminder_recipient_email = fields.Char(
        string="Reminder Email To",
        default="your.personal.email@gmail.com"
    )

    # Timing rule: how many days before deadline to trigger reminder
    reminder_days_before = fields.Selection([
        ('7', '7 Days Before Deadline'),
        ('15', '15 Days Before Deadline'),
        ('30', '30 Days Before Deadline'),
        ('60', '60 Days Before Deadline'),
        ('90', '90 Days Before Deadline'),
    ], string='Reminder Timing', default='30', required=True)

    # Responsible Odoo user (default = current logged in user)
    user_id = fields.Many2one(
        'res.users',
        string='Responsible',
        default=lambda self: self.env.user,
        tracking=True
    )

    # Computed fields
    days_to_deadline = fields.Integer(
        string='Days Remaining',
        compute='_compute_days_to_deadline',
        store=True
    )
    total_value = fields.Monetary(
        string='Total Value',
        compute='_compute_total_value',
        store=True
    )
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        default=lambda self: self.env.company.currency_id
    )

    # Workflow state machine
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='draft', readonly=True, required=True, tracking=True)

    # Used for kanban card colors (computed logic below)
    color = fields.Integer(string='Color Index', compute='_compute_color')

    # ==========================
    # Computed Fields
    # ==========================
    @api.depends('purchase_deadline')
    def _compute_days_to_deadline(self):
        """Calculate how many days are left until the deadline."""
        today = date.today()
        for record in self:
            record.days_to_deadline = (record.purchase_deadline - today).days if record.purchase_deadline else 0

    @api.depends('quantity', 'price')
    def _compute_total_value(self):
        """Compute line total = quantity × price."""
        for record in self:
            record.total_value = record.quantity * record.price

    @api.depends('state', 'purchase_deadline')
    def _compute_color(self):
        """
        Compute kanban color coding:
        - 1 (red): Cancelled or past deadline
        - 2 (orange): Deadline within 7 days
        - 7 (green): Confirmed and on track
        - 9 (blue): Draft/new
        - 0: Default/other
        """
        today = date.today()
        for record in self:
            if record.state == 'cancelled':
                record.color = 1
            elif record.purchase_deadline and record.purchase_deadline < today:
                record.color = 1
            elif record.purchase_deadline and (record.purchase_deadline - today).days <= 7:
                record.color = 2
            elif record.state == 'confirmed':
                record.color = 7
            elif record.state == 'draft':
                record.color = 9
            else:
                record.color = 0

    # ==========================
    # Business Actions
    # ==========================
    def action_confirm(self):
        """Move record to 'confirmed' state."""
        self.state = 'confirmed'

    def action_draft(self):
        """
        Reset to 'draft' state.
        Cancelled records cannot be re-opened (business rule).
        """
        for record in self:
            if record.state == 'cancelled':
                raise UserError("Cannot reset a cancelled reminder to Draft. Please create a new record instead.")
            record.state = 'draft'

    # ==========================
    # Overrides
    # ==========================
    def write(self, vals):
        """
        Override write():
        - Track changes to 'purchase_deadline' in chatter.
        - Post a message with old and new date.
        """
        self.ensure_one()  # Defensive: we only handle one record safely

        if 'purchase_deadline' in vals and self.purchase_deadline and self.purchase_deadline != fields.Date.to_date(
                vals['purchase_deadline']):
            old_date = self.purchase_deadline.strftime('%Y-%m-%d')
            new_date = fields.Date.to_date(vals['purchase_deadline']).strftime('%Y-%m-%d')

            # Post a chatter log
            self.message_post(
                body=f"**Purchase Deadline Modified:** {old_date} → {new_date}",
                subtype_xmlid='mail.mt_note',
                message_type='notification'
            )
        return super(RemainderRecord, self).write(vals)

    # ==========================
    # Cron Job Logic
    # ==========================
    @api.model
    def _check_and_send_deadline_reminder(self):
        """
        Daily cron task:
        - Check if today matches 'reminder_days_before' for any record.
        - If yes:
            1. Send reminder email using the template.
            2. Create an activity for the responsible user.
            3. Log the action in chatter.
        """
        today = date.today()
        records_to_check = self.search([('state', 'in', ('draft', 'confirmed'))])
        template = self.env.ref('remainder.email_template_remainder_deadline', raise_if_not_found=False)

        if template:
            for record in records_to_check:
                if not record.purchase_deadline:
                    continue

                days_to_remind = int(record.reminder_days_before)
                target_reminder_date = record.purchase_deadline - timedelta(days=days_to_remind)

                if today == target_reminder_date:
                    # Send email to the custom recipient
                    email_values = {'email_to': record.reminder_recipient_email}
                    template.send_mail(record.id, email_values=email_values, force_send=True)

                    # Create To-Do activity for responsible user
                    record.activity_schedule(
                        'mail.mail_activity_data_todo',
                        user_id=record.user_id.id,
                        summary=f'DEADLINE ALERT: Follow up on {record.product_name} (Due in {days_to_remind} days)',
                        note=f"Reminder email sent to {record.reminder_recipient_email}. "
                             f"Follow up before: {record.purchase_deadline}.",
                        date_deadline=today
                    )

                    # Log reminder in chatter
                    record.message_post(
                        body=f"Deadline reminder email sent and activity created for {record.user_id.name}.",
                        subtype_xmlid='mail.mt_note'
                    )
        return True
