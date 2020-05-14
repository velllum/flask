from builtins import super
from builtins import float

from app import db
import re

"""=============================================== калькулятор ед. измерения ======================================="""

# создаем таблицу с именами видов всех единиц измерения
class Category(db.Model):
    __tablename__ = 'category'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(255))
    slug = db.Column(db.String(255))
    title = db.Column(db.String(255))
    description = db.Column(db.Text())

    # # создаем связь между таблицей постов и тегов , также связь будет и в тегах через свойство posts
    # types = db.relationship('Type', secondary=Category_Type, backref=db.backref('categories', lazy='dynamic'))

    # связь с таблицей Unit одна ко многим
    u = db.relationship('Unit', back_populates='category')

    # связь с таблицей Type одна ко многим
    t = db.relationship('Type', back_populates='category')

    def __init__(self, *args, **wkargs):
        super(Category, self).__init__(*args, **wkargs)

    def __repr__(self):
        return f'{self.id} | {self.name} | {self.slug} | {self.title} | {self.description}'


# создаем таблицу, связь многие ко многим Type (типов конвертеров) и Si_units (видов единиц измерений)
Type_Si_units = db.Table('type_si_units',
                         db.Column('type_id', db.Integer, db.ForeignKey('type.id')),
                         db.Column('si_units_id', db.Integer, db.ForeignKey('si_units.id'))
                         )


# создаем таблицу для видов единиц измерения
class Type(db.Model):
    __tablename__ = 'type'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(255))
    description = db.Column(db.Text())
    slug = db.Column(db.Text())

    # создаем связь между таблицей Si_units через перм. si , также связь будет и в таблице Si_units через прем. types
    si = db.relationship('Si_units', secondary=Type_Si_units, backref=db.backref('ty', lazy='dynamic'))

    # связ с таблицей Unit
    u = db.relationship('Unit', back_populates='type')

    # связ с таблицей Category
    category_id = db.Column(db.Integer(), db.ForeignKey('category.id'))
    category = db.relationship('Category', back_populates='t')

    def __init__(self, *args, **wkargs):
        super(Type, self).__init__(*args, **wkargs)

    def __repr__(self):
        return f'{self.id} | {self.name} | {self.slug} | {self.description}'


# создаем таблицу для видов единиц измерения
class Si_units(db.Model):
    __tablename__ = 'si_units'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(255))
    slug = db.Column(db.Text())

    # связ с таблицей Unit
    u = db.relationship('Unit', back_populates='si_units')

    def __init__(self, *args, **wkargs):
        super(Si_units, self).__init__(*args, **wkargs)

    def __repr__(self):
        return f'{self.id} | {self.name} | {self.slug}'


# создаем таблицу для единиц измерения
class Unit(db.Model):
    __tablename__ = 'unit'
    id = db.Column(db.Integer(), primary_key=True)
    unit = db.Column(db.Float(), default=0)
    name = db.Column(db.String(255))
    symbol = db.Column(db.String(255))
    name_symbol = db.Column(db.String(255))
    description = db.Column(db.Text())

    slug = db.Column(db.Text())
    type_name = db.Column(db.String(255))
    type_category = db.Column(db.String(255))
    type_converter = db.Column(db.String(255))

    type_id = db.Column(db.Integer(), db.ForeignKey('type.id'))
    type = db.relationship('Type', back_populates='u')

    category_id = db.Column(db.Integer(), db.ForeignKey('category.id'))
    category = db.relationship('Category', back_populates='u')

    si_units_id = db.Column(db.Integer(), db.ForeignKey('si_units.id'))
    si_units = db.relationship('Si_units', back_populates='u')

    def __init__(self, *args, **wkargs):
        super(Unit, self).__init__(*args, **wkargs)

    def __repr__(self):
        return f'{self.id} | {self.name} | {self.unit} | {self.symbol} | {self.type_category} | {self.type_name}'
        
    # ================================================== методы модели =====================================================

    # переводим единицы измерения
    @staticmethod
    def get_result_calc(s, u, v):
        obj = db.session.query(Unit).filter_by(slug=s).first()
        return (u / obj.unit) * float(v)

    # убераем все html теги из текста
    def clear_html_description(self):
        return re.sub(r'<[^>]*>', '', self.description)


