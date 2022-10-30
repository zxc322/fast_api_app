from typing import Dict

async def paginate_data(page, count, total_pages, end, limit, url) -> Dict:
    paginate = {'page': page,
                'objects_count': count,
                'total_pages': total_pages,
                'pages': dict()}

    if end >= count:
                paginate['pages']['next'] = None
                if page > 1:
                        paginate['pages']['previous'] = '/{}/?page={}&limit={}'.format(url, page-1, limit)
                else:
                        paginate['pages']['previous'] = None
    else:
            if page > 1:
                    paginate['pages']['previous'] = '/{}/?page={}&limit={}'.format(url, page-1, limit)
            else:
                    paginate['pages']['previous'] = None

            paginate['pages']['next'] = '/{}/?page={}&limit={}'.format(url, page+1, limit)

    return paginate