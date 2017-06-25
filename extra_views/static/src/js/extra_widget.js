odoo.define('ExtraWidget', function(require) {
    "use strict";

    var config = require('web.config');
    var core = require('web.core');
    var Model = require('web.DataModel');
    var formats = require('web.formats');
    var Widget = require('web.Widget');

    var _t = core._t;
    var QWeb = core.qweb;

    // hide top legend when too many item for device size
    var MAX_LEGEND_LENGTH = 25 * (1 + config.device.size_class);

    return Widget.extend({
        className: "o_extra_svg_container",
        init: function(parent, model, options) {
            this._super(parent);
            this.context = options.context;
            this.fields = options.fields;
            this.fields.__count__ = { string: _t("Count"), type: "integer" };
            this.model = new Model(model, { group_by_no_leaf: true });
            this.extra_view_options= options.extra_view_options;
            this.domain = options.domain || [];
            this.groupbys = options.groupbys || [];
            this.mode = options.mode || "bar";
            this.measure = options.measure || "__count__";
            this.stacked = options.stacked;
            this.name = this.getParent().ViewManager.title;
        },
        start: function() {
            return this.load_data().then(this.proxy('display_graph'));
        },
        update_data: function(domain, groupbys) {
            this.domain = domain;
            this.groupbys = groupbys;
            return this.load_data().then(this.proxy('display_graph'));
        },
       /* set_measure: function(measure) {
            this.measure = measure;
            return this.load_data().then(this.proxy('display_graph'));
        },*/
        load_data: function() {
            var self = this;
            self.fields_contact = self.groupbys.slice(0);
            if (self.measure !== '__count__'.slice(0))
                self.fields_contact = self.fields_contact.concat(this.measure);
            return self.model
                .query( self.fields_contact)
                .filter(self.domain)
                .context(self.context)
                .lazy(false)
                .group_by(self.groupbys)
                .then(this.proxy('prepare_data'));
        },
        prepare_data: function() {
            var raw_data = arguments[0],
                is_count = this.measure === '__count__';
            var data_pt, j, values, value;
            this.data = [];
            this.labels = []
            for (var i = 0; i < raw_data.length; i++) {
                data_pt = raw_data[i].attributes;
                values = [];
                if (this.groupbys.length === 1) data_pt.value = [data_pt.value];
                for (j = 0; j < data_pt.value.length; j++) {
                    values[j] = this.sanitize_value(data_pt.value[j], data_pt.grouped_on[j]);
                    if (this.labels.length > j) {
                        this.labels[j].push(values[j])
                    } else {
                        this.labels.push([])
                        this.labels[j].push(values[j])
                    }
                }
                value = is_count ? data_pt.length : data_pt.aggregates[this.measure];
                this.data.push({
                    labels: values,
                    value: value
                });
            }
        },
        sanitize_value: function(value, field) {
            if (value === false) return _t("Undefined");
            if (value instanceof Array) return value[1];
            if (field && this.fields[field] && (this.fields[field].type === 'selection')) {
                var selected = _.where(this.fields[field].selection, { 0: value })[0];
                return selected ? selected[1] : value;
            }
            return value;
        },
        display_graph: function() {
            var self=this;
            self.$el.empty();
            if (!self.data.length) {
                self.$el.append(QWeb.render('ExtraViews.error', {
                    title: _t("没有数据"),
                    description: _t("No data available for this chart. " +
                        "Try to add some records, or make sure that " +
                        "there is no active filter in the search bar."),
                }));
            } else {
                self.display_views();
            }
        },
        display_views: function() {
            var self = this;
            _.each(self.extra_view_options, function (view_option) {
                var myChart = echarts.init(self.$el.parents().find("#"+view_option[1].div_id)[0]);
                var my_options = self.get_options(view_option[0], view_option);
                myChart.setOption(my_options, true);
            });
          /*  var myChart = echarts.init(self.$el.parents().find('#main_bar')[0]);
            var myChart_pie = echarts.init(self.$el.parents().find('#main_pie')[0]);
            var my_options = self.get_bar_option();
            var my_options_pie = self.get_pie_option();
            myChart.setOption(my_options, true);
            myChart_pie.setOption(my_options_pie, true);*/
            return  true;
        },
        get_options: function(mode_name, args) {
            return eval("this.get_" + mode_name + "_option("+JSON.stringify(args)+")");
        },
        prepare_bar_data: function(view_option, xaxis_data, legend_data) {
            var self = this,
                series_data = [];
            _.each(self.data, function(data_row) {
                if (xaxis_data && !legend_data) {
                    series_data.push(data_row.value);
                } else if (xaxis_data && legend_data) {
                    var row_index = series_data.find(function(row) {
                        console.log(data_row.labels[1]);
                        return row.name === data_row.labels[1];
                    });
                    if (row_index) {
                        row_index.data.push(data_row.value)
                    } else {
                        series_data.push({
                            'name': data_row.labels[1],
                            'type': 'bar',
                            'stack': self.context.bar_type && data_row.labels[1] || 'sum',
                            'data': [data_row.value]
                        });
                    };
                };

            });
            return {
                    xaxis_data:xaxis_data,
                    legend_data:legend_data,
                    series_data:series_data,
                }
        },
        get_bar_option: function(view_option) {
            var self = this;
            console.log(self.fields_contact, view_option);
            var show_legend_field_index= view_option[1].fields[0];
            var show_xaxis_field_index= view_option[1].fields[1];
            var legend_data = this.labels && _.unique(this.labels[self.fields_contact.indexOf(show_legend_field_index)]) || [];
            var xaxis_data = this.labels && _.unique(this.labels[self.fields_contact.indexOf(show_xaxis_field_index)]) || [];
            var return_val = self.prepare_bar_data(view_option, legend_data, xaxis_data);
            var option = {
                title: {
                    text: self.name,
                    x: 'left'
                },
                tooltip: {
                    show: true
                },
                toolbox: self.bar_tool_box(),
                calculable: true,
                legend: {
                    x: 'right',
                    data: return_val.legend_data || []
                },
                xAxis: [{
                    type: 'category',
                    data: return_val.xaxis_data || []
                }],
                yAxis: [{
                    type: 'value'
                }],
                series: return_val.series_data || [],
            };
            return option;
        },
        prepare_pie_data: function(xaxis_data) {
            var self = this,
                series_data=[];
            _.each(self.data, function(data_row) {
                 var common_data = xaxis_data.filter(function(v){ return data_row.labels.indexOf(v) > -1 })[0]
                var row_index = series_data.find(function(row) {
                    console.log(data_row.labels[0]);
                    return row.name === common_data;
                })
                if (row_index) {
                    row_index.value += data_row.value
                } else {
                    series_data.push({ 'value': data_row.value, 'name': common_data})
                }
            });
            return series_data
        },
        get_pie_option: function(view_option) {
            var self = this;
            var show_xaxis_field_index= view_option[1].fields[0];

            var xaxis_data = this.labels && _.unique(this.labels[self.fields_contact.indexOf(show_xaxis_field_index)]) || [];
            console.log(xaxis_data);
            var series_data = self.prepare_pie_data(xaxis_data);
            var option = {
                title: {
                    text: self.name,
                },
                tooltip: {
                    trigger: 'item',
                    formatter: "{a} <br/>{b} : {c} ({d}%)"
                },
                legend: {
                    x: 'right',
                    data: xaxis_data
                },
                toolbox: self.pie_tool_box(series_data),
                calculable: true,
                series: [{
                    name: self.name,
                    type: 'pie',
                    radius: '55%',
                    center: ['50%', '60%'],
                    data: series_data,
                }],
            };
            return option;
        },

        bar_tool_box: function() {
            var toolbox = {
                show : true,
                orient: 'vertical',
                x: 'right',
                y: 'center',
                feature : {
                    mark : {show: true},
                    dataView : {show: true, readOnly: false},
                    magicType : {show: true, type: ['line', 'bar', 'stack', 'tiled']},
                    restore : {show: true},
                    saveAsImage : {show: true}
                }
            };
            return toolbox;
        },

        pie_tool_box: function(series_data) {
            var toolbox = {
                show: true,
                orient: 'vertical',
                x: 'right',
                y: 'center',
                feature: {
                    mark: { show: true },
                    dataView: { show: true, readOnly: false },
                    magicType: {
                        show: true,
                        type: ['pie', 'funnel'],
                        option: {
                            funnel: {
                                x: '25%',
                                width: '50%',
                                funnelAlign: 'left',
                                max: Math.max(series_data)
                            }
                        }
                    },
                    restore: { show: true },
                    saveAsImage: { show: true }
                }
            };
            return toolbox;
        }
    });
});