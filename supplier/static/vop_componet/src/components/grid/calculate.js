export default {
  data () {
    const rowHeight = 30
    const serialWidth = 70
    const checkboxWidth = 30
    const scrollerWidth = 20
    const height = this.leftHeight ? window.innerHeight - this.leftHeight : 500
    let originPointX = serialWidth
    if (this.showCheckbox) {
      originPointX += checkboxWidth
    }
    let toolbarHeight = 0
    if (this.showToolbar) {
      toolbarHeight = 60
    }
    return {
      width: 0,
      height,
      rowHeight,
      scrollerWidth,
      fixedWidth: 0,
      bodyWidth: 0,
      bodyHeight: 0,
      serialWidth,
      checkboxWidth: 30,
      fillWidth: 0,
      toolbarHeight,

      allCells: [],
      displayCells: [],
      allRows: [],
      displayRows: [],
      allColumns: [],
      displayColumns: [],
      allFixedCells: [],
      displayFixedCells: [],
      fixedColumns: [],
      renderButtons: [],
      checkboxs: [],
      selected: [],

      offset: {
        x: 0,
        y: 0
      },
      originPoint: {
        x: originPointX,
        y: rowHeight
      },
      maxPoint: {
        x: 0,
        y: height - scrollerWidth
      }
    }
  },
  watch: {
    showCheckbox () {
      this.initSize()
    },
    leftHeight () {
      this.initSize()
    }
  },
  mounted () {
    this.width = this.$refs.grid.offsetWidth - 2

    this.height = this.leftHeight ? window.innerHeight - this.leftHeight : 500
    this.maxPoint.y = this.height - this.scrollerWidth

    this.bodyWidth = this.originPoint.x
    for (const column of this.columns) {
      this.bodyWidth += column.width ? column.width : 100
    }
    if (this.bodyWidth < this.width - this.scrollerWidth) {
      this.fillWidth = (this.width - this.bodyWidth - this.scrollerWidth) / this.columns.length
      this.bodyWidth = this.width - this.scrollerWidth
    }
  },
  methods: {
    /**
         * 获取所有数据单元格，首次渲染调用一次（较耗时）
         * @param {*} value
         * @param {*} columns
         */
    getAllCells (value, columns) {
      this.allCells = []
      this.allRows = []
      this.allColumns = []
      this.allFixedCells = []
      this.fixedColumns = []
      this.fixedWidth = 0
      const { rowHeight, ctx, getTextLine, allRows, allCells, allColumns, fixedColumns, allFixedCells } = this
      let rowIndex = 0
      let sumSaleprice = 0
      let sumPurchasePrice = 0
      for (const item of value) {
        let maxHeight = rowHeight
        let cellIndex = 0
        const cellTemp = []
        if (item.salePrice > 0 && item.purchasePrice > 0) {
          sumSaleprice += parseFloat(item.salePrice)
          sumPurchasePrice += parseFloat(item.purchasePrice)
        }
        for (const column of columns) {
          if (rowIndex === 0) {
            if (column.fixed) {
              this.fixedWidth += column.width
              fixedColumns.push({
                cellIndex,
                ...column
              })
              allColumns.push({
                height: rowHeight,
                cellIndex,
                ...column,
                checked: true
              })
            } else {
              allColumns.push({
                height: rowHeight,
                cellIndex,
                ...column,
                checked: true
              })
            }
          }
          let text = ''
          let buttons
          let textLine
          if (column.renderText) {
            text = column.renderText(item)
          } else if (column.renderButton) {
            buttons = column.renderButton(this.data[rowIndex], rowIndex)
          } else {
            text = item[column.key]
          }
          if (text || text === 0) {
            textLine = getTextLine(ctx, text, column.width ? column.width : 100)
            let textLineCount = 0
            if (textLine) {
              textLineCount = textLine.length
            }
            if (textLineCount > 1) {
              if (maxHeight < rowHeight + ((textLineCount - 1) * 18)) {
                maxHeight = rowHeight + ((textLineCount - 1) * 18)
              }
            }
          }

          if (column.fixed) {
            cellTemp.push({
              width: column.width ? column.width : 100,
              content: item[column.key],
              key: column.key,
              rowIndex,
              cellIndex,
              paintText: textLine,
              fixed: column.fixed === true,
              readOnly: column.readOnly === true,
              buttons,
              renderText: column.renderText,
              renderButton: column.renderButton,
              rowData: item,
              type: column.type,
              cellPosition: this.words[cellIndex] + (rowIndex + 1)
            })
          } else {
            cellTemp.push({
              width: column.width ? column.width : 100,
              content: item[column.key],
              key: column.key,
              rowIndex,
              cellIndex,
              paintText: textLine,
              fixed: column.fixed === true,
              readOnly: column.readOnly === true,
              buttons,
              renderText: column.renderText,
              renderButton: column.renderButton,
              rowData: item,
              type: column.type,
              cellPosition: this.words[cellIndex] + (rowIndex + 1)
            })
          }
          cellIndex += 1
        }
        allCells.push(cellTemp)

        let showDot = false
        if (this.showDot) {
          if (item[this.showDot.key] === this.showDot.value) {
            showDot = true
          }
        }
        allRows.push({
          height: maxHeight,
          rowIndex,
          showDot
        })
        rowIndex += 1
      }
      if (sumSaleprice > 0 && sumPurchasePrice > 0) {
        this.sumRate = parseFloat((((sumSaleprice - sumPurchasePrice) / sumSaleprice) * 100).toFixed(2))
      } else {
        this.sumRate = 0
      }
      for (const item of fixedColumns) {
        const temp = []
        let index = 0
        for (const row of allCells) {
          const cell = row[item.cellIndex]
          temp.push({
            ...cell,
            height: allRows[index].height
          })
          index += 1
        }
        allFixedCells.push(temp)
      }
    },
    fullScreen () { },
    initSize () {
      if (this.$refs.grid) {
        this.width = this.$refs.grid.offsetWidth - 2
        this.height = this.leftHeight ? window.innerHeight - this.leftHeight : 500

        if (this.showCheckbox) {
          if (this.initSelected) {
            this.selected = [...this.initSelected]
          }
          this.originPoint.x = this.serialWidth + this.checkboxWidth
          this.bodyWidth += this.checkboxWidth
        } else {
          this.originPoint.x = this.serialWidth
          this.bodyWidth -= this.checkboxWidth
        }
        this.bodyWidth = this.originPoint.x
        let columnCount = 0
        for (const column of this.allColumns) {
          if (column.checked) {
            this.bodyWidth += column.width ? column.width : 100
            columnCount += 1
          }
        }
        this.fillWidth = 0
        if (this.bodyWidth < this.width - this.scrollerWidth) {
          this.fillWidth = (this.width - this.bodyWidth - this.scrollerWidth) / columnCount
          this.bodyWidth = this.width - this.scrollerWidth
        }
        this.setBodyHeight(this.allRows, this.originPoint)
        this.setFixedWidth(this.allColumns, this.fillWidth)
        this.setMaxpoint(this.width, this.height, this.fixedWidth, this.scrollerWidth, this.fillWidth)
        this.resetScrollBar(this.maxPoint, this.bodyWidth, this.bodyHeight, this.fixedWidth)
        requestAnimationFrame(this.rePainted)
      }
    },
    setFixedWidth (allColumns, fillWidth) {
      this.fixedWidth = 0
      for (const column of allColumns) {
        if (column.checked && column.fixed) {
          this.fixedWidth += column.width ? column.width : 100
          this.fixedWidth += fillWidth
        }
      }
    },
    setBodyHeight (allRows, { y }) {
      this.bodyHeight = y + this.toolbarHeight
      for (const row of allRows) {
        this.bodyHeight += row.height
      }
    },
    setMaxpoint (width, height, fixedWidth, scrollerWidth, fillWidth) {
      if (fillWidth > 0) {
        this.maxPoint.x = width - scrollerWidth
      } else {
        this.maxPoint.x = width - scrollerWidth - fixedWidth
      }
      this.maxPoint.y = height - scrollerWidth
    },
    setAllCells (startIndex) {
      const { rowHeight, ctx, getTextLine, allRows, allCells, columns } = this
      let rowIndex = startIndex
      let sumSaleprice = 0
      let sumPurchasePrice = 0
      for (let i = startIndex; i < this.data.length; i += 1) {
        const item = this.data[i]
        let maxHeight = rowHeight
        let cellIndex = 0
        const cellTemp = []
        if (item.salePrice > 0 && item.purchasePrice > 0) {
          sumSaleprice += parseFloat(item.salePrice)
          sumPurchasePrice += parseFloat(item.purchasePrice)
        }
        for (const column of columns) {
          let text = ''
          let buttons
          let textLine
          if (column.renderText) {
            text = column.renderText(item)
          } else if (column.renderButton) {
            buttons = column.renderButton(this.data[rowIndex], rowIndex)
          } else {
            text = item[column.key]
          }
          if (text || text === 0) {
            textLine = getTextLine(ctx, text, column.width ? column.width : 100)
            let textLineCount = 0
            if (textLine) {
              textLineCount = textLine.length
            }
            if (textLineCount > 1) {
              if (maxHeight < rowHeight + ((textLineCount - 1) * 18)) {
                maxHeight = rowHeight + ((textLineCount - 1) * 18)
              }
            }
          }
          cellTemp.push({
            width: column.width ? column.width : 100,
            content: item[column.key],
            key: column.key,
            rowIndex,
            cellIndex,
            paintText: textLine,
            fixed: column.fixed === true,
            readOnly: column.readOnly === true,
            buttons,
            renderText: column.renderText,
            renderButton: column.renderButton,
            rowData: item,
            type: column.type
          })
          cellIndex += 1
        }
        allCells.push(cellTemp)

        let showDot = false
        if (this.showDot) {
          if (item[this.showDot.key] === this.showDot.value) {
            showDot = true
          }
        }
        allRows.push({
          height: maxHeight,
          rowIndex,
          showDot
        })
        rowIndex += 1
      }
      if (sumSaleprice > 0 && sumPurchasePrice > 0) {
        this.sumRate = parseFloat((((sumSaleprice - sumPurchasePrice) / sumSaleprice) * 100).toFixed(2))
      } else {
        this.sumRate = 0
      }
      this.setBodyHeight(this.allRows, this.originPoint)
      this.resetScrollBar(this.maxPoint, this.bodyWidth, this.bodyHeight, this.fixedWidth)
    },
    setCellItem (rowIndex, cellIndex, text) {
      const { ctx, allRows, allCells, getTextLine, rowHeight } = this
      const row = allRows[rowIndex]
      const cell = allCells[rowIndex][cellIndex]
      let maxHeight = 0
      const textLine = getTextLine(ctx, text, cell.width)
      let textLineCount = 0
      if (textLine) {
        textLineCount = textLine.length
      }
      if (textLineCount > 1) {
        if (maxHeight < rowHeight + ((textLineCount - 1) * 18)) {
          maxHeight = rowHeight + ((textLineCount - 1) * 18)
        }
      }
      if (maxHeight > row.height) {
        row.height = maxHeight
      }
      cell.content = text
      cell.paintText = textLine
    },
    setCellItemByKey (rowIndex, key, text) {
      const { ctx, allRows, allCells, getTextLine, rowHeight } = this
      const row = allRows[rowIndex]
      const cells = allCells[rowIndex]
      let index = 0
      let cell = null
      if (key === 'salePrice' || key === 'purchasePrice') {
        this.calculateSumRate()
        if (this.focusCell) {
          if (rowIndex === this.focusCell.rowIndex) {
            this.calculateRate([this.focusCell.rowData])
          }
        }
      }
      for (const item of cells) {
        if (item.key === key) {
          cell = allCells[rowIndex][index]
          break
        }
        index += 1
      }
      if (cell) {
        let maxHeight = 0
        const textLine = getTextLine(ctx, text, cell.width)
        let textLineCount = 0
        if (textLine) {
          textLineCount = textLine.length
        }
        if (textLineCount > 1) {
          if (maxHeight < rowHeight + ((textLineCount - 1) * 18)) {
            maxHeight = rowHeight + ((textLineCount - 1) * 18)
          }
        }
        if (maxHeight > row.height) {
          row.height = maxHeight
          this.initSize()
        }
        cell.content = text
        cell.paintText = textLine
        if (this.focusCell) {
          if (this.focusCell.rowIndex === rowIndex && this.focusCell.cellIndex === cell.cellIndex) {
            this.focusCell.content = text
            this.focusCell.paintText = textLine
          }
        }
      }
    },
    calculateRate (data) {
      let sumSaleprice = 0
      let sumPurchasePrice = 0
      for (const item of data) {
        if (item.salePrice > 0 && item.purchasePrice > 0) {
          sumSaleprice += parseFloat(item.salePrice)
          sumPurchasePrice += parseFloat(item.purchasePrice)
        }
      }
      if (sumSaleprice > 0 && sumPurchasePrice > 0) {
        this.rate = parseFloat((((sumSaleprice - sumPurchasePrice) / sumSaleprice) * 100).toFixed(2))
      } else {
        this.rate = 0
      }
    },
    calculateSumRate () {
      let sumSaleprice = 0
      let sumPurchasePrice = 0
      for (const item of this.data) {
        if (item.salePrice > 0 && item.purchasePrice > 0) {
          sumSaleprice += parseFloat(item.salePrice)
          sumPurchasePrice += parseFloat(item.purchasePrice)
        }
      }
      if (sumSaleprice > 0 && sumPurchasePrice > 0) {
        this.sumRate = parseFloat((((sumSaleprice - sumPurchasePrice) / sumSaleprice) * 100).toFixed(2))
      } else {
        this.sumRate = 0
      }
    },
    setCellItemAll (rowIndex, data) {
      let index = 0
      for (const item of data) {
        this.setCellItem(rowIndex, index, item)
        index += 1
      }
    },
    setCellRenderText (cell) {
      const text = cell.renderText(cell.rowData)
      const row = this.allRows[cell.rowIndex]
      if (text) {
        let maxHeight = 0
        const textLine = this.getTextLine(this.ctx, text, cell.width)
        let textLineCount = 0
        if (textLine) {
          textLineCount = textLine.length
        }
        if (textLineCount > 1) {
          if (maxHeight < this.rowHeight + ((textLineCount - 1) * 18)) {
            maxHeight = this.rowHeight + ((textLineCount - 1) * 18)
          }
        }
        if (maxHeight > row.height) {
          row.height = maxHeight
        }
        cell.content = text
        cell.paintText = textLine
      } else {
        cell.content = ''
        cell.paintText = []
      }
      return cell
    },
    getDisplayColumns () {
      const { offset: { x }, originPoint, maxPoint, allColumns, fillWidth } = this
      const temp = []
      let startX = originPoint.x + x

      for (const column of allColumns) {
        if (column.checked) {
          const width = column.width + fillWidth
          if (width + startX > originPoint.x && startX < maxPoint.x) {
            const columnClone = Object.assign({}, column, { x: startX, width })
            temp.push(columnClone)
          }
          startX += width
        }
      }
      setTimeout(() => { this.displayColumns = [...temp] }, 0)
      return temp
    },
    /**
       * 初始化显示行列
       */
    initDisplayItems () {
      const displayColumns = this.getDisplayColumns()
      const displayRows = this.getDisplayRows()
      const displayCells = this.getDisplayCells(displayRows, displayColumns)
      const displayFixedCells = this.getDisplayFixedCells(displayRows)
      if (this.focusCell) {
        this.freshFocusCell(this.focusCell.rowIndex, this.focusCell.cellIndex, displayRows, displayColumns)
        const lastOffset = this.focusCell.offset
        if (lastOffset.x !== this.offset.x || lastOffset.y !== this.offset.y) {
          this.focusCell.x -= lastOffset.x - this.offset.x
          this.focusCell.y -= lastOffset.y - this.offset.y
          this.focusCell.offset = { ...this.offset }
        }
      }
      if (this.selectArea) {
        const lastOffset = this.selectArea.offset
        this.selectArea.x -= lastOffset.x - this.offset.x
        this.selectArea.y -= lastOffset.y - this.offset.y
        this.selectArea.offset = { ...this.offset }
        let height = 0
        const rowDatas = []
        for (let i = this.selectArea.rowIndex; i < (this.selectArea.rowIndex + this.selectArea.rowCount); i += 1) {
          height += this.allRows[i].height
          rowDatas.push(this.allCells[i][0].rowData)
        }
        this.selectArea.height = height
        this.calculateRate(rowDatas)
      }
      if (this.multiSelect) {
        this.multiSelect.x -= this.multiSelect.offset.x - this.offset.x
        this.multiSelect.offset = { ...this.offset }
      }
      if (this.rowFocus) {
        const lastOffset = this.rowFocus.offset
        if (lastOffset.x !== this.offset.x || lastOffset.y !== this.offset.y) {
          this.rowFocus.y -= lastOffset.y - this.offset.y
          this.rowFocus.cellY -= lastOffset.y - this.offset.y
          if (!this.rowFocus.fixed) {
            this.rowFocus.x -= lastOffset.x - this.offset.x
            this.rowFocus.cellX -= lastOffset.x - this.offset.x
          }
          this.rowFocus.offset = { ...this.offset }
        }
      }
      return { displayColumns, displayRows, displayCells, displayFixedCells }
    },
    getDisplayRows () {
      const { offset: { y }, originPoint, maxPoint, allRows, toolbarHeight } = this
      const temp = []
      let startY = originPoint.y + y + toolbarHeight
      for (const row of allRows) {
        if (startY + row.height > originPoint.y + toolbarHeight &&
                    startY < maxPoint.y) {
          const rowClone = Object.assign({}, row, { y: startY })
          temp.push(rowClone)
        } else if (startY >= maxPoint.y) {
          break
        }
        startY += row.height
      }
      setTimeout(() => { this.displayRows = [...temp] }, 0)
      return temp
    },
    getDisplayCells (displayRows, displayColumns) {
      const temp = []
      const { allCells, fillWidth, setCellRenderText } = this
      for (const row of displayRows) {
        const cellTemp = []
        for (const column of displayColumns) {
          let cell = allCells[row.rowIndex][column.cellIndex]
          if (cell.renderText) {
            cell = setCellRenderText(cell)
          }
          if (cell.renderButton) {
            cell.buttons = column.renderButton(this.data[cell.rowIndex], cell.rowIndex)
          }
          const cellClone = Object.assign({}, cell, { x: column.x, y: row.y, width: cell.width + fillWidth, height: row.height }) //eslint-disable-line
          cellTemp.push(cellClone)
        }
        temp.push(cellTemp)
      }
      setTimeout(() => { this.displayCells = [...temp] }, 0)
      return temp
    },
    getDisplayFixedCells (displayRows) {
      const temp = []
      const { allFixedCells, fillWidth } = this
      for (const fixedCell of allFixedCells) {
        const fixedCellTemp = []
        for (const row of displayRows) {
          const fixed = fixedCell[row.rowIndex]
          if (fixed.renderButton) {
            fixed.buttons = fixed.renderButton(this.data[fixed.rowIndex], fixed.rowIndex)
          }
          const fixedCellClone = Object.assign({}, fixed, { y: row.y, width: fixed.width + fillWidth, height: row.height })
          fixedCellTemp.push(fixedCellClone)
        }
        temp.push(fixedCellTemp)
      }
      setTimeout(() => { this.displayallFixedCells = [...temp] }, 0)
      return temp
    },
    freshFocusCell (rowIndex, cellIndex, displayRows, displayColumns) {
      const firstRowIndex = displayRows[0].rowIndex
      const lastRowIndex = displayRows[displayRows.length - 1].rowIndex
      if (rowIndex >= firstRowIndex && rowIndex <= lastRowIndex) {
        this.focusCell.height = displayRows[rowIndex - firstRowIndex].height
      }
      for (const item of displayColumns) {
        if (item.cellIndex === cellIndex) {
          this.focusCell.width = item.width
        }
      }
    },
    focusCellByOriginCell (cell) {
      for (const row of this.displayCells) {
        for (const item of row) {
          if (item.rowIndex === cell.rowIndex && item.key === cell.key) {
            const focusCell = Object.assign({}, item, { offset: { ...this.offset } })
            this.focusCell = focusCell
            this.rowFocus = {
              cellX: focusCell.x,
              cellY: focusCell.y,
              rowIndex: this.focusCell.rowIndex,
              offset: { ...this.offset }
            }
            this.paintFocusCell(focusCell)
            return focusCell
          }
        }
      }
      return null
    }
  }
}
