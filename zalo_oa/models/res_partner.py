# -*- coding: utf-8 -*-

import requests
import logging
import base64
_logger = logging.getLogger(__name__)
from odoo import fields, models, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    zalo_id = fields.Char(string='Zalo ID')
    image_url = fields.Char(string='URL image')
    zalo_chat = fields.Many2one(comodel_name='chat.zalo', string='Lịch sử chat zalo')

    # @api.depends('zalo_id')
    # def get_chat(self):
    #     model_zalochat = self.env['chat.zalo'].search([('zalo_id','=',self.zalo_id)],limit=1)
    #     self.zalo_chat =model_zalochat.id

    def get_image_from_url(self, url):
        """
        :return: Returns a base64 encoded string.
        """
        data = ""
        try:
            data = base64.b64encode(requests.get(url.strip()).content).replace(b"\n", b"")
        except Exception as e:
            _logger.warning("Can’t load the image from URL %s" % url)
            logging.exception(e)
        return data

    @api.onchange("image_url")
    def compute_image(self):
        for record in self:
            image_1920 = None
            if record.image_url:
                image_1920 = self.get_image_from_url(record.image_url)

            record.update({"image_1920": image_1920, })

    def check_partner_zalo(self, zalo_id):
        record_zalo = self.search([('zalo_id','=',zalo_id)])
        if record_zalo:
            return record_zalo
        else:return False




