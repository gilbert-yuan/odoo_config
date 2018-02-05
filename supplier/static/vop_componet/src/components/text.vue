<style type="text/css">
.text-input textarea {
    position:absolute;
    top:0;
    left:0;
    height:100%;
    border: 1px solid #cccccc;
    border-radius: 3px;
    -webkit-box-shadow: rgba(0, 0, 0, 0.2) 0 1px 2px 0;
	-moz-box-shadow: rgba(0, 0, 0, 0.2) 0 1px 2px 0;
	-ms-box-shadow: rgba(0, 0, 0, 0.2) 0 1px 2px 0;
	-o-box-shadow: rgba(0, 0, 0, 0.2) 0 1px 2px 0;
	box-shadow: rgba(0, 0, 0, 0.2) 0 1px 2px 0;
    width: 100%;
    padding-left: 5px;
    padding-top: 6px;
    font-size: 18px;
    resize: none;
}

.text-input .expandingArea {
    position:relative;
    font-size: 18px;
}

.text-input pre {
    display:block;
    font-size: 18px;
    visibility:hidden;
}
</style>

<template>
    <div class="text-input">
        <div class="expandingArea ">
            <pre><span>{{model.value}}</span><br></pre>
            <textarea @input.prevent="input_change" placeholder="输入描述内容" @keydown.down="next_textarea"
                      @keydown.up="prev_textarea" @keydown.enter="enter_input"  v-model="model.value"></textarea>
        </div>
    </div>
</template>

<script>
import Vue from 'vue'
export default {
  props: ['model', 'index'],
  methods: {
    enter_input: function (env) {
      if (env.shiftKey) {
        env.preventDefault()
        var eventHub = new Vue()
        eventHub.$emit('add-text', this.index)
      }
    },
    next_textarea: function (env) {
      if (env.shiftKey) {
        env.preventDefault()
        var eventHub = new Vue()
        eventHub.$emit('next-textarea', this.index)
      }
    },
    prev_textarea: function (env) {
      if (env.shiftKey) {
        env.preventDefault()
        var eventHub = new Vue()
        eventHub.$emit('prev-textarea', this.index)
      }
    },
    input_change: function (env) {
      var eventHub = new Vue()
      eventHub.$emit('text-input-change', this.index)
    }
  }
}
</script>
