
$("#gen_key").click(function() {
    var rotimg = $(this).children("i");
    rotimg.addClass("rotated");
    $.get("/rskgenuiid", function(data) {
        $("#site_key").val(data);
    });
});

$("#Kill_Modal").click(function() {
    $("#site_host").val("");
    $("#site_path").val("");
    $("#site_user").val("");
    $("#site_wp_api").val("");
    $('#site_data').modal('hide');
});

function prep_modal(modal_title, site_id, site_host, site_path, site_user, site_wp_api, site_mode) {
    $('#modal_title').text(modal_title);
    $('#site_id').val(site_id);
    $('#site_host').val(site_host);
    $('#site_path').val(site_path);
    $('#site_user').val(site_user);
    $('#site_wp_api').val(site_wp_api);
    $('#site_mode').val(site_mode);
    $('#site_data').modal('show');
}

