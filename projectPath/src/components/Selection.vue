<template>
  <div>
    <template v-if="disable">
      <selector :title="title"
                :placeholder="placeholder"
                v-model="data"
                :options="options|selectionOptions">
      </selector>
    </template>
    <template v-else>
      <group>
        <cell :title="title" :value="data|get_select_value(options)" ></cell>
      </group>
    </template>
  </div>
</template>

<script>
  import { Selector, Cell, Group } from 'vux'
  export default {
    props: ['title', 'placeholder', 'data', 'options', 'disable'],
    name: 'Selection',
    components: {
      Selector,
      Cell,
      Group
    },

    methods: {

    }
  }
</script>
