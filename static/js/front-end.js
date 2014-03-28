$(document).ready(function(){

	  $("#id_topGroup").append("<option value='-1'>请选择分组</option>");
  	$("#id_bizGroup").append("<option value='-1'>请选择分组</option>");
    $("#id_uName").addClass("uneditable-input");

    //$("#id_machineGroup").selectpicker();

  	$.get("/ldap/ajax/topgroup/",function(data,status){
    	var tg = eval(data);
		$("#id_topGroup").append(tg);
  	});

  	$("#id_topGroup").change(function(){
  		var top_id = $("#id_topGroup").val();
  		$("#id_bizGroup").empty().append("<option value='-1'>请选择分组</option>");
  		$("#id_machineGroup").empty();
  		if (top_id != -1) {
	  		$.get("/ldap/ajax/bizgroup/"+top_id ,function(data,status){
	      		var bg = eval(data);
		  		$("#id_bizGroup").append(bg);
	    	});
		};
  	});

  	$("#id_bizGroup").change(function(){
  		var biz_id = $("#id_bizGroup").val();
  		$("#id_machineGroup").empty();
  		if (biz_id != -1) {
	  		$.get("/ldap/ajax/machinegroup/"+biz_id ,function(data,status){
	      		var mg = eval(data);
		  		$("#id_machineGroup").append(mg);
          //$("#id_machineGroup").selectpicker('refresh');
	    	});
		};
  	});

  	$("#id_machineGroup").dblclick(function(){
  		var mg_id = $("#id_machineGroup").val();
  		var mg_name = $("#id_machineGroup option[value='"+ mg_id +"']").text();
  		var mg_option = "<option value='"+ mg_id +"'>"+ mg_name +"</option>";
  		$("#id_selectedMachines").append(mg_option);
  		$("#id_machineGroup option[value='"+ mg_id +"']").remove();
  		refresh_selected();
  	});

  	$("#id_selectedMachines").dblclick(function(){
  		var mg_id = $("#id_selectedMachines").val();
  		var mg_name = $("#id_selectedMachines option[value='"+ mg_id +"']").text();
  		var mg_option = "<option value='"+ mg_id +"'>"+ mg_name +"</option>";
  		$("#id_machineGroup").append(mg_option);
  		$("#id_selectedMachines option[value='"+ mg_id +"']").remove();
  		refresh_selected();
  	});

  	function refresh_selected(){
  		$("#id_chosenIP").empty();
      $("#id_selectedMachines option").each(function() {
          if($(this).val()>0){
          	$.get("/ldap/ajax/machine/"+$(this).val(), function(data,status){
          		var ip = eval(data);
  		  		$("#id_chosenIP").append(ip);
          	})
          }
      });
  	};
});