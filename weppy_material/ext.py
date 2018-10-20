# -*- coding: utf-8 -*-
"""
    weppy_md1.ext
    -------------

    Provides the materializecss extension for weppy

    :copyright: (c) 2018 by Yevhenii Dehtiar
    :license: BSD, see LICENSE for more details.
"""

import os
import shutil
from weppy.extensions import Extension, TemplateExtension, TemplateLexer
from weppy.forms import FormStyle
from weppy.html import tag, asis


class MD1(Extension):
    default_static_folder = 'md1'
    default_config = dict(
        set_as_default_style=True,
        static_folder='md1',
        date_format="dd mmm, yyyy",
        datetime_format="dd mmm, yyyy",
        time_pickseconds=True,
    )
    assets = [
        'materialize.min.css',
        'materialize.min.js',
    ]

    def on_load(self):
        # init and create required folder
        self.env.folder = os.path.join(
            self.app.static_path, self.config.static_folder)
        if not os.path.exists(self.env.folder):
            os.mkdir(self.env.folder)
        # load assets and copy to app
        for asset in self.assets:
            static_file = os.path.join(self.env.folder, asset)
            if not os.path.exists(static_file):
                source_file = os.path.join(
                    os.path.dirname(__file__), 'assets', asset)
                shutil.copy2(source_file, static_file)
        # set formstyle if needed
        if self.config.set_as_default_style:
            self.app.config.ui.forms_style = MD1FormStyle
        # init template extension
        self.env.assets = self.assets
        self.app.add_template_extension(MD1Template)

    @property
    def FormStyle(self):
        return MD1FormStyle


class MD1Lexer(TemplateLexer):
    evaluate_value = False

    def process(self, ctx, value):
        for asset in self.ext.env.assets:
            file_ext = asset.rsplit(".", 1)[-1]
            url = '/static/' + self.ext.config.static_folder + '/' + asset
            if file_ext == 'js':
                static = (
                    '<script type="text/javascript" src="' + url +
                    '"></script>')
            elif file_ext == 'css':
                static = (
                    '<link rel="stylesheet" href="' + url +
                    '" type="text/css">')
            else:
                continue
            ctx.html(static)
        # add material icons from external cdn
        url = (
            '//fonts.googleapis.com/icon?family=Material+Icons'
        )
        static = '<link href="' + url + '" rel="stylesheet">'
        ctx.html(static)


class MD1Template(TemplateExtension):
    namespace = 'MD1'
    lexers = {'include_md1': MD1Lexer}


_datepicker_xml = """
<script type="text/javascript">
     document.addEventListener('DOMContentLoaded', function() {
        var options = {
            autoClose: true,
            firstDay: 1,
            format: '%(format)s',
        }
        var elems = document.querySelectorAll('.datepicker');
        var instances = M.Datepicker.init(elems, options);
      });
</script>"""

_timepicker_xml = """
<script type="text/javascript">
    document.addEventListener('DOMContentLoaded', function() {
        var options = {
            showClearBtn: true,
            useSeconds: %(use_seconds)s,
            autoClose: true,
            twelveHour: false
        }
        var elems = document.querySelectorAll('#%(divid)s');
        var instances = M.Timepicker.init(elems, options);
      });
</script>"""

_select_xml = """
<script type="text/javascript">
    document.addEventListener('DOMContentLoaded', function() {
        var elems = document.querySelectorAll('#%(divid)s');
        var instances = M.FormSelect.init(elems, {});
      });
</script>"""


_select_multi_xml = """
<script type="text/javascript">
    document.addEventListener('DOMContentLoaded', function() {
        var elems = document.querySelectorAll('#%(divid)s');
        var instances = M.FormSelect.init(elems, {});
      });
</script>"""

main_widgets = ['select', 'input']
js_widgets = ['script']
css_widgets = ['css']


