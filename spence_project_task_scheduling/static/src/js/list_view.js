odoo.define('spence_task_scheduler.ListView', function (require) {
    "use strict";

    const ListModel = require('web.ListModel');
    const ListRenderer = require('web.ListRenderer');
    const ListController = require('web.ListController');
    const ListView = require('web.ListView');
    
    const SpreadsheetListModel = ListModel.extend({
        // Trigger an update when dragging rows
        resequence: function (modelName, resIDs, parentID, options) {
            return this._super.apply(this,arguments).then(()=>{
                this.trigger_up('reload')
            })
        },
    })

    const SpreadsheetListController = ListController.extend({
        // After updating the values on the backend, we trigger the ui to update.
        _saveRecord: function (recordId, options) {
            const res =  this._super.apply(this, arguments);
            this.trigger_up('reload');
            return res;
        },        
    })

    const SpreadsheetListRenderer = ListRenderer.extend({
        // Since the order of the rows matter, we remove the ability to sort
        _renderHeaderCell: function (node) {
            const $th = this._super.apply(this,arguments)
            $th.removeClass('o_column_sortable')
            return $th
        }
    })

    const SpreadsheetListView = ListView.extend({
        config: _.extend({}, ListView.prototype.config, {
            Model: SpreadsheetListModel,
            Renderer: SpreadsheetListRenderer,
            Controller: SpreadsheetListController,
        }),
    });

    const viewRegistry = require('web.view_registry');
    viewRegistry.add('spreadsheet_list_view', SpreadsheetListView);

    return SpreadsheetListView;
})