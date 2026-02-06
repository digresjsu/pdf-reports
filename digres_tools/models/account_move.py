from odoo import fields, models, api  # type: ignore

class AccountMove(models.Model):
    _inherit = ['account.move', 'digres.change.tracker.mixin']
    _name = 'account.move'

#TODO: implement base_tax
###########################################################################
# Fields
###########################################################################

    currency_rate_inverted = fields.Float(
        string = 'Inverted Currency Rate',
        digits = (12, 6),
        compute = '_compute_currency_rate_inverted',
    )

    dph_term = fields.Char(
        string = 'DPH Term',
        compute='_compute_dph_term',
        store=True
    )

    # base_tax = fields.Monetary(
    #     string = 'Base Tax',
    #     compute = '_compute_base_tax',
    #     store=True
    # )


###########################################################################
# Compute
###########################################################################

    @api.depends('invoice_date')
    def _compute_dph_term(self):
        for move in self:
            if move.invoice_date:
                move.dph_term = move.invoice_date.strftime('%m/%y')

    @api.depends('invoice_currency_rate')
    def _compute_currency_rate_inverted(self):
        for move in self:
            if move.invoice_currency_rate:
                move.currency_rate_inverted = 1.0 / move.invoice_currency_rate
            else:
                move.currency_rate_inverted = 0.0