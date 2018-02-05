<style type="text/css">
.image-input:hover {
    background-color: #F7F7F7;
}

.image-input > img {
    transition: all .3s ease;
}

.image-input {
    position: relative;
    border: 1px solid #cccccc;
    border-radius: 3px;
    padding: 5px 10px;
    -webkit-box-shadow: rgba(0, 0, 0, 0.2) 0 1px 2px 0;
	-moz-box-shadow: rgba(0, 0, 0, 0.2) 0 1px 2px 0;
	-ms-box-shadow: rgba(0, 0, 0, 0.2) 0 1px 2px 0;
	-o-box-shadow: rgba(0, 0, 0, 0.2) 0 1px 2px 0;
	box-shadow: rgba(0, 0, 0, 0.2) 0 1px 2px 0;
}

.image-input-mask-container {
    position: absolute;
    display: flex;
    align-items: center;
    justify-content: center;
    top: 5px;
    left: 10px;
    height: 200px;
    width: 250px;
}

.image-input-mask {
    background: url('../assets/loading.gif') no-repeat;
    width: 56px;
    height: 56px;
    display: block;
}

</style>

<template>
    <div class="image-input">
        <img :src="real_get_url(model.value, model.type)" style="width:250px;height: 250px" @load="load" />
        <div v-if="!loaded" class="image-input-mask-container" ><span class="image-input-mask"></span></div>
    </div>
</template>

<script>
export default {
  props: ['model', 'product_id', 'editor_sku'],
  data () {
    return { loaded: false, imageWidth: 250, imageHeight: 200, mask_height: 0 }
  },
  created () {
    if (!this.model.value) {
      if (['image/png', 'image/jpeg', 'image/gif'].indexOf(this.model.file.type) < 0) return
      var self = this
      var reader = new FileReader()
      reader.onload = function (event) {
        self.model.value = event.target.result
      }
      reader.readAsDataURL(this.model.file)
      if (self.model.id === 0) {
        var formdata = new FormData()
        formdata.append('file', this.model.file)
        formdata.append('editor_sku', this.editor_sku)
        formdata.append('image_url', this.model.value)
        formdata.append('product_id', this.product_id)
        formdata.append('index', this.model.index)
        if (this.editor_sku) {
          self.$http.post('/images/add', formdata, {headers: { 'Content-Type': 'multipart/form-data' }}).then(function (response) {
            if (response.data.result === 'error') {
              alert(response.data)
            }
          })
        }
      }
    }
  },
  events: {
    preview_picture: function (preview) {
      this.imageWidth = preview ? 50 : 250
    }
  },
  methods: {
    real_get_url (value, type) {
      if (type === 'jd') {
        return 'http://img13.360buyimg.com/n0/' + value
      }
      return value
    },
    load (e) {
      this.loaded = true
    }
  }
}
</script>
