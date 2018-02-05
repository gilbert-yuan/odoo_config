<template>
  <div>
    <template v-if="binaryVal">
      <img class="previewer-demo-img" v-for="(item, index) in imageList" 
      :src="item.src" width="100"  :key='index'
      @click="show(index)">
      <div v-transfer-dom>
        <previewer :list="imageList" ref="previewer" :options="options"></previewer>
      </div>
    </template>
  </div>

</template>

<script>
  import { Previewer, TransferDom } from 'vux'
  export default {
    props: ['binaryVal', 'imgTitle'],
    name: 'BinayImage',
    directives: {
      TransferDom
    },
    components: {
      Previewer
    },
    data: function () {
      return {
        imageList: [],
        imageIndex: 0,
        options: {
          getThumbBoundsFn (index) {
            // find thumbnail element
            let thumbnail = document.querySelectorAll('.previewer-demo-img')[index]
            // get window scroll Y
            let pageYScroll = window.pageYOffset || document.documentElement.scrollTop
            // optionally get horizontal scroll
            // get position of element relative to viewport
            let rect = thumbnail.getBoundingClientRect()
            // w = width
            return {x: rect.left, y: rect.top + pageYScroll, w: rect.width}
            // Good guide on how to get element coordinates:
            // http://javascript.info/tutorial/coordinates
          }
        }
      }
    },
    methods: {
      show (index) {
        this.$refs.previewer.show(index)
      }
    },
    created: function () {
      this.imageList = [{
        src: 'data:image/png;base64,' + this.binaryVal,
        title: this.imgTitle
      }]
    },
    watch: {
      binaryVal (newVal, oldVal) {
        this.imageList = [{
          src: 'data:image/png;base64,' + newVal,
          title: this.imgTitle
        }]
      }
    }
  }
</script>

<style scoped>
  .copyright {
    font-size: 12px;
    color: #ccc;
    text-align: center;
  }
  .text-scroll {
    border: 1px solid #ddd;
    border-left: none;
    border-right: none;
  }
  .text-scroll p{
    font-size: 12px;
    text-align: center;
    line-height: 30px;
  }
  .black {
    background-color: #000;
  }
  .title{
    line-height: 100px;
    text-align: center;
    color: #fff;
  }
  .animated {
    animation-duration: 1s;
    animation-fill-mode: both;
  }
  .vux-indicator.custom-bottom {
    bottom: 30px;
  }
  @-webkit-keyframes fadeInUp {
    from {
      opacity: 0;
      transform: translate3d(0, 100%, 0);
    }
    100% {
      opacity: 1;
      transform: none;
    }
  }
  @keyframes fadeInUp {
    from {
      opacity: 0;
      transform: translate3d(0, 100%, 0);
    }
    100% {
      opacity: 1;
      transform: none;
    }
  }
  .fadeInUp {
    animation-name: fadeInUp;
  }
  .swiper-demo-img img {
    width: 100%;
  }
</style>
