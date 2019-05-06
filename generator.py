import requests
import ast


class KajGenerator(object):

    def MakeUsername(self, count=None):
        '''
        generates a list of strings
        '''
        url = "http://names.drycodes.com/"
        params = {}
        if count is not None:
            url = url + str(count)

        r = requests.get(url, params=params)
        print(r)
        if r.status_code is 200:
            if r.text is not None:
                parsed_names = ast.literal_eval(r.text)
                return parsed_names
        else:
            print('error in getting random nickname')
            return None
