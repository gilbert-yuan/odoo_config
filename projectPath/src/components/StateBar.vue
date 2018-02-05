
<template>
  <flow>
    <template v-for="(option, index) in fieldSelection">
      <template v-if="index < nowIndex">
        <flow-state :state="index" 
        :title="option[1]" 
        :key='index'
        is-done></flow-state>
        <flow-line is-done></flow-line>
      </template>

      <template v-else-if="index === fieldSelection.length">
        <flow-state :state="index" 
        :title="option[1]"
        :key='index'
        ></flow-state>
      </template>

      <template v-else-if="index === nowIndex">
        <flow-state :state="index"
          :key='index'
          :title="option[1]"></flow-state>
        <flow-line tip="进行中"></flow-line>
      </template>

      <template v-else>
        <flow-state :state="index" 
        :key='index'
        :title="option[1]"></flow-state>
        <flow-line></flow-line>
      </template>
    </template>
  </flow>
</template>

<script>
  import { Flow, FlowState, FlowLine } from 'vux'
  export default {
    props: ['fieldSelection', 'NowState'],
    name: 'StateBar',
    components: {
      Flow,
      FlowState,
      FlowLine
    },
    data: function () {
      return {
        nowIndex: 0
      }
    },
    created: function () {
      for (var selection of this.fieldSelection) {
        this.nowIndex++
        if (this.NowState === selection[0]) {
          break
        }
      }
    },
    methods: {

    },
    watch: {

    }

  }
</script>
