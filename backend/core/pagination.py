"""
Custom paginator that wraps all list responses in a consistent envelope.

Standard DRF pagination response:
  {
    "count": 100,
    "next": "http://...",
    "previous": null,
    "results": [...]
  }

Our response adds success flag and is easier to handle in React:
  {
    "success": true,
    "count": 100,
    "total_pages": 5,
    "current_page": 1,
    "next": "http://...",
    "previous": null,
    "results": [...]
  }
"""
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class StandardPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'   # ?page_size=50
    max_page_size = 100
    page_query_param = 'page'             # ?page=2

    def get_paginated_response(self, data):
        return Response({
            'success': True,
            'count': self.page.paginator.count,
            'total_pages': self.page.paginator.num_pages,
            'current_page': self.page.number,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'results': data,
        })

    def get_paginated_response_schema(self, schema):
        """Describes the pagination envelope for API documentation."""
        return {
            'type': 'object',
            'properties': {
                'success': {'type': 'boolean'},
                'count': {'type': 'integer'},
                'total_pages': {'type': 'integer'},
                'current_page': {'type': 'integer'},
                'next': {'type': 'string', 'nullable': True},
                'previous': {'type': 'string', 'nullable': True},
                'results': schema,
            }
        }