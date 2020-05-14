from app import db


class BreadCrumb:
    def __init__(self, url=None, obj=None):
        self.add_urls = [{'link': '/converter', 'name': 'Конвертер величин'}, {'link': '/', 'name': 'Главная'}]
        self.count = url.count('/') - 1
        self.obj = obj
        self.url = url
        self.lis = []


    def breadcrumb(self):
        for i, ob in zip(range(self.count), self.obj):
            link = self.url.rsplit('/', i)
            name = link[0].rsplit('/')
            self.lis.append({'link': link[0], 'name': self.breadcrumb_request(ob=ob, slug=name[-1])})

        self.lis.extend(self.add_urls)
        self.lis.reverse()

        return self.lis

    def breadcrumb_request(self, ob, slug):
        obj = db.session.query(ob).filter_by(slug=slug).first()
        return obj.name

    def __str__(self):
        return f'< class BreadCrumb > {self.url} | {self.obj}'
