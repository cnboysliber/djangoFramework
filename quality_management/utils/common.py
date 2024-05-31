
def get_user_info(request):  # add接口加入用户信息
    data = request.data
    _mutable = data._mutable
    data._mutable = True
    data['creator'] = request.user.username
    data['updater'] = request.user.username
    data._mutable = _mutable
    return request

# def get_version_info(queryset_month, queryset_version, queryset_child):
#     if queryset_month is not None:
#         for item_month in queryset_month:
#             queryset_version = self.queryset_version.filter(status=cnt.ACTIVE, month_version_id=item_month['id']). \
#                 values('id', 'name').order_by('-update_time')
#             if queryset_version is not None:
#                 for item_version in queryset_version:
#                     queryset_child = self.queryset_child.filter(status=cnt.ACTIVE, version_id=item_version['id']). \
#                         values('system_name', 'version_num').order_by('-update_time')
#                     if queryset_child is not None:
#                         for item_child in queryset_child:
#                             version_list.append({'year_month': item_month['year_month'],
#                                                  'name': item_version['name'],
#                                                  'system_name': item_child['system_name'],
#                                                  'version_num': item_child['version_num']})
#                     else:
#                         version_list.append({'year_month': item_month['year_month'], 'name': item_version['name']})
#             else:
#                 version_list.append({'year_month': item_month['year_month']})
#     else:
#         version_list = None