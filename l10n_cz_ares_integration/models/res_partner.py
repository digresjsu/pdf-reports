from odoo import models, api, _  # type: ignore
from odoo.exceptions import UserError  # type: ignore
import requests
import re
import logging

_logger = logging.getLogger(__name__)

ARES_URL = "https://ares.gov.cz/ekonomicke-subjekty-v-be/rest/ekonomicke-subjekty/{ico}"


class ResPartner(models.Model):
    _inherit = 'res.partner'

    def _get_ico(self, vat):
        """Extract 8-digit IČO from a VAT/DIČ string like 'CZ12345678' or '12345678'."""
        if not vat:
            return None
        ico = re.sub(r'^CZ', '', vat.strip().upper())
        return ico if re.match(r'^\d{8}$', ico) else None

    def _get_ares_data(self, ico):
        """GET subject data from ARES using IČO."""
        try:
            resp = requests.get(ARES_URL.format(ico=ico), timeout=10)
            if resp.status_code == 200:
                return resp.json()
            if resp.status_code != 404:
                _logger.warning("ARES returned HTTP %s for IČO %s", resp.status_code, ico)
        except Exception as e:
            _logger.warning("ARES request failed for IČO %s: %s", ico, e)
        return None

    def _ares_data(self, data):
        """Build a vals dict from an ARES response."""
        vals = {}
        if data.get('obchodniJmeno'):
            vals['name'] = data['obchodniJmeno']
        if data.get('dic'):
            vals['vat'] = data['dic']
        
        street = data.get('sidlo', {})
        if street.get('nazevUlice'):
            if street.get('cisloDomovni'):
                if street.get('orientacniCislo'):
                    vals['street'] = f"{street['nazevUlice']} {street['cisloDomovni']}/{street['orientacniCislo']}"
                else:
                    vals['street'] = f"{street['nazevUlice']} {street['cisloDomovni']}"
            else:
                vals['street'] = street['nazevUlice']
        if street.get('psc'):
            vals['zip'] = street['psc']
        if street.get('nazevObce'):
            vals['city'] = street['nazevObce']
        
        if street.get('kodStatu'):
            country = self.env['res.country'].search([('code', '=', street['kodStatu'])], limit=1)
            if country:
                vals['country_id'] = country.id

        return vals

    # ------------------------------------------------------------------
    # Manual button
    # ------------------------------------------------------------------

    def action_fetch_from_ares(self):
        for partner in self:
            ico = partner._get_ico(partner.vat)
            if not ico:
                raise UserError(
                    _("Cannot extract IČO from VAT field: '%s'.\n")
                    % (partner.vat or '')
                )
            data = partner._get_ares_data(ico)
            if data is None:
                raise UserError(_("No ARES record found for IČO: %s") % ico)
            vals = partner._ares_data(data)
            if vals:
                partner.with_context(_ares_sync=True).write(vals)

    def write(self, vals):
        result = super().write(vals)
        if 'vat' in vals and not self.env.context.get('_ares_sync'):
            for record in self:
                ico = record._get_ico(vals['vat'])
                if ico:
                    data = record._get_ares_data(ico)
                    if data:
                        update = record._ares_data(data)
                        if update:
                            record.with_context(_ares_sync=True).write(update)
        return result
