frappe.ui.form.on('Sales Invoice',{
    refresh: function (frm) {  
        if (frm.doc.docstatus == 1){
            frm.add_custom_button('Send Message', () => {
				frm.trigger("show_send_media_dialog");
            })
        }
    },
    show_send_media_dialog: function (frm) {  
        if (cur_frm.doc.d){
            cur_frm.doc.d.show();
            // frm.trigger("set_reset_message_button");
        }else{
            let new_fields = []
            new_fields.push({   
                "label": __("Media Type"), 
                "fieldname": "media_type", 
                "fieldtype": "Select", 
                "options": "SMS\nWhatsApp\nEmail",
                "reqd": 1})

            new_fields.push({
                "label": __("Mobile"),
                "fieldname": "mobile",
                "fieldtype": "Data",
                "depends_on": `eval: ["SMS","WhatsApp"].includes(doc.media_type)`,
                "read_only": 1})
            
            new_fields.push({   
                "label": __("Message Template"),
                "fieldname": "template",
                "fieldtype": "Link",
                "options": "SMS Template",
                "reqd": 1,
                onchange: function () {
                    var args = cur_frm.doc.d.get_values();
                    if (args.template != undefined) {
                        frappe.db.get_doc('SMS Template', args.template).then(doc => {
                            cur_frm.doc.d.set_value('message', doc.sms_text);
                            cur_frm.trigger("set_token");
                        })
                    }
                }})

            new_fields.push({   
                "label": __("Message"),
                "fieldname": "message",
                "fieldtype": "Long Text",
                "read_only": 1})

            cur_frm.doc.d = new frappe.ui.Dialog({
                fields: new_fields,
                primary_action: function (e) {
                    var v = cur_frm.doc.d.get_values();
                },
                primary_action_label: __('Send')
            })
            if (cur_frm.doc.mobile) {
                cur_frm.doc.d.set_value('mobile', cur_frm.doc.mobile);
            }
            cur_frm.doc.d.show()

        }
    },
    set_token: function () {  
        var args = cur_frm.doc.d.get_values();

        frappe.db.get_list("SMS Token",{
            fields: ["token", "days"],
            filters: {
                docstatus: 1,
                docname: cur_frm.docname,
                document_type: cur_frm.doctype
            }
        }).then( records =>{
            if (records.length > 0){
                var token = records[0].token;
                frappe.db.get_doc('SMS Template', args.template).then(doc => {
                    cur_frm.doc.d.set_value('message', doc.sms_text);
                }).then(r =>{
                    args.message = args.message.replace("{{token}}", token);
                    var doc_args = cur_frm.doc
                    args.message = frappe.render_template(`${args.message}`, {doc : doc_args}); 
                    cur_frm.doc.d.set_value("message", args.message);
                    if (!cur_frm.doc.access_token){
                        frappe.db.set_value('Sales Invoice', cur_frm.doc.name, 'access_token', token)
                        .then(r => {
                            cur_frm.reload_doc()
                        })
                    }
                })
            }else{
                var token = frappe.utils.get_random(16)
                frappe.db.get_doc('SMS Template', args.template).then(doc => {
                    cur_frm.doc.d.set_value('message', doc.sms_text);
                }).then(r =>{
                    args.message = args.message.replace("{{token}}", token);
                    var doc_args = cur_frm.doc
                    args.message = frappe.render_template(`${args.message}`, {doc : doc_args}); 
        
                    frappe.db.insert({
                        doctype: 'SMS Token',
                        token: token,
                        docname: cur_frm.docname,
                        document_type: cur_frm.doctype,
                        days: 10,
                        docstatus: 1
        
                    }).then(doc => {
                        cur_frm.doc.d.set_value("message", args.message);
                        if (!cur_frm.doc.access_token){
                            frappe.db.set_value('Sales Invoice', cur_frm.doc.name, 'access_token', token)
                            .then(r => {
                                cur_frm.reload_doc()
                            })
                        }
                    })
                })
            }
        })
    }
})