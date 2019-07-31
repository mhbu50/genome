frappe.ui.form.on('Patient', {
	validate: function(frm) {
        if(frm.doc.__islocal){
            // frm.set_value("hash_id",Math.random().toString(36).substr(2, 10));
        }	 
  }
});
