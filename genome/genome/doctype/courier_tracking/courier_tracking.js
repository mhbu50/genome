// Copyright (c) 2020, Accurate Systems and contributors
// For license information, please see license.txt

frappe.ui.form.on('Courier Tracking', {
	refresh: function(frm) {
		frm.events.set_query(frm);
	},
	set_query: function (frm){
		frm.set_query('courier', () => {
			return {
				filters: {
					'supplier_group': 'Courier'
				}
			}
		})
	}
});
