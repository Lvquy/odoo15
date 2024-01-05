# -*- coding: utf-8 -*-
# Copyright (c) 2020-Present InTechual Solutions. (<https://intechualsolutions.com/>)

import openai

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class Channel(models.Model):
    _inherit = 'mail.channel'

    def _notify_thread(self, message, msg_vals=False, **kwargs):
        rdata = super(Channel, self)._notify_thread(message, msg_vals=msg_vals, **kwargs)
        chatzalo_channel_id = self.env.ref('zalo_oa.channel_zalo')
        user_chatzalo = self.env.ref("zalo_oa.user_chatzalo")
        partner_chatzalo = self.env.ref("zalo_oa.channel_zalo")

        chatzalo_channel_id.with_user(user_chatzalo).message_post(body='test', message_type='comment', subtype_xmlid='mail.mt_comment')


        return rdata
