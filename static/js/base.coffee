#网页加载完成时
#$ ->
#  $('input[name=\"keywords\"]').focus ->
#    $("div.headernav span:first").removeClass()
#    $("input[name=\"keywords\"]").removeClass()
#    $("div.headernav span:first").addClass "input"
#    $("input[name=\"keywords\"]").addClass "input"
#
#  $("input[name=\"keywords\"]").blur ->
#    $("div.headernav span:first").removeClass "input"
#    $("input[name=\"keywords\"]").removeClass "input"
#    unless $("input[name=\"keywords\"]").val() is ""
#      $("div.headernav span:first").addClass "exists"
#      $("input[name=\"keywords\"]").addClass "exists"

toggleNav = (name) ->
  names = [ "tags", "months", "links" ]
  #停止效果
  $("." + name + ":eq(0)").stop()

  #收起其它的下拉
  for i in [0..names.length - 1]
    unless $("." + names[i] + ":eq(0)").css("top") is "-3000px"
      height = $("." + names[i] + ":eq(0)").height()
      curname = names[i]
      $("." + names[i] + ":eq(0)").animate({top: "-" + (height - 40) + "px"}, callback = do (curname) -> ->
        $("." + curname + ":eq(0)").css top: "-3000px"
      )

  if $("." + name + ":eq(0)").css("top") is "-3000px"
    height = $("." + name + ":eq(0)").height()
    $("." + name + ":eq(0)").css top: "-" + (height - 40) + "px"
    $("." + name + ":eq(0)").animate top: "40px"

del_confirm = (id) ->
  false  unless confirm("是否删除id为" + id + "的文章")
reply = (index, id) ->
  #显示回复对话框到对应的位置，并设置index值
  comment_form = $("#comment_form").clone()
  $("#comment_form").detach()
  $("#comment-" + id).after comment_form
  $("#comment_form input[name=index]").eq(0).val index
  $("#comment_form").append "<a href=\"javascript:close_reply()\">关闭</a>"
close_reply = ->
  #关闭回复对话框，使之显示到最下方
  $("#comment_form a").eq(0).detach()
  comment_form = $("#comment_form").clone()
  $("#comment_form").detach()
  $("div.article").append comment_form
  $("#comment_form input[name=index]").eq(0).val -1

_bdhmProtocol = (if "https:" is document.location.protocol then " https://" else " http://")
document.write unescape("%3Cscript src='" + _bdhmProtocol + "hm.baidu.com/h.js%3F35e3e826c18b903de353ce54647c8ba4' type='text/javascript'%3E%3C/script%3E")
