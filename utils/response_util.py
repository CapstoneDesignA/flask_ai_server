def to_failure_response(msg):
    response = {'isSuccess': False, 'message': msg}
    return response


def to_success_response(data):
    response = {'isSuccess': True, 'data': data}
    return response
