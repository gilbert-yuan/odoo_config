
<template>
  <div id="vux-editor">
    <div class="editor-loading">
      <div class="editor-loading-layer" :style="{width: loading_index + '%'}">
      </div>
    </div>

    <div class="editor-button">
      <a class="editor-button-save" @click="save">{{is_save? "保存成功": "保存编辑器"}}</a>
      <a v-if="many2one_choose.length === 0" class="editor-button-new" @click.prevent.stop="newRecord" >添加描述信息</a>
      <div v-if="many2one_choose.length > 0" class="many2one-choose" @mouseleave="choose_leave" @mouseover="choose_over">
        <a class="editor-button-new" >添加内容</a>
        <ul class="many2one-choose-list" v-show="is_display_many2one_choose" transition="expand">
          <li @click.prevent.self="do_many2one_choose(many2one)" v-for="many2one in many2one_choose">{{many2one.string}}</li>
          <li @click.prevent.self="newRecord" >添加描述信息</li>
        </ul>
      </div>
      <a class="editor-button-hidden" @click.prevent.stop="display_device">{{is_display_device? "关闭预览" : "打开预览"}}</a>
    </div>

    <div class="dftg-editor" @dragover.prevent="dragover" @dragend.prevent="dragend" @drop.prevent="drop" @dragenter.prevent.stop="dragenter" @dragleave.prevent.stop.self="dragleave" :class="{dragging: dragging}" >
      <ul id="product_items">
        <li @click="click_item(item_index)" class="editor-item" :class="{choosed: item_index == choose_index}" v-for="(item, item_index) in items" :data-index="item_index">
          <component :config="config" :model="item" :index="item_index" :is='item.component'>
          </component>
          <ul class="operator-set" @mouseleave="leave_operator">
            <li v-for="(operator, operator_index) in operators" @click.prevent.stop="do_operator(operator.method, item, item_index)"
                class="operator_icon" :class="operator.operator_icon" @mouseover.prevent.stop.self="move_operator(operator.method, item, item_index)"></li>

            <ul v-if="many2one_choose.length > 0" class="many2one-operator-choose-list" v-show="display_operator_choose === item_index" transition="expand">
              <li @click.prevent.self="do_operator_many2one_choose(many2one, item, item_index)" v-for="many2one in many2one_choose">{{many2one.string}}</li>
              <li @click.prevent.self="do_operator_many2one_choose(many2one, item, item_index, 'text')" >添加描述信息</li>
            </ul>
          </ul>
        </li>
      </ul>
      <div class="editor-comment" :class="[items.length > 1 || items[0].component === 'image-input'? 'editor-comment-hide': '' ]">
        <p>直接在图片拖放到这里就可以自动上传图片</p>
        <p>使用shift + 回车键直接创建一个新的行</p>
        <p>使用shift + 上/下 在不同行直接来回切换</p>
        <p>使用右边的保存编辑器按钮来保存所有编辑的描述</p>
      </div>
    </div>

    <div class="editor-device" v-show="is_display_device">
      <div class="editor-content">
        <template v-for="item in items">
          <div v-if="item.component === 'text-input'">{{ item.value}}</div>
          <img v-if="item.component === 'image-input'" :src="item.value" />
        </template>
      </div>
    </div>
  </div>
</template>

