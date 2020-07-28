// Copyright (c) 2020, Accurate Systems and contributors
// For license information, please see license.txt

frappe.ui.form.on('Lab Test Finding', {
	refresh: function(frm) {

	}
});

frappe.ui.form.on('Lab Test Finding Diseases', {
	set_disease_sub_type: function (frm, cdt, cdn) {  
		let row = frappe.get_doc(cdt, cdn)
		if (row.disease_name){
			frappe.db.get_doc('Diseases', row.disease_name)
			.then(doc => {
				let value = ''
				for (let i in doc.diseases_sub_types){
					value += '\n' + doc.diseases_sub_types[i].disease_sub_type
				}
				let d = new frappe.ui.Dialog({
					title: 'Enter details',
					fields: [
						{
							label: 'Disease Sub Type',
							fieldname: 'disease_sub_type',
							fieldtype: 'Select',
							options: value
						},
					],
					primary_action_label: 'Select',
					primary_action(values) {
						row.disease_sub_type = values.disease_sub_type;
						d.hide();
						frm.refresh_field('diseases');
					}
				});
				
				d.show();
			})
		}else{
			frappe.msgprint(__('Please select disease name first.'))
		}
	}
})