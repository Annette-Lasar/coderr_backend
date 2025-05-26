from rest_framework.pagination import PageNumberPagination


class SixPerPagePagination(PageNumberPagination):
    """
    Custom pagination class that limits the API response to 6 items 
    per page by default.
    """
    page_size = 6
    page_size_query_param = 'page_size'
    max_page_size = 100
