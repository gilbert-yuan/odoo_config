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
    <panel :list="treeList" type='5' style="position:autoFixed; top: 84px;"></panel>
  </div>
</template>

<script>
  import {Panel, Search} from 'vux'
  export default {
    props: ['treeList', 'searchResult', 'searchVal', 'onCancel', 'onSubmit', 'getResult', 'resultClick'],
    name: 'Tree',
    components: {
      Panel,
      Search,
    }
  }
</script>

<style lang="less">
  @import '~vux/src/styles/reset.less';
  .weui-cells.vux-search_show {
    margin-top: 0!important;
    overflow-y: auto!important;
    position: fixed!important;
    width: 100%!important;
    height: auto!important;
    .weui-cell:last-child {
      margin-bottom: 0px!important;
    }
    &::-webkit-scrollbar {
      display: none;
    }
    &::after {
      display: none;
    }
  }
</style>

