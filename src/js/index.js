
// Global variables
var t0 = 0;

function check_input() {
    var filled =
        $("#select-series").val() != "" &&
        $("#select-sample").val() != "" &&
        $("#select-subsystem").val() != "" &&
        $("#select-data-run").val() != "" &&
        $("#select-ref-run").val() != "";

    if(filled) {
        $("#sample_chk").attr('class', 'list-group-item list-group-item-success');
        $("#submit").removeAttr('disabled');
    } else {
        $("#sample_chk").attr('class', 'list-group-item list-group-item-danger');
        $("#submit").attr('disabled', 'disabled');
    }
}

// End form functions

// Query handlers
function pass_object(new_object) {
    url = (window.location.href + "plots.php?query=" + encodeURIComponent(new_object));
    document.location.href = url;
}

function handle_response(response) {
    console.log(response);
    console.log("Run time: " + String(Math.floor(Date.now() / 1000) - t0));
    try {
        // Handle output from main.py
        console.log("query to be stored:");
        console.log(response["query"]);
        console.log("response:");
        console.log(response["response"]["payload"]);
        var resp = response["response"];

        if (resp["status"] == "fail") {
            $("#internal_err").text(resp["fail_reason"]);
            $("#submit").show();
            $("#internal_err").show();
        }

        else {
            localStorage["data"] = response["query"]["data_info"];
            localStorage["ref"] = response["query"]["ref_info"];
            localStorage["user_id"] = response["query"]["user_id"];
            reduced_resp = [localStorage["data"], localStorage["ref"], localStorage["user_id"]];
            pass_object(reduced_resp);
            $("#finished").show();
        }
    }
    catch(TypeError) {
        // Handle crashes, system error, timeouts, etc.
        console.log(response["responseText"]);
        var resp_txt = response["responseText"];
        var err_msg = "";

        console.log(resp_txt.indexOf("504"));
        if (resp_txt.indexOf("504") <= -1) {
            err_msg = "Error: Gateway timed out. Could not reach server."
        }
        else {
            err_msg = "Error: An internal error occured."
        }

        $("#internal_err").text(err_msg);

        $("#submit").show();
        $("#internal_err").show();
    }
    finally {
        $("#load").hide();
        $("#load_msg").text("Loading...");
        $("#load_msg").hide();
    }
}

function handle_processes(response) {
    console.log(response);
    console.log("Run time: " + String(Math.floor(Date.now() / 1000) - t0));

    try {
        // Handle output from main.py
        console.log("query to be stored:");
        console.log(response["query"]);
        console.log("response:");
        console.log(response["response"]["payload"]);
        var resp = response["response"];

        if (resp["status"] == "fail") {
            $("#load").hide()
            $("#load_msg").hide()
            $("#internal_err").text(resp["fail_reason"]);
            $("#submit").show();
            $("#internal_err").show();
        }

        else if (response["query"]["type"] == "retrieve_data") {
            console.log("data retrieved");
            $("#load_msg").text("Loading reference...")
            response["query"]["type"] = "retrieve_ref";
            submit(response["query"]);
        }

        else if (response["query"]["type"] == "retrieve_ref") {
            console.log("processing")
            response["query"]["type"] = "process";
            $("#load_msg").text("Processing...")
            $.ajaxSetup({timeout:0});
            $.get("src/scripts/handler.py", response["query"])
                .done(function(response) {})
                .always(handle_response);
        }
    }
    catch(TypeError) {
        // Handle crashes, system error, timeouts, etc.
        console.log(response["responseText"]);
        var resp = response["responseText"];
        var err_msg = "";

        console.log(resp.indexOf("504"));
        if (resp.indexOf("504") > -1) {
            err_msg = "Error: Gateway timed out. Could not reach server."
        }
        else {
            err_msg = "Error: An internal error occured."
        }

        $("#load").hide()
        $("#load_msg").hide()
        $("#internal_err").text(err_msg);

        $("#submit").show();
        $("#internal_err").show();
    }

}

function submit(query) {
    console.log("retrieving");
    console.log(query);
    $("#load").show();
    $("#load_msg").show();
    $("#submit").hide();
    $("#finished").hide();
    $("#input_err").hide();
    $("#internal_err").hide();
    t0 = Math.floor(Date.now() / 1000);
    console.log(t0);

    $.ajaxSetup({timeout:0}); // Set timeout to 5 minutes
    $.get("src/scripts/handler.py", query)
        .done(function(response) {})
        .always(handle_processes);
}

function get_search(external_query) {
    // Use json to get object from stringified search query
    new_query = JSON.parse(external_query);
    $("#sample_list").val(new_query["sample"]);
    $("#" + new_query["sample"]).show();
    $("#data_sample").text("/" + new_query["sample"] + "/");
    $("#ref_sample").text("/" + new_query["sample"] + "/");

    cur_sample = new_query["sample"];
    if (new_query["sample"] == "SingleMuon") {
        $("#SingleMuon_dataInput").val(new_query["data_info"]);
        $("#SingleMuon_refInput").val(new_query["ref_info"]);
    }
    if (new_query["sample"] == "Cosmics") {
        $("#Cosmics_dataInput").val(new_query["data_info"]);
        $("#Cosmics_refInput").val(new_query["ref_info"]);
    }
    check_input();
    updt_sample();

    $("#load").hide();
    $("#load_msg").hide();
    $("#finished").hide();
    $("#input_err").hide();
    $("#internal_err").hide();
    submit(new_query);
}
// End query handlers

// Main function
$(function() {
    console.log(localStorage);

    // Initital hides
    $("#load").hide();
    $("#load_msg").hide();
    $("#finished").hide();
    $("#input_err").hide();
    $("#internal_err").hide();
    $("#SingleMuon").hide();
    $("#Cosmics").hide();

    // Initial Disables
    $("#submit").attr('disabled', 'disabled');

    // Update plots link if search stored in local storage
    if (localStorage.hasOwnProperty("data")) {
        $("#plots_url").attr('href', window.location.href + "plots.php?query=" + encodeURIComponent([localStorage["data"], localStorage["ref"], localStorage["user_id"]]));
    }


    // Prevent 'enter' key from submitting forms (gives 404 error with full data set name form)
    $(window).keydown(function(event) {
        if (event.keyCode == 13) {
            event.preventDefault();
            return false;
        }
    });

    $('select').selectize({
        create: true,
        createOnBlur: true,
        onChange: check_input
    });

    $("#select-series").selectize();
    $("#select-sample").selectize();
    $("#select-subsystem").selectize();
    $("#select-data-run").selectize();
    $("#select-ref-run").selectize();
    
    // If user refreshes after a search has failed, ensures that all form info will be properly stored
    check_input();

    // Main query handler
    $("#submit").click(function(){
        $("#load").hide();
        $("#load_msg").text("Loading data...")
        $("#finished").hide();
        $("#input_err").hide();
        $("#internal_err").hide();
        var query = {
            "type": "retrieve_data",
            "series": $("#select-series").val(),
            "sample": $("#select-sample").val(),
            "subsystem": $("#select-subsystem").val(),
            "data_info": $("#select-data-run").val(),
            "ref_info": $("#select-ref-run").val(),
            "user_id": Date.now(),
        };
        submit(query);
    });

    // Update form if query passed from search page
    if (localStorage.hasOwnProperty("external_query")) {
        get_search(localStorage["external_query"]);
        localStorage.removeItem("external_query");
    }

});

