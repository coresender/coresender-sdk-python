from .core import CoresenderApiResponse


class SendEmailResponse:
    __slots__ = ('message_id', 'custom_id', 'status', 'errors')

    def __init__(self, data: dict):
        self.message_id = data['message_id']
        self.custom_id = data['custom_id']
        self.status = data['status']
        self.errors = data['errors'] or ''

    def __repr__(self):
        r = ', '.join(['%s="%s"' % (item, getattr(self, item)) for item in self.__slots__])
        r = '<SendEmailResponse ' + r + '>'
        return r


class SendEmail(CoresenderApiResponse):
    def __init__(self, http_status, data):
        self.entries = [SendEmailResponse(item) for item in data['data']]
        self.http_status = http_status

    @property
    def all_accepted(self):
        return self.http_status == 200

    def __repr__(self):
        return '<SendEmail entries=%r>' % (self.entries, )

    def __iter__(self):
        return iter(self.entries)
