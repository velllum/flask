from flask import render_template, request, send_from_directory
from datetime import datetime
from sqlalchemy import func, distinct

from app import app

from flask_breadcrumbs import register_breadcrumb



"""============================================= основные страницы сайта ============================================="""
@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404

@app.route("/")
@register_breadcrumb(app, '.', 'Главная')
def index():
    data = Data.query.limit(10).all()
    news = News.query.order_by(News.date_sort.desc()).limit(5).all()
    types = Type.query.filter(Type.category_id==1).all()
    data_count = db.session.query(func.count(Data.ids)).scalar()
    maker_count = db.session.query(Data.ManufacturerSI).distinct()
    return render_template('index.html', page_name='Сайт по метрологии', news=news, types=types, data_count=data_count, maker_count=maker_count.count(), data=data)

@app.route("/about")
def about():
    return render_template('about.html', page_name='О нас')

@app.route('/robots.txt')
@app.route('/sitemap.xml')
def static_from_root():
    return send_from_directory(app.static_folder, request.path[1:])

@app.context_processor
def inject_now():
    return dict(now=datetime.utcnow())



"""=============================================== калькулятор ед. измерения ======================================="""
from flask import jsonify, url_for, redirect, flash, session
from helpers.breadcrumb import BreadCrumb
from models import Unit, Category, Type


# аякс запрос для получения списка конвертаров из выбьранного списка калькуляторов
@app.route('/processCalculator', methods=['POST'])
def processCalculator():
    slug = request.form.get('calculator')
    if slug:
        type = Category.query.filter(Category.slug == slug).first()
        d = {i.slug: i.name for i in type.t}
        return jsonify(d)

# аякс запрос для получения списка единиц измерения из выбьранного списка коверторов
@app.route('/processType', methods=['POST'])
def processType():
    slug = request.form.get('type')
    if slug:
        slug_type = Type.query.filter(Type.slug == slug).first()
        d = {}
        for s in slug_type.si:
            t = {}
            d[s.name] = t
            for unit in s.u:
                if unit.type_id == slug_type.id:
                    t[unit.slug] = f'{unit.name}'
        return jsonify(d)

#================================================================================================================
# главная страница с выводом калькуляторов
@app.route("/converter/", methods=['GET', 'POST'])
@app.route("/converter", methods=['GET', 'POST'])
def main_conv():
    if request.method == 'POST':

        session['value'] = request.form.get('num')
        session['symbol'] = request.form.get('symbol')

        slug = request.form.get('calculator')
        type = request.form.get('type')

        if slug == 'hidden':
            flash("-- тип калькулятора --")
        elif slug != None and slug != 'hidden' and type != None and type != 'hidden':
            return redirect(url_for('type_conv', slug=slug, type=type))
        elif slug != None and slug != 'hidden':
            return redirect(url_for('category_conv', slug=slug))

    return render_template('converter/main_conv.html', value=session.get('value', ''), categories=Category.query.all(), page_name='Калькуляторы единиц измерений')


# страница калькулятора с выводом конвертеров
@app.route("/converter/<string:slug>/", methods=['GET', 'POST'])
@app.route("/converter/<string:slug>", methods=['GET', 'POST'])
def category_conv(slug):
    if request.method == 'POST':

        session['value'] = request.form.get('num')
        session['symbol'] = request.form.get('symbol')
        session['type'] = request.form.get('type')

        type = session.get('type', '')
        s = request.form.get('calculator')

        if type == 'hidden':
            flash("-- тип конвертера --")
        elif s != None and s != 'hidden' and type != None and type != 'hidden':
            return redirect(url_for('type_conv', slug=s, type=type))
        elif s != None and s != 'hidden' and s != slug:
            return redirect(url_for('category_conv', slug=s))

    slug_type = Type.query.filter(Type.slug == session.get('type', '')).first()
    slug_categories = Category.query.filter(Category.slug == slug).first()

    return render_template('converter/category_conv.html', value=session.get('value', ''), symbol=session.get('symbol', ''),
                           type=session.get('type', ''), slug_type=slug_type, slug=slug, categories=Category.query.all(),
                           breadcrumbs=BreadCrumb(url=url_for('category_conv', slug=slug), obj=[Category]).breadcrumb(),
                           slug_category=slug_categories, page_name='Конвертеры калькулятора')


