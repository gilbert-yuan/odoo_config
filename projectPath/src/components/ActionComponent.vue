<template>
  <div>
    <search
      @result-click="resultClick"
      @on-change="getResult"
      :results="searchResult"
      v-model="searchVal"
      position="fixed"
      limit='5'
      @on-cancel="onCancel"
      :autoFixed="true"
      style=" top: 44px"
      @on-submit="onSubmit"
      ref="search"></search>
    <scroller style="position:fixed; top: 84px;width:100%"
      :on-refresh="refresh"
      refresh-layer-color="#4b8bf4"
      loading-layer-color="#ec4949"
      :on-infinite="infinite">
      <svg class="spinner" style="stroke: #4b8bf4;" slot="refresh-spinner" viewBox="0 0 64 64">
        <g stroke-width="7" stroke-linecap="round">
          <line x1="10" x2="10" y1="27.3836" y2="36.4931">
            <animate attributeName="y1" dur="750ms" values="16;18;28;18;16;16"
                     repeatCount="indefinite">
            </animate>
            <animate attributeName="y2" dur="750ms" values="48;46;36;44;48;48"
                     repeatCount="indefinite">
            </animate>
            <animate attributeName="stroke-opacity" dur="750ms" values="1;.4;.5;.8;1;1"
                     repeatCount="indefinite">
            </animate>
          </line>
          <line x1="24" x2="24" y1="18.6164" y2="45.3836">
            <animate attributeName="y1" dur="750ms" values="16;16;18;28;18;16"
                     repeatCount="indefinite">
            </animate>
            <animate attributeName="y2" dur="750ms" values="48;48;46;36;44;48"
                     repeatCount="indefinite">
            </animate>
            <animate attributeName="stroke-opacity" dur="750ms" values="1;1;.4;.5;.8;1"
                     repeatCount="indefinite">
            </animate>
          </line>
          <line x1="38" x2="38" y1="16.1233" y2="47.8767">
            <animate attributeName="y1" dur="750ms" values="18;16;16;18;28;18"
                     repeatCount="indefinite">
            </animate>
            <animate attributeName="y2" dur="750ms" values="44;48;48;46;36;44"
                     repeatCount="indefinite">
            </animate>
            <animate attributeName="stroke-opacity" dur="750ms" values=".8;1;1;.4;.5;.8"
                     repeatCount="indefinite">
            </animate>
          </line>
          <line x1="52" x2="52" y1="16" y2="48">
            <animate attributeName="y1" dur="750ms" values="28;18;16;16;18;28"
                     repeatCount="indefinite">
            </animate>
            <animate attributeName="y2" dur="750ms" values="36;44;48;48;46;36"
                     repeatCount="indefinite">
            </animate>
            <animate attributeName="stroke-opacity" dur="750ms" values=".5;.8;1;1;.4;.5"
                     repeatCount="indefinite">
            </animate>
          </line>
        </g>
      </svg>
      <panel :list="treeList"
             type='5'
             v-if="0 < treeList.length"
             ></panel>
    </scroller>
  </div>
