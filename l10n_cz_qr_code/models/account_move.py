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

#Imports for borderless QR
try:
    import qrcode
    from qrcode.constants import ERROR_CORRECT_M as QR_ERROR_CORRECT
    from io import BytesIO
except ImportError:
    qrcode = None
    QR_ERROR_CORRECT = None #type: ignore
    BytesIO = None
    _logger.warning("qrcode library not found, fallback to qrplatba for QR code generation")

class AccountMove(models.Model):
    _inherit = 'account.move'

    # fields
    l10n_cz_qr_code_img = fields.Binary(string="QR Code Image", compute="_compute_l10n_cz_qr_code", store=True)

    @api.depends('amount_total', 'currency_id', 'partner_id', 'invoice_date_due', 'amount_residual', 'payment_reference', 'ref')
    def _compute_l10n_cz_qr_code(self):
        """Compute final QR code"""
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
                    _logger.info("CZQR: Generated QR code for %s", move.name)
            except Exception as e:
                _logger.error("CZQR: Error generating QR code for %s: %s", move.name, str(e))
                move.l10n_cz_qr_code_img = False

    def _l10n_cz_get_account_number(self):
        """Get current record account number"""
        self.ensure_one()
        bank_acc = self.partner_bank_id
        
        return bank_acc.acc_number or None

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
        if self.currency_id.name != 'CZK':
            return False
        if not self.partner_bank_id:
            return False
        return True
    
    def _l10n_cz_get_variable_symbol(self):
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
            _logger.info("CZQR: No valid Czech account number for %s", self.name)
            return False
        
        kwargs = {}
        vs = self._l10n_cz_get_variable_symbol()
        if vs:
            kwargs['x_vs'] = vs

        if self.invoice_date_due:
            kwargs['due_date'] = fields.Date.to_date(self.invoice_date_due)
        
        if self.ref:
            kwargs['message'] = self.ref[:60]

        if QRPlatbaGenerator is None:
            _logger.warning("CZQR: qrplatba library not available, cannot generate QR for %s", self.name)
            return False

        generator = QRPlatbaGenerator(
            account_number,
            self.amount_residual,
            **kwargs,
        )

        no_border = self.env['ir.config_parameter'].sudo().get_param(
            'l10n_cz_qr_code.no_border'
        ) == 'True'

        # Borderless QR
        if no_border:
            if qrcode is None or QR_ERROR_CORRECT is None or BytesIO is None:
                _logger.warning("CZQR: qrcode library not available, cannot generate borderless QR for %s", self.name)
                return False
            
            qr = qrcode.QRCode(
                version=None,
                error_correction=QR_ERROR_CORRECT,
                box_size=10,
                border=0,
            )

            qr.add_data(generator.get_text())
            qr.make(fit=True)

            img = qr.make_image(fill_color='black', back_color='white')
            buffer = BytesIO()
            img.save(buffer, 'PNG')
            _logger.info("CZQR: Generated QR with values %s %s %s", account_number, self.amount_residual, kwargs)
            return base64.b64encode(buffer.getvalue())
        
        else:
            img = generator.make_image(box_size=5, border=1)
            svg_data = img.to_string(encoding='unicode')

            if cairosvg is None:
                _logger.warning("CZQR: cairosvg library not available, cannot convert SVG to PNG for %s", self.name)
                return False

            png_data = cairosvg.svg2png(
                bytestring=svg_data.encode('utf-8'),
                output_width=200,
                output_height=200,
            )

            if not png_data:
                _logger.error("CZQR: Failed to convert SVG to PNG for %s", self.name)
                return False
            _logger.info("CZQR: Generated QR with values %s %s %s", account_number, self.amount_residual, kwargs)
            return base64.b64encode(png_data)