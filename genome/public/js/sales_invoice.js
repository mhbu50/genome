frappe.ui.form.on('Sales Invoice',{
    refresh: function (frm) {  
        if (frm.doc.docstatus == 1){
            frm.add_custom_button('Send Message', () => {
                frappe.db.get_list('Print Format', {
                    fields: ['name', 'standard'],
                    filters: {
                        doc_type: 'Sales Invoice'
                    }
                }).then(records => {
                    let print_formats = ""
                    for (let i in records){
                        print_formats +=`\n${records[i].name}`
                    }
                    cur_frm.doc.d_print_format_options = print_formats
                    frm.trigger("show_send_media_dialog");
                })
            })
        }
    },
    show_send_media_dialog: function (frm) {  
        if (cur_frm.doc.d){
            cur_frm.doc.d.show();
        }else{
            // Getting Mobile Numbers
            let patient_numbers = "";
            let patient_default_number = "";

            frappe.call("genome.api.lab_test.get_patient_mobile_numbers",{
                "patient": frm.doc.patient
            }).then(r => {
                
                if (r.message.length > 0){
                    patient_numbers = r.message.split("\n");
                    patient_default_number = patient_numbers[0];
                }else{
                    patient_numbers = "Not Available";
                    patient_default_number = "Not Available";
                }

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
                        "fieldtype": "Select",
                        "options": patient_numbers,
                        "default": patient_default_number,
                        "depends_on": `eval: ["SMS","WhatsApp"].includes(doc.media_type)`
                    })
                
                new_fields.push({
                    "label": __("Print Format"),
                    "fieldname": "print_format",
                    "fieldtype": "Select",
                    "options": cur_frm.doc.d_print_format_options,
                    "reqd": 1,
                    onchange: function () {
                        const template = cur_frm.doc.d.get_value('template')
                        if (template){
                            cur_frm.doc.d.set_value('template', template)
                        }
                        }
                    })
                
                new_fields.push({   
                    "label": __("Message Template"),
                    "fieldname": "template",
                    "fieldtype": "Link",
                    "options": "SMS Template",
                    "reqd": 1,
                    onchange: function () {
                        let args = cur_frm.doc.d.get_values();
                        if (args.template != undefined) {
                            frappe.db.get_doc('SMS Template', args.template).then(doc => {
                                frappe.call("genome.api.sales_invoice.get_attachment_link", {
                                    doc: cur_frm.doc.name,
                                    print_format: args.print_format
                                }).then(r =>{
                                    let doc_args = cur_frm.doc
                                    args.message = frappe.render_template(`${doc.sms_text}`, {doc : doc_args}); 
                                    args.message += '\n\n' + r.message
                                    cur_frm.doc.d.set_value('message', args.message);
                                })
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
                        let v = cur_frm.doc.d.get_values();
                        frappe.call("frappe.core.doctype.sms_settings.sms_settings.send_sms",
                        {receiver_list: [v.mobile], msg: v.message})
                        .then(r =>{
                            cur_frm.doc.d.hide()
                        })
                    },
                    primary_action_label: __('Send')
                })
                if (cur_frm.doc.patient_mobile) {
                    cur_frm.doc.d.set_value('mobile', cur_frm.doc.patient_mobile);
                }
                cur_frm.doc.d.show()
            })
        }
    }
})