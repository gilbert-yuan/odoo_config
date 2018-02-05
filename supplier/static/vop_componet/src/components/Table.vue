<template>
    <div>
        <grid :grid-data="data" :columns="columns" :showCheckbox="showCheckbox" :columnSet="columnSet" :left-height="20" @focus="focus" @updateValue="update" :showRate="false"></grid>
    </div>
</template>

<script>
import Grid from './grid'
export default {
  name: 'ctable',
  components: {
    Grid
  },
  data () {
    return {
      columnSet: false,
      showCheckbox: false,
      data: [],
      columns: [
          { title: '品牌', key: 'brandName', width: 80 },
          { title: '商品名称', key: 'goodsName', width: 150 },
          { title: '规格型号', key: 'sn', width: 100 },
          { title: '物料编码', key: 'materialNo', width: 100 },
          { title: '单位', key: 'unit', width: 70 },
          { title: '数量', key: 'requiredQuantity', width: 70 },
          { title: '客户备注', key: 'customerRemarks', width: 150 },
          { title: '采购价(元)', key: 'purchasePrice', width: 80 },
          { title: '销售价(元)', key: 'salePrice', width: 80 },
          { title: '货期', width: 100, key: 'shipDesc' }
      ]
    }
  },
  created () {
    for (let i = 0; i < 10; i += 1) {
      this.data.push({
        brandName: '博世',
        goodsName: '电钻',
        sn: 'SDFSD',
        materialNo: '1231',
        unit: '个',
        requiredQuantity: 10,
        customerRemarks: '测试测试',
        purchasePrice: 10.2,
        salePrice: 12.3,
        shipDesc: 10
      })
    }
  },
  methods: {
    update (value) {
    },
    focus (value) {
    }
  }
}
</script>
