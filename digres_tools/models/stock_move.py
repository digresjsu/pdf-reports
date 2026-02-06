from odoo import fields, models, api  # type: ignore

class StockMove(models.Model):
    _inherit = ['stock.move', 'digres.change.tracker.mixin']
    _name = 'stock.move'


###########################################################################
# Fields
###########################################################################

    registration_price = fields.Float(
        string = 'Registration Price',
        compute = '_compute_registration_price',
        store=True
    )

###########################################################################
# Compute
###########################################################################

    @api.depends('price_unit', 'product_qty')
    def _compute_registration_price(self):
        for move in self:
            move.registration_price = move.price_unit * move.product_qty