export default {
  methods: {
    getTextLine (ctx, text, width) {
      if (!text && text !== 0) {
        return null
      }
      const chr = `${text}`.split('')
      let temp = ''
      const row = []
      for (let a = 0; a < chr.length; a += 1) {
        if (ctx.measureText(temp).width >= width - 20) {
          row.push(temp)
          temp = ''
        }
        temp += chr[a]
      }
      row.push(temp)
      return row
    },
    getCellAt (x, y) {
      for (const rows of this.displayCells) {
        for (const cell of rows) {
          if (x >= cell.x && y >= cell.y && x <= cell.x + cell.width && y <= cell.y + cell.height) {
            return Object.assign({}, cell, { offset: { ...this.offset } })
          }
        }
      }
      return null
    },
    getCheckboxAt (x, y) {
      for (const check of this.checkboxs) {
        if (x >= check.x && y >= check.y && x <= check.x + check.width && y <= check.y + check.height) {
          return Object.assign({}, check)
        }
      }
      return null
    },
    getButtonAt (x, y) {
      for (const button of this.renderButtons) {
        if (x >= button.x && y >= button.y && x <= button.x + button.width && y <= button.y + button.height) {
          return Object.assign({}, button)
        }
      }
      return null
    },
    getHeadWord (x, y) {
      if (y > this.toolbarHeight - this.rowHeight && y < this.toolbarHeight) {
        for (const column of this.displayColumns) {
          if (x > column.x && x < column.x + column.width) {
            return Object.assign({}, column)
          }
        }
      }
      return null
    },
    getCellsBySelect (area) {
      const cells = []
      for (let i = area.rowIndex; i < area.rowIndex + area.rowCount; i += 1) {
        const row = this.allCells[i]
        const temp = []
        let startX = 0
        let maxWidth = Infinity
        for (let j = 0; j < row.length; j += 1) {
          if (area.cellIndex === j) {
            maxWidth = startX + area.width
          }
          if (startX < maxWidth && j >= area.cellIndex) {
            temp.push(row[j])
          } else if (startX > maxWidth) {
            break
          }
          startX += row[j].width + this.fillWidth
        }
        cells.push(temp)
      }
      return cells
    },
    getCellByRowAndKey (rowIndex, key) {
      const cells = this.allCells[rowIndex]
      for (const cell of cells) {
        if (cell.key === key) {
          return cell
        }
      }
      return null
    },
    showInput (x, y, width, height) {
      this.isEditing = true
      this.inputStyles = {
        position: 'absolute',
        top: `${y - 1}px`,
        left: `${x - 1}px`,
        minWidth: `${width + 2}px`,
        maxWidth: `${this.maxPoint.x - x > 300 ? 300 : this.maxPoint.x - x}px`,
        minHeight: `${height + 2}px`
      }
    },
    hideInput () {
      this.isEditing = false
      this.inputStyles = {
        top: '-10000px',
        left: '-10000px'
      }
    },
    showTipMessage (message) {
      this.tipMessage = message
      this.showTip = true
      setTimeout(() => {
        this.showTip = false
      }, 2000)
    },
    evalUtil (expression) {
      const value = expression.replace('=', '').replace(/ /ig, '').toUpperCase()// 取等号后表达式，去除空格
      const expressions = value.split('&')
      const result = []
      for (const expression of expressions) {
        let regionType = ''
        let equation = expression
        const indexArray = []
        if (expression.indexOf('=>') !== -1) { // 指定了区域
          const region = expression.split('=>')[0]
          equation = expression.split('=>')[1]
          const regionReg = /^(include)?\(.+\)|(exclude|!)\(.+\)$/i
          if (regionReg.test(region)) {
            const regionValue = region.match(/\(.+\)/)[0].replace('(', '').replace(')', '').split(',')
            for (const item of regionValue) {
              if (item.indexOf('-') !== -1) {
                const temp = item.split('-')
                if (temp.length === 2) {
                  if (!isNaN(temp[0]) && !isNaN(temp[1]) && parseInt(temp[0], 10) > 0 && parseInt(temp[0], 10) < parseInt(temp[1], 10)) {
                    for (let i = temp[0] - 1; i < temp[1]; i += 1) {
                      indexArray.push(i)
                    }
                  }
                } else {
                  throw new Error('区域表达式非法')
                }
              } else if (!isNaN(item)) {
                indexArray.push(parseInt(item, 10) - 1)
              } else {
                throw new Error('区域表达式非法')
              }
            }
            if (/^(include)?\(.+\)$/i.test(region)) {
              regionType = 'include'
            } else if (/^(exclude|!)\(.+\)$/i.test(region)) {
              regionType = 'exclude'
            }
          } else {
            throw new Error('区域表达式非法')
          }
        }
        if (equation) {
          let index = 0
          for (const word of this.words) {
            if (equation.indexOf(word) !== -1) {
              equation = equation.replace(new RegExp(word, 'gi'), `this.allCells[$x$][${index}].content`)
            }
            index += 1
          }
        }
        result.push({ equation, indexArray, regionType })
      }
      return result
    }
  }
}
