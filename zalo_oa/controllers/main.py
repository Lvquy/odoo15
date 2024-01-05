# -*- coding: utf-8 -*-


from odoo import http, _
from odoo.http import request
import logging, json

_logger = logging.getLogger(__name__)


class ZaloController(http.Controller):

    @http.route('/zalo/callback', type='http', auth='public', csrf=False, methods=['GET', 'POST'])
    def zalo_callback(self, **params):
        if http.request.httprequest.method == 'POST':
            # params là dữ liệu bạn nhận được từ Zalo khi sử dụng phương thức POST
            log = _logger.info("Received Zalo Callback (POST): %s", params)
            print('________   log: ',log)
            # Thực hiện xử lý theo logic của bạn
            if params:
                print('post ______ params: ',params)
            return "OK"
        elif http.request.httprequest.method == 'GET':
            # Xử lý dữ liệu từ callback tại đây
            # params là dữ liệu bạn nhận được từ Zalo khi sử dụng phương thức GET
            log = _logger.info("Received Zalo Callback (GET): %s", params)
            print('________   log: ',log)
            if params:
                print('get ______ params: ',params)
            return "OK"

    @http.route('/webhook/zalo', type='json', auth='public', methods=['POST','GET'], csrf=False)
    def handle_webhook(self, **post):
        data_zalo = {}
        try:
            # Lấy dữ liệu từ request
            data_json = request.jsonrequest
            print(data_json)
            data_zalo["event_name"] = event_name = data_json.get("event_name")
            ResPartner = request.env['res.partner'].sudo()
            ChatZalo = request.env['chat.zalo'].sudo()
            ICS = request.env['res.config.settings'].sudo()

            if event_name == 'follow':
                zalo_id = data_zalo['zalo_id'] = data_json.get("follower").get('id')
                check_zalo = ICS.check_zalo(zalo_id=zalo_id)
                body = 'Zalo OA: New Follower'
                if check_zalo:
                    res_partner_id = ResPartner.search([('zalo_id','=',zalo_id)],limit=1)
                    ICS.push_notifi_zl(res_partner_id=res_partner_id.id,body=body)
                else:
                    get_info = ICS.get_info_even_folow(zalo_id=zalo_id)
                    new_zalo = ChatZalo.create({
                        'name': get_info.get("display_name"),
                        'image_url':get_info.get('avatar'),
                        'zalo_id':zalo_id
                    })
                    new_zalo.compute_image()
                    data_zalo['new_zalo_id'] = new_zalo.id
                    check_partner = ICS.check_partner(zalo_id=zalo_id)
                    if check_partner:
                        pass
                    else:
                        new_partner = ResPartner.create({
                            'name':get_info.get("display_name"),
                            'zalo_id':zalo_id,
                            'image_url': get_info.get('avatar'),
                            'zalo_chat':int(data_zalo.get('new_zalo_id'))
                        })
                        new_partner.compute_image()
                    ICS.push_notifi_zl(res_partner_id=new_partner.id,body=body)

            if event_name == 'user_send_text':
                zalo_id = data_zalo['zalo_id'] = data_json.get("sender").get('id')
                message_text = data_json.get("message").get('text')
                check_zalo = ICS.check_zalo(zalo_id=zalo_id)
                if check_zalo:
                    author = check_zalo.name
                    ICS.create_log_zalo(zalo_id=zalo_id, mess=message_text,author=author)
                    data_zalo['res_partner_id'] = ResPartner.search([('zalo_id','=',zalo_id)],limit=1).id
                else:
                    # print('# zalo chưa có trong hệ thống')
                    get_info = ICS.get_name_zalo(zalo_id=zalo_id)
                    new_zalo = ChatZalo.create({
                        'name': get_info.get("display_name"),
                        'image_url':get_info.get("avatar"),
                        'zalo_id':zalo_id
                    })
                    new_zalo.compute_image()
                    author = new_zalo.name
                    ICS.create_log_zalo(zalo_id=zalo_id, mess=message_text, author=author)

                    new_partner = ResPartner.create({
                        'name':get_info.get("display_name"),
                        'zalo_id':zalo_id,
                        'image_url':get_info.get("avatar"),
                        'zalo_chat':new_zalo.id
                    })
                    new_partner.compute_image()
                    data_zalo['res_partner_id'] = new_partner.id

                # push notifi
                ICS.push_notifi_zl(res_partner_id=data_zalo.get('res_partner_id'), body=message_text)

            if event_name == 'user_submit_info':
                info_data = data_json.get("info")
                zalo_id = data_zalo['zalo_id'] = data_json.get("sender").get('id')
                ICS.user_submit_info(zalo_id=zalo_id,
                                     name=info_data.get("name"),
                                     phone=info_data.get("phone"),
                                     city=info_data.get("city"),
                                     district=info_data.get("district"),
                                     address=info_data.get("address")
                                     )
                # print('Đã cập nhật thông tin')
                partner_id = ResPartner.search([('zalo_id','=',zalo_id)],limit=1)
                zalo_name = partner_id.name
                ICS.push_notifi_zl(res_partner_id=partner_id.id, body='Khách hàng %s đã cập nhật thông tin qua Zalo' %zalo_name)

            if event_name == 'oa_send_text':
                zalo_id = data_json.get('recipient').get('id')
                mess = data_json.get('message').get('text')
                author = data_json.get('sender').get('admin_id') + ' - OA'
                check_zalo = ICS.check_zalo(zalo_id=zalo_id)
                if check_zalo:
                    ICS.create_log_zalo(zalo_id=zalo_id,mess=mess,author=author)
                else:
                    print('Khong thay tk zalo tuong ung')

            return "Webhook data received successfully"
        except Exception as e:
            return f"Error handling webhook data: {str(e)}"



