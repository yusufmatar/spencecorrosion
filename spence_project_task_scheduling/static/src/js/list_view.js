odoo.define('spence_task_scheduler.ListView', function (require) {
    "use strict";

    const ListModel = require('web.ListModel');
    const ListRenderer = require('web.ListRenderer');
    const ListController = require('web.ListController');
    const ListView = require('web.ListView');

    const UpdateAllListModel = ListModel.extend({
        resequence: function (modelName, resIDs, parentID, options) {
            return this._super.apply(this,arguments).then(()=>{
                this.trigger_up('reload')
            })
        },
    })

    const UpdateAllListController = ListController.extend({
        _saveRecord: function (recordId, options) {
            const res =  this._super.apply(this, arguments);
            this.trigger_up('reload');
            return res;
        },        
    })

    const UpdateAllListRenderer = ListRenderer.extend({
        // Since the order of the rows matter, we remove the ability to sort
        _renderHeaderCell: function (node) {
            const $th = this._super.apply(this,arguments)
            $th.removeClass('o_column_sortable')
            return $th
        }
    })

    var UpdateAllListView = ListView.extend({
        config: _.extend({}, ListView.prototype.config, {
            Model: UpdateAllListModel,
            Renderer: UpdateAllListRenderer,
            Controller: UpdateAllListController,
        }),
    });

    var viewRegistry = require('web.view_registry');
    viewRegistry.add('update_all_list_view', UpdateAllListView);

    return UpdateAllListView;
})