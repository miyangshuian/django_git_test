//顶部搜索栏搜索方法
function search_click(){
    var keywords = $('#search_keywords').val(),
        request_url = '';
    if(keywords == ""){
        alert("请输入搜索关键字")
        return
    }

    request_url = "/bk/pro/list/cat/0#?keywords=" + keywords
        // }else if(type == "teacher"){
        //     request_url = "/org/teacher?keywords="+keywords
        // }else if(type == "org"){
        //     request_url = "/org/list?keywords="+keywords
        // }

    window.location.href = request_url
}
$(function() {
    //顶部搜索栏搜索按钮事件
    $('#jsSearchBtn').on('click',function(){
        search_click()
    });
    //搜索表单键盘事件
    $("#search_keywords").keydown(function(event){
        if(event.keyCode == 13){
             $('#jsSearchBtn').trigger('click');
        }
    });
});

