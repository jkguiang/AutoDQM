
// Global variables
var t0 = 0;
var cur_sample = "none"; // So script knows what sample is selected
var data_info = ""; // To be sent with query
var ref_info = ""; // To be sent with query
var prefix = ""; // Sample name that is placed in front of dataset name

// Form functions: mostly for updating 'preview' wells
function updt_data() {
    var path = document.getElementById("path").value;

    $('#preview').text("");
    $('#preview').text("/" + prefix + "/" + path);
    check_input();
}

function updt_ref() {
    var ref_path = document.getElementById("ref_path").value;

    $('#ref_preview').text("");
    $('#ref_preview').text("/" + prefix + "/" + ref_path);
    check_input();
}

function updt_sample() {

    if (cur_sample == "RelVal") {
        var sample_input = document.getElementById(cur_sample + "_input").value;
        prefix = cur_sample + sample_input;
        data_info = sample_input;
        ref_info = sample_input;
        $("#data_sample").attr('placeholder', "/"+ prefix +"/");
        $("#ref_sample").attr('placeholder', "/"+ prefix +"/");
    }
    else if (cur_sample == "SingleMuon") {
        data_info = document.getElementById(cur_sample + "_dataInput").value;
        ref_info = document.getElementById(cur_sample + "_refInput").value;
        prefix = cur_sample;
    }
    updt_data();
    updt_ref();
    check_input();
}

