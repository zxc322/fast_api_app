class Log:
    """ Completing text to write it to the file """

    def write_to_file_created(user):
        user = user.replace(', ', ',\n')
        full_text = '[INFO]\nnew user have been CREATED!\n'
        full_text += user + '\n'
        full_text += '=' * 100 + '\n'
        return full_text


    def write_to_file_updated(id, field, old, new):
        full_text = '[INFO]\nUser with id "{}" have been changed!\n'.format(id)
        full_text += 'Field [{}] have been changed\n'.format(field)
        full_text += 'Value "{}" replaced by "{}"\n'.format(old, new)
        full_text += '=' * 100 + '\n'
        return full_text


    def write_to_file_deleted(id):
        full_text = '[INFO]\nUser with id "{}" have been deleted!\n'.format(id)
        full_text += '=' * 100 + '\n'
        return full_text


def paginate_data(page, count, total_pages, end, limit):
    paginate = {'page': page,
                'objects_count': count,
                'total_pages': total_pages,
                'pages': dict()}

    if end >= count:
                paginate['pages']['next'] = None
                if page > 1:
                        paginate['pages']['previous'] = '/users/?page={}&limit={}'.format(page-1, limit)
                else:
                        paginate['pages']['previous'] = None
    else:
            if page > 1:
                    paginate['pages']['previous'] = '/users/?page={}&limit={}'.format(page-1, limit)
            else:
                    paginate['pages']['previous'] = None

            paginate['pages']['next'] = '/users/?page={}&limit={}'.format(page+1, limit)

    return paginate