<script>
  import textInput from './text.vue'
  import imageInput from './image.vue'
  import Vue from 'vue'
  import Sortable from 'sortablejs'
  var $ = require('jquery')
  var data = {
    loading_index: 0,
    items: [{value: '', component: 'text-input', record: {}}],
    operators: [
      {'method': 'plus', 'operator_icon': 'operator_icon_plus'},
      {'method': 'delete', 'operator_icon': 'operator_icon_delete'}
    ],
    is_display_many2one_choose: false,
    display_operator_choose: -1,
    dragging: false,
    choose_index: -1,
    loading: false,
    delete_items: [],
    is_display_device: true,
    is_fullscreen: false,
    original_height: 0,
    is_preview: false,
    is_save: false
  }
  function _wrapTextItem (value) {
    return {
      id: 0,
      value: value || '',
      component: 'text-input',
      record: {}
    }
  }
  function prevSortable () {
    var el = document.getElementById('product_items')
    Sortable.create(el, {
      ghostClass: 'ghost',
      group: 'foo',
      animation: 150,
      onUpdate: function (env) {
        // 使用attr而不是data来获取实际的index，vue重绘了界面之后，使用data依然取到的是存在数据节点以前的值
        env.item.remove()
        env.from.insertBefore(env.item, $(env.from).find('.editor-item').get(env.oldIndex))
        data.items.splice(env.newIndex, 0, data.items.splice(env.oldIndex, 1)[0])
      }
    })
  }

  // function _wrapImageItem(value, file) {
  function _wrapImageItem (file) {
    return {
      id: 0,
      value: '',
      component: 'image-input',
      file: file,
      record: {}
    }
  }

  function _wrapMany2oneItem (choose) {
    return {
      id: 0,
      record: {
        value: choose.value || '',
        model_id: 0,
        model: choose.model,
        domain: choose.domain,
        name: choose.name,
        placeholder: choose.placeholder
      },
      component: 'many2one-input'
    }
  }

  function nextFocus (index) {
    var next = $('.editor-item[data-index="' + index + '"]').next()
    if (next.length > 0) {
      if (next.find('textarea, input').length > 0) {
        next.find('textarea, input').focus()
      } else {
        nextFocus(index + 1)
      }
    }
  }

  function prevFocus (index) {
    var prev = $('li[data-index="' + index + '"]').prev()
    if (prev.length > 0) {
      if (prev.find('textarea, input').length > 0) {
        prev.find('textarea, input').focus()
      } else {
        prevFocus(index - 1)
      }
    }
  }
  export default {
    props: ['config'],
    name: 'editor',
    mounted: function () {
      prevSortable.bind(this)()
    },
    data: function () { return data },
    events: {
      'add-text': function (index) {
        this.items.splice(index + 1, 0, _wrapTextItem(''))
        Vue.nextTick(function () {
          nextFocus(index)
        })
      },
      'next-textarea': nextFocus,
      'prev-textarea': prevFocus,
      'text-input-change': function () {
        this.is_save = false
        var eventHub = new Vue()
        eventHub.$emit('text-input-change')
      }
    },
    components: {
      Sortable,
      'text-input': textInput,
      'image-input': imageInput
    },
    computed: {
      many2one_choose: function () {
        return this.config.many2one || []
      }
    },
    created: function () {
      this.get()
    },
    methods: {
      choose_leave: function () {
        if (this.is_display_many2one_choose) {
          this.is_display_many2one_choose = false
        }
      },
      choose_over: function () {
        if (!this.is_display_many2one_choose) {
          this.is_display_many2one_choose = true
        }
      },
      display_device: function () {
        this.is_display_device = !this.is_display_device
      },
      get: function () {
        var self = this
        var getFunc = self.config.getFunc || function () {
          return $.when($.post(self.config.get_url || '/editor/get', {
            editor_id: self.config.osv.editor_id,
            osv_info: JSON.stringify(self.config.osv)
          }))
        }
        var getDone = self.config.getDone || function (results) {
          results = JSON.parse(results)
          results.forEach(function (result) {
            if (result.component === 'many2one-input') {
              result.record = JSON.parse(result.value)
            }
          })
          self.items = results
          self.loading = false
        }
        this.loading_more(getFunc).then(getDone)
      },
      do_many2one_choose: function (choose) {
        var self = this
        self.is_display_many2one_choose = false
        self.items.push(_wrapMany2oneItem(choose))

        Vue.nextTick(function () {
          nextFocus(self.items.length - 2)
        })
      },
      newRecord: function () {
        var self = this
        self.is_display_many2one_choose = false
        self.items.push(_wrapTextItem())

        Vue.nextTick(function () {
          nextFocus(self.items.length - 2)
        })
      },
      save: function () {
        var self = this
        var saveFunc = this.config.saveFunc || function () {
          var formdata = new FormData()
          formdata.append('osv_info', JSON.stringify(this.config.osv))
          formdata.append('editor_id', this.config.osv.editor_id)
          formdata.append('delete_items', JSON.stringify(this.delete_items))
          for (var index in self.items) {
            var item = self.items[index]
            if (item.component === 'image-input') {
              formdata.append(index, item.file || '')
              formdata.append(index + '-id', JSON.stringify({id: item.id}))
            } else if (item.component === 'text-input') {
              formdata.append(index, JSON.stringify({
                id: item.id,
                value: item.value,
                component: item.component
              }))
            } else if (item.component === 'many2one-input') {
              formdata.append(index, JSON.stringify({
                id: item.id,
                value: JSON.stringify(item.record),
                component: item.component
              }))
            }
          }
          var xhr = new XMLHttpRequest()
          xhr.open('post', this.config.save_url || '/editor/save')
          xhr.onreadystatechange = function (e) {
            if (xhr.readyState === 4 && xhr.status === 200) {
              self.loading = false
              var response = JSON.parse(xhr.responseText)
              if ($.isArray(response)) {
                response.forEach(function (item) {
                  self.items[item[0]].id = item[1]
                })
              }
              self.is_save = true
              self.delete_items = []
            }
          }
          xhr.onerror = function (e) {
            alert('发生了一些错误，请联系管理员')
          }
          xhr.send(formdata)
        }
        this.loading_more(saveFunc)
      },
      loading_more: function (finish, check) {
        var self = this
        if (self.loading) return true
        if (check && check.apply(self)) return true

        self.loading = true
        self.loading_index = 0

        function next () {
          self.loading_index = ++self.loading_index % 100
          if (self.loading) setTimeout(next, 30)
          else self.loading_index = 0
        }

        next()
        return finish.apply(self)
      },
      leave_operator: function () {
        this.display_operator_choose = -1
      },
      move_operator: function (method, item, index) {
        if (method === 'plus') {
          this.display_operator_choose = index
        }
      },
      do_operator_many2one_choose: function (many2one, item, index, text) {
        var self = this
        self.display_operator_choose = -1
        self.items.splice(index + 1, 0, text ? _wrapTextItem('') : _wrapMany2oneItem(many2one))

        Vue.nextTick(function () {
          nextFocus(index)
        })
      },
      do_operator: function (method, item, index) {
        if (method === 'plus') {
          if (this.many2one_choose.length === 0) {
            this.items.splice(index + 1, 0, _wrapTextItem())
            Vue.nextTick(function () {
              nextFocus(index)
            })
          }
        } else if (method === 'delete') {
          if (this.items[index].id > 0) {
            this.delete_items.push(this.items[index].id)
          }

          this.items.splice(index, 1)
        }
      },
      click_item: function (index) {
        this.choose_index = this.choose_index === index ? -1 : index
      },
      dragover: function () {
      },
      dragend: function () {
        this.dragging = false
      },

      drop: function (e) {
        this.dragging = false

        for (var i = 0; i < e.dataTransfer.files.length; i++) {
          this.preview_file(e.dataTransfer.files[i])
        }
      },
      preview_file: function (file) {
        this.items.push(_wrapImageItem(file))
      },

      dragenter: function () {
        this.dragging = true
      },

      dragleave: function () {
        this.dragging = false
      }
    },
    watch: {
      'items': function (items) {
        if (items.length <= 0) {
          this.items = [{value: '', component: 'text-input'}]
        }

        this.is_save = false
      }
    }
  }
