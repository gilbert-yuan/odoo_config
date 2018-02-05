<template>
    <div ref="grid" class="excel-table" :style="`height:${height+2}px;`" @paste="doPaste">

        <div class="input-content" :style="inputStyles" ref="input" contenteditable="true" @input="setValueTemp" @blur="handleInputBlur" @keydown.tab.prevent @keydown.enter.prevent @keydown.esc.prevent></div>
        <div class="input-content" ref="inputSelect" contenteditable="true" @keydown.prevent></div>
        <div class="horizontal-container" :style="{width:`${width-scrollerWidth+2}px`}" @click="scroll($event,0)">
            <div class="scroll-bar-horizontal" ref="horizontal" @mousedown="dragMove($event,0)" :style="{width:horizontalBar.size+'px',left:horizontalBar.x+'px'}">
                <div :style="horizontalBar.move?'background-color:#a1a1a1;':'background-color:#c1c1c1;'"></div>
            </div>
        </div>
        <canvas ref="canvas" :width="width" :height="height" :style="`width:500px;height:400px;`"></canvas>
    </div>
</template>

<script>
import painted from './painted'
import events from './events'
import calculate from './calculate'
import scroller from './scroller'
import checkbox from './checkbox.vue'
import history from './history'
import utils from './utils'

// type: default,noextent
export default {
  mixins: [utils, calculate, painted, events, scroller, history],
  components: { checkbox },
  props: {
    columns: Array,
    gridData: Array,
    type: {
      type: String,
      default: 'default'
    },
    showCheckbox: {
      type: Boolean,
      default: false
    },
    leftHeight: Number,
    showDot: Object,
    columnSet: {
      type: Boolean,
      default: false
    },
    storageKey: {
      type: String,
      default: 'gridStorage'
    },
    initSelected: Array,
    autoAddRow: {
      type: Boolean,
      default: false
    },
    templateData: Object,
    showToolbar: {
      type: Boolean,
      default: true
    },
    showRate: {
      type: Boolean,
      default: false
    }
  },
  data () {
    return {
      keys: { 37: 1, 38: 1, 39: 1, 40: 1 },

      ctx: null,

      isDown: false,
      isEditing: false,
      isSelect: false,
      isFocus: false,
      isMultiSelect: false,

      selectArea: null,
      focusCell: null,
      multiSelect: null,

      currentText: '',
      inputStyles: {},
      valueTemp: '',
      data: null,
      showColumnSet: false,
      ratio: 1,
      showTip: false,
      tipMessage: '',
      isPaste: false,
      initRows: 300,
      fxContent: '',
      fxFocus: false,
      input: '',
      fxTip: '',
      sumRate: 0,
      rate: 0
    }
  },
  computed: {
    showBatchEditBtn () {
      if (this.isSelect) {
        if (this.selectArea.width > this.allColumns[this.selectArea.cellIndex].width) {
          return false
        }
        return true
      }
      return false
    },
    batchEditStyle () {
      const { x, y, width, height } = this.selectArea
      let _y = y
      if (y < 90) {
        _y = 90
      }
      if (y + height < 90) {
        _y = -90
      }
      return {
        left: `${x + width + 2}px`,
        top: `${_y}px`
      }
    }
  },
  watch: {
    gridData (value) {
      this.data = [...value]
      this.initCanvas()
      this.painted(this.initDisplayItems())
      this.initEvent()
    },
    focusCell: {
      handler (value) {
        if (value) {
          this.fxContent = value.content
        }
      },
      deep: true
    },
    selectArea (value) {
      if (value) {
        const selectCells = this.getCellsBySelect(this.selectArea)
        let copyText = '<table>'
        for (const row of selectCells) {
          let temp = '<tr>'
          for (const cell of row) {
            temp += `<td>${cell.content}</td>`
          }
          temp += '</tr>'
          copyText += temp
        }
        copyText += '</table>'
        this.$refs.inputSelect.innerHTML = copyText
      }
    },
    fxContent (value) {
      if (`${value}` && (`${value}`).indexOf('=') === 0) {
        // TODO 根据获取到的区域公式，显示虚线框
        // console.log(this.evalUtil(`${value}`)) //eslint-disable-line
      }
    }
  },
  created () {
    this.data = [...this.gridData]
    this.$on('updateNoSave', (data) => {
      this.saveItems(data, false)
    })
    this.$on('update', (data) => {
      this.$emit('updateValue', this.saveItems(data, true))
    })
    this.$on('updateItem', (data) => {
      this.saveItem(data, true)
    })
  },
  mounted () {
    this.$nextTick(function () { //eslint-disable-line
      if (this.data.length > 0) {
        this.initCanvas()
        // this.painted(this.initDisplayItems())
        this.initSize()
        this.initEvent()
      }
    })
  },
  destroyed () {
    this.removeEvent()
  },
  methods: {
    doPaste () {
      this.isPaste = true
    },
    setValueTemp (e) {
      this.valueTemp = e.target.innerText
      this.fxContent = this.valueTemp
      const { width, height, serialWidth } = this.focusCell
      let { x, y } = this.focusCell
      if (x < serialWidth) {
        this.offset.x += serialWidth - x
        x = serialWidth
      }
      if (y < this.rowHeight) {
        this.offset.y += this.rowHeight - y
        y = this.rowHeight
      }
      if (!this.isPaste) {
        // 正常键盘录入
        this.selectArea = null
        this.isSelect = false
        this.rePainted()
        this.showInput(x, y, width, height)
      } else if (!this.isEditing) {
        this.isPaste = false
        const objE = document.createElement('div')
        objE.innerHTML = e.target.innerHTML
        const dom = objE.childNodes
        e.target.innerHTML = ''
        const pasteData = []
        for (let i = 0; i < dom.length; i += 1) {
          if (dom[i].tagName === 'TABLE') {
            const trs = dom[i].querySelectorAll('tr')
            for (const tr of trs) {
              const arrTmp = []
              for (const td of tr.cells) {
                let str = td.innerText
                str = str.replace(/^\s+|\s+$/g, '')
                arrTmp.push(str)
                const colspan = td.getAttribute('colspan')
                if (colspan) {
                  for (let i = 1; i < colspan; i += 1) {
                    arrTmp.push('')
                  }
                }
              }
              pasteData.push(arrTmp)
            }
          } else {
            pasteData.push([this.valueTemp])
          }
        }
        const modifyData = []
        let lastCellIndex = 0
        let startCellAt = 0
        let startRowIndex = this.focusCell.rowIndex
        for (const row of pasteData) {
          if (this.autoAddRow || startRowIndex < this.allRows.length) {
            let startCellIndex = this.getStartIndexByCellIndex(this.focusCell.cellIndex)
            startCellAt = startCellIndex
            if (startCellIndex || startCellIndex === 0) {
              let key = this.allColumns[startCellIndex].key
              const temp = {
                rowData: this.autoAddRow ? null : this.allCells[startRowIndex][0].rowData,
                index: startRowIndex,
                items: []
              }
              let readOnly = false
              for (let i = 0; i < row.length; i += 1) {
                if (readOnly) {
                  temp.items.push({
                    key: '',
                    value: ''
                  })
                } else {
                  temp.items.push({
                    key,
                    value: row[i]
                  })
                }
                const nextColumn = this.nextKeyByIndex(startCellIndex)
                if (nextColumn) {
                  key = nextColumn.key
                  startCellIndex = nextColumn.index
                  readOnly = nextColumn.readOnly
                } else {
                  break
                }
              }
              if (startCellIndex - 1 > lastCellIndex) {
                lastCellIndex = startCellIndex - 1
              }
              startRowIndex += 1
              modifyData.push(temp)
            }
          }
        }
        // let height = 0
        let width = 0
        if (startRowIndex - this.focusCell.rowIndex > 1 || lastCellIndex - startCellAt > 0) {
          // for (let i = this.focusCell.rowIndex; i < startRowIndex; i += 1) {
          //     height += this.allRows[i].height
          // }
          for (let i = startCellAt; i <= lastCellIndex; i += 1) {
            if (this.allColumns[i].checked) {
              width += this.allColumns[i].width + this.fillWidth
            }
          }
          this.selectArea = { x: this.focusCell.x, y: this.focusCell.y, width, rowIndex: this.focusCell.rowIndex, cellIndex: this.focusCell.cellIndex, rowCount: Math.abs(startRowIndex - this.focusCell.rowIndex), offset: { ...this.offset } }
          this.isSelect = true
        }
        this.$emit('update', modifyData)
      } else {
        // 编辑状态下
        this.isPaste = false
        e.target.innerHTML = e.target.innerText
      }
    },
    getStartIndexByCellIndex (cellIndex) {
      let startIndex = 0
      for (const item of this.allColumns) {
        if (item.cellIndex === cellIndex) {
          return startIndex
        }
        startIndex += 1
      }
      return null
    },
    nextKeyByIndex (index) {
      for (let i = index + 1; i < this.allColumns.length; i += 1) {
        if (this.allColumns[i].checked) {
          return {
            key: this.allColumns[i].key,
            index: i,
            readOnly: this.allColumns[i].readOnly
          }
        }
      }
      return null
    },
    validateKeyType (key) {
      for (const item of this.allColumns) {
        if (item.key === key) {
          if (item.type === 'number') {
            return {
              type: 'number',
              title: item.title
            }
          }
          return {
            type: 'string',
            title: item.title
          }
        }
      }
      return {
        type: 'string'
      }
    },
    save () {
      if (this.focusCell && this.isEditing) {
        if (this.$refs.input.innerText !== this.allCells[this.focusCell.rowIndex][this.focusCell.cellIndex].content) {
          this.$emit('updateItem', {
            index: this.focusCell.rowIndex,
            key: this.focusCell.key,
            value: this.$refs.input.innerText
          })
        }
      }
    },
    saveItem (data, history) {
      const { index, key } = data
      let value = data.value
      const curColumn = this.validateKeyType(key)

      if (curColumn) {
        if (curColumn.type === 'number') {
          const re = /^(([1-9][0-9]*\.[0-9][0-9]*)|([0]\.[0-9][0-9]*)|([1-9][0-9]*)|([0]{1}))$/
          if (value && !re.test(value)) {
            this.showTipMessage(`【 ${curColumn.title} 】单元格只支持数字。`)
            return
          }
          if (!value) {
            value = null
          }
        }
        if (history) {
          this.pushState({
            type: 'edit',
            before: { ...data, value: this.data[index][key] },
            after: { ...data }
          })
        }
        this.data[index][key] = value
        this.setCellItemByKey(index, key, value)
        this.rePainted()
        this.$emit('updateValue', [{ rowData: this.data[index], items: [{ key, value }] }])
      }
    },
    saveItems (data, history) {
      const returnData = []
      const re = /^(([1-9][0-9]*\.[0-9][0-9]*)|([0]\.[0-9][0-9]*)|([1-9][0-9]*)|([0]{1}))$/
      const errorTemp = []
      const historyTemp = {
        type: 'editMore',
        focusCell: this.focusCell,
        selectArea: this.selectArea,
        after: [...data]
      }
      if (data.length > this.data.length) {
        if (this.autoAddRow) {
          const startIndex = this.data.length
          const length = data.length - this.data.length
          for (let i = 0; i < length; i += 1) {
            this.data.push({ ...this.templateData })
          }
          this.setAllCells(startIndex)
          this.initRows = this.data.length
        } else {
          data.splice(this.data.length, data.length - this.data.length)
        }
      }
      const beforeData = []
      for (const row of data) {
        const beforeTemp = {
          rowData: row.rowData,
          index: row.index,
          items: []
        }
        const temp = {
          rowData: row.rowData,
          items: [],
          index: row.index
        }
        for (const item of row.items) {
          const curColumn = this.validateKeyType(item.key)
          if (curColumn) {
            if (curColumn.type === 'number') {
              if (item.value && !re.test(item.value)) {
                if (errorTemp.indexOf(curColumn.title) === -1) {
                  errorTemp.push(curColumn.title)
                }
                continue
              }
              if (!item.value) {
                item.value = null
              }
            }
            beforeTemp.items.push({
              key: item.key,
              value: this.data[row.index][item.key]
            })
            this.data[row.index][item.key] = item.value
            this.setCellItemByKey(row.index, item.key, item.value)
            temp.items.push({
              key: item.key,
              value: item.value
            })
          }
        }
        returnData.push(temp)
        beforeData.push(beforeTemp)
      }
      historyTemp.before = [...beforeData]
      if (history) {
        this.pushState(historyTemp)
      }
      if (errorTemp.length > 0) {
        this.showTipMessage(`【 ${errorTemp.join(',')} 】单元格只支持数字。`)
      }

      this.rePainted()
      return returnData
    },
    handleFxInput () {
      this.fxTip = ''
      if (this.fxContent.indexOf('=') !== 0) {
        if (!this.focusCell.readOnly) {
          if (this.multiSelect) {
            const modifyData = []
            for (let i = 0; i < this.allRows.length; i += 1) {
              const key = this.focusCell.key
              const temp = {
                rowData: this.focusCell.rowData,
                index: i,
                items: [{
                  key,
                  value: this.fxContent
                }]
              }
              modifyData.push(temp)
            }
            this.$emit('update', modifyData)
          } else {
            this.$emit('updateItem', {
              index: this.focusCell.rowIndex,
              key: this.focusCell.key,
              value: this.fxContent
            })
          }
        }
      }
    },
    handleFxBlur () {
      this.fxFocus = false
      this.paintFocusCell(this.focusCell)
    },
    handleInputBlur () {
      // if (this.fxContent && (`${this.fxContent}`).indexOf('=') === 0) {
      //     this.evalExpression()
      // }
      // setTimeout(() => {
      //     if (!this.fxFocus) {
      //         this.paintFocusCell(this.focusCell)
      //     }
      // }, 50)
    },
    handleFxKeyup (e) {
      if (e.keyCode === 13 && this.fxContent.indexOf('=') === 0) {
        this.evalExpression()
      }
    },
    // =include(1-3,5)=>h*1.1 & include(4,6--)=>i*1.2
    evalExpression () {
      try {
        const result = this.evalUtil(this.fxContent)
        for (const item of result) {
          if (item.indexArray && item.indexArray.length > 0 && item.regionType) {
            this.doEquation(...item)
          } else {
            this.doEquation(item.equation)
          }
        }
      } catch (error) {
        this.fxTip = '非法表达式'
      }
    },
    doEquation (equation, indexs, type) {
      if (indexs && type) {
        const modifyData = []
        if (type === 'include') {
          this.fxContent = eval(equation.replace('$x$', indexs[0])) //eslint-disable-line
          for (const i of indexs) {
            const key = this.focusCell.key
            let valueTemp = eval(equation.replace('$x$', i)) //eslint-disable-line
            if (this.focusCell.type === 'number') {
              valueTemp = parseFloat(valueTemp.toFixed(2))
            }
            const temp = {
              rowData: this.allCells[i][this.focusCell.cellIndex].rowData,
              index: i,
              items: [{
                key,
                value: valueTemp
              }]
            }
            modifyData.push(temp)
          }
        } else {
          let isFirstIndex = true
          for (let i = 0; i < this.allRows.length; i += 1) {
            if (indexs.indexOf(i) === -1) {
              if (isFirstIndex) {
                this.fxContent = eval(equation.replace('$x$', i)) //eslint-disable-line
              }
              isFirstIndex = false
              const key = this.focusCell.key
              let valueTemp = eval(equation.replace('$x$', i)) //eslint-disable-line
              if (this.focusCell.type === 'number') {
                valueTemp = parseFloat(valueTemp.toFixed(2))
              }
              const temp = {
                rowData: this.allCells[i][this.focusCell.cellIndex].rowData,
                index: i,
                items: [{
                  key,
                  value: valueTemp
                }]
              }
              modifyData.push(temp)
            }
          }
        }
        this.$emit('update', modifyData)
      } else if (this.multiSelect) {
        const modifyData = []
        this.fxContent = eval(equation.replace('$x$', 0)) //eslint-disable-line
        for (let i = 0; i < this.allRows.length; i += 1) {
          const key = this.focusCell.key
          let valueTemp = eval(equation.replace('$x$', i)) //eslint-disable-line
          if (this.focusCell.type === 'number') {
            valueTemp = parseFloat(valueTemp.toFixed(2))
          }
          const temp = {
            rowData: this.allCells[i][0].rowData,
            index: i,
            items: [{
              key,
              value: valueTemp
            }]
          }
          modifyData.push(temp)
        }
        this.$emit('update', modifyData)
      } else {
        this.fxContent = eval(equation.replace('$x$', this.focusCell.rowIndex)) //eslint-disable-line
        this.$emit('updateItem', {
          index: this.focusCell.rowIndex,
          key: this.focusCell.key,
          value: this.fxContent
        })
      }
    },
    handleDoRegionExpress () {
      if (this.selectArea) {
        const { rowIndex, rowCount } = this.selectArea
        this.fxContent = `=include(${rowIndex + 1}-${rowIndex + rowCount})=>`
        this.focusFxInput()
        this.selectArea = null
        this.isSelect = false
        this.rePainted()
      }
    },
    focusFxInput () {
      setTimeout(() => {
        this.$refs['fx-input'].focus()
      }, 0)
    }
  }
}
</script>

