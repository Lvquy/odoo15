# -*- coding: utf-8 -*-


from odoo import fields, models, api, _
from datetime import date, datetime
from odoo.exceptions import UserError
import base64
import xlrd
import os
import subprocess, json
from bs4 import BeautifulSoup
import requests
from odoo.http import request

from odoo import api, fields, models
import requests
import logging
import base64

_logger = logging.getLogger(__name__)
from pushbullet import Pushbullet

class ImageFromURLMixin:
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


class ZaloOA(models.Model):
    _name = 'zalo.oa'
    _description = 'Zalo OA'
    _rec_name = 'name'
    _inherit = 'mail.thread'

    name = fields.Char(string='Tiêu đề bài viết', size=150)
    description_post = fields.Text(string='Miêu tả', help='Giới hạn 300 ký tự')
    author_post = fields.Char(string='Tác giả', size=50)
    body_post = fields.Html(string='Nội dung')
    call_to_action = fields.Boolean(default=False, string='Call to action')
    content_action = fields.Char(string='Nội dung action')
    link_action = fields.Char(string='URL action')

    def show_toast(self):
        pb = Pushbullet("o.8ghYL8JqjSptWixWddXTQ6VUOXjkOrqH")
        print(pb.channels)
        push_note = pb.push_note("This is the title", "This is the body")
        my_channel = pb.channels[0]
        push = my_channel.push_note("Hello Channel!", "Hello My Channel")
        return push_note

class ZaloBlog(models.Model):
    _inherit = 'blog.post'
    _description = 'Zalo OA'

    def push_2_oa(self):
        ICP = self.env['ir.config_parameter'].sudo()
        url = 'https://openapi.zalo.me/v2.0/article/create'
        access_token = ICP.get_param('zalo_oa.access_token')
        web_base_url = ICP.get_param('web.base.url')
        web_base_url = "https://bienquangcaotruongphat.vn"
        headers = {
            "access_token": access_token,
            "Content-Type": "application/json"
        }

        # lấy toàn bộ url img
        soup = BeautifulSoup(self.content, 'html.parser')
        img_tags = soup.find_all('img')
        image_urls = [{'src': web_base_url + img['src'], 'alt': img.get('alt', '')} for img in img_tags]
        body = [
            {
                "type": "text",
                "content": self.name
            },
        ]
        for i in image_urls:
            body.append(
                {
                    "type": "image",
                    "url": i.get("src"),
                    "caption": i.get("alt")
                }
            )

        data = {
            "type": "normal",
            "title": self.name,
            "author": self.author_id.name,
            "cover": {
                "cover_type": "photo",
                "photo_url": "https://bienquangcaotruongphat.vn/web/image/3966-fdbcaf20/bien-quang-cao-dep.jpeg?access_token=2860a960-6e15-4ede-9def-c927c96709a8",
                "status": "show"
            },
            "description": self.website_meta_description,
            "body": body,
            "status": "hide",
            "comment": "show"
        }
        print(data)
        data_json = json.dumps(data)

        res = requests.post(url=url, headers=headers, data=data_json)
        if res.status_code == 200:
            print('ok', res.json())

            token = res.json().get("data")["token"] if res.json().get("error") != -223 else None
            print(token)
        else:
            print('err', res.text)

        if token:
            url_verify = 'https://openapi.zalo.me/v2.0/article/verify'
            headers_verify = {
                "access_token": access_token,
                "Content-Type": "application/json"
            }
            data_verify = json.dumps({
                "token": token
            })
            try:
                verify = requests.post(url=url_verify, headers=headers_verify, data=data_verify)
                if verify.status_code == 200:
                    print('verified', verify.json())
                else:
                    print('err verify', verify.text)
            except requests.exceptions.RequestException as e:
                print(f"Error making request: {e}")


class ChatZalo(models.Model, ImageFromURLMixin):
    _name = 'chat.zalo'
    _description = 'Nhận thông tin từ webhook khởi tạo chat zalo'
    _rec_name = 'name'

    name = fields.Char(string='Tên khách')
    image_url = fields.Char(string='URL image')
    image = fields.Binary(string="Image", store=True,
                          attachment=False)
    zalo_id = fields.Char(string='ID Zalo')
    log_chat = fields.One2many(comodel_name='log.chat', inverse_name='ref_chat', string='Log chat')
    mess = fields.Text(string='Mess')

    @api.onchange("image_url")
    def compute_image(self):
        for record in self:
            image = None
            if record.image_url:
                image = self.get_image_from_url(record.image_url)

            record.update({"image": image, })

    def send_mess(self):
        print('send')
        if self.mess:
            ICP = self.env['ir.config_parameter'].sudo()
            access_token = ICP.get_param('zalo_oa.access_token')
            print(access_token)
            url = 'https://openapi.zalo.me/v3.0/oa/message/cs'
            headers = {'access_token': access_token}
            body = {
                "recipient": {
                    "user_id": self.zalo_id
                },
                "message": {
                    "text": self.mess
                }
            }

            requests.post(url=url, headers=headers, data=json.dumps(body))
            self.log_chat.create({
                'text_chat': self.mess,
                'author': 'Trường Phát',
                'ref_chat': self.id,
                'date_chat': datetime.now()
            })
            self.mess = False

class LogChatZalo(models.Model):
    _name = 'log.chat'
    _description = 'lịch sử chat zalo của người dùng'
    _rec_name = 'ref_chat'

    text_chat = fields.Text(string='Text chat')
    ref_chat = fields.Many2one(comodel_name='chat.zalo', string='Tk Zalo')
    date_chat = fields.Datetime(string='Date', default=datetime.now())
    author = fields.Char(string='Người gửi')

