$ ->
  uploader = new qq.FileUploader
    element: $("#file-uploader")[0]
    action: "/godupload"
    allowedExtensions: [ "jpg", "gif", "png", "gz", "bz2", "zip", "7z" ]
    sizeLimit: 10485760
    minSizeLimit: 0
    debug: false
    onSubmit: (id, fileName) ->

    onComplete: (id, fileName, responseJSON) ->
      prefix = responseJSON["prefix"]
      filename = responseJSON["filename"]
      url = prefix + "-" + filename
      #执行添加到文章附件
      add_to_article prefix, filename

  editor = CodeMirror.fromTextArea $('textarea[name=content]').eq(0)[0], {lineNumbers: true, lineWrapping: true}
  editor.setOption "theme", "monokai"

addTag = (tag) ->
  #去除空格，并以英文半角逗号分隔
  s = $("input[name=\"tags\"]").val().replace(RegExp(" ", "g"), "").split(",")
  for i in [s.length..0]
    #去除空元素
    s.splice i, 1  if s[i] is ""
  #添加新元素到结尾
  s.splice s.length, 0, tag  if s.indexOf(tag) is -1
  $("input[name=\"tags\"]").val s.join(",")
  undefined

#添加到文章附件
add_to_article = (prefix, filename) ->
  #组合成url
  url = prefix + "/" + filename
  files = $("input[name=\"files\"]").val().split ","
  #如果只有一个''，那就使它变成空数组
  files = []  if files[0] is ""
  if files.indexOf(url) is -1
    #将url添加到files当中去
    files.push url
    #写入到input中
    $("input[name=\"files\"]").val files.join(",")
    #从tempfile中移除
    $("a[name=\"" + url + "\"]").remove()
    $("div#articlefile").append "<a name=\"" + url + "\" href=\"/upload/" + url + "\" target=\"_blank\">" + filename + "</a> <a name=\"" + url + "\" href=\"javascript:remove_from_article('" + prefix + "','" + filename + "')\">移除</a> "
  undefined

#移除
remove_from_article = (prefix, filename) ->
  url = prefix + "/" + filename
  files = $("input[name=\"files\"]").val().split ","
  #删除元素
  files.splice files.indexOf(url), 1
  #写入到input中
  $("input[name=\"files\"]").val files.join(",")
  #从articlefile删除
  $("a[name=\"" + url + "\"]").remove()
  $("div#tempfile").append "<a name=\"" + url + "\" href=\"javascript:add_to_article('" + prefix + "','" + filename + "')\">" + filename + "</a> <a name=\"" + url + "\" href=\"javascript:del_file('" + prefix + "','" + filename + "')\">删除</a> "
  undefined

del_file = (prefix, filename) ->
  url = prefix + "/" + filename
  $.ajax
    url: "/delfile/" + url
    type: "GET"
    timeout: 30000
    cache: false
    error: ->

    success: (html) ->
      #从tempfile中删除
      $("a[name=\"" + url + "\"]").remove()  if html is "OK"
  undefined