<style lang="scss" scoped>
* {
  box-sizing: border-box;
}

.excel-table {
  border: 1px solid #d4d4d4;
  position: relative;
  min-width: 714px;
  .toolbar {
    position: absolute;
    background-color: #f9f9f9;
    height: 29px;
    width: 100%;
    .toolbar__focus {
      height: 30px;
      border-right: 1px solid #d4d4d4;
      line-height: 30px;
      text-align: center;
      font-size: 14px;
      display: inline-block;
    }
    .toobar__fx {
      display: inline-block;
      vertical-align: top;
      width: 415px;
      label {
        width: 70px;
        display: inline-block;
        height: 30px;
        line-height: 30px;
        font-size: 12px;
        text-align: right;
      }
      .toobar__fx-tip {
        color: #e0000b;
        font-size: 12px;
        display: inline-block;
        width: 60px;
      }
      .toobar__fx-content {
        display: inline-block;
        vertical-align: top;
        input {
          width: 270px;
          outline: none;
          border-top: none;
          border-bottom: none;
          border-left: 1px solid #d4d4d4;
          border-right: 1px solid #d4d4d4;
          height: 29px;
          line-height: 29px;
          padding: 5px 15px;
          font-size: 12px;
        }
      }
    }
  }
  .toobar__rate {
    display: inline-block;
    vertical-align: top;
    label {
      font-size: 12px;
      line-height: 30px;
      margin-right: 15px;
      span {
        color: #03a2fe;
      }
    }
    label.help {
      background-color: #999;
      color: #fff;
      font-weight: 900;
      width: 20px;
      display: inline-block;
      text-align: center;
      line-height: 20px;
      border-radius: 10px;
      cursor: pointer;
      position: relative;
      .help-content {
        display: none;
        position: absolute;
        background-color: #fff;
        border: 1px solid #ddd;
        box-shadow: 3px 3px 10px rgba(0, 0, 0, 0.3);
        color: #666;
        width: 275px;
        text-align: left;
        padding-left: 10px;
        left: -240px;
        top: 24px;
        z-index: 11;
      }
      &:before {
        content: " ";
        display: none;
        position: absolute;
        width: 10px;
        height: 10px;
        background-color: #fff;
        transform: rotate(45deg);
        top: 22px;
        right: 6px;
        z-index: 10;
        border: 1px solid #ddd;
        box-shadow: 3px 3px 10px rgba(0, 0, 0, 0.3);
      }
      &:after {
        content: " ";
        display: none;
        position: absolute;
        width: 10px;
        height: 10px;
        background-color: #fff;
        transform: rotate(45deg);
        top: 22px;
        right: 6px;
        z-index: 12;
      }
      &:hover {
        .help-content {
          display: block;
        }
        &:after {
          display: inline-block;
        }
        &:before {
          display: inline-block;
        }
      }
    }
  }
  .horizontal-container {
    position: absolute;
    height: 18px;
    left: 0;
    bottom: 0;
    background: #f1f1f1;
    user-select: none;
    .scroll-bar-horizontal {
      position: absolute;
      bottom: 1px;
      height: 16px;
      padding: 0 2px;
      > div {
        width: 100%;
        height: 16px;
      }
    }
  }
  .vertical-container {
    user-select: none;
    position: absolute;
    width: 18px;
    top: 0;
    right: 0;
    background: #f1f1f1;
    .scroll-bar-vertical {
      position: absolute;
      right: 1px;
      width: 16px;
      padding: 2px 0;
      > div {
        width: 16px;
        height: 100%;
      }
    }
  }

  .input-content {
    padding: 5px;
    top: -10000px;
    left: -10000px;
    outline: none;
    box-shadow: rgba(0, 0, 0, 0.4) 0px 2px 5px;
    border: 2px solid #4285f4;
    color: #666;
    border-radius: 0px;
    font-size: 12px;
    position: fixed;
    background-color: #fff;
    z-index: 10;
  }
  .focus-area {
    display: none;
    border: 2px solid #4285f4;
    top: -10000px;
    left: -10000px;
    position: absolute;
    z-index: 5;
  }
  .select-area {
    z-index: 5;
    display: none;
    border: 1px solid #03a2fe;
    top: -10000px;
    left: -10000px;
    background-color: rgba(160, 195, 255, 0.2);
    position: absolute;
    transition: 0.1s all;
  }
  canvas {
    user-select: none;
    background-color: #fff;
  }
  .column-set {
    position: absolute;
    width: 150px;
    background-color: #fff;
    box-shadow: rgba(0, 0, 0, 0.4) 0px 2px 5px;
    left: 71px;
    padding: 0 8px;
    font-size: 12px;
    color: #495060;
    .column-set__title {
      height: 30px;
      line-height: 30px;
      border-bottom: 1px solid #ddd;
    }
    .column-set__content {
      overflow: auto;
      padding: 5px;
      color: #495060;
      ul {
        margin: 0;
        padding: 0;
        list-style: none;
        li {
          font-size: 12px;
          height: 30px;
          line-height: 30px;
        }
      }
    }
    .column-set__footer {
      height: 40px;
      line-height: 40px;
      border-top: 1px solid #ddd;
      text-align: right;
    }
  }
  button {
    height: 25px;
    width: 56px;
    line-height: 24px;
    background-color: #fff;
    border: 1px solid #ddd;
    outline: none;
    cursor: pointer;
    color: #333;
    &:hover {
      background-color: #f9f9f9;
    }
    &:active {
      background-color: #f5f5f5;
    }
  }
  .tip {
    position: absolute;
    width: 300px;
    top: 10px;
    right: 30px;
    background-color: #fff;
    box-shadow: rgba(0, 0, 0, 0.4) 0px 2px 5px;
    padding: 10px 10px 10px 50px;
    word-wrap: break-word;
    font-size: 12px;
    color: #666;
    .tip-icon {
      position: absolute;
      display: inline-block;
      width: 20px;
      height: 20px;
      background-size: 100%;
      left: 15px;
    }
  }
  .slide-fade-enter-active {
    transition: all 0.2s ease;
  }
  .slide-fade-leave-active {
    transition: all 0.1s cubic-bezier(1, 0.5, 0.8, 1);
  }
  .slide-fade-enter,
  .slide-fade-leave-to {
    transform: translateX(10px);
    opacity: 0;
  }
  .select-tip-btn {
    z-index: 10;
    position: absolute;
    width: 70px;
    border: 1px solid #bbb;
    box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.2);
  }
}
</style>

