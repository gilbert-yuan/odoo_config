<template>
 <div id="app-box">
   <router-view></router-view>
   <p>现在你看到我了</p>
   <ctable></ctable>
 </div>
</template>
<script>
  import CTable from './components/Table.vue'
  export default {
    components: {
      CTable
    },
    data () {
      return {

      }
    }
  }
</script>

<style lang="less">
</style>
