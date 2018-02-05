<template>
  <group :title='cLabel'>
    {{valIds}} {{cVal}}
    <div v-for="row in currencyTreeList">
      <cell :title="row.title"
      :inline-desc="row.desc"
      link="https://vux.li/demos/v2/?x-page=v2-doc-home#/component/cell"
      ></cell>
    </div>
  </group>
</template>
<script>
  import {Group, Cell} from 'vux'

  export default {
    name: 'One2Many',
    props: ['label', 'field', 'valIds'],
    components: {
      Group, Cell
    },
    data: function () {
      return {
        fields: [],
        cLabel: this.label,
        cField: this.field,
        cVal: this.valIds,
        currencyTreeList: [],
        resModel: '',
        allRecordData: []
      }
    },
    watch: {
      cVal: function (newVal, oldVal) {
        this.currencyTreeList = []
        var self = this
        var searchReadUrl = '/mobile/odoo/search_read'
        console.log(this.cField.relation)
        this.resModel = this.cField.relation
        console.log(self.cField)
        console.log(newVal)
        if (this.cValIds) {
          this.$http.get(searchReadUrl, {
            params: {
              model: this.cField.relation,
              domain: JSON.stringify([['id', 'in', this.cValIds]])
            }
          }).then(function (res) {
            this.allRecordData = res.data
            for (var view in this.cField.views) {
              if (view === 'tree') {
                console.log(this.cField.views)
                this.compute_list(this.cField.views[view].arch.field)
              }
            }
          })
        }
      }
    },
    created: function () {
      var self = this
      var searchReadUrl = '/mobile/odoo/search_read'
      console.log(this.cField.relation)
      self.resModel = this.cField.relation
      console.log(self.cField)
      console.log(this.cVal)
      if (self.cVal) {
        self.$http.get(searchReadUrl, {
          params: {
            model: this.cField.relation,
            domain: JSON.stringify([['id', 'in', self.cVal]])
          }
        }).then(function (res) {
          self.allRecordData = res.data
          console.log(self.cField.views)
          for (var view in self.cField.views) {
            if (view === 'tree') {
              console.log(self.cField.views)
              self.compute_list(self.cField.views[view].arch.field)
            }
          }
        })
      }
    },
    methods: {
      compute_list: function (fields) {
        var self = this
        var allFieldUrl = '/mobile/odoo/name_get'
        var recordIds = []
        self.currencyTreeList = []
        for (let recordRow of self.allRecordData) {
          recordIds.push(recordRow.id)
        }
        self.$http.get(allFieldUrl, {
          params: {
            model: self.resModel,
            ids: JSON.stringify(recordIds)
          }
        }).then(function (res) {
          if (res.data) {
            var nameIndex = 0
            for (let recordRow of self.allRecordData) {
              var oneRecord = {
                title: '',
                desc: '',
                url: {},
                meta: {}
              }
              oneRecord.title = res.data[nameIndex] && res.data[nameIndex++][1]
              let descMessage = ''
              for (var field in fields) {
                let fieldRow = fields[field]
                if (recordRow[field]) {
                  if (['float', 'integer', 'datetime'].indexOf(fieldRow.type) >= 0) {
                    descMessage = descMessage + '  ' + fieldRow.string + ':' + recordRow[field]
                  } else if (['boolean'].indexOf(fieldRow.type) >= 0) {
                    descMessage = descMessage + '  ' + fieldRow.string + ':' + (recordRow[field] === 'false' ? '√' : '×')
                  } else if (['char', 'text'].indexOf(fieldRow.type) >= 0) {
                    descMessage = descMessage + '  ' + fieldRow.string + ':' + recordRow[field]
                  } else if (['selection'].indexOf(fieldRow.type) >= 0) {
                    for (let selectionArray of fieldRow.selection) {
                      if (selectionArray[0] === recordRow[field]) {
                        descMessage = descMessage + '  ' + fieldRow.string + ':' + selectionArray[1]
                        break
                      }
                    }
                  }
                }
              }
              oneRecord.desc = descMessage
              oneRecord.url = '/odoo/' + self.$route.params.menu_id + '/' + self.$route.params.action_id + '/form/' + recordRow.id
              self.currencyTreeList.push(oneRecord)
            }
          }
        })
      }
    }
  }
</script>
