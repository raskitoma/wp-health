$("#toggle_status").on("click", function() {
    var check_status_loc = "<span>OFFLINE</span>";
    var check_status_class = "fas fa-eye-slash fa-2x text-danger";
    if ($(this).hasClass("bg-danger")) {
        console.log("OFFLINE -> ONLINE");
        $(this).removeClass("bg-danger");
        $(this).addClass("bg-success");
        $(this).html("<i class='fa fa-check-circle'></i> Online");
        check_status_loc = "<span>ONLINE</span>";
        check_status_class = "fas fa-eye fa-2x text-success";
        fetch("/wcdisable").then(function(response) {
            console.log("Engine Online! " + response);
        });   
    } else {
        console.log("ONLINE -> OFFLINE");
        $(this).removeClass("bg-success");
        $(this).addClass("bg-danger");
        $(this).html("<i class='fa fa-times-circle'></i> Offline");
        check_status_loc = "<span>OFFLINE</span>";
        check_status_class = "fas fa-eye-slash fa-2x text-danger";
        fetch("/wcdisable").then(function(response) {
            console.log("Engine Offline!" + response);
        });    
        }
    $("#check_mode").html(check_status_loc);
    $("#sys_status").removeAttr('class');
    $("#sys_status").addClass(check_status_class);
});
