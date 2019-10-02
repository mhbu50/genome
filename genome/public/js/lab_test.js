
frappe.ui.form.on('Lab Test', {
	refresh :  function(frm){
	
		if(frm.doc.docstatus==1 && frm.doc.sms_sent==0){
			$("[data-label='Send%20SMS']").hide();
			frm.add_custom_button(__('Send SMS '), function() {
				frappe.call({
					method: "genome.genome.tool.add_pdf",
                    args: {
						doc: frm.doc.name
					}
				}).then((result) => {
					console.log("result",result);
					
					frappe.call({
						method: "erpnext.healthcare.doctype.healthcare_settings.healthcare_settings.get_sms_text",
						args:{doc: frm.doc.name},
						callback: function(r) {
							if(!r.exc) {
								var printed = r.message.printed;
								make_sms_dialog(frm, printed);
							}
						}
					});
				})

				
			});
		}

	}
});

var make_sms_dialog = function(frm, printed) {
	var number = frm.doc.mobile;
	debugger;
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