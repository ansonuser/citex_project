
function create_vue(define_fileds, main_key, custom_method){
  return new Vue({
    delimiters:['[[',']]'],
    el:'#app',
    data() {
        return {
        items: [],
        fields: define_fileds,
    timenow:30,
    totalRows: 1,
    currentPage: 1,
    perPage: 10,
    pageOptions: [10, 20, 30],
    timeOptions:[30, 60, 90, 'All'],
    sortDesc: false,
    filter: null,
    }
  },
    mounted() {
    // Set the initial number of items
        this.totalRows = this.items.length;
    },
    methods:{
        onFiltered(filteredItems){
        this.totalRows = filteredItems.length;
        this.currentPage = 1;
        },
        showform(item){
            custom_method(item[main_key]);
        }
    },
  })

}

function modified_table_abc(int, url_link){
  var a = $('[name="modified-body"]').find('input[name], select[name]');
  var post_data = {};
  for (var i in a){         
      if((a[i].name in post_data)& (typeof(post_data[a[i].name]) != 'object')){
          var prev = post_data[a[i].name];
          post_data[a[i].name] =  [prev, a[i].value];
      }else if(a[i].name in post_data){
          post_data[a[i].name].push(a[i].value)
      }else{
          post_data[a[i].name] = a[i].value
      }
  }
  post_data['mode'] = int;
  $.ajax({
      url: url_link,
      type:"POST",
      data: post_data,
      success: function(x){
          $('.show').find('.modal-header').find('.close').click();
          $('select[name="select_time_limit"]').trigger("change");
          var message = warning_info_function('Success', '更新成功', '"badge badge-success"');
          $("#warning-info").append(message);
          $("[data-target='#warning_id']").click();
      }    
  })
}    


function renewtable(kwd, bind_keys, url_link){
  var time_input = $('select[name="select_time_limit"]').val();
  if(time_input =='All'){
      time_input = 3000;
  }
  $.ajax({
      url:url_link,
      data:{'data':kwd,
            'limit': time_input},
      type:'POST',
      success:function(x){
          var new_data = [];
          var keys = bind_keys
          for(var i in x['form']){
              var each = {}
              for(var k in keys){
                  each[keys[k]] = x['form'][i][k]
              }
              new_data[i] = each
          }
          table_vue.items = new_data;
          table_vue.totalRows = new_data.length;
      }
  })
}

function check_abc(message, kwd, url_link){
  var result = true;
  var order_stock_po = $(message);
  $.ajax({
      url:url_link,
      data:{'data':kwd},
      type:"POST",
      success:function(x){
          for(var k in x){
              if(k == order_stock_po){
                  result = false;
                  break
              }
          }
      }
  })
  return result;
}


function update_abc(all_condition, form_id, ms1, ms2, ms3, url_link, other_info){  
  if(all_condition){
      var form = $(form_id);
      $.ajax({
          url:url_link,
          type:"POST",
          data:other_info === null?form.serialize():form.serialize() + other_info,
          dataType:"json",
          success: function(result){
            if(result['result'] == "success"){
                $("#fade_message").show(0).delay(1000).queue(function(){$("#fade_message").hide()});
                    setTimeout(function(){
                    location.reload();
                }, 1000);
            }
          }
      })
      return true;
  }else{
      var message = warning_info_function(ms1, ms2, ms3);
      $("#warning-info").append(message);
      $("[data-target='#warning_id']").click();
      return false;
  }      
}



function feedinput_abc(obj, kwd, form_name, customer_trigger, url_link, val){
  var ask_no = val==null?obj.parentNode.parentNode.parentNode.children[0].innerText:val;
  var result = $("[name='modified-body']");
  result.empty();
  $.ajax({
      url:url_link,
      data: { 'data':kwd,'val':ask_no},
      type:'POST',
      success: function(data){
          var keys = Object.keys(data);
          var count = 0;
          function recursive(current_row){
              if (current_row.getAttribute('name') === 'product_form' ){
                  return result
              }else{
                  result.append(current_row.outerHTML);
                  do{
                      var b = $(result).find('input[name="'+ keys[count]+ '"]').val(data[keys[count]]);
                      if(b.length != 0){
                          if(keys[count] == 'company_number_id'){
                              var c = $(result).find('[name="'+ keys[count]+ '"]');
                              c[0].nextElementSibling.remove();
                              c.val(data[keys[count]]).on("input", customer_trigger).trigger("input");           
                          }
                          count += 1;
                      }else{
                          break;
                      }
                  }while(1)
                  return recursive(current_row.nextElementSibling)
              }
          }
          var a = $(form_name)[0].children[0].nextElementSibling
          recursive(a);
          $(result).append($('<div name="product_form"></div>'));
          product = data['product'];
          n = product.length;
          count = 0
          var k2 = Object.keys(product[0])
          while(count != n){
            addcolumn_product(1);
            var a = $(result).find("input[list='product_number_id']")[count];
            $(a).val(product[count]['product_number_id']).on("input", product_tree).trigger("input");
            var b = $(a.parentNode.nextElementSibling.children[0]);
            for(var k in k2){
              if(k != 0){
                b = $(b[0].parentNode.nextElementSibling);
                b = b.find('input').attr({'value':product[count][k2[k]]});
              }
            }
            count += 1;
          }
          addcolumn_product(1);
      },
  }).done(function(){
    $("[name='modified-body']").find(":hidden").removeAttr('hidden');
  })
  return ask_no;
}



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
            $("#ask_no").append($("<option></option>").attr({"value":key}));  
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