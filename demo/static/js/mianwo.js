/**
 * Created by Heaton on 2016/12/21.
 */
 function toDecimal2(x) {
        var f = parseFloat(x);
        if (isNaN(f)) {
            return false;
        }
        var f = Math.round(x*100)/100;
     var s = f.toString();
        var rs = s.indexOf('.');
        if (rs < 0) {
            rs = s.length;
            s += '.';
        }
        while (s.length <= rs + 2) {
            s += '0';
        }
        return s;
    }



 function toDecimal(x) {
     var f = parseFloat(x);
        if (isNaN(f)) {
           return;
        }
        f = Math.round(x*100)/100;
        return f;
    }

    nosubmit=0;
      function goprojectview(vv) {

          if(nosubmit==1)
              toastr.warning('保存项目失败，请检测是否填写正确!');
          else
          {

              $('#id_suoZaiDiKuai').attr('disabled',false);
              $('#newform').submit();
          }

    }

    function SetReadOnly(obj){
 if(obj){
     obj.onbeforeactivate = function(){return false;};
     obj.onfocus = function(){obj.blur();};
     obj.onmouseover = function(){obj.setCapture();};
     obj.onmouseout = function(){obj.releaseCapture();};
    }
}


Date.prototype.dateAdd = function(interval,number)
{
    var d = this;
    var k={'y':'FullYear', 'q':'Month', 'm':'Month', 'w':'Date', 'd':'Date', 'h':'Hours', 'n':'Minutes', 's':'Seconds', 'ms':'MilliSeconds'};
    var n={'q':3, 'w':7};
    eval('d.set'+k[interval]+'(d.get'+k[interval]+'()+'+((n[interval]||1)*number)+')');
    return d;
}
Date.prototype.dateDiff = function(interval,objDate2)
{
    var d=this, i={}, t=d.getTime(), t2=objDate2.getTime();
    i['y']=objDate2.getFullYear()-d.getFullYear();
    i['q']=i['y']*4+Math.floor(objDate2.getMonth()/4)-Math.floor(d.getMonth()/4);
    i['m']=i['y']*12+objDate2.getMonth()-d.getMonth();
    i['ms']=objDate2.getTime()-d.getTime();
    i['w']=Math.floor((t2+345600000)/(604800000))-Math.floor((t+345600000)/(604800000));
    i['d']=Math.floor(t2/86400000)-Math.floor(t/86400000);
    i['h']=Math.floor(t2/3600000)-Math.floor(t/3600000);
    i['n']=Math.floor(t2/60000)-Math.floor(t/60000);
    i['s']=Math.floor(t2/1000)-Math.floor(t/1000);
    return i[interval];
}

Date.prototype.Format = function(fmt)
{ //author: meizz
    var o = {
        "M+" : this.getMonth()+1,                 //月份
        "d+" : this.getDate(),                    //日
        "h+" : this.getHours(),                   //小时
        "m+" : this.getMinutes(),                 //分
        "s+" : this.getSeconds(),                 //秒
        "q+" : Math.floor((this.getMonth()+3)/3), //季度
        "S"  : this.getMilliseconds()             //毫秒
    };
    if(/(y+)/.test(fmt))
        fmt=fmt.replace(RegExp.$1, (this.getFullYear()+"").substr(4 - RegExp.$1.length));
    for(var k in o)
        if(new RegExp("("+ k +")").test(fmt))
            fmt = fmt.replace(RegExp.$1, (RegExp.$1.length==1) ? (o[k]) : (("00"+ o[k]).substr((""+ o[k]).length)));
    return fmt;
}



function inittablewidth() {

   totalw = 0;
$('table th').each(function () {

    th = $(this).text();
    thw=th.length*16+10;

    if(th=='月份')
        thw=80;


    totalw+=thw;

    $(this).css('width',thw);

});

$('table.table').css('width',totalw);
    $('table.table').parent().css('overflow','auto');

}

//十六进制颜色值域RGB格式颜色值之间的相互转换

