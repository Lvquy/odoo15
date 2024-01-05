from odoo import api, fields, models
import requests
import logging
import base64
_logger = logging.getLogger(__name__)
class ImageFromURLMixin:
   def get_image_from_url(self, url):
       """
       :return: Returns a base64 encoded string.
       """
       data = ""
       try:
           # Python 2
           # data = requests.get(url.strip()).content.encode("base64").replace("\n", "")
           # Python 3
           data = base64.b64encode(requests.get(url.strip()).content).replace(b"\n", b"")
       except Exception as e:
           _logger.warning("Can’t load the image from URL %s" % url)
           logging.exception(e)
       return data

from odoo import api, fields, models
class Custom(models.Model, ImageFromURLMixin):
   _name = "custom.custom"
   _description = "Custom"
   image_url = fields.Char(string="Image URL", required=True)
   image = fields.Binary(string="Image", compute="_compute_image", store=True,
                         attachment=False)
   @api.depends("image_url")
   def _compute_image(self):
     for record in self:
           image = None
           if record.image_url:
               image = self.get_image_from_url(record.image_url)
               self.check_access_rule()
           record.update({"image": image, })