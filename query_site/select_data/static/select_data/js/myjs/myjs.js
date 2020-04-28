function warning_info_function(message1, message2, color){

  return $('<div class="modal fade"  role="dialog" style="padding-top: 30px;"  aria-labelledby="tile" aria-hidden="true" tabindex="-1" id="warning_id">' + 
            '<div class="modal-dialog" role="document" style="border-color: black; border-width: 2px;">'+
              '<div class="modal-content">'+
                '<div class="modal-header" style="background:rgb(203, 203, 236) ; border-color: black;">'+
                  '<h3 class="modal-title">'+' <span class='+ color+'> '+ message1 + '</span></h3>' +
                  '<button type="button" class="close" data-dismiss="modal" aria-label="Close" onclick="close_modal()">'+
                    '<span aria-hidden="true">&times;</span>'+
                  '</button>'+
                '</div>'+
                '<div class="modal-body" style="background-color: #c5dbdf; border-color: #8ba0b6; border-width: 5px;">'+
                  '<p style="font-weight: bolder;font-size: 20px; color:deepskyblue(138, 68, 68);">' + message2 + '</p>'+
                '</div>'+
              '</div>'+
            '</div>'+
          '</div>')
}





var chinese = {
  "emptyTable": "無資料...",
  "processing": "處理中...",
  "loadingRecords": "載入中...",
  "lengthMenu": "顯示 _MENU_ 項結果",
  "zeroRecords": "沒有符合的結果",
  "info": "顯示第 _START_ 至 _END_ 項結果，共 _TOTAL_ 項",
  "infoEmpty": "顯示第 0 至 0 項結果，共 0 項",
  "infoFiltered": "(從 _MAX_ 項結果中過濾)",
  "infoPostFix": "",
  "search": "搜尋:",
  "paginate": {
      "first": "第一頁",
      "previous": "上一頁",
      "next": "下一頁",
      "last": "最後一頁"
  },
  "aria": {
      "sortAscending": ": 升冪排列",
      "sortDescending": ": 降冪排列"
  }
}

$('[placeholder]').focus(function() {
    var input = $(this);
    if (input.val() == input.attr('placeholder')) {
      input.val('');
      input.removeClass('placeholder');
    }
  }).blur(function() {
    var input = $(this);
    if (input.val() == '' || input.val() == input.attr('placeholder')) {
      input.addClass('placeholder');
      input.val(input.attr('placeholder'));
    }
  }).blur();

function close_modal(){
    $(".show").removeClass("show").removeAttr("style").attr("style","display: none;").attr("aria-hidden","true");
}


function check_submit(){
  var product_name = $("[for='product_name']");
  count = 0
  for(var i=0; i<product_name.length; i++){
      if(product_name[i].nextElementSibling.value != ""){
          count += 1;
          if($(product_name[i]).parent()[0].nextElementSibling.lastElementChild.value == ""){
              $($(product_name[i]).parent()[0].nextElementSibling.lastElementChild).attr({"style":"border-color:red;"})
              // alert("請檢查輸入是否有誤!");
              return false;
          }
      }
  }
  if (count == 0){
      // alert("請檢查輸入是否有誤!");
      return false;
  }else{
    return true;
  }
}

function required_all(){
  var count = 0;
  $('[required]').each(function(){
    if(this.value == ''){
      count += 1;
      // alert('Warning!');
      return false;
    }
  })
  return (count==0)?true:false;
}


function ask_noing(url_link){
  $.ajax({
    url : url_link,
    type:"POST",
    data: {'data':"ask_no"},
    success:function(result){
        var i = 0;
        for(var key in result){
            $("#ask_order_no").append($("<option></option>").attr({"value":key}));  
        }
    }
  })

}



function companying(url_link){
  $.ajax({
    url : url_link,
    type:"POST",
    data: {'data':"company"},
    success:function(result){
        var i = 0;
        for(var key in result){
            $("#company_number_id").append($("<option></option>").attr({"value":key}));  
        }
    }
  })

}

function ordernoing(url_link){
  $.ajax({
    url : url_link,
    type:"POST",
    data: {'data':"order_no"},
    success:function(result){
        for(var key in result){
            $("#order_no").append($("<option></option>").attr({"value":key}));
        }                              
    }
  })
}

function producting(url_link){
  $.ajax({
    url : url_link,
    type:"POST",
    data: {'data':"product"},
    success:function(result){
        for(var key in result){
            $("#product_number_id").append($("<option></option>").attr({"value":key}));
        }                     
    }
  })
}


function employeeing(url_link){
    $.ajax({
      url : url_link,
      type:"POST",
      data: {'data':"empolyee"},
      success:function(result){
          for(var key in result){
              $("#employee_id").append($("<option></option>").attr({"value":key}));
          }                              
      }
    })
}





function custom_tree_url(e, url_link){
  var a = e.target.value;
  var b = e.target; 
  var bool = $("#company_number_id").find("option").filter(function(){
                                            if(a==this.value){
                                              return true;
                                            }else{
                                              return false;
                                            }})
  if(bool.length > 0){         
            $.ajax({
            url : url_link,
            type:"POST",
            data:{'data':"company_content",
                    'val': a},
            success: function(result){
                for(var key in result){
                    b = b.parentNode.nextElementSibling;
                    var input_text = result[key];
                    b = b.lastElementChild;
                    $(b).attr({"value":input_text })
                    }
                }
            })
        }
        else{
          var c = e.target.parentNode.parentNode;
          $.each($(c).find("input[disabled='disabled']"), function(){$(this).removeAttr("value")});
        }

}

function product_tree_url(e, url_link){
  var a = e.target.value;
  var b = e.target; 
  var bool = $("#product_number_id").find("option").filter(function(){
                                                if(a==this.value){
                                                  return true;
                                                }else{
                                                  return false;
                                                }})
  if(bool.length > 0){
          $.ajax({
          url:url_link,
          type: "POST",
          data:{
              "data": "product_content", 
              "val":a},
          success: function(result){
                  for(var key in result){
                      b = b.parentNode.nextElementSibling;
                      var input_text = result[key];
                      b = b.lastElementChild;
                      $(b).attr({"value":input_text})
                  }
            }})
        
      }else{
      var c = e.target.parentNode.parentNode;
      $.each($(c).find("input[disabled='disabled']"), function(){$(this).removeAttr("value")});
  }

  if(a !=""){
    $(b.parentElement.nextElementSibling.lastElementChild).attr("required","required");
  }
}

function addcolumn_product(idx){
  var current_id = document.getElementsByName("product_number_id").length;//control datalist use once only
  var new_row = $($('[name="growth_row"]')[0]).clone();
  if($('[name="growth_row"]').length > 1 || idx == 0){
    $($($($('[name="growth_row"]')[idx]).removeAttr("name").children()[0]).children()[1]).removeAttr("onclick");
  }
  if(current_id === 1||idx==1){
      new_row.children()[0].children[2].remove();
  }
  $(new_row).attr("name", "growth_row");
  $($($( new_row.children()[0].children[1]).on("input", product_tree)).removeAttr("onclick")).attr('onclick','addcolumn_product('+idx+')');
  $($('[name="product_form"]')[idx]).append(new_row);
}

// function select_table_time(e, url_link, time){
//   $.ajax()

// }