//-------------------------------------
//十六进制颜色值的正则表达式
var reg = /^#([0-9a-fA-f]{3}|[0-9a-fA-f]{6})$/;
/*RGB颜色转换为16进制*/
String.prototype.colorHex = function(){
    var that = this;
    if(/^(rgb|RGB)/.test(that)){
        var aColor = that.replace(/(?:||rgb|RGB)*/g,"").split(",");
        var strHex = "#";
        for(var i=0; i<aColor.length; i++){
            var hex = Number(aColor[i]).toString(16);
            if(hex === "0"){
                hex += hex;
            }
            strHex += hex;
        }
        if(strHex.length !== 7){
            strHex = that;
        }
        return strHex;
    }else if(reg.test(that)){
        var aNum = that.replace(/#/,"").split("");
        if(aNum.length === 6){
            return that;
        }else if(aNum.length === 3){
            var numHex = "#";
            for(var i=0; i<aNum.length; i+=1){
                numHex += (aNum[i]+aNum[i]);
            }
            return numHex;
        }
    }else{
        return that;
    }
};

//-------------------------------------------------

/*16进制颜色转为RGB格式*/
String.prototype.colorRgb = function(){
    var sColor = this.toLowerCase();
    if(sColor && reg.test(sColor)){
        if(sColor.length === 4){
            var sColorNew = "#";
            for(var i=1; i<4; i+=1){
                sColorNew += sColor.slice(i,i+1).concat(sColor.slice(i,i+1));
            }
            sColor = sColorNew;
        }
        //处理六位的颜色值
        var sColorChange = [];
        for(var i=1; i<7; i+=2){
            sColorChange.push(parseInt("0x"+sColor.slice(i,i+2)));
        }
        return "RGB(" + sColorChange.join(",") + ")";
    }else{
        return sColor;
    }
};

function addoplity(rgb,op) {
rgba =  rgb.colorRgb().substring(0,rgb.colorRgb().length-1)+','+op+')';
 return rgba.replace(/RGB/,'rgba');


}
function qianfenformat (num) {
    return (num.toFixed(2) + '').replace(/\d{1,3}(?=(\d{3})+(\.\d*)?$)/g, '$&,');
}


String.format = function() {
    if( arguments.length == 0 )
        return null;

    var str = arguments[0];
    for(var i=1;i<arguments.length;i++) {
        var re = new RegExp('\\{' + (i-1) + '\\}','gm');
        str = str.replace(re, arguments[i]);
    }
    return str;
}


// Array.prototype.removeByValue = function(val) {
//   for(var i=0; i<this.length; i++) {
//     if(this[i] == val) {
//       this.splice(i, 1);
//       break;
//     }
//   }
// }
 function cainian_save() {
       $.post('/invest/cainian/save/'+cid+'/',{data:JSON.stringify(mydata)},function (data) {
         if(data=='ok')
         {

             toastr.info('保存成功!')
             window.location= window.location.href;
         }
           else
             toastr.info('保存失败，检查信息!')
       }) ;
    }



     function calctotal() {

     cols.forEach(function (e) {
         totalcol=0


         mydata.forEach(function (ee) {

             tdv= ee[e];
                 totalcol+=Number(tdv);


         });


         $('#mytable tr:eq(2)').find('td:eq('+keys.indexOf(e)+')').text(toDecimal2(totalcol));


     });

 }

function calcrow(event) {
    tdv =  $(this).val();
    tdk=$(this).data('name');
    tdpro=$(this).data('proid');

    pro = mydata.find(function (e) {

        return e.proid==tdpro;
    });

    pro[tdk]=tdv;

    console.log(pro[tdk]);



    totalrow=0;
    for(i=0;i<6;i++)
    {

        tdv= pro['m'+i];

       if(!isNaN(tdv))
       {

           totalrow+=Number(tdv);
           pro['totalhalf']=totalrow;
       }

    }
    $(this).parent().parent().find('td:eq('+keys.indexOf('totalhalf')+')').text(toDecimal2(totalrow));
    for(i=6;i<12;i++)
    {
        tdv= pro['m'+i];

        if(!isNaN(tdv))
        {

            totalrow+=Number(tdv);
            pro['totalyear']=totalrow;
        }


    }
    $(this).parent().parent().find('td:eq('+keys.indexOf('totalyear')+')').text(toDecimal2(totalrow));


    if(event.data.yearcol>0)
    cainian_checkrow(event.data.yearcol,event.data.totalcol,this,event.data.limit);




    calctotal();
}


function initcainiandata() {
         mydata.forEach(function (e) {
           trr = document.createElement('tr');
           trr.className='myrow';

           for(i=0;i<keys.length;i++)
           {
               td=document.createElement('td');
               vv=0;
               if(!isNaN(Number(e[keys[i]])))
                   vv=toDecimal2(  e[keys[i]]);
               else
                   vv=  e[keys[i]];

               box = document.createElement('input');
               box.value = vv;
               box.className='kbj';
               // box.style.width='80px';
               $(box).attr('data-name',keys[i]);
               $(box).attr('data-proid',e['proid']);
               // $(box).change(calcrow);

               if(keys_edit.indexOf(keys[i])>-1)
               td.appendChild(box);
               else
                   td.textContent =vv;

               trr.appendChild(td);

           }



           $('#mytable tbody').append(trr);
        });

}



function cainian_checkrow(yearcol,totalcol,box,limit) {

    yeardata =Number( $(box).parent().parent().find('td:eq('+yearcol+')').text());
    totalrow =Number( $(box).parent().parent().find('td:eq('+totalcol+')').text());

    console.log('check:',yeardata,totalrow,limit);
   lmm=0-limit;
    if((totalrow-yeardata)>limit || (totalrow-yeardata)<lmm)
    {

        toastr.info('超出本项目年度总金额!请调整!')
        $(box).parent().parent().find('td:eq('+yearcol+')').css('background-color','#f5b7c2');
    }else
    {

        $(box).parent().parent().find('td:eq('+yearcol+')').css('background-color','#fff');
    }
}


function cainian_setrowcheck(yearcol,totalcol) {

    $('#mytable tr:gt(2)').each(function () {
        yeardata = Math.abs(Number(  $(this).find('td:eq('+yearcol+')').text()));
        totalrow = Math.abs(Number(  $(this).find('td:eq('+totalcol+')').text()));
        console.log(yeardata,totalrow);
                if((totalrow-yeardata)>10 || (totalrow-yeardata)<-10)
        {

            $(this).find('td:eq('+yearcol+')').css('background-color','#f5b7c2');
        }


    });
}




function cainian_reset() {

                        toastr.info("确认重置当前页面分解吗?此操作会清空已保存的当前数据<br/><button type='button'  class='btn btn-warning' onclick='getcainianreset()'>确认!</button>" +
                            "&nbsp;&nbsp;&nbsp;&nbsp;<button type='button'  class='btn btn-warning'>取消</button>" +
                            "");


    }

    function getcainianreset() {

        $.get('/invest/cainian/reset/'+tabname,function(data){

           if(data=='ok')
           {

               toastr.info('财年分解重置成功!');
            window.location = window.location.href;
           }
        });
    }













//
// $(document).ready(function () {
//   hh=  $('div.layout-sidebar-backdrop').height();
//   panelcontenth=$('div.layout-content-body').height();
//     if(typeof(adjustheight)=='undefined' &&   panelcontenth<hh)
//       $('div.layout-content-body').height(hh-130);
//      // if(panelcontenth>800)
//      //     $('div.layout-content-body').height(hh+50);
//
// });

function adjustfooter() {

    hh=  $('div.layout-sidebar-backdrop').height();
    panelcontenth=$('div.layout-content-body').height();
        $('div.layout-content-body').css('height','xxx');
}
$(function () {

});

function getCookie(name) {
  var cookieValue = null;

  if (document.cookie && document.cookie != '') {
    var cookies = document.cookie.split(';');

    for (var i = 0; i < cookies.length; i++) {
      var cookie = jQuery.trim(cookies[i]);

      // Does this cookie string begin with the name we want?
      if (cookie.substring(0, name.length + 1) == (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }

  return cookieValue;
}