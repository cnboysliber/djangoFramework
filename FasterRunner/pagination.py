"""
Pagination serializers determine the structure of the output that should
be used for paginated responses.
"""
from collections import OrderedDict

from rest_framework import pagination
from rest_framework.response import Response


class MyCursorPagination(pagination.CursorPagination):
    """
    Cursor 光标分页 性能高，安全
    """
    page_size = 10
    ordering = '-update_time'
    page_size_query_param = "page"
    max_page_size = 999


class MyPageNumberPagination(pagination.PageNumberPagination):
    """
    普通分页，数据量越大性能越差
    """
    page_size = 10
    page_size_query_param = 'size'
    page_query_param = 'page'
    max_page_size = 999

    def paginate_queryset(self, queryset, request, view=None):
        """
        Paginate a queryset if required, either returning a
        page object, or `None` if pagination is not configured for this view.
        """
        page_size = self.get_page_size(request)
        if not page_size:
            return None

        paginator = self.django_paginator_class(queryset, page_size)
        page_number = request.query_params.get(self.page_query_param, 1)
        if page_number in self.last_page_strings:
            page_number = paginator.num_pages
        if (paginator.count + 1) // page_size + 1 < int(page_number):
            page_number = (paginator.count + 1) // page_size + 1
        try:
            self.page = paginator.page(page_number)
        except Exception as exc:
            msg = self.invalid_page_message.format(
                page_number=page_number, message=str(exc)
            )
            raise paginator.NotFound(msg)

        if paginator.num_pages > 1 and self.template is not None:
            # The browsable API should display pagination controls.
            self.display_page_controls = True

        self.request = request
        return list(self.page)

    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('count', self.page.paginator.count),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('results', data)
        ]))


class MyLimitOffsetPagination(pagination.LimitOffsetPagination):
    limit_query_param = 'size'
    offset_query_param = "page"

