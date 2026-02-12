from odoo import models, fields


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    l10n_cz_qr_code_enabled = fields.Boolean(
        string="Enable QR Code for Czech payments",
        default=False,
        config_parameter='l10n_cz_qr_code.enabled',
        )
    