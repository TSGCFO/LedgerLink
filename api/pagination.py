from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from collections import OrderedDict
from django.conf import settings

class StandardResultsSetPagination(PageNumberPagination):
    """
    Standard pagination class for consistent list endpoint responses.
    
    Response format:
    {
        "success": true,
        "data": {
            "count": total number of items,
            "total_pages": total number of pages,
            "current_page": current page number,
            "page_size": number of items per page,
            "results": [...] // array of items
        },
        "links": {
            "next": url for next page,
            "previous": url for previous page,
            "first": url for first page,
            "last": url for last page
        }
    }
    """
    page_size = getattr(settings, 'REST_FRAMEWORK', {}).get('PAGE_SIZE', 10)
    page_size_query_param = 'page_size'
    max_page_size = 100
    
    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('success', True),
            ('data', OrderedDict([
                ('count', self.page.paginator.count),
                ('total_pages', self.page.paginator.num_pages),
                ('current_page', self.page.number),
                ('page_size', self.get_page_size(self.request)),
                ('results', data)
            ])),
            ('links', OrderedDict([
                ('next', self.get_next_link()),
                ('previous', self.get_previous_link()),
                ('first', self.get_first_link()),
                ('last', self.get_last_link())
            ]))
        ]))
    
    def get_first_link(self):
        """
        Get the URL for the first page.
        """
        if not self.page.paginator.num_pages:
            return None
        url = self.request.build_absolute_uri()
        return self.remove_query_param(url, self.page_query_param)
    
    def get_last_link(self):
        """
        Get the URL for the last page.
        """
        if not self.page.paginator.num_pages:
            return None
        url = self.request.build_absolute_uri()
        page_number = self.page.paginator.num_pages
        return self.replace_query_param(url, self.page_query_param, page_number)
    
    def get_page_size(self, request):
        """
        Get the page size from query parameters or use default.
        Ensures the page size doesn't exceed the maximum allowed.
        """
        if self.page_size_query_param:
            try:
                page_size = int(request.query_params.get(
                    self.page_size_query_param, self.page_size
                ))
                return min(page_size, self.max_page_size)
            except (TypeError, ValueError):
                pass
        return self.page_size

class LargeResultsSetPagination(StandardResultsSetPagination):
    """
    Pagination class for endpoints that need to handle larger page sizes.
    Useful for admin interfaces or bulk operations.
    """
    page_size = 100
    max_page_size = 1000

class SmallResultsSetPagination(StandardResultsSetPagination):
    """
    Pagination class for endpoints that should return fewer results.
    Useful for mobile apps or performance-critical endpoints.
    """
    page_size = 5
    max_page_size = 20