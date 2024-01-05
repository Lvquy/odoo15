odoo.define('zalo_oa.zalo_oa', function (require) {
    "use strict";

    var core = require('web.core');
    var WebClient = require('web.WebClient');

    var _t = core._t;

    WebClient.include({
        display_notification: function (notification) {
            this.do_notify(
                notification.params.title || _t('Notification'),
                notification.params.message || '',
                notification.params.sticky || false,
                notification.params.type || 'info'
            );
        },
    });
});
