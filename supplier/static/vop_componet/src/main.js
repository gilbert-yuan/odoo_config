import Vue from 'vue'
import Editor from './components/Editor.vue'
import Images from './components/Images.vue'
import CTable from './components/Table.vue'

new Vue({
  el: '#product-editor',
  components: { Editor, Images, CTable }
})
Vue.config.devtools = true
Vue.component('editor', Editor)
Vue.component('images', Images)
Vue.component('ctable', CTable)
window.Vue = Vue
