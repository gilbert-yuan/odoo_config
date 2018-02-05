<template>
  <div id="app" style="height:100%;">
    <drawer
      width="200px;"
      :show.sync="drawerVisibility"
      :show-mode="showModeValue"
      :placement="showPlacementValue"
      :drawer-style="{'background-color':'#35495e', width:'200px'}">
      <div slot="drawer" style="margin-top:20px;">
        <group title="ODOO">
          <template v-for="(menu1, index) in first_level_menu">
            <cell :title="menu1.name" :value="menu1.name" @click.native="onclick_first_level_menu(menu1.child_menu)"
                  :key='index'>
            </cell>
          </template>
        </group>
        <group title="侧边栏类型">
          <radio v-model="showMode" :options="['push', 'overlay']" @on-change="onShowModeChange"></radio>
        </group>
        <group title="侧边栏弹为位置">
          <radio v-model="showPlacement" :options="['left', 'right']" @on-change="onPlacementChange"></radio>
        </group>
      </div>
      <view-box ref="viewBox">
        <x-header :right-options="{showMore: true}" slot="header"
                  :title="vux.title"
                  @on-click-more="showMenus = true"
                  style="width:100%;position:fixed;left:0;top:0;z-index:100;">
          <span v-if="$route.name==='menu'|| $route.name==='app' " slot="overwrite-left" @click="drawerVisibility = !drawerVisibility"  >
            <x-icon type="navicon" size="35" style="fill:#fff;position:relative;top:-8px;left:-3px;"></x-icon>
          </span>
        </x-header>
        <div slot="default" style="position:relative;top: 44px;width:100%;bottom: 80px" >
          <transition :name="'vux-pop-' + (direction === 'forward' ? 'in' : 'out')">
            <keep-alive>
              <router-view class="router-view"></router-view>
            </keep-alive>
          </transition>
        </div>
        <div slot="bottom">
          <tabbar >
            <template v-for="(menu2, index) in second_level_menu">
              <tabbar-item :key='index' @click.native="onclick_second_level_menu(menu2)">
                 <span class="demo-icon-22 vux-demo-tabbar-icon-home"
                       slot="icon" style="position:relative;top: -2px;">&#xe637;</span>
                <span slot="label">{{ menu2.name }}</span>
              </tabbar-item>
            </template>
          </tabbar>
        </div>
      </view-box>
    </drawer>
    <div v-transfer-dom>
      <actionsheet :menus="menus" v-model="showMenus" show-cancel></actionsheet>
    </div>
    <!--   <div v-transfer-dom>
        <loading :show="isLoading" text="加载中...."></loading>
      </div> -->
    <loading v-model="isLoading"></loading>
  </div>
</template>
<script>
  import {
    Tabbar,
    TabbarItem,
    Drawer,
    Radio,
    Group,
    Cell,
    Loading,
    ViewBox,
    XHeader,
    Actionsheet,
    TransferDom
  } from 'vux'
  import {mapState} from 'vuex'
  export default {
    directives: {
      TransferDom
    },
    name: 'app',
    components: {
      Tabbar,
      TabbarItem,
      Radio,
      XHeader,
      Drawer,
      Group,
      Cell,
      ViewBox,
      Actionsheet,
      Loading
    },
    data: function () {
      return {
        menus: {
          menu1: '提问',
          menu2: '新建'
        },
        showMenus: false,
        showMore: true,
        first_level_menu: [],
        second_level_menu: [],
        drawerVisibility: false,
        showMode: 'push',
        showModeValue: 'push',
        showPlacement: 'left',
        showPlacementValue: 'left',
        showLeftMenu: true,
        show_third_menu: true,
        last_leve_menu: []
      }
    },
    created: function () {
      var url = '/mobile/odoo/get_first_level_menu'
      var self = this
      self.$vux.loading.show()
      self.$http.get(url).then(function (res) {
        self.$vux.loading.hide()
        self.first_level_menu = res.data
        if (self.first_level_menu[0]) {
          self.onclick_first_level_menu(self.first_level_menu[0].child_menu)
        }
      })
    },
    methods: {
      onShowModeChange (val) {
        /** hide drawer before changing showMode **/
        this.drawerVisibility = false
        setTimeout(one => {
          this.showModeValue = val
        }, 400)
      },
      onPlacementChange (val) {
        /** hide drawer before changing position **/
        this.drawerVisibility = false
        setTimeout(one => {
          this.showPlacementValue = val
        }, 400)
      },
      onclick_first_level_menu (childMenu) {
        var self = this
        self.drawerVisibility = false
        self.second_level_menu = childMenu
        if (self.second_level_menu && self.second_level_menu[0]) {
          self.vux.third_menu = self.second_level_menu[0].child_menu
          if (this.$route.params.menud_id !== self.second_level_menu[0].id) {
          // self.vux.title = self.second_level_menu[0].name
            self.$router.push({name: 'menu', params: {'menu_id': self.second_level_menu[0].id}})
          }
        }
      },
      headerTransition () {
        return this.direction === 'forward' ? 'vux-header-fade-in-right' : 'vux-header-fade-in-left'
      },
      onclick_second_level_menu (menu) {
        var self = this
        self.vux.third_menu = menu.child_menu
        self.$router.push({name: 'menu', params: {'menu_id': menu.id}})
        self.vux.title = menu.name
      }
    },
    computed: {
      ...mapState({
        route: state => state.route,
        path: state => state.route.path,
        isLoading: state => state.vux.isLoading,
        direction: state => state.vux.direction,
        vux: state => state.vux
      })
    }
  }
