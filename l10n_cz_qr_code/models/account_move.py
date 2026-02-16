import base64
import logging
from odoo import models, fields, api #type: ignore

_logger = logging.getLogger(__name__)

#External Imports
try:
    from qrplatba import QRPlatbaGenerator
except ImportError:
    QRPlatbaGenerator = None
    _logger.warning("qrplatba library not found")

try:
    import cairosvg
except ImportError:
    cairosvg = None
    _logger.warning("cairosvg library not found")

#Inherits
class AccountMove(models.Model):
    _inherit = 'account.move'

    # fields
    l10n_cz_qr_code_img = fields.Binary(string="QR Code Image", compute="_compute_l10n_cz_qr_code", store=True)

    #Compute final QR
    @api.depends('amount_total', 'currency_id', 'partner_id', 'invoice_date_due')
    def _compute_l10n_cz_qr_code(self):
        enabled = self.env['ir.config_parameter'].sudo().get_param('l10n_cz_qr_code.enabled', False)
        for move in self:
            move.l10n_cz_qr_code_img = False
            if not enabled:
                continue
            if not move._l10n_cz_can_generate_qr_code():
                continue

            try:
                png_data = move._l10n_cz_generate_qr_png()
                if png_data:
                    move.l10n_cz_qr_code_img = png_data
            except Exception as e:
                _logger.error("Error generating QR code for %s: %s", move.name, str(e))
                move.l10n_cz_qr_code_img = False

    def _l10n_cz_get_account_number(self):
        """Get account number from odoo database, supports different formats
        1234567890/0100, CZ1501001111002212345678"""

        self.ensure_one()
        bank_acc = self.partner_bank_id

        # Czech format 1234567890/0100
        if bank_acc.acc_number and '/' in bank_acc.acc_number:
            return bank_acc.acc_number.strip()
        
        iban = bank_acc.sanitized_acc_number or bank_acc.acc_number or ''
        iban = iban.replace(' ', '').upper()

        if iban.startswith('CZ') and len(iban) == 24:
            bank_code = iban[4:8]
            prefix = iban[8:14].lstrip('0')
            base_number = iban[14:24].lstrip('0')

            if prefix:
                return f"{prefix}-{base_number}/{bank_code}"
            return f"{base_number}/{bank_code}"
        
        return None

    def _l10n_cz_can_generate_qr_code(self):
        """Check if QR code can be generated for current invoice"""
        self.ensure_one()
        if QRPlatbaGenerator is None or cairosvg is None:
            return False
        if self.move_type not in ['out_invoice', 'out_refund']:
            return False
        if self.state != 'posted':
            return False
        if self.payment_state in ('paid', 'in_payment', 'reversed'):
            return False
        if not self.partner_bank_id:
            return False
        return True
    
    def _l10n_get_variable_symbol(self):
        """Return variable symbol for invoice - number"""
        self.ensure_one()

        ref = self.payment_reference or self.name or ''
        vs = ''.join(filter(str.isdigit, ref))
        return vs[:10] if vs else None
    
    def _l10n_cz_generate_qr_png(self):
        """Generate QR as b64-encoded png"""
        self.ensure_one()
        account_number = self._l10n_cz_get_account_number()
        if not account_number:
            _logger.info("No valid Czech account number for %s", self.name)
            return False
        
        kwargs = {}
        vs = self._l10n_get_variable_symbol()
        if vs:
            kwargs['variable_symbol'] = vs

        if self.invoice_date_due:
            kwargs['due_date'] = fields.Date.to_date(self.invoice_date_due)
        
        if self.ref:
            kwargs['message'] = self.ref[:60]

        if QRPlatbaGenerator is None:
            _logger.warning("qrplatba library not available, cannot generate QR for %s", self.name)
            return False

        generator = QRPlatbaGenerator(
            account_number,
            self.amount_residual,
            **kwargs,
        )

        img = generator.make_image(box_size=10, border=1)
        svg_data = img.to_string(encoding='unicode')

        if cairosvg is None:
            _logger.warning("cairosvg library not available, cannot convert SVG to PNG for %s", self.name)
            return False

        png_data = cairosvg.svg2png(
            bytestring=svg_data.encode('utf-8'),
            output_width=200,
            output_height=200,
        )
        if not png_data:
            _logger.error("Failed to convert SVG to PNG for %s", self.name)
            return False
        return base64.b64encode(png_data)