from rest_framework.renderers import JSONRenderer

class EmberJSONRenderer(JSONRenderer):

    def render(self, data, accepted_media_type=None, renderer_context=None):
        if isinstance(data,dict):
            if not data.pop('NOCHANGE',False):
                data = {'status': 'ok','data':data}
        else:
            data = {'status': 'ok', 'data': data}


        return super(EmberJSONRenderer, self).render(data, accepted_media_type, renderer_context)
