# -*- coding: utf-8 -*-
from odoo import api, fields, models
import subprocess, json
from datetime import datetime
import logging

_logger = logging.getLogger(__name__)
from odoo.exceptions import UserError
import requests
from odoo.http import request

class ResConfigSetting(models.TransientModel):
    _inherit = 'res.config.settings'

    app_id = fields.Char(string='app_id')
    secret_key = fields.Char(string='secret_key')
    refresh_token = fields.Char(string='refresh_token')
    access_token = fields.Char(string='access_token')
    create_date_token = fields.Date(string='create_date_token')
    code_token_zalo = fields.Char(string='code_token_zalo')

    @api.model
    def set_values(self):
        ICP = self.env['ir.config_parameter'].sudo()

        ICP.set_param('zalo_oa.app_id', self.app_id)
        ICP.set_param('zalo_oa.secret_key', self.secret_key)
        ICP.set_param('zalo_oa.refresh_token', self.refresh_token)
        ICP.set_param('zalo_oa.access_token', self.access_token)
        ICP.set_param('zalo_oa.create_date_token', self.create_date_token)
        ICP.set_param('zalo_oa.code_token_zalo', self.code_token_zalo)

        super(ResConfigSetting, self).set_values()

    @api.model
    def get_values(self):
        ICP = self.env['ir.config_parameter'].sudo()
        res = super(ResConfigSetting, self).get_values()

        res['app_id'] = ICP.get_param('zalo_oa.app_id')
        res['secret_key'] = ICP.get_param('zalo_oa.secret_key')
        res['refresh_token'] = ICP.get_param('zalo_oa.refresh_token')
        res['access_token'] = ICP.get_param('zalo_oa.access_token')
        res['create_date_token'] = ICP.get_param('zalo_oa.create_date_token')
        res['code_token_zalo'] = ICP.get_param('zalo_oa.code_token_zalo')

        return res

    def get_access_token_zalo(self):
        ICP = self.env['ir.config_parameter'].sudo()
        app_id = ICP.get_param('zalo_oa.app_id')
        secret_key = ICP.get_param('zalo_oa.secret_key')
        refresh_token = ICP.get_param('zalo_oa.refresh_token')
        url = 'https://oauth.zaloapp.com/v4/oa/access_token'
        headers = {
            "secret_key": secret_key
        }
        body = {
            "app_id": app_id,
            "refresh_token": refresh_token,
            "grant_type": "refresh_token"
        }

        try:
            response = requests.post(url, headers=headers, data=body, timeout=6)
            response.raise_for_status()  # Raise an HTTPError for bad responses
            data = response.json()

            print(data)
            access_token_new = data.get('access_token')
            refresh_token_new = data.get('refresh_token')

            print(access_token_new)
            print(refresh_token_new)
            ICP.set_param('zalo_oa.access_token', access_token_new)
            ICP.set_param('zalo_oa.refresh_token', refresh_token_new)
            ICP.set_param('zalo_oa.create_date_token', datetime.today())

        except requests.exceptions.RequestException as e:
            # Handle errors, e.g., log the error
            print(f"Error making request: {e}")

    def get_first_token_zalo(self):
        ICP = self.env['ir.config_parameter'].sudo()
        app_id = ICP.get_param('zalo_oa.app_id')
        secret_key = ICP.get_param('zalo_oa.secret_key')
        code_token_zalo = ICP.get_param('zalo_oa.code_token_zalo')
        url = 'https://oauth.zaloapp.com/v4/oa/access_token'

        headers = {
            "secret_key": secret_key
        }
        body = {
            "app_id": app_id,
            "code": code_token_zalo,
            "grant_type": "authorization_code"
        }

        try:
            response = requests.post(url, headers=headers, data=body)
            response.raise_for_status()  # Raise an HTTPError for bad responses
            data = response.json()

            # Assuming the response contains an access_token field
            print(data)
            if data.get('access_token'):
                access_token_new = data.get('access_token')
                refresh_token_new = data.get('refresh_token')

                print(access_token_new)
                print(refresh_token_new)
                ICP.set_param('zalo_oa.access_token', access_token_new)
                ICP.set_param('zalo_oa.refresh_token', refresh_token_new)
                ICP.set_param('zalo_oa.create_date_token', datetime.today())
            else:
                print('Error')

        except requests.exceptions.RequestException as e:
            # Handle errors, e.g., log the error
            print(f"Error making request: {e}")

    def get_info_even_folow(self, zalo_id):
        print('get_info_even_folow')
        ICP = self.env['ir.config_parameter'].sudo()
        access_token = ICP.get_param('zalo_oa.access_token')
        url = "https://openapi.zalo.me/v2.0/oa/getprofile"
        data_params = {'user_id': zalo_id}
        headers = {'access_token': access_token}
        response = requests.get(url=url, data=json.dumps(data_params), headers=headers)
        data_json = response.json()
        # print(data_json)
        vals = {
            'avatar': data_json.get('data').get('avatars').get('240'),
            'display_name': data_json.get('data').get('display_name'),
            'birth_date': data_json.get('data').get('birth_date')
        }
        return vals

    def user_submit_info(self, zalo_id, **kwargs):
        print('user_submit_info')
        ResPartner = self.env['res.partner'].sudo().search([('zalo_id', '=', zalo_id)], limit=1)
        if ResPartner:
            if kwargs.get("name"):
                ResPartner.write({
                    'name': kwargs.get("name"),
                })
            if kwargs.get("phone"):
                str_phone = str(kwargs.get("phone"))
                new_phone = "0" + str_phone[2:]
                ResPartner.write({
                    'mobile': new_phone
                })
            if kwargs.get("city"):
                ResPartner.write({
                    'city': kwargs.get("city")
                })
            if kwargs.get("district"):
                ResPartner.write({
                    'street2': kwargs.get("district")
                })
            if kwargs.get("address"):
                ResPartner.write({
                    'street': kwargs.get("address")
                })

    def check_zalo(self, zalo_id):
        print('check_zalo')
        record_zalo = self.env['chat.zalo'].search([('zalo_id', '=', zalo_id)])
        if record_zalo:
            return record_zalo
        else:
            False
    def check_partner(self, zalo_id):
        print('check_partner')
        record_zalo = self.env['res.partner'].search([('zalo_id', '=', zalo_id)])
        if record_zalo:
            return record_zalo
        else:
            False
    def push_notifi_zl(self,res_partner_id,body):
        print("push_notifi_zl")
        channel_id = self.env['mail.channel'].sudo().search([('name', 'ilike', 'zalo')], limit=1)
        notification_ids = [((0, 0, {
            'res_partner_id': res_partner_id,
            'notification_type': 'inbox'}))]
        channel_id.message_post(author_id=res_partner_id,
                                body=body,
                                message_type='notification',
                                subtype_xmlid="mail.mt_comment",
                                notification_ids=notification_ids,
                                partner_ids=[res_partner_id],
                                notify_by_email=False,
                                )
    def create_log_zalo(self,zalo_id, mess,author):
        ChatZalo = self.env['chat.zalo']
        record_zl = ChatZalo.search([('zalo_id','=',zalo_id)],limit=1)
        record_zl.write({
            'log_chat':[(0, 0, {
                    'text_chat': mess,
                    'author': author,
                    'date_chat': datetime.now()
                })]
        })
    def get_name_zalo(self,zalo_id):
        # lọc từ cuộc trò truyện ra tên người dùng
        url_get_user = 'https://openapi.zalo.me/v2.0/oa/conversation'
        ICP = self.env['ir.config_parameter'].sudo()
        access_token = ICP.get_param('zalo_oa.access_token')
        headers = {"access_token": access_token}
        params_request = {"offset": 0, "user_id": zalo_id, "count": 1}
        params_json = json.dumps(params_request)
        res = requests.get(url=url_get_user, headers=headers, data=params_json)
        if res.json().get("error") == -216:
            print('het han token')
            Res_CS = request.env['res.config.settings'].sudo()
            Res_CS.get_access_token_zalo()
            print('lay lai token xong')
            res = requests.get(url=url_get_user, headers=headers, data=params_json)
        data_res = (res.json().get("data")[0])
        print('data', data_res)
        target_id = zalo_id
        if data_res['from_id'] == target_id:
            target_data = {
                'id': data_res['from_id'],
                'display_name': data_res['from_display_name'],
                'avatar': data_res['from_avatar']
            }
        elif data_res['to_id'] == target_id:
            target_data = {
                'id': data_res['to_id'],
                'display_name': data_res['to_display_name'],
                'avatar': data_res['to_avatar']
            }
        else:
            target_data = None
        return target_data
