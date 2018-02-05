<template>
  <div>
    <template  v-for="(menu3, index) in last_leve_menu" >
      <cell :title="menu3.name"
       :value="menu3.name" is-link
       :key='index'
       @click.native="onclick_third_level_menu(menu3)"></cell>
    </template>
  </div>
</template>

<script>
  import { Cell } from 'vux'
  import {mapState} from 'vuex'

  export default {
    name: 'ChildMenu',
    components: {
      Cell
    },
    data: function () {
      return {
        last_leve_menu: []
      }
    },
    computed: {
      ...mapState({
        vux: state => state.vux
      })
    },
    created: function () {
      var self = this
      self.last_leve_menu = self.vux.third_menu
    },
    methods: {
      onclick_third_level_menu (menu) {
        this.$router.push({name: 'tree', params: {menu_id: menu.id, action_id: menu.action.split(',')[1]}})
        this.vux.title = menu.name
      }
    },
    watch: {
      '$route': function () {
        var self = this
        self.last_leve_menu = self.vux.third_menu
      }
    }
  }
</script>
