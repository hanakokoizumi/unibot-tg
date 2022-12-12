from PIL import Image as PILImage
import os
import requests
asset_path = 'assets/online'


class Image:
    ANTIALIAS = PILImage.ANTIALIAS

    @classmethod
    def open(cls, *args, **kwargs):
        try:
            return PILImage.open(*args, **kwargs)
        except FileNotFoundError as e:
            print(e.filename + " not found")
            if e.filename.startswith(asset_path):
                filename = e.filename.replace(asset_path + '/', '')
                if not os.path.exists(os.path.abspath(os.path.join(e.filename, '..'))):
                    os.makedirs(os.path.abspath(os.path.join(e.filename, '..')))
                resp = requests.get('https://assets.pjsek.ai/file/pjsekai-assets/%s' % filename)
                if resp.status_code == 200:
                    with open(e.filename, 'wb') as f:
                        f.write(resp.content)
                    return PILImage.open(*args, **kwargs)
            else:
                raise e

    @classmethod
    def new(cls, *args, **kwargs):
        return PILImage.new(*args, **kwargs)
