class Log:
    """ Generate text to write it to the file """

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