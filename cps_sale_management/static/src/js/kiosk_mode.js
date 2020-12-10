odoo.define('hr.attendance', function (require) {
'use strict';
var core = require('web.core');
var ajax = require('web.ajax');
var qweb = core.qweb;
ajax.loadXML('/hr_attendancce/static/src/xml/attendance.xml', qweb);
});