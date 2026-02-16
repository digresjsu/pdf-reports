from odoo import models, fields, api  # type: ignore
import logging

_logger = logging.getLogger(__name__)
# Úprava write() pro sledování změn
class ChangeTrackerMixin(models.AbstractModel):
    _name = 'digres.change.tracker.mixin'
    _description = 'Change Tracker Mixin'

    #TODO: kontrola stored computed fields - asi předdefinované, aby se nemusel dělat check na každý field
    #Upraví metodu write() u všech modelů co dědí z tohoto mixinu
    #Po uložení zkontroluje hodnoty polí a pokud se změnily, každá změna vytvoří záznam v tabulce
    def write(self, vals):
        # ukáže se v .sh logu
        # _logger.info('=== WRITE CALLED === vals: %s', vals)
        old_value = {}
        for rec in self:
            old_value[rec.id] = {}
            for field_name in vals:
                if field_name not in self._fields:
                    continue
                field_obj = self._fields[field_name]
                old_value[rec.id][field_name] = rec._format_value(field_obj, rec[field_name])
        res = super().write(vals)

        changes = []
        for rec in self:
            for field_name, old_str in old_value[rec.id].items():
                field_obj = self._fields[field_name]
                new_str = rec._format_value(field_obj, rec[field_name])
                
                if old_str != new_str:
                    changes.append({
                        'res_model': self._name,
                        'res_id': rec.id,
                        'field_name': field_obj.string or field_name,
                        'old_value': old_str,
                        'new_value': new_str,
                        'changed_on': fields.Datetime.now(),
                    })
        
        if changes:
            self.env['digres.record.change.tracker'].sudo().create(changes)
        return res

    # Přeformátuje vše na string, pro snažší porovnání a uložení
    def _format_value(self, field_obj, value):
        if value is False or value is None:
            return ''
        if field_obj.type == 'many2one':
            return value.display_name if value else ''
        if field_obj.type in ('many2many', 'one2many'):
            return ', '.join(value.mapped('display_name'))
        if field_obj.type == 'selection':
            sel = dict(field_obj.selection) if isinstance(field_obj.selection, list) else {}
            return sel.get(value, str(value))
        return str(value)