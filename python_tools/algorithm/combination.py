two_list = [['移库类型（只能创建新批次/序列号）', '移库类型（只能使用已有批次/序列号）', '移库类型（能使用已有（和创建）批次/序列号）'], ['1', '2'], ['!', '#']]
def combination_list(target_list, val_index, result_list):
    if len(target_list) == len(result_list) :
        for (list_index, val) in enumerate(result_list):
            print('%s)' % list_index, val)
        print()
    else: 
        for val in target_list[val_index]:
            next_index = 0
            result_list_new = result_list[::]
            result_list_new.append(val)
            next_index = val_index + 1
            combination_list(target_list, next_index, result_list_new)
combination_list(two_list, 0, [])
