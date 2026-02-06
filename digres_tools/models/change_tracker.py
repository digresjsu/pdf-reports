from odoo import api, models, fields  # type: ignore
from datetime import timedelta
# Model pro intuo export změn ve fakturách
# Ukazuje historii změn posledních 6 dnů.

#Pole: 
# move_id: Many2one na account.move
# field_name: název pole, které se změnilo
# old_value: stará hodnota
# new_value: nová hodnota
# changed_on: datum a čas změny
# record_name: název záznamu (pro lepší přehlednost)

class RecordChangeTracker(models.Model):
    _name = 'digres.record.change.tracker'
    _description = 'Record Changes History'
    _order = 'create_date desc'

    res_model = fields.Char(string='Model', required=True)
    res_id = fields.Integer(string='Record ID', required=True)
    field_name = fields.Char(string='Field Name', required=True)
    old_value = fields.Text(string='Old Value')
    new_value = fields.Text(string='New Value')
    changed_on = fields.Datetime(string='Changed On', default=fields.Datetime.now, required=True)

    record_name = fields.Char(string='Record Name', compute='_compute_record_name', store=True)


    @api.depends('res_model', 'res_id')
    def _compute_record_name(self):
        for rec in self:
            if rec.res_model and rec.res_id:
                doc = self.env[rec.res_model].browse(rec.res_id)
                rec.record_name = doc.display_name if doc.exists() else 'Deleted Record'
            else:
                rec.record_name = False