"""===================================================== поиск по базе =============================================="""
from datetime import datetime
from slugify import slugify
from sqlalchemy import func


# создаем таблицу вид прибора
class Type_device(db.Model):
    __tablename__ = 'type_device'
    __searchable__ = ['name']
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(255))
    description = db.Column(db.String(255))
    slug = db.Column(db.String(255))
    count = db.Column(db.Integer())


    def __init__(self, *args, **wkargs):
        super(Type_device, self).__init__(*args, **wkargs)

    def __repr__(self):
        return f'{self.id} | {self.name} | {self.description} | {self.slug}'



class Data(db.Model):
    __tablename__ = 'updated_data'
    __searchable__ = ['NumberSI', 'NameSI', 'DesignationSI', 'ManufacturerSI']

    ids = db.Column(db.Integer, primary_key=True)
    dates = db.Column(db.DateTime, default=datetime.now())  # Дата записи в базу

    date = db.Column(db.String(255))  # дата опубликования
    NameSI = db.Column(db.Text())  # Наименование СИ
    NumberSI = db.Column(db.String(255))  # Номер госреестра
    MPISI = db.Column(db.String(600))  # Межповерочный интервал МПИ
    CertificateLifeSI = db.Column(db.String(255))  # Срок свидетельства
    DesignationSI = db.Column(db.Text())  # Обозначение типа СИ
    YearSI = db.Column(db.Integer())  # Лет
    ManufacturerTotalSI = db.Column(db.Text())  # Изготовитель средства измерения
    CountrySI = db.Column(db.String(255))  # Страна
    SettlementSI = db.Column(db.String(255))  # Населенный пункт
    ManufacturerSI = db.Column(db.Text())  # Предприятие-изготовитель
    DescriptionSI = db.Column(db.String(255))  # Описание типа ссылка
    MethodVerifSI = db.Column(db.String(255))  # Методики поверки ссылка
    DescriptionSiName = db.Column(db.String(255))  # Описание типа имя файла
    MethodVerifSiName = db.Column(db.String(255))  # Методики поверки имя файла
    FactoryNumSI = db.Column(db.Text())  # Заводской номер
    id = db.Column(db.Integer())  # ID

    # name_device = db.Column(db.String(255))  # наименование прибора ( манометры, напоромеры, дифманометры )
    Maker = db.Column(db.Text())  # Сгенерированный ManufacturerTotalSI
    Slug = db.Column(db.Text())  # Сгенерированный NameSI + id

    def __init__(self, *args, **wkargs):
        super(Data, self).__init__(*args, **wkargs)

    def __repr__(self):
        return f'{self.ids} | {self.ManufacturerTotalSI} | {self.MethodVerifSI} | {self.DescriptionSI}'

    # ================================================== методы модели =====================================================

    # получить кольичетво производителей
    def get_count(self, value):
        return db.session.query(func.count(Data.Maker)).filter(Data.Maker == value).scalar()

    # получаем из ссылки id
    def get_id_from_link(self, link):
        if link:
            return link.rsplit('-', 1)[-1]

    # создаем ссылку
    def create_link(self):
        if self.NameSI:
            return f'{slugify(self.NameSI)}-{self.ids}'
        return f'{self.NumberSI}-{self.ids}'

    # шаблон для реализации вывода подсветки поиска
    def repl(self, match):
        return f'<mark>{match[0]}</mark>'

    # выборка из поиска найденного значения
    def rex_select_row(self, text, value):
        if value is not None and value != '':
            return re.sub(fr'{value.split()[0]}\s*([А-Яа-яЁёA-Za-z0-9]*)', self.repl, text, flags=re.IGNORECASE)
        return text



"""===================================================== обновленная база поиска ===================================================="""