</template>
<script>
  import {Panel, Search} from 'vux'
  import {mapState} from 'vuex'
  export default {
    components: {
      Panel,
      Search
    },
    data: function () {
      return {
        scrollerStatus: '',
        searchVal: '',
        fields: [],
        show_views: {tree: {field: []}, search: {field: []}},
        all_field: {},
        currentAction: '',
        allRecordData: [],
        one_record_data: [],
        treeList: [],
        view_type: 'tree',
        form_fields: [],
        show_views_temporary: [],
        limit: 6,
        is_all_records_data: false,
        now_record_length: false,
        offset: 0,
        refresh_result_length: 0,
        dataDomain: [],
        results: [],
        value: 'test',
        searchResult: []
      }
    },
    computed: {
      ...mapState({
        vux: state => state.vux
      })
    },
    created: function () {
      this.$nextTick(function () {
        this.get_view_data()
      })
    },
    watch: {
      '$route': function (to, from) {
        this.treeList = []
        this.dataDoamin = []
        this.is_all_records_data = false
        this.vux.isLoading = true
        this.$nextTick(function () {
          this.vux.isLoading = false
          this.get_view_data()
        })
      },
      searchVal (newVal, oldVal) {
        var self = this
        for (var result of self.searchResult) {
          if (newVal && self.all_field) {
            result.title = newVal + '-' + self.all_field[result.other].string
          } else {
            result.title = self.all_field[result.other].string
          }
        }
      }
    },
    methods: {
      setFocus () {
        this.$refs.search.setFocus()
      },
      getResult () {
        return this.searchResult
      },
      onFocus () {

      },
      onCancel () {
        var self = this
        self.offset = 0
        self.treeList = []
        self.is_all_records_data = false
        self.dataDoamin = JSON.stringify([])
        self.get_more_data(0, 'fresh')
      },
      onSubmit () {
      },
      resultClick (result) {
        var self = this
        this.dataDoamin = JSON.stringify([[result.other, 'ilike', self.searchVal]])
        self.get_more_data(0, 'search')
      },
      get_search_field: function (searchView) {
        let parseString = require('xml2js').parseString
        parseString(searchView.arch, function (result, err) {
          if (err && err.search) {
            for (var field of err.search.field) {
              try {
                if (!self.all_field.hasOwnPrototype) {
                  self.searchResult.push({
                    title: self.all_field[field.$.name].string,
                    other: field.$.name
                  })
                }
              } catch (err) {
              }
            }
          }
        })
      },
      get_more_data: function (offset, type) {
        var searchReadUrl = '/mobile/odoo/search_read'
        var self = this
        self.$vux.loading.show()
        if (!self.currentAction) {
          return
        }
        this.$http.get(searchReadUrl, {
          params: {
            model: self.currentAction.res_model,
            offset: offset,
            limit: self.limit,
            domain: self.dataDoamin
          }
        }).then(function (res) {
          self.now_record_length = res.data.length
          if (type === 'add' && self.views) {
            if (res.data.length !== 6) {
              self.is_all_records_data = true
            } else {
              self.is_all_records_data = false
            }
            self.allRecordData = self.allRecordData.concat(res.data)
            self.xml_convert_to_json(self.views, res.data)
          } else if (self.views) {
            self.allRecordData = res.data
            self.treeList = []
            self.xml_convert_to_json(self.views, self.allRecordData)
          }
        })
      },
      get_view_data: function () {
        var url = '/mobile/odoo/action/load'
        var self = this
        self.$vux.loading.show()
        self.$http.get(url, {params: {action_id: self.$route.params.action_id}}).then(function (res) {
          self.$vux.loading.hide()
          self.currentAction = res.data.action
          self.views = res.data.views
          self.all_field = res.data.fields
          if (res.data.searchView) {
            self.get_search_field(res.data.searchView)
          }
          if (self.currentAction) {
            if (!self.currentAction.views) {
            }
            setTimeout(function () {
              self.get_more_data(self.offset, 'fresh')
            }, 100)
          }
        })
      },

      xml_get_all_field: function (form) {
        for (var xmlTag in form) {
          if (xmlTag === 'field') {
            if (Array.isArray(form[xmlTag])) {
              this.show_views_temporary.form.push.apply(this.show_views_temporary.form, form[xmlTag])
            } else {
              this.show_views_temporary.form.push(form[xmlTag])
            }
          } else if (typeof form[xmlTag] === 'object') {
            this.xml_get_all_field(form[xmlTag])
          }
        }
      },
      refresh: function (done) {
        var self = this
        self.offset = 0
        self.treeList = []
        self.is_all_records_data = false
        setTimeout(function () {
          self.get_more_data(0, 'fresh')
          done()
        }, 300)
      },
      infinite: function (done) {
        var self = this
        if (self.is_all_records_data || self.now_record_length < 6) {
          setTimeout(function () {
            done(true)
            self.is_all_records_data = false
          }, 1000)
          return
        }
        setTimeout(function () {
          self.offset = self.offset + 6
          self.get_more_data(self.offset, 'add')
          done()
        }, 1000)
      },
      xml_convert_to_json: function (fieldViews, recordData) {
        let self = this
        for (var view in fieldViews.fields_views) {
          let parseString = require('xml2js').parseString
          if (view === 'list') {
            self.all_field = fieldViews.fields_views[view].fields
            parseString(fieldViews.fields_views[view].arch, function (result, err) {
              self.fields = []
              for (var fieldIndex in err.tree.field) {
                self.fields.push(err.tree.field[fieldIndex].$.name)
              }
              self.compute_list(self.fields, recordData)
            })
          } else if (view === 'search') {
            for (let [key, searchField] in fieldViews.fields_views[view].fields) {
              self.searchResult.push({
                title: searchField.string,
                other: key
              })
            }
          }
        }
      },
      compute_list: function (fields, allRecordData) {
        var self = this
        var allFieldUrl = '/mobile/odoo/name_get'
        var recordIds = []
        for (let recordRow of allRecordData) {
          recordIds.push(recordRow.id)
        }
        self.$http.get(allFieldUrl, {
          params: {
            model: self.currentAction.res_model,
            ids: JSON.stringify(recordIds)
          }
        }).then(function (res) {
          self.$vux.loading.hide()
          if (res.data) {
            let nameIndex = 0
            for (let recordRow of allRecordData) {
              let oneRecord = {
                title: '',
                desc: '',
                url: {},
                meta: {}
              }
              oneRecord.title = res.data[nameIndex] && res.data[nameIndex++][1]
              let otherMessage = ''
              let descMessage = ''
              for (let field of fields) {
                if (recordRow[field]) {
                  let fieldRow = self.all_field[field]
                  if (['float', 'integer', 'datetime'].indexOf(fieldRow.type) >= 0) {
                    otherMessage = otherMessage + '  ' + fieldRow.string + ':' + recordRow[field]
                  } else if (['boolean'].indexOf(fieldRow.type) >= 0) {
                    otherMessage = otherMessage + '  ' + fieldRow.string + ':' + (recordRow[field] === 'false' ? '√' : '×')
                  } else if (['char', 'text'].indexOf(fieldRow.type) >= 0) {
                    descMessage = descMessage + '  ' + fieldRow.string + ':' + recordRow[field]
                  } else if (['many2one'].indexOf(fieldRow.type) >= 0) {
                    let man2oneIndex = 1
                    descMessage = descMessage + '  ' + fieldRow.string + ':' + recordRow[field][man2oneIndex]
                  } else if (['selection'].indexOf(fieldRow.type) >= 0) {
                    for (var selectionArray of fieldRow.selection) {
                      if (selectionArray[0] === recordRow[field]) {
                        descMessage = descMessage + '  ' + fieldRow.string + ':' + selectionArray[1]
                        break
                      }
                    }
                  }
                }
              }
              oneRecord.meta.other = otherMessage
              oneRecord.desc = descMessage
              oneRecord.url = '/odoo/' + self.$route.params.menu_id + '/' + self.$route.params.action_id + '/form/' + recordRow.id
              self.treeList.push(oneRecord)
            }
          }
        })
      }
    }
  }
</script>

<style lang="less">
  @import '~vux/src/styles/reset.less';
  .weui-cells.vux-search_show {
    margin-top: 0 !important;
    overflow-y: auto !important;
    position: fixed !important;
    width: 100% !important;
    height: auto !important;
    .weui-cell:last-child {
      margin-bottom: 0px !important;
    }
  }
</style>