</script>
<style type="text/css">
  #vux-editor {
    width: 100%;
    position: relative
  }

  .dftg-editor {
    min-height: 800px;
    width: 60%
  }

  .dftg-editor ul {
    padding-left: 0
  }

  .dftg-editor li {
    line-height: 1.4;
    font-size: 18px;
    list-style-type: none;
    margin: 10px 12px;
  }

  .dftg-editor .ghost {
    background-color: red;
    box-shadow:0 0 5px 3px rgba(0,150,200,1)
  }

  .dftg-editor.dragging {
    border: 5px dashed #03A9F4
  }


  .editor-item {
    position: relative;
    background-color: #fff
  }

  .editor-item:hover .operator-set {
    display: block;
  }

  .editor-item:hover textarea {
    background-color: #F7F7F7 !important;
    -webkit-box-shadow: rgba(0, 0, 0, 0.2) 0 1px 2px 0 inset;
    -moz-box-shadow: rgba(0, 0, 0, 0.2) 0 1px 2px 0 inset;
    -ms-box-shadow: rgba(0, 0, 0, 0.2) 0 1px 2px 0 inset;
    -o-box-shadow: rgba(0, 0, 0, 0.2) 0 1px 2px 0 inset;
    box-shadow: rgba(0, 0, 0, 0.2) 0 1px 2px 0 inset
  }

  .operator-set {
    display: none;
    position: absolute;
    right: 0;
    top: -2px
  }

  .operator_icon:hover {
    background-color: #aaa
  }

  .operator_icon {
    margin: 0;
    display: inline-block;
    border-radius: 5px;
    color: white;
    width: 16px;
    height: 16px
  }

  .operator_icon_plus {
    background: url('/supplier/static/img/add.png') no-repeat;
    background-size: 16px 16px
  }

  .operator_icon_delete {
    background: url('/supplier/static/img/garbage.png') no-repeat;
    background-size: 16px 16px
  }

  .editor-comment {
    position: absolute;
    font-size: 18px;
    width: 60%;
    text-align: center;
    top: 130px;
    opacity: .3;
    z-index: 0;
    pointer-events: none
  }

  .editor-comment > p {
    margin: 15px 0
  }

  .editor-comment-hide {
    display: none
  }

  .editor-button {
    width: 60%
  }

  .editor-button  a:hover,
  .many2one-choose-list > li:hover,
  .many2one-operator-choose-list > li:hover {
    background-color: #795548
  }

  .editor-button  a {
    padding: 8px 10px;
    border-radius: 4px;
    color: white !important;
    font-weight: bold;
    display: inline-block;
    margin-bottom: 10px;
    text-align: center;
    margin: 4px 12px
  }

  .many2one-choose {
    display: inline-block;
    position: relative
  }

  .expand-enter-active, .expand-leave-active {
    transition: all .3s ease;
    height: 300px;
    overflow: hidden
  }

  .expand-enter, .expand-leave-active {
    height: 0;
    opacity: 0
  }

  .many2one-operator-choose-list {
    list-style-type: none;
    position: absolute;
    margin: 0;
    padding: 0;
    z-index: 10;
    top: 5px;
    right: 65px;
    height: inherit
  }

  .many2one-operator-choose-list > li {
    cursor: pointer;
    width: 80px;
    padding: 8px 10px;
    margin: 1px 12px;
    background-color: #9C27B0;
    color: white;
    text-align: center;
    font-size: 12px
  }

  .many2one-choose-list {
    list-style-type: none;
    position: absolute;
    margin: 0;
    padding: 0;
    z-index: 10;
    width: 100%;
    height: inherit
  }

  .many2one-choose-list > li {
    cursor: pointer;
    padding: 8px 10px;
    margin: 1px 12px;
    background-color: #9C27B0;
    color: white;
    text-align: center
  }

  .editor-button-save {
    background: #2196F3
  }

  .editor-button-new {
    width: 100px;
    background: #9C27B0
  }

  .editor-button-hidden {
    background: #FF5722
  }

  .editor-button-fullscreen {
    background: #FFC107
  }

  .editor-button-preview {
    background: #607D8B
  }

  .editor-loading {
    position: absolute;
    height: 10px;
    width: 100%;
    top: 0
    /*background-color: red;*/
  }

  .editor-loading-layer {
    height: 2px;
    background-color: #2196F3
  }

  .editor-device {
    position: absolute;
    top: -50px;
    right: 20px;
    width: 340px;
    height: 740px;
    background: url('/supplier/static/img/iphone.png') no-repeat;
    background-position: -200px;
    transition: background-image .1s linear
  }

  .editor-content {
    height: 500px;
    background-color: #eee;
    position: relative;
    top: 121px;
    width: 281px;
    margin: 0 auto;
    overflow: hidden;
    font-size: 16px;
    line-height: 1.04;
    word-break: break-all;
    overflow-y: auto
  }

  .editor-content > div {
    padding: 2px 4px
  }

  .editor-content p {
    padding: 0;
    margin: 0
  }

  .editor-content > img {
    width: 100%
  }

  .editor-fullscreen {
    transition: all .3s ease;
    position: fixed;
    width: 100%;
    overflow: visible;
    left: 0px;
    background-color: #eee !important;
    overflow-y: auto
  }
</style>