# страница ковертера с выводом конвертируемых единиц
@app.route("/converter/<string:slug>/<string:type>/", methods=['GET', 'POST'])
@app.route("/converter/<string:slug>/<string:type>", methods=['GET', 'POST'])
def type_conv(slug, type):
    if request.method == 'POST':

        session['value'] = request.form.get('num')
        session['symbol'] = request.form.get('symbol')

        s = request.form.get('calculator')
        t = request.form.get('type')
        sym = session.get('symbol', '')

        if s != None and s != 'hidden' and t != 'hidden' and t != None and t != type:
            return redirect(url_for('type_conv',  slug=s, type=t))
        elif s != None and s != 'hidden' and t == 'hidden':
            return redirect(url_for('category_conv', slug=s))
        elif s != None and s != 'hidden' and t != None and t != 'hidden' and sym != 'hidden':
            return redirect(url_for('type_conv', slug=s, type=t))
        elif sym == 'hidden':
            flash("-- един. измерения --")
        elif t == 'hidden':
            flash("-- тип конвертера --")

    slug_categories = Category.query.filter(Category.slug == slug).first()
    slug_type = Type.query.filter(Type.slug == type).first()

    return render_template('converter/type_conv.html', slug=slug, slug_category=slug_categories, slug_type=slug_type,
                           categories=Category.query.all(), value=session.get('value', ''), symbol=session.get('symbol', ''),
                           breadcrumbs=BreadCrumb(url=url_for('type_conv', slug=slug, type=type), obj=[Type, Category]).breadcrumb(),
                           type=type, get_result_calc=Unit.get_result_calc, page_name='Единицы измерения')


# страница единицы измерения с выводом конвертируемых единиц
@app.route("/converter/<string:slug>/<string:type>/<string:unit>/", methods=['GET', 'POST'])
@app.route("/converter/<string:slug>/<string:type>/<string:unit>", methods=['GET', 'POST'])
def unit_conv(slug, type, unit):
    if request.method == 'POST':

        session['value'] = request.form.get('num')
        symbol = request.form.get('symbol')

        return redirect(url_for('unit_conv', slug=slug, type=type, unit=symbol))

    slug_categories = Category.query.filter(Category.slug == slug).first()
    slug_type = Type.query.filter(Type.slug == type).first()
    slug_unit = Unit.query.filter(Unit.slug == unit).first()

    return render_template('converter/unit_conv.html', slug=slug, slug_category=slug_categories, slug_type=slug_type, u=unit,
                           categories=Category.query.all(), value=session.get('value', ''), slug_unit=slug_unit,
                           breadcrumbs=BreadCrumb(url=url_for('unit_conv', slug=slug, type=type, unit=unit), obj=[Unit, Type, Category]).breadcrumb(),
                           type=type, get_result_calc=Unit.get_result_calc, page_name='Единица измерения')



"""===================================================== поиск по базе =============================================="""
from flask_breadcrumbs import register_breadcrumb
from models import Type_device, Data
from forms import SearchForm
from app import db
import requests
import yadisk

DATA = Data()
TYPE_DEVICE = Type_device()
PACH = '/sate-pdf-files-3-2020/'

YANDEX = yadisk.YaDisk(token="token_key") # ключ подтверждения токен

@app.route("/search/")
@app.route("/search")
@register_breadcrumb(app, '.search', 'Поиск по базе')
def search():
    q = request.args.get('query')
    page = request.args.get('page', 1, type=int)
    if q:
        datas = Data.query.msearch(q.strip(), fields=['NumberSI', 'NameSI', 'DesignationSI', 'ManufacturerSI'])
        pages = datas.paginate(page=page, per_page=20)

        if pages.total:
            flash("Результат поиска по запросу")
        else:
            flash("По вашему запросу ни чего не найденно!")
    else:
        pages = Data.query.paginate(page=page, per_page=20)
    return render_template('/search/search.html', pages=pages, rex_select_row=DATA.rex_select_row, page_name='Справочник типов средств измерений')