class updated_data(db.Model):
    __tablename__ = 'data'

    ids = db.Column(db.Integer, primary_key=True)
    dates = db.Column(db.DateTime, default=datetime.now())  # Дата записи в базу

    date = db.Column(db.String(255))  # дата опубликования
    NameSI = db.Column(db.Text())  # Наименование СИ
    NumberSI = db.Column(db.String(255))  # Номер госреестра
    MPISI = db.Column(db.String(600))  # Межповерочный интервал МПИ
    CertificateLifeSI = db.Column(db.String(255))  # Срок свидетельства
    DesignationSI = db.Column(db.Text())  # Обозначение типа СИ
    YearSI = db.Column(db.Integer())  # Лет
    ManufacturerTotalSI = db.Column(db.Text())  # Изготовитель средства измерения
    CountrySI = db.Column(db.String(255))  # Страна
    SettlementSI = db.Column(db.String(255))  # Населенный пункт
    ManufacturerSI = db.Column(db.Text())  # Предприятие-изготовитель
    DescriptionSI = db.Column(db.String(255))  # Описание типа ссылка
    MethodVerifSI = db.Column(db.String(255))  # Методики поверки ссылка
    DescriptionSiName = db.Column(db.String(255))  # Описание типа имя файла
    MethodVerifSiName = db.Column(db.String(255))  # Методики поверки имя файла
    FactoryNumSI = db.Column(db.Text())  # Заводской номер
    id = db.Column(db.Integer())  # ID

    Maker = db.Column(db.Text())  # Сгенерированный ManufacturerTotalSI
    Slug = db.Column(db.Text())  # Сгенерированный NameSI + id

    def __init__(self, *args, **wkargs):
        super(updated_data, self).__init__(*args, **wkargs)

    def __repr__(self):
        return f'{self.ids} | {self.ManufacturerTotalSI} | {self.MethodVerifSI} | {self.DescriptionSI}'



"""===================================================== новости ===================================================="""

from PIL import Image

RU_SLUG_VALUES = {
    'metrologiya': 'Метрология',
    'standartizatsiya': 'Стандартизация',
    'zakonodatelstvo': 'Законодательство',
    'meropriyatiya': 'Мероприятия',
    'nauka': 'Наука и техника',
    'novosti_kompaniy': 'Новости компании',
    'drugie-novosti': 'Другие новости',
}


class News(db.Model):
    __tablename__ = 'news'
    id = db.Column(db.Integer(), primary_key=True)
    title = db.Column(db.String(400))
    slug = db.Column(db.String(400), unique=True)
    content = db.Column(db.Text())
    date_cont = db.Column(db.String(50))
    date = db.Column(db.DateTime(), default=datetime.now())
    date_sort = db.Column(db.DateTime())
    image = db.Column(db.String(400))
    category = db.Column(db.String(50))

    def __init__(self, *args, **wkargs):
        super(News, self).__init__(*args, **wkargs)

    # реализация для просмотра в объекте его свойств через консоль
    def __repr__(self):
        return f'{self.id} | {self.title} | {self.slug} | {self.content}'
        
    # ================================================== методы модели =====================================================

    # убераем все html теги из текста
    def clear_html_content(self):
        return re.sub(r'<[^>]*>', '', self.content)

    # вывод категории
    def get_category(self):
        for key, value in RU_SLUG_VALUES.items():
            if key == self.category:
                return str(value)

    # вывод категории в заголовок h1
    @staticmethod
    def convert_category_news(name):
        for key, value in RU_SLUG_VALUES.items():
            if key == name:
                return str(value)

    # вывод картинки
    def get_image(self):
        if not self.image:
            return 'news/video-poster.jpg'
        return f'news/image/{self.image}'

    # порезать картинку и сохранить
    def convert_thumbnail_image(self):
        thumbnail = f'static/news/image_thumbnail/thumbnail-{self.image}'
        image = Image.open(f'static/{self.get_image()}')
        cropped = image.crop((0, 0, min(image.size), min(image.size)))
        cropped.save(thumbnail)
        return thumbnail

    # вывод картинки эскиза
    def get_thumbnail(self):
        if not self.image:
            return 'news/video-poster.jpg'
        thumbnail = f'news/image_thumbnail/thumbnail-{self.image}'
        if thumbnail:
            return thumbnail
        return self.convert_thumbnail_image()

