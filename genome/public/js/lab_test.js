
frappe.ui.form.on('Lab Test', {
    onload: function (frm) {  
        frm.set_query('provider_category_lab', () =>{
            return {
                filters: {
                    supplier_group: 'Reference Lab'
                }
            }
        })
        frm.set_query('provider_sample_collection', () =>{
            return {
                filters: {
                    supplier_group: 'Collection Agency'
                }
            }
        })
    },
	refresh :  function(frm){
		if (!frm.is_new()){
            frm.add_custom_button('Send Message', () => {
				frm.trigger("show_send_media_dialog");
            })
            frappe.call('genome.utils.lab_test.get_lab_test_finding_count',{ patient: frm.doc.patient, labtest: frm.doc.name }).then(r =>{
                let count = r.message;
                let html = frappe.render_template('lab_test_dashboard', {count});
                frm.dashboard.add_section(html);
                frm.dashboard.show();
                var lab_test_patient = frm.doc.patient;
                var lab_test_id = frm.doc.name;
                $(`[data-doctype= "Lab Test Finding"] a`).click(function (e) { 
                    e.preventDefault();
                    frappe.run_serially([
                        () => frappe.set_route('List', 'Lab Test Finding', 'List'),
                        () => {
                            if (cur_list.filter_area){
                                cur_list.filter_area.filter_list.clear_filters()
                            }
                        },
                        () => cur_list.lab_test_id = lab_test_id,
                        () => cur_list.refresh(),
                        () => frappe.listview_settings['Lab Test Finding'].onload(cur_list)
                    ]);
                });
                $(`[data-doctype= "Lab Test Finding"] button`).click(function (e) { 
                    e.preventDefault();
                    frappe.run_serially([
                        () => frappe.new_doc('Lab Test Finding'),
                        () => cur_frm.doc.patient = lab_test_patient,
                        () => cur_frm.doc.lab_test_id = lab_test_id,
                        () => cur_frm.refresh_fields(['patient', 'lab_test_id'])
                    ]);
                });
            })
        }
    },
    show_send_media_dialog: function (frm) {  
        if (cur_frm.doc.d){
            cur_frm.doc.d.show();
            frm.trigger("set_reset_message_button");
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
                "depends_on": `eval: ["SMS","WhatsApp"].includes(doc.media_type)`})
            
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
                "fieldtype": "Long Text"})

            new_fields.push({   
                "label": __("Reset Message"),
                "fieldname": "reset_message",
                "fieldtype": "Button"})
            
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
            frm.trigger("set_reset_message_button");

        }
    },
    set_reset_message_button: function () {  
        cur_frm.doc.d.fields_dict.reset_message.$input.click(function () {
            var args = cur_frm.doc.d.get_values();
            frappe.db.get_doc('SMS Template', args.template).then(doc => {
                cur_frm.doc.d.set_value('message', doc.sms_text);
                cur_frm.trigger("set_token");
            })
        });
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
                    })
                })
            }
        })
    }
});

var make_sms_dialog = function(frm, printed) {
	var number = frm.doc.mobile;
	// debugger;
	if(frm.doc.sms_sent == 1){
		frappe.msgprint(__('Messages is already sent!'));
	}
	var dialog = new frappe.ui.Dialog({
		title: 'Send SMS',
		width: 400,
		fields: [
			{fieldname:'sms_type', fieldtype:'Read Only', label:'Type', Default:
			'Printed', hidden:1},
			{fieldname:'number', fieldtype:'Data', label:'Mobile Number', reqd:1},
			{fieldname:'messages_label', fieldtype:'HTML'},
			{fieldname:'messages', fieldtype:'HTML'}
		],
		primary_action_label: __("Send"),
		primary_action : function(){
			var values = dialog.fields_dict;
			if(!values){
				return;
			}
			send_sms(values,frm);
			dialog.hide();
		}
	});
	dialog.set_values({
		'sms_type': "Printed",
		'number': number
	});
	dialog.fields_dict.messages_label.html("Message".bold());
	dialog.fields_dict.messages.html(printed);
	var fd = dialog.fields_dict;
	$(fd.sms_type.input).change(function(){
		dialog.set_values({
			'number': number
		});
		fd.messages_label.html("Message".bold());
		fd.messages.html(printed);
	});
	dialog.show();
};

var send_sms = function(v,frm){
	var doc = frm.doc;
	debugger
	var number = v.number.last_value;
	var messages = v.messages.wrapper.innerText;
	frappe.call({
		method: "frappe.core.doctype.sms_settings.sms_settings.send_sms",
		args: {
			receiver_list: [number],
			msg: messages
		},
		callback: function(r) {
			if(r.exc) {frappe.msgprint(r.exc); return; }
			else{
				frappe.call({
					method: "erpnext.healthcare.doctype.lab_test.lab_test.update_lab_test_print_sms_email_status",
					args: {print_sms_email: "sms_sent", name: doc.name},
					callback: function(){
						cur_frm.reload_doc();
					}
				});
			}
		}
	});
};