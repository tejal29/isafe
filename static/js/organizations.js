$( document ).ready(function(){

  $("#organization_button").on("click", function(e){
    NProgress.start();
    $("#error").removeClass("alert alert-danger"); 
    $("#error").removeClass("alert alert-info"); 
    $("#error").empty();
  	var name = $("input[name='name']").val();  //get the form values
  	var email = $("input[name='email']").val();
  	var phone = $("input[name='phone']").val();
    var twitter = $("input[name='twitter']").val();
    var address = $("input[name='address']").val();
  	var description = $("textarea[name='description']").val();
  	var categories = $('input:checkbox:checked').map(function() { //create JS object with all of the categories checked to pass to get requests
                        return this.value;
                        }).get();
    if (name == "" || email == "" || phone == "" || twitter == ""|| address == ""|| description == "") {
      $("#error").addClass("alert alert-danger"); 
      $("#error").html("Please fill out all form fields.");
    }
    else {
    	$.getJSON('/complete_registration', { name: name, email: email, phone: phone, twitter: twitter, address: address, description: 
                                    description, categories: JSON.stringify(categories) } ).done(function(data){ //this will add a marker on the map for the incident the user just reported
        feature_layer.setGeoJSON([]); //empty the feature_layer of objects
        try {
            addMarkerLayer(data);
        }
        catch(err){
            $("#error").addClass("alert alert-info"); 
            $("#error").html("This incident has already been reported.");
        };
      });
    };
    NProgress.done();
  });

  //this adds default values to the form
  $("input[name='time_input']").attr("value",moment().format("HH:mm"));
  $("input[name='date_input']").attr("value",moment().format("YYYY-MM-DD"));
  $("input[name='address_input']").attr("value","683 Sutter Street, San Francisco, CA");
  $("textarea[name='description']").html("Write a brief introduction.");
  $("#theft").prop("checked",true);

  //this will have the tab in the navbar for this page be active
  $('#heat_route').removeClass('active');
  $('#markers_route').removeClass('active');
  $('#trends_route').removeClass('active');
  $('#report_route').addClass('active');
  $('#journey_route').removeClass('active');
  $('#home_route').removeClass('active');

});
