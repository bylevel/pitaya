jQuery.cookie=function(name,value,options){if(void 0===value){var cookieValue=null;if(document.cookie&&""!=document.cookie)for(var cookies=document.cookie.split(";"),i=0;cookies.length>i;i++){var cookie=jQuery.trim(cookies[i]);if(cookie.substring(0,name.length+1)==name+"="){cookieValue=decodeURIComponent(cookie.substring(name.length+1));break}}return cookieValue}options=options||{},null===value&&(value="",options.expires=-1);var expires="";if(options.expires&&("number"==typeof options.expires||options.expires.toUTCString)){var date;"number"==typeof options.expires?(date=new Date,date.setTime(date.getTime()+1e3*60*60*24*options.expires)):date=options.expires,expires="; expires="+date.toUTCString()}var path=options.path?"; path="+options.path:"",domain=options.domain?"; domain="+options.domain:"",secure=options.secure?"; secure":"";document.cookie=[name,"=",encodeURIComponent(value),expires,path,domain,secure].join("")};var close_reply,del_confirm,reply,toggleNav,_bdhmProtocol;toggleNav=function(name){var callback,curname,height,i,names,_i,_ref;for(names=["tags","months","links"],$("."+name+":eq(0)").stop(),i=_i=0,_ref=names.length-1;_ref>=0?_ref>=_i:_i>=_ref;i=_ref>=0?++_i:--_i)"-3000px"!==$("."+names[i]+":eq(0)").css("top")&&(height=$("."+names[i]+":eq(0)").height(),curname=names[i],$("."+names[i]+":eq(0)").animate({top:"-"+(height-40)+"px"},callback=function(curname){return function(){return $("."+curname+":eq(0)").css({top:"-3000px"})}}(curname)));return"-3000px"===$("."+name+":eq(0)").css("top")?(height=$("."+name+":eq(0)").height(),$("."+name+":eq(0)").css({top:"-"+(height-40)+"px"}),$("."+name+":eq(0)").animate({top:"40px"})):void 0},del_confirm=function(id){return confirm("是否删除id为"+id+"的文章")?void 0:!1},reply=function(index,id){var comment_form;return comment_form=$("#comment_form").clone(),$("#comment_form").detach(),$("#comment-"+id).after(comment_form),$("#comment_form input[name=index]").eq(0).val(index),$("#comment_form").append('<a href="javascript:close_reply()">关闭</a>')},close_reply=function(){var comment_form;return $("#comment_form a").eq(0).detach(),comment_form=$("#comment_form").clone(),$("#comment_form").detach(),$("div.article").append(comment_form),$("#comment_form input[name=index]").eq(0).val(-1)},_bdhmProtocol="https:"===document.location.protocol?" https://":" http://",document.write(unescape("%3Cscript src='"+_bdhmProtocol+"hm.baidu.com/h.js%3F35e3e826c18b903de353ce54647c8ba4' type='text/javascript'%3E%3C/script%3E"));