function check_input() {
    var passed = true;

    data_inp = document.getElementById("path").value;
    ref_inp = document.getElementById("ref_path").value;
    data_split = data_inp.split("/");
    ref_split = ref_inp.split("/");

    // Sample form filled
    if (cur_sample == "SingleMuon") {
        if  (document.getElementById(cur_sample + "_dataInput").value != "" && document.getElementById(cur_sample + "_refInput").value != "") {
            $("#sample_chk").attr('class', 'list-group-item list-group-item-success')
        }

        else {
            $("#sample_chk").attr('class', 'list-group-item list-group-item-danger');
            passed = false;
        }
    }
    if (cur_sample == "RelVal") {
        if  (document.getElementById(cur_sample + "_input").value != "") {
            $("#sample_chk").attr('class', 'list-group-item list-group-item-success')
        }

        else {
            $("#sample_chk").attr('class', 'list-group-item list-group-item-danger');
            passed = false;
        }
    }
    // One slash
    if ( (data_split.length - 1) == 1 && (ref_split.length - 1) == 1 ) {
        var passed_slash = true;
        $("#slash_chk").attr('class', 'list-group-item list-group-item-success');
    }
    else {
        $("#slash_chk").attr('class', 'list-group-item list-group-item-danger');
        passed = false;
    }
    // Text on both sides of slash
    if ( passed_slash && data_split.indexOf("") <= -1 && ref_split.indexOf("") <= -1 ) {
        $("#form_chk").attr('class', 'list-group-item list-group-item-success');
    }
    else {
        $("#form_chk").attr('class', 'list-group-item list-group-item-danger');
        passed = false;
    }
    // Ends with DQMIO
    if (data_split[data_split.length - 1] == "DQMIO" && ref_split[ref_split.length - 1] == "DQMIO") {
        $("#dqmio_chk").attr('class', 'list-group-item list-group-item-success');
    }
    else {
        $("#dqmio_chk").attr('class', 'list-group-item list-group-item-danger');
        passed = false;
    }

    if (passed) {
        $("#submit").removeAttr('disabled');
    }
    else {
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
            if (cur_sample == "RelVal") {
                localStorage["data"] = response["query"]["data_info"];
                localStorage["ref"] = response["query"]["ref_info"];
            }
            else if (cur_sample == "SingleMuon") {
                localStorage["data"] = response["query"]["data_info"];
                localStorage["ref"] = response["query"]["ref_info"];
            }
            reduced_resp = [localStorage["data"], localStorage["ref"], response["query"]["user_id"]];
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
            $.get("src/handler.py", response["query"])
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
    $.get("src/handler.py", query)
        .done(function(response) {})
        .always(handle_processes);
}

function check_query(query) {
    var fail = false;

    var path = document.getElementById("path").value;
    var ref_path = document.getElementById("ref_path").value;
    if (path == "" || ref_path == "")   {
        fail = true;
    }
    if (fail) {
        $("#input_err").show();
    }

    else {
        $("#input_err").hide();
        console.log(query);
        submit(query);
    }
}

function get_search(external_query) {
    // Use json to get object from stringified search query
    new_query = JSON.parse(external_query);
    $("#sample_list").val(new_query["sample"]);
    $("#" + new_query["sample"]).show();
    $("#data_sample").text("/" + new_query["sample"] + "/");
    $("#ref_sample").text("/" + new_query["sample"] + "/");
    $("#path").removeAttr('disabled');
    $("#ref_path").removeAttr('disabled');

    cur_sample = new_query["sample"];
    if (new_query["sample"] == "SingleMuon") {
        $("#SingleMuon_dataInput").val(new_query["data_info"]);
        $("#SingleMuon_refInput").val(new_query["ref_info"]);
        $("#path").val(new_query["data_query"].split("/" + new_query["sample"] + "/")[1]);
        $("#ref_path").val(new_query["ref_query"].split("/" + new_query["sample"] + "/")[1]);
        prefix = "SingleMuon";
    
    }
    if (new_query["sample"] == "RelVal") {
        $("#RelVal_input").val(new_query["data_info"]);
        prefix = new_query["sample"] + new_query["data_info"];
        $("#path").val(new_query["data_query"].split("/" + prefix + "/")[1]);
        $("#ref_path").val(new_query["ref_query"].split("/" + prefix + "/")[1]);
    
    }
    updt_data();
    updt_ref();
    check_input();
    updt_sample();
    updt_data();
    updt_ref();

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
    $("#RelVal").hide();

    // Initial Disables
    $("#path").attr('disabled', 'disabled');
    $("#ref_path").attr('disabled', 'disabled');
    $("#submit").attr('disabled', 'disabled');

    // Update plots link if search stored in local storage
    if (localStorage.hasOwnProperty("data")) {
        $("#plots_url").attr('href', window.location.href + "plots.php?query=" + encodeURIComponent([localStorage["data"], localStorage["ref"]]));
    }

    // If user refreshes after a search has failed, ensures that all form info will be properly stored
    check_input();

    // Prevent 'enter' key from submitting forms (gives 404 error with full data set name form)
    $(window).keydown(function(event) {
        if (event.keyCode == 13) {
            event.preventDefault();
            return false;
        }
    });

    // Select menu functions
    $("#sample_list").val("none");
    var relval_ex = "e.g. CMSSW_9_1_1_patch1-91X_upgrade2023_realistic_v1_D17-v1/DQMIO";
    var singlemu_ex = "e.g. Run2017C-PromptReco-v1/DQMIO";
    var none_ex = "Please select a sample."
    $("#sample_list").on('change', function() {
        // Store current sample (global variable)
        cur_sample = this.value;
        prefix = this.value;

        // Reset fields
        if (cur_sample != "none"){
            $("#" + cur_sample)[0].reset();
            updt_data();
            updt_ref();
            updt_sample();
        }

        // Disable data set name input if no sample selected
        if (this.value == "none") {
            $("#path").attr('disabled', 'disabled');
            $("#ref_path").attr('disabled', 'disabled');
            $("#path").attr('placeholder', none_ex);
            $("#ref_path").attr('placeholder', none_ex);
            $("#data_sample").text("/sample/");
            $("#ref_sample").text("/sample/");
        }
        else {
            $("#path").removeAttr('disabled');
            $("#ref_path").removeAttr('disabled');
            if (this.value == "RelVal") {
                $("#path").attr('placeholder', relval_ex);
                $("#ref_path").attr('placeholder', relval_ex);
                $("#data_sample").text("/" + prefix + "/");
                $("#ref_sample").text("/" + prefix + "/");
            }
            if (this.value == "SingleMuon") {
                $("#path").attr('placeholder', singlemu_ex);
                $("#ref_path").attr('placeholder', singlemu_ex);
                $("#data_sample").text("/" + prefix + "/");
                $("#ref_sample").text("/" + prefix + "/");
            }
        }

        // Show proper input for selected sample
        var opts = document.getElementById("sample_list").options;
        for ( var i = 0; i < opts.length; i++ ) {
            if (opts[i].value == this.value) {
                $("#" + this.value).show();
            }
            else {
                $("#" + opts[i].value).hide();
            }
        }
    });

    // Main query handler
    $("#submit").click(function(){
        $("#load").hide();
        $("#load_msg").text("Loading data...")
        $("#finished").hide();
        $("#input_err").hide();
        $("#internal_err").hide();
        var query = {
            "type": "retrieve_data",
            "data_query": $("#preview").text(),
            "ref_query": $("#ref_preview").text(),
            "sample": cur_sample,
            "data_info": data_info,
            "ref_info": ref_info,
            "user_id": Date.now(), 
        };
        check_query(query);
    });

    // Update form if query passed from search page
    if (localStorage.hasOwnProperty("external_query")) {
        get_search(localStorage["external_query"]);
        localStorage.removeItem("external_query");
    }

});

