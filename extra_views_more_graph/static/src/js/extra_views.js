odoo.define('ExtraViews', function(require) {
    "use strict";
    /*---------------------------------------------------------
     * Odoo Graph view
     *---------------------------------------------------------*/

    var core = require('web.core');
    var data_manager = require('web.data_manager');
    var ExtraWidget = require('ExtraWidget');
    var View = require('web.View');

    var _lt = core._lt;
    var _t = core._t;
    var QWeb = core.qweb;

    var ExtraViews = View.extend({
        className: 'o_graph',
        display_name: _lt('ExtraViews'),
        icon: 'fa-bar-chart',
        require_fields: true,

        init: function() {
            this._super.apply(this, arguments);

            this.measures = [];
            this.active_measure = '__count__';
            this.initial_groupbys = [];
            this.widget = undefined;
        },
        willStart: function() {
            var self = this;
            var fields_def = data_manager.load_fields(this.dataset).then(this.prepare_fields.bind(this));
            this.fields_view.arch.children.forEach(function(field) {
                var name = field.attrs.name;
                if (field.attrs.interval) {
                    name += ':' + field.attrs.interval;
                }
                if (field.attrs.type === 'measure') {
                    self.active_measure = name;
                } else {
                    self.initial_groupbys.push(name);
                }
            });
            return $.when(this._super(), fields_def);
        },
        update_measure: function() {
            var self = this;
            this.$measure_list.find('li').each(function(index, li) {
                $(li).toggleClass('selected', $(li).data('field') === self.active_measure);
            });
        },
        do_show: function() {
            this.do_push_state({});
            return this._super();
        },
        prepare_fields: function(fields) {
            var self = this;
            this.fields = fields;
            _.each(fields, function(field, name) {
                if ((name !== 'id') && (field.store === true)) {
                    if (field.type === 'integer' || field.type === 'float' || field.type === 'monetary') {
                        self.measures[name] = field;
                    }
                }
            });
            this.measures.__count__ = { string: _t("Count"), type: "integer" };
        },
        do_search: function(domain, context, group_by) {
            var self = this;
            self.client_view = self.getParent().getParent().getParent();
            self.control_panel = $(self.client_view.$el.find('.o_control_panel')[0]);
            self.sub_menu = $(self.client_view.$el.find('.o_sub_menu')[0]);
            self.control_panel.css('display','none');
            self.sub_menu .css('display','none');
            if (!this.widget) {
                var extra_view_options = eval("("+this.fields_view.arch.attrs.extra_views_options+")");
                self.$el.append("<div class='container-fluid'><div class='row row-fluid'></div></div>");
                var row_div = self.$el.find('.row');
                var average_height =($(window).height()-35)/((extra_view_options.length - 1)/2 + 1);
                _.each(extra_view_options, function (views_option, index, list) {
                    var gragh_id = 'main_'+views_option[0]+index;
                    row_div.append($("<div id='"+gragh_id+"' class='col-md-6'\
                        style='min-width: 480px;min-height:"+average_height+"px;'></div>"));
                    extra_view_options[index][1].div_id = gragh_id;
                });
                /*<div id='main_pie' class='col-md-6' style='min-width: 480px;min-height:600px;'></div></div>");*/
                this.initial_groupbys = context.graph_groupbys || (group_by.length ? group_by : this.initial_groupbys);
                this.widget = new ExtraWidget(this, this.model, {
                    measure: context.graph_measure || this.active_measure,
                    mode: context.graph_mode || this.active_mode,
                    domain: domain,
                    groupbys: this.initial_groupbys,
                    context: context,
                    extra_view_options: extra_view_options,
                    fields: this.fields,
                    stacked: this.fields_view.arch.attrs.stacked !== "False"
                });
                this.widget.appendTo(this.$el);
            } else {
                var groupbys = group_by.length ? group_by : this.initial_groupbys.slice(0);
                this.widget.update_data(domain, groupbys);
            }
        },
        get_context: function() {
            return !this.widget ? {} : {
                graph_mode: this.widget.mode,
                graph_measure: this.widget.measure,
                graph_groupbys: this.widget.groupbys
            };
        },

        destroy: function() {
            var self =this;
            if (this.$buttons) {
                this.$buttons.find('button').off(); // remove jquery's tooltip() handlers
            }
            self.control_panel.css('display','inherit');
            self.sub_menu.css('display','inherit');
            return this._super.apply(this, arguments);
        },
    });

    core.view_registry.add('extra_views', ExtraViews);
    return ExtraViews;

});