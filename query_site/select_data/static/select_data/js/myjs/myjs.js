// var abc = "This is myjs."

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
              alert("請檢查輸入是否有誤!");
              return false;
          }
      }
  }
  if (count == 0){
      alert("請檢查輸入是否有誤!");
      return false;
  }else{
    return true;
  }
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


function producting(url_link){
  $.ajax({
    url : url_link,
    type:"POST",
    data: {'data':"product"},
    success:function(result){
        for(var key in result){
            $("#product_number_id0").append($("<option></option>").attr({"value":key}));
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
  $("#company_number_id").find("option").filter(function(){
                                                          if(a==this.value){         
                                                          $.ajax({
                                                          url : url_link,
                                                          type:"POST",
                                                          data:{'data':"company_content",
                                                                  'val': a},
                                                          success: function(result){
                                                              var b = document.getElementsByName("company_number_id")[0];
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
                                                          var c = document.getElementById("company_number_id").parentNode.parentNode;
                                                          $.each($(c).find("input[disabled='disabled']"), function(){$(this).removeAttr("value")});
                                                      }
                                                                                          
                                                   })

}

function product_tree_url(e, url_link){
  var a = e.target.value;
  var b = e.target; 
  console.log(b);
  $("#product_number_id0").find("option").filter(function(){
                                                          if(a==this.value){
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

                                                    })
  if(a !=""){
    $(b.parentElement.nextElementSibling.lastElementChild).attr("required","required");
  }
  }
