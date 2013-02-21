#-*- encoding:utf-8 -*-
# 解析rst格式，并附加pygments代码高亮
from docutils import nodes
from docutils.parsers.rst import directives
from docutils.core import publish_parts
from rst_directive import Pygments
directives.register_directive('code', Pygments)
directives.register_directive('sourcecode', Pygments)

def html_body(source):
    """
    转换rst输出html的body部分

    examples:

        source = u'''
        .. code:: python

          def hello():
              print "hello world"
        '''
        html_body(source)
    """
    try:
        parts = publish_parts(source, writer_name='html', settings_overrides={'input_encoding':'unicode'})
    except:
        return ""
    return parts['html_body']