class MD1FormStyle(FormStyle):
    @staticmethod
    def widget_bool(attr, field, value, _id=None):
        fid = _id or field.name
        res = []
        res.append(tag.input(
            _name=field.name, _type='checkbox', _id=fid,
            _value=str(value) if value is not None else '0'))
        res.append(tag.span(field.name))
        return tag.p(tag.label(*res), _id=fid,)

    @staticmethod
    def widget_date(attr, field, value, _class='date', _id=None):
        def load_js():
            dformat = attr.get('date_format', attr['env'].date_format)
            s = asis(_datepicker_xml % dict(
                     divid=fid + "_cat",
                     format=dformat
                     ))
            return s

        fid = _id or field.name

        return tag.div(
            tag.input(
                _name=field.name, _type='text', _id=fid + "_cat", _class="datepicker",
                _value=str(value) if value is not None else ''),
            load_js(),
        )

    @staticmethod
    def widget_time(attr, field, value, _class='time', _id=None):
        def load_js():
            pick_seconds = "true" if use_seconds else "false"
            s = asis(
                _timepicker_xml % dict(
                    divid=fid + "_cat",
                    use_seconds=pick_seconds
                ))
            return s

        use_seconds = attr.get('time_pickseconds',
                               attr['env'].time_pickseconds)
        fid = _id or field.name
        _value = str(value) if value is not None else ''
        if not use_seconds:
            _value = _value[:-2]

        return tag.div(
            tag.input(
                _name=field.name, _type='text', _id=fid + "_cat", _class="timepicker",
                _value=str(value) if value is not None else ''),
            load_js(),
        )

    @staticmethod
    def widget_datetime(attr, field, value, _class='datetimepicker', _id=None):
        return MD1FormStyle.widget_date(attr, field, value, _class="datepicker", _id=None)

    @staticmethod
    def _default_select_option():
        return tag.option('Choose your option', _value="")

    @staticmethod
    def widget_select(attr, field, value, _class='', _id=None):
        def selected(k):
            return 'selected' if str(value) == str(k) else None

        def load_js():
            s = asis(
                _select_xml % dict(
                    divid=fid
                ))
            return s

        fid = _id or field.name
        options, multiple = FormStyle._field_options(field)

        if multiple:
            return MD1FormStyle.widget_multiple(
                attr, field, value, options, _class=_class, _id=_id)

        option_items = [MD1FormStyle._default_select_option(), ]
        option_items += [
            tag.option(n, _value=k, _selected=selected(k)) for k, n in options]

        return tag.div(
            tag.select(*option_items, _name=field.name, _class=_class, id=_id or field.name),
            load_js(),
        )

    @staticmethod
    def widget_multi(attr, field, value, _class='', _id=None):
        def selected(k):
            return 'selected' if str(value) == str(k) else None

        def load_js():
            s = asis(
                _select_multi_xml % dict(
                    divid=fid
                ))
            return s
        fid = _id or field.name

        options, multiple = FormStyle._field_options(field)
        option_items = [MD1FormStyle._default_select_option(), ]
        option_items += [tag.option(n, _value=k, _selected=selected(k)) for k, n in options]

        return tag.div(
            tag.select(*option_items, _multiple=True, _name=field.name, _class=_class, _id=_id or field.name),
            load_js(),
        )

    def on_start(self):
        from weppy.expose import Expose
        self.attr['env'] = Expose.application.ext.MD1.config
        self.parent = tag.div(_class="card-panel")

    @staticmethod
    def unpack_widget(widget):
        from weppy.html import HtmlTag
        js = ()

        if len(list(widget)) > 1:
            w = widget[0]
            for component in widget.components:
                if isinstance(component, asis):
                    js += (component, )
                elif isinstance(component, HtmlTag) and any(w_type in str(component) for w_type in main_widgets):
                    w = component
        else:
            w = widget
        return w, js

    @staticmethod
    def perform_widget(widget, label=None, error=None, comment=None):

        def _helper():
            helper = dict(_class='helper-text')
            if error:
                helper['data'] = {
                    'error': str(error),
                    'success': ""
                }
                main_widget.add_class('invalid')
                main_widget.add_class('validate')
            return tag.span(comment or '', **helper)

        main_widget, js_init = MD1FormStyle.unpack_widget(widget)
        elems = (main_widget, label, )

        if error or comment:
            elems += (_helper(), )

        return elems, js_init

    def create_label(self, label):
        widget, js = self.unpack_widget(self.element.widget)
        wid = widget['_id']
        attr = dict(_for=wid)
        # M needs a handy activating labels
        if widget['_class']:
            if 'switch' in str(widget['_class']):  # to all switches
                attr['_class'] = 'active'
        if widget['_value'] or 'select' in str(widget):  # if input has value
            attr['_class'] = 'active'
        return tag.label(label, **attr)

    def create_comment(self, comment):
        return comment

    def create_error(self, error):
        return error

    def add_widget(self, widget):
        _class = 'input-field col s12'
        label = self.element.label
        error = self.element.error
        comment = self.element.comment
        elems, js_init = MD1FormStyle.perform_widget(widget, label, error, comment)
        self.parent.append(
            tag.div(
                tag.div(*elems, _class=_class),
                *js_init,
                _class="row"
            )
        )

    def add_buttons(self):
        submit = tag.button(self.attr['submit'], _type='submit',
                            _class='waves-effect waves-light btn')
        buttons = tag.div(submit, _class="col s12")
        self.parent.append(tag.div(buttons, _class='row'))

    def render(self):
        self.attr['_class'] = self.attr.get('_class', 'col s12')
        return FormStyle.render(self)