def rout_content_sear():
    query = Data.query.filter(Data.ids == DATA.get_id_from_link(request.view_args['link'])).first()
    return [{'text': query.NumberSI, 'BASE_URL': query.create_link()}]

@app.route("/search/<string:link>/")
@app.route("/search/<string:link>")
@register_breadcrumb(app, '.search.content', '', dynamic_list_constructor=rout_content_sear)
def content(link):
    data = Data.query.filter(Data.ids == DATA.get_id_from_link(link)).first_or_404()
    return render_template('search/search_content.html', content=data)
    
    
# скачать pdf файл
@app.route("/search/download/<string:file>")
def download_file(file):
    if YANDEX.check_token():
        url = YANDEX.get_download_link(f'{PACH}{file}')
        return redirect(url, code=302)


# открыть pdf файл
@app.route("/search/open/<string:file>")
def open_file(file):
    if YANDEX.check_token():
        meta = YANDEX.get_meta(path=f'{PACH}{file}')
        if meta.public_key:
            return redirect(meta.public_url, code=302)
        YANDEX.publish(path=f'{PACH}{file}')
        return redirect(url_for('open_file', file=file), code=302)


@app.route("/search/maker/", methods=['GET', 'POST'])
@app.route("/search/maker", methods=['GET', 'POST'])
@register_breadcrumb(app, '.search.maker', 'Компании')
def maker():
    pages = db.session.query(Data.ManufacturerSI, Data.Maker).distinct()
    form = SearchForm()
    if form.validate_on_submit():
        query = form.query.data.strip()
        list = [(DATA.rex_select_row(i[0], query), i[1], DATA.get_count(i[1])) for i in pages if query in i[0] or query.title() in i[0]]
        if list:
            flash("Результат поиска по запросу")
        else:
            flash("По вашему запросу ни чего не найденно!")
        return render_template('search/maker.html', form=form, list=list, pages=None, page_name='Фирмы изготовители СИ', query=form.query.data)
    else:
        page = request.args.get('page', 1, type=int)
        list_pages = pages.paginate(page=page, per_page=30)
        list = [(i[0], i[1], DATA.get_count(i[1])) for i in list_pages.items]
        return render_template('search/maker.html', form=form, list=list, pages=list_pages, page_name='Фирмы изготовители СИ')



def rout_maker_content_sear():
    query = Data.query.filter(Data.Maker == request.view_args['maker']).first()
    return [{'text': query.ManufacturerSI, 'BASE_URL': query.Maker}]

@app.route("/search/maker/<string:maker>/")
@app.route("/search/maker/<string:maker>")
@register_breadcrumb(app, '.search.maker.maker_content', '', dynamic_list_constructor=rout_maker_content_sear)
def maker_content(maker):
    data = Data.query.filter(Data.Maker == maker).all()
    return render_template('search/search_maker.html', page_name='Все СИ :', count=len(data), content=data)



"""=================================================== новости ======================================================="""
from models import News

@app.route("/news/")
@app.route("/news")
def news():
    page = request.args.get('page', 1, type=int)
    pages = News.query.order_by(News.date_sort.desc()).paginate(page=page, per_page=10)
    return render_template('news/news.html', pages=pages, page_name='Все самые последнии новости')


@app.route("/news/<string:category>/")
@app.route("/news/<string:category>")
def news_category(category):
    page = request.args.get('page', 1, type=int)
    pages = News.query.order_by(News.date_sort.desc()).filter(News.category==category).paginate(page=page, per_page=10)
    return render_template('news/news_category.html', active_page_2=category, pages=pages, page_name=f'{News.convert_category_news(category)}')


@app.route("/news/<string:category>/<string:slug>/")
@app.route("/news/<string:category>/<string:slug>")
def news_content(category, slug):
    new = News.query.filter(News.slug == slug).first_or_404()
    return render_template('news/news_content.html', active_page_2=category, new=new, page_name=new.title)
    
    
