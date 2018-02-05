// The Vue build version to load with the `import` command
// (runtime-only or standalone) has been set in webpack.base.conf with an alias.
import Vue from 'vue'
import FastClick from 'fastclick'
import VueRouter from 'vue-router'
import App from './App'
import Vuex from 'vuex'
import VueScroller from 'vue-scroller'
import { BusPlugin, DatetimePlugin, LocalePlugin, DevicePlugin, ToastPlugin, AlertPlugin, ConfirmPlugin, LoadingPlugin, AjaxPlugin } from 'vux'

Vue.use(ToastPlugin)
Vue.use(AlertPlugin)
Vue.use(ConfirmPlugin)
Vue.use(LoadingPlugin)
Vue.use(AjaxPlugin)
Vue.use(DevicePlugin)
Vue.use(LocalePlugin)
Vue.use(DatetimePlugin)
Vue.use(BusPlugin)
Vue.use(VueRouter)
Vue.use(Vuex)
Vue.use(VueScroller)

// plugins
/**
 * 设置vuex
 */
const store = new Vuex.Store({}) // 这里你可能已经有其他 module
require('es6-promise').polyfill()

store.registerModule('vux', { // 名字自己定义
  state: {
    isLoading: false,
    demoScrollTop: 0,
    direction: 'forward',
    title: '首页',
    third_menu: []
  },
  mutations: {
    updateLoadingStatus: function (state, payload) {
      state.isLoading = payload
    },
    UPDATE_DIRECTION: function (state, payload) {
      state.direction = payload
    },
    updateTitle: function (state, payload) {
      state.title = payload
    }
  }
})

const routes = [{
  name: 'menu',
  path: '/odoo/:menu_id',
  component: function (resolve) {
    require(['./components/ChildMenu'], resolve)
  }
}, {
  name: 'tree',
  path: '/odoo/:menu_id/:action_id/tree',
  component: function (resolve) {
    require(['./components/ActionComponent'], resolve)
  }
}, {
  name: 'form',
  path: '/odoo/:menu_id/:action_id/form/:record_id',
  component: function (resolve) {
    require(['./components/formComponent'], resolve)
  }
}]

const router = new VueRouter({
  mode: 'history',
  linkActiveClass: 'active',
  routes
})

FastClick.attach(document.body)

router.beforeEach(function (to, from, next) {
  store.commit('updateLoadingStatus', true)
  next()
})
router.afterEach(function (to) {
  setTimeout(function () {
    store.commit('updateLoadingStatus', false)
  }, 300)
})

/***
 * Vux转场动画
 */

const history = window.sessionStorage
history.clear()
var historyCount = history.getItem('count') * 1 || 0
history.setItem('/', 0)

router.beforeEach(function (to, from, next) {
  const toIndex = history.getItem(to.path)
  const fromIndex = history.getItem(from.path)
  if (toIndex) {
    if (!fromIndex || parseInt(toIndex, 10) > parseInt(fromIndex, 10) || (toIndex === '0' && fromIndex === '0')) {
      store.commit('UPDATE_DIRECTION', {direction: 'forward'})
    } else {
      store.commit('UPDATE_DIRECTION', {direction: 'reverse'})
    }
  } else {
    ++historyCount
    history.setItem('count', historyCount)
    to.path !== '/' && history.setItem(to.path, historyCount)
    store.commit('UPDATE_DIRECTION', {direction: 'reverse'})
  }
  next()
})

// 作者：Yunfly
// 链接：http://www.jianshu.com/p/a29d5ecfaadb
//   來源：简书
// 著作权归作者所有。商业转载请联系作者获得授权，非商业转载请注明出处。
/* eslint-disable no-new */
/***
 * all filter
 */

Vue.filter('menu_to_link', function (value) {
  return '/second/nemu/' + value.id
})

Vue.filter('get_menu_ico_path', function (value) {
  if (value && value.indexOf(',') > 0) {
    var menuPath = value.split(',')
    return '/mobile/' + menuPath[0] + '/' + menuPath[1]
  }
})

Vue.filter('obj_str_to_id', function (value) {
  if (value && value.indexOf(',') > 0) {
    var menuPath = value.split(',')
    return menuPath[1]
  }
})
// Vue.http.interceptors.push(function (request, next) {
//   $.showLoading('请稍等...')
//   next(function (response) {
//     $.hideLoading('请稍等...')
//     return response
//   });
// });

Vue.filter('get_select_value', function (value, fieldTypeSelection) {
  for (var selectionIndex in fieldTypeSelection) {
    if (fieldTypeSelection[selectionIndex][0] === value) {
      return fieldTypeSelection[selectionIndex][1]
    }
  }
})
Vue.filter('object_has_key', function (value, key) {
  if (value && key && value[key]) {
    return true
  } else {
    return true
  }
})
Vue.filter('tree_field_format', function (value, fieldType) {
  if (value && fieldType) {
    if (fieldType.type === 'boolean') {
      return value ? '√' : '×'
    } else if (fieldType.type === 'many2one') {
      return value[1]
    } else if (fieldType.type === 'selection') {
      for (var selectionIndex in fieldType.selection) {
        if (fieldType.selection[selectionIndex][0] === value) {
          return fieldType.selection[selectionIndex][1]
        }
      }
    } else if (fieldType.type === 'char') {
      return value
    } else {
      return value
    }
  } else {
    return '无'
  }
})
Vue.filter('length', function (value) {
  if (value == null) return 0
  if (typeof value !== 'string') {
    value += ''
  }
  return value.replace(/[^\x00-\xff]/g, '01').length
})
Vue.filter('selectionOptions', function (values) {
  var options = []
  for (var val in values) {
    options.push({'key': values[val][0], 'value': values[val][1]})
  }
  return options
})

// Vue.filter('getMany2oneLink', function (values, Many2oneField) {
//   var url = '/mobile/odoo/getActionId'
//   this.$http.get(url).then(function (res) {
//     return '/mobile/' + this.$router.menu_id + '/' + res.body.actionId + '/' + values
//   })
// })

new Vue({
  router,
  store,
  render: h => h(App)
}).$mount('#app-box')

