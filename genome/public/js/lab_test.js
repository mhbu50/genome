
frappe.ui.form.on('Lab Test', {
	refresh :  function(frm){
	
		if(frm.doc.docstatus==1 && frm.doc.sms_sent==0){
			frm.add_custom_button(__('Send SMS 2'), function() {
				frappe.call({
					method: "genome.genome.tool.add_pdf",
                    args: {
						doc: frm.doc.name,
						disease: frm.doc.disease,
						lab_test_result_file: frm.doc.lab_test_result_file,
						arabic_result_file: frm.doc.arabic_result_file
					},
					callback: function(r) {
						// frappe.msgprint(__("There were."));
					}
				});
			});
		}

	}
});
