<template>
  <div id="vux-images">
    <div class="editor-loading">
      <div class="editor-loading-layer" :style="{width: loading_index + '%'}">
      </div>
    </div>
    <div class="dftg-editor" @dragover.prevent="dragover" @dragend.prevent="dragend" @drop.prevent="drop" @dragenter.prevent.stop="dragenter" @dragleave.prevent.stop.self="dragleave" :class="{dragging: dragging}" >
      <ul id="items">
        <li @click="click_item(item_index)" class="editor-item" :class="{choosed: item_index == choose_index}" v-for="(item, item_index) in items" :data-index="item_index">
          <component :config="config" :model="item" :editor_sku="config.osv.editor_sku"  :product_id="config.osv.editor_id" :index="item_index" :is='item.component'>
          </component>
          <ul class="operator-set" @mouseleave="leave_operator">
            <li v-for="(operator, operator_index) in operators" @click.prevent.stop="do_operator(operator.method, item, item_index)"
                class="operator_icon" :class="operator.operator_icon" @mouseover.prevent.stop.self="move_operator(operator.method, item, item_index)"></li>
          </ul>
        </li>
      </ul>
      <div class="editor-comment" :class="[items.length > 1 || items[0].component === 'image-input'? 'editor-comment-hide': '' ]">
        <p>直接在图片拖放到这里就可以自动上传图片</p>
      </div>
    </div>
  </div>
</template>

<script>
  import imageInput from './image.vue'
  import Vue from 'vue'
  import axios from 'axios'
  import Sortable from 'sortablejs'
  var $ = require('jquery')
  Vue.prototype.$http = axios
  var data = {
    loading_index: 0,
    items: [{value: '', component: 'text-input', record: {}}],
    operators: [
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
    is_preview: false
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
    var el = document.getElementById('items')
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
    name: 'images',
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
        var eventHub = new Vue()
        eventHub.$emit('text-input-change')
      }
    },
    components: {
      Sortable,
      'image-input': imageInput
    },
    created: function () {
      this.get()
    },
    methods: {
      get: function () {
        var self = this
        var getFunc = self.config.getFunc || function () {
          return $.when($.post(self.config.get_url || '/images/get', {
            editor_id: self.config.osv.editor_id,
            editor_sku: self.config.osv.editor_sku,
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
      newRecord: function () {
        var self = this
        self.is_display_many2one_choose = false
        self.items.push(_wrapTextItem())
        Vue.nextTick(function () {
          nextFocus(self.items.length - 2)
        })
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
      do_operator: function (method, item, index) {
        if (method === 'delete') {
          if (this.items[index].id > 0) {
            this.$http.post('/image/delete', {
              'id': this.items[index].id
            }).then(function (response) {})
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
      },
      imageChangeList: function (orderChangeList, ids) {
        this.$http.post('/image/change_order', {
          change_list: orderChangeList,
          ids: ids
        }).then(function (response) {
          if (response.data.result === 'error') {}
        })
      },
      addNewImage: function (addImageList) {
//        console.log(addImageList)
//        this.$http.post('/images/add', {'addmage_list': JSON.stringify(addImageList)}).then(function (response) {
//          if (response.data.result === 'error') {
//            alert(response.data)
//          }
//        })
      }
    },
    watch: {
      'items': function (items) {
        var self = this
        var orderChangeList = []
        var addImageList = []
        var ids = []
        if (items.length <= 0) {
          this.items = [{value: '', component: 'text-input'}]
        }
        items.forEach(function (item, index) {
          if (item.index !== index) {
            item.index = index
            orderChangeList.push({
              id: item.id, index: index, editor_sku: self.config.osv.editor_sku, file_url: item.value})
            ids.push('' + item.id)
          }
          if (item.id === 0) {
            addImageList.push({
              index: item.index,
              image: item.file,
              file_url: item.value,
              product_id: self.config.osv.editor_id,
              editor_sku: self.config.osv.editor_sku
            })
          }
        })
        if (ids.length > 0 && orderChangeList.length > 0) {
          self.imageChangeList(orderChangeList, ids)
        }
        if (addImageList.length > 0) {
          self.addNewImage(addImageList)
        }
      }
    }
  }
</script>
<style type="text/css">
  #vux-images {
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
    background: url('../assets/add.png') no-repeat;
    background-size: 16px 16px
  }

  .operator_icon_delete {
    background: url('../assets/garbage.png') no-repeat;
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
</style>
