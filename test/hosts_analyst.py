#!/usr/bin/python
import decimal

a = ((1L, 0), (1L, 0), (1L, 2), (1L, 0), (1L, 0), (1L, 1), (177L, 2))

host_list = list()
for item in a:
    host_list.append(item[0])
unique_host_list = list(set(host_list))

host_list_dict = dict().fromkeys(unique_host_list,None)


def get_total_and_success(id):
    total_item = 0
    success_item = 0
    for i in a:
        if i[0] == id:
            if i[1] == 0:
                success_item += 1
            total_item += 1
    return total_item,success_item


for host_id in unique_host_list:
    total_item,success_item = get_total_and_success(host_id)
    host_list_dict[host_id] =  int(decimal.Decimal(success_item)/decimal.Decimal(total_item)*100)
