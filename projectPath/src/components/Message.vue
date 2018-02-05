<template>
  <div class="timeline-demo">
  <timeline>
    <timeline-item v-for="(message, index) in messages" :key='index'>
      <h4 class="recent">{{message.create_uid[1]}}</h4>
      <p class="recent">{{message.body}}</p>
      <p class="recent">{{message.create_date}}</p>
    </timeline-item>
  </timeline>
  </div>
</template>

<script>
  import {Timeline, TimelineItem} from 'vux'
  export default {
    props: ['message_ids'],
    name: 'Message',
    components: {
      TimelineItem,
      Timeline
    },
    data: function () {
      return {
        messages: []
      }
    },
    created: function () {
      var loadViewUrl = '/mobile/odoo/load_all_messages'
      var self = this
      let parseString = require('xml2js').parseString
      this.$http.get(loadViewUrl, {
        params: {
          message_ids: JSON.stringify(self.message_ids)
        }
      }).then(function (res) {
        console.log(res)
        self.messages = res.data
        for (var mIndex in self.messages) {
          if (self.messages[mIndex].data) {
            parseString(self.messages[mIndex].data, function (result, err) {
              self.messages[mIndex].body = err.p
            })
          }
//          } else if (self.messages[mIndex] && self.messages[mIndex].tracking_value_ids) {
//            self.messages = false
//            self.$http.get('/mobile/odoo/search_read', {
//              params: {
//                model: 'mail.tracking.value',
//                domain: JSON.stringify([['id', 'in', self.messages[mIndex].tracking_value_ids]])
//              }
//            }).then(function (res) {
//
//            })
//          }
        }
      })
    }
//    watch: {
//      message_ids (newVal, oldVal) {
//        var loadViewUrl = '/mobile/odoo/load_all_messages'
//        var self = this
//        let parseString = require('xml2js').parseString
//        if (self.message_ids) {
//          this.$http.get(loadViewUrl, {
//            params: {
//              message_ids: JSON.stringify(self.message_ids)
//            }
//          }).then(function (res) {
//            console.log(res)
//            self.messages = res.data
//            for (var mIndex in self.messages) {
//              if (self.messages[mIndex].data) {
//                parseString(self.messages[mIndex].data, function (result, err) {
//                  self.messages[mIndex].data = err.p
//                })
//              }
//            }
//          })
//        }
//      }
 //   }
  }
</script>
<style lang="less">
  .timeline-demo {
    p {
      color: #888;
      font-size: 0.8rem;
    }
    h4 {
      color: #666;
      font-weight: normal;
    }
    .recent {
      color: rgb(4, 190, 2)
    }
  }
</style>
