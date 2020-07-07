frappe.listview_settings['Lab Test Finding'] = {
    onload: function (listview) {
        if (cur_list.lab_test_id){
            cur_list.filter_area.filter_list.clear_filters();
            listview.filter_area.filter_list.add_filter(
            'Lab Test Finding', 'lab_test_id', 'Equals', cur_list.lab_test_id)
            listview.refresh()
        }
    }
}