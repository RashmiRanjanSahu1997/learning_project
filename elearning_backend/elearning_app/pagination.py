from rest_framework.pagination import PageNumberPagination
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
import math


def get_pagination(request,obj):
    data_count = len(obj)
    if data_count > 0:
        count = data_count
    else:
        count = 1
    page_size = request.query_params.get('page_size',count)
    page_index = request.query_params.get("page_index",1)
    res_data = Paginator(obj,page_size)
    try: 
        page_obj = res_data.page(page_index)
    except PageNotAnInteger :
        page_obj = res_data.page(1)
    except ZeroDivisionError:
        page_obj = res_data.page(1)
    except EmptyPage:
        page_obj = []

    try:
        total_page =  math.ceil(int(data_count)/int(page_size))
    except Exception as e:
        total_page =  math.ceil(int(data_count)/1)
    return page_obj,total_page