<template>
    <cell :title="title" :value="value"   is-link  @click.native="onclick_many2one()"></cell>
</template>

<script>
  import { Cell } from 'vux'
  export default {
    props: ['title', 'value', 'field', 'menu', 'id'],
    name: 'Many2one',
    components: {
      Cell
    },
    data: function () {
      return {
        disable: false,
        many2one_link: {path: ''}
      }
    },
    created: function () {

    },
    methods: {
      onclick_many2one: function () {
        var url = '/mobile/odoo/getActionId'
        var self = this
        self.$http.get(url, {params: {model: self.field.relation}}).then(function (res) {
          self.many2one_link.path = '/mobile/' + self.menu + '/' + res.data.actionId + '/form/' + self.id
        })
      }
    }
  }
</script>
