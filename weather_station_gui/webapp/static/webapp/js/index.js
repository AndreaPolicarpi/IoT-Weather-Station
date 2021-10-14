function list_filter() {
    var input, filter, ul, li, a, i, txtValue;
    input = document.getElementById("myInput");
    filter = input.value.toUpperCase();
    ul = document.getElementById("sensor_list");
    li = ul.getElementsByTagName("li");
    for (i = 0; i < li.length; i++) {
        a = li[i].getElementsByTagName("a")[0];
        txtValue = a.textContent || a.innerText;
        if (txtValue.toUpperCase().indexOf(filter) > -1) {
            li[i].style.display = "";
        } else {
            li[i].style.display = "none";
        }
    }
}

function change_settings(change, input_id) {
    change_value = parseFloat(document.getElementById(input_id).value)
    console.log(change_value)
    window.location = "/webapp/" + $("#sensor_id").text() + "/" + change + "/" + change_value;
}

$(document).ready(function () {
    $("#edit_maxtemp").click(function () {
        var valuemaxtemp = parseFloat($("#maxtempvalue").text())
        console.log(valuemaxtemp)
        $("#maxtemp").html("<input type=\"number\" step=\"0.1\" name=\"input_maxtemp\"" +
            "id=\"input_maxtemp\" value=\"" + valuemaxtemp +
            "\" style =\"{width: 5px;}\">");

        $("#td_edit_maxtemp").html("<div><button onclick=\"change_settings('maxtemp', 'input_maxtemp')\"  id=\"check_maxtemp\" class=\"btn btn-success\"><i class='far fa-check-circle' style=\"color:white\"></i></button>" +
            "<button onclick=\"location.reload()\" id=\"dismiss_maxtemp\" class=\"btn btn-danger\"><i class=\"far fa-times-circle\" style=\"color:white\"></i></button></div>");
    });

    $("#edit_mintemp").click(function () {
        var valuemintemp = parseFloat($("#mintempvalue").text())
        console.log(valuemintemp)
        $("#mintemp").html("<input type=\"number\" step=\"0.1\" name=\"input_mintemp\"" +
            "id=\"input_mintemp\" value=\"" + valuemintemp +
            "\" style =\"{width: 5px;}\">");

        $("#td_edit_mintemp").html("<div><button onclick=\"change_settings('mintemp', 'input_mintemp')\"  id=\"check_mintemp\" class=\"btn btn-success\"><i class='far fa-check-circle' style=\"color:white\"></i></button>" +
            "<button onclick=\"location.reload()\" id=\"dismiss_mintemp\" class=\"btn btn-danger\"><i class=\"far fa-times-circle\" style=\"color:white\"></i></button></div>");
    });

    $("#edit_maxhum").click(function () {
        var valuemaxhum = parseFloat($("#maxhumvalue").text())
        console.log(valuemaxhum)
        $("#maxhum").html("<input type=\"number\" step=\"0.1\" name=\"input_maxhum\"" +
            "id=\"input_maxhum\" value=\"" + valuemaxhum +
            "\" style =\"{width: 5px;}\">");

        $("#td_edit_maxhum").html("<div><button onclick=\"change_settings('maxhum', 'input_maxhum')\"  id=\"check_maxhum\" class=\"btn btn-success\"><i class='far fa-check-circle' style=\"color:white\"></i></button>" +
            "<button onclick=\"location.reload()\" id=\"dismiss_maxhum\" class=\"btn btn-danger\"><i class=\"far fa-times-circle\" style=\"color:white\"></i></button></div>");
    });

    $("#edit_minhum").click(function () {
        var valueminhum = parseFloat($("#minhumvalue").text())
        console.log(valueminhum)
        $("#minhum").html("<input type=\"number\" step=\"0.1\" name=\"input_minhum\"" +
            "id=\"input_minhum\" value=\"" + valueminhum +
            "\" style =\"{width: 5px;}\">");

        $("#td_edit_minhum").html("<div><button onclick=\"change_settings('minhum', 'input_minhum')\"  id=\"check_minhum\" class=\"btn btn-success\"><i class='far fa-check-circle' style=\"color:white\"></i></button>" +
            "<button onclick=\"location.reload()\" id=\"dismiss_minhum\" class=\"btn btn-danger\"><i class=\"far fa-times-circle\" style=\"color:white\"></i></button></div>");
    });

    $("#edit_sampling").click(function () {
        var valuesampling = parseFloat($("#samplingvalue").text())
        console.log(valuesampling)
        $("#sampling").html(
                    "<select id=\"input_sampling\" class=\"form-select\" aria-label=\"Default select example\">"+
                    "<option selected>Select the sampling rate</option>"+
                    "<option value=\"250\">250ms</option>"+
                    "<option value=\"500\">500ms</option>"+
                    "<option value=\"100\">1000ms</option>"+
                    "</select>"
                )

        $("#td_edit_sampling").html("<div><button onclick=\"change_settings('sampling', 'input_sampling')\"  id=\"check_sampling\" class=\"btn btn-success\"><i class='far fa-check-circle' style=\"color:white\"></i></button>" +
            "<button onclick=\"location.reload()\" id=\"dismiss_sampling\" class=\"btn btn-danger\"><i class=\"far fa-times-circle\" style=\"color:white\"></i></button></div>");
    });


});