</script>

<style lang="less">
  @import '~vux/src/styles/reset.less';
  @import '~vux/src/styles/reset.less';
  @import '~vux/src/styles/1px.less';
  @import '~vux/src/styles/tap.less';

  html, body {
    height: 100%;
    width: 100%;
    overflow-x: hidden;
    overflow-y: auto;
  }

  .vux-pop-out-enter-active,
  .vux-pop-out-leave-active,
  .vux-pop-in-enter-active,
  .vux-pop-in-leave-active {
    will-change: transform;
    transition: all 250ms;
    height: 100%;
    top: 0;
    position: absolute;
    backface-visibility: hidden;
    perspective: 1000;
  }

  .vux-pop-out-enter {
    opacity: 0;
    transform: translate3d(-100%, 0, 0);
  }

  .vux-pop-out-leave-active {
    opacity: 0;
    transform: translate3d(100%, 0, 0);
  }

  .vux-pop-in-enter {
    opacity: 0;
    transform: translate3d(100%, 0, 0);
  }

  .vux-pop-in-leave-active {
    opacity: 0;
    transform: translate3d(-100%, 0, 0);
  }

  body {
    background-color: #fbf9fe;
  }

  body {
    background-color: #fbf9fe;
  }

  html, body {
    height: 100%;
    width: 100%;
    overflow-x: hidden;
  }

  .demo-icon-22 {
    font-family: 'vux-demo';
    font-size: 22px;
    color: #888;
  }

  .weui-tabbar.vux-demo-tabbar {
    /** backdrop-filter: blur(10px);
    background-color: none;
    background: rgba(247, 247, 250, 0.5);**/
  }

  .vux-demo-tabbar .weui-bar__item_on .demo-icon-22 {
    color: #F70968;
  }

  .vux-demo-tabbar .weui-tabbar_item.weui-bar__item_on .vux-demo-tabbar-icon-home {
    color: rgb(53, 73, 94);
  }

  .demo-icon-22:before {
    content: attr(icon);
  }

  .vux-demo-tabbar-component {
    background-color: #F70968;
    color: #fff;
    border-radius: 7px;
    padding: 0 4px;
    line-height: 14px;
  }

  .weui-tabbar__icon + .weui-tabbar__label {
    margin-top: 0 !important;
  }

  .vux-demo-header-box {
    z-index: 100;
    position: absolute;
    width: 100%;
    left: 0;
    top: 0;
  }

  @font-face {
    font-family: 'vux-demo';  /* project id 70323 */
    src: url('https://at.alicdn.com/t/font_h1fz4ogaj5cm1jor.eot');
    src: url('https://at.alicdn.com/t/font_h1fz4ogaj5cm1jor.eot?#iefix') format('embedded-opentype'),
    url('https://at.alicdn.com/t/font_h1fz4ogaj5cm1jor.woff') format('woff'),
    url('https://at.alicdn.com/t/font_h1fz4ogaj5cm1jor.ttf') format('truetype'),
    url('https://at.alicdn.com/t/font_h1fz4ogaj5cm1jor.svg#iconfont') format('svg');
  }

  .demo-icon {
    font-family: 'vux-demo';
    font-size: 20px;
    color: #04BE02;
  }

  .demo-icon-big {
    font-size: 28px;
  }

  .demo-icon:before {
    content: attr(icon);
  }

  .router-view {
    width: 100%;
  }

  .vux-pop-out-enter-active,
  .vux-pop-out-leave-active,
  .vux-pop-in-enter-active,
  .vux-pop-in-leave-active {
    will-change: transform;
    transition: all 500ms;
    height: 100%;
    top: 46px;
    position: absolute;
    backface-visibility: hidden;
    perspective: 1000;
  }

  .vux-pop-out-enter {
    opacity: 0;
    transform: translate3d(-100%, 0, 0);
  }

  .vux-pop-out-leave-active {
    opacity: 0;
    transform: translate3d(100%, 0, 0);
  }

  .vux-pop-in-enter {
    opacity: 0;
    transform: translate3d(100%, 0, 0);
  }

  .vux-pop-in-leave-active {
    opacity: 0;
    transform: translate3d(-100%, 0, 0);
  }

  .menu-title {
    color: #888;
  }
</style>

