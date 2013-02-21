#-*- encoding:utf-8 -*-

from os import path

settings = {
"static_path":path.join(path.dirname(__file__),"../static"),
"template_path":path.join(path.dirname(__file__),"../templates"),
"cookie_secret":"a50ea71d-b899-47b7-85d0-aa2b427d2fbd",
}
