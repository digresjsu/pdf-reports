from odoo import models, fields #type: ignore

class ResPartnerCompanyNameHistory(models.Model):
    _name = 'digres.company.name.history'
    _description = 'Company Name History'

    partner_id = fields.Many2one('res.partner', string='Partner')
    name = fields.Char(string='Previous Name', required=True)
    valid_from = fields.Date(string='Valid From', required=True)
    valid_until = fields.Date(string='Valid Until', required=True)


class ResPartner(models.Model):
    _inherit = 'res.partner'
    _name = 'res.partner'

    company_name_history_ids = fields.One2many(
        'digres.company.name.history',
        'partner_id',
        string='Company Name History',
    )

    # Přidá "akci" po potvrzení
    # self: aktuální záznam
    # vals: změny v poli
    # kontroluje jestli se změnilo pole name  -> zapíše do historie
    def write(self, vals):
        if 'name' in vals:
            for partner in self:
                if partner.name and partner.name != vals['name']:
                    last_history = self.env['digres.company.name.history'].search([('partner_id', '=', partner.id)], order='valid_until desc', limit=1)

                    if last_history:
                        valid_from = last_history.valid_until
                    else:
                        valid_from = partner.create_date.date()

                    self.env['digres.company.name.history'].create({
                        'partner_id': partner.id,
                        'name': partner.name,
                        'valid_from': valid_from,
                        'valid_until': fields.Date.today(),
                    })
        #zavolá původní metodu write
        return super().write(vals)