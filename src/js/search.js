
// Global variables
var cur_tag = "#data";
var cur_search = ""; // Stores most recent search (files or dsnames) type so script knows which div to fill
var cur_sample = ""; // Stores current sample (RelVal, SingleMuon) so script knows whether to require run selection
var info = ""; // Stores info for sample, passed to query when selection is completed
var query = {
    "type": "retrieve_data",
    "sample": "", 
    "data_info": "", 
    "ref_info": "", 
    "user_id": "",
}; // Stores query to be sent to index.php
var t0 = 0;

// Form functions: mostly for updating 'preview' wells
function check_search() {
    // Ensure form is filled
    if ( document.getElementById("search_txt").value == "" ) {
        $("#search").attr('disabled', 'disabled');
    }
    // TODO Add some check for correct input here
    else {
        $("#search").removeAttr('disabled');
    }
}

function check_selection() {
    is_good = true;
    // Get selection, update cur_sample
    if ($(cur_tag).text().indexOf("SingleMuon") > -1) {
        cur_sample = "SingleMuon";
    }
    else if ($(cur_tag).text().indexOf("RelVal") > -1) {
        cur_sample = "RelVal";
    }

    // Check for good selection
    if ($(cur_tag).text() == "No selection.") {
        is_good = false;
    }
    // Check for cur_sample-related requirements
    if (cur_sample == "SingleMuon") {
        $("#run_well").show();
        $("#data_run").attr("class", "alert alert-success");
        $("#ref_run").attr("class", "alert alert-info");
        $("#get_files").removeAttr('disabled');
        if ($("#run").text() == "No selection.") {
            is_good = false;
        }
        else {
            info = $("#run").text();
        }
    }
    else if (cur_sample == "RelVal") {
        $("#get_files").attr('disabled', 'disabled');
        $("#run_well").hide();
        $("#data_run").attr("class", "alert alert-grey");
        $("#ref_run").attr("class", "alert alert-grey");
        info = $(cur_tag).text().split("/")[1]
    }
    else {
        $("#get_files").attr('disabled', 'disabled');
        info = "";
        is_good = false;
    }

    // Final check
    if (is_good) {
        $("#select").removeAttr('disabled');
    }
    else {
        $("#select").attr('disabled', 'disabled');
    }
}

function check_submission() {
    is_good = true;
    if ($("#data_preview").text() == "No data selected.") {
        is_good = false;
    }
    if ($("#ref_preview").text() == "No reference selected.") {
        is_good = false;
    }
    if (cur_sample == "SingleMuon" || cur_sample == "RelVal") {
        if (query["data_info"] == "" || query["ref_info"] == "") {
            is_good = false;
        }
    }
    if (is_good) {
        $("#submit").removeAttr('disabled');
    }
    else {
        $("#submit").attr('disabled', 'disabled');
    }
}

// End form functions

// Query handlers
function display(new_list) {
    console.log("display ran");
    console.log(cur_search);
    console.log(new_list);

    toappend = "";

    if (cur_search == "dsnames") {
        var ul = $("#dsnames");
        var tag = "dsname";

        for (var i = 0; i < new_list.length; i++) {
            toappend += "<a class='list-group-item' id="+ tag +"_"+ i +">"+ new_list[i] +"</a>";
        }

        ul.append(toappend);

        // dsname list item functionality
        $('[id^='+ tag +'_]').click(function() {
            $('[id^=' +tag+ '_]').attr("class", "list-group-item");
            $(this).attr("class", "list-group-item active");
            if ($(cur_tag).text() != $(this).text()) {
                // Reset file list and run selection if navigates to different list item
                $("#files").html("");
                $("#run").text("No selection.");
            }
            $(cur_tag).text("");
            $(cur_tag).text($(this).text());
            check_selection();
        });
    }
    if (cur_search == "files") {
        var ul = $("#files");
        var tag = "file";

        console.log(new_list.length);

        toappend += "<div class='row' id='page_1'>";
        var counter = 1;

        for (var i = 0; i < new_list.length; i++) {
            toappend += "<a class='list-group-item' id="+ tag +"_"+ i +">"+ new_list[i] +"</a>";
            if ((i + 1) % 10 == 0 && i != 0) {
                toappend += "</div>";
                if (i == 9) {
                    toappend += "<div class='row text-center' id='pagenavbar_"+ counter +"'>";
                    toappend += "   <hr>";
                    toappend += "   <div class='col-sm-2'><input class='btn btn-default btn-sm' id='nav_1' type='button' value='1' disabled></div>";
                    toappend += "   <div class='col-sm-3'></div>";
                    toappend += "   <div class='col-sm-2'><p>"+counter+"</p></div>";
                    toappend += "   <div class='col-sm-3'></div>";
                    toappend += "   <div class='col-sm-2'><input class='btn btn-success btn-sm' id='nav_"+(counter+1)+"' type='button' value="+(counter+1)+"></div>";
                    toappend += "</div>";
                }
                else {
                    toappend += "<div class='row text-center' id='pagenavbar_"+ counter +"' hidden>";
                    toappend += "   <hr>";
                    toappend += "   <div class='col-sm-2'><input class='btn btn-success btn-sm' id='nav_"+(counter-1)+"'  type='button' value="+(counter-1)+"></div>";
                    toappend += "   <div class='col-sm-3'></div>";
                    toappend += "   <div class='col-sm-2'><p>"+counter+"</p></div>";
                    toappend += "   <div class='col-sm-3'></div>";
                    toappend += "   <div class='col-sm-2'><input class='btn btn-success btn-sm' id='nav_"+(counter+1)+"'  type='button' value="+(counter+1)+"></div>";
                    toappend += "</div>";
                }
                counter += 1;
                toappend += "<div class='row' id='page_"+ counter +"' hidden>";
            }
        }

        if (new_list.length % 10 != 0) {
            toappend += "</div>";
            toappend += "<div class='row text-center' id='pagenavbar_"+ counter +"' hidden>";
            toappend += "   <hr>";
            toappend += "   <div class='col-sm-2'><input class='btn btn-success btn-sm' id='nav_"+(counter - 1)+"'  type='button' value="+(counter - 1)+"></div>";
            toappend += "   <div class='col-sm-3'></div>";
            toappend += "   <div class='col-sm-2'><p>"+counter+"</p></div>";
            toappend += "   <div class='col-sm-3'></div>";
            toappend += "   <div class='col-sm-2'><input class='btn btn-default btn-sm' id='nav_"+(counter)+"'  type='button' value="+counter+" disabled></div>";
            toappend += "</div>";
        }

        ul.append(toappend);

        // File list item functionality
        $('[id^='+ tag +'_]').click(function() {
            $('[id^=' +tag+ '_]').attr("class", "list-group-item");
            $(this).attr("class", "list-group-item active");
            $("#run").text("");
            $("#run").text($(this).text());
            check_selection();
        });

        // Allows for navigation between lists of files
        $('[id^=nav_]').click(function() {
            show_value = $(this).attr('value');
            $('[id^=pagenavbar_]').hide();
            $('[id^=page_]').hide();
            $("#page_" + show_value).show();
            $("#pagenavbar_" + show_value).show();
        });
    }


}

function handle_response(response) {
    console.log(response); 
    console.log("Run time: " + String(Math.floor(Date.now() / 1000) - t0));
    try {
        // Handle output from main.py
        console.log(response["response"]["payload"]);
        var resp = response["response"];

        if (resp["status"] == "failed") {
            $("#internal_err").text(resp["fail_reason"]);
            $("#internal_err").show();
        }                            

        else {
            display(resp["payload"]);
            $("#finished").show();
        }
    }
    catch(TypeError) {
        console.log("typeerror")
        // Handle crashes, system error, timeouts, etc.
        console.log(response["responseText"]);
        var resp = response["responseText"];
        var err_msg = "";
        
        $("#internal_err").text(err_msg);
        $("#internal_err").show();
    }
    finally {
        $("#search").show();
        $("#get_files").show();
        $("#"+ cur_search +"_load").hide();
    }
}

function submit(query) {
    console.log("submitting query");
    console.log(query);
    $("#"+ cur_search +"_load").show();
    t0 = Math.floor(Date.now() / 1000);
    console.log(t0);

    $.ajaxSetup({timeout:300000}); // Set timeout to 5 minutes
    $.get("src/scripts/handler.py", query)
        .done(function(response) {})
        .always(handle_response);
}

function check(query) {
    $("#input_err").hide();
    console.log(query);
    submit(query);
}
// End query handlers

// Main function
$(function() {
    // Main hides
    $("#dsnames_load").hide();
    $("#files_load").hide();
    $("#ref_well").hide();
    $("#run_well").hide();

    // Error hides
    $("#internal_err").hide();
    $("#input_err").hide();

    // Ensure run previews are greyed out
    $("#data_run").attr("class", "alert alert-grey");
    $("#ref_run").attr("class", "alert alert-grey");

    // Ensure proper radio is selected
    $("#data_check").prop('checked', true);
    $("#toggle_submit").prop('checked', true);
    $("#ref_check").removeAttr('checked');

    // Ensure proper buttons are disabled
    check_selection();
    check_submission();

    // Prevent 'enter' key from submitting forms (gives 404 error with full data set name form)
    $(window).keydown(function(event) {
        if (event.keyCode == 13) {
            event.preventDefault();
            return false;
        }
    });

    // Update plots link if query stored in local storage
    if (localStorage.hasOwnProperty("data")) {
        $("#plots_url").attr('href', "plots.php?query=" + encodeURIComponent([localStorage["data"], localStorage["ref"], localStorage["user_id"]]));
    }


    // Main query handler
    $("#search").click(function() {
        cur_search = "dsnames";

        $("#search").hide();
        $("#internal_err").hide();
        $("#dsnames").html("");
        $("#files").html("");
        var query = {
            "type": "search",
            "user_id": "None",
            "search": (document.getElementById("search_txt").value + "*"),
        }
        check(query);
    });

    $("#get_files").click(function() {
        cur_search = "files";

        $("#get_files").hide();
        $("#internal_err").hide();
        $("#files").html("");
        var query = {
            "type": "search",
            "user_id": "None",
            "search": $(cur_tag).text(),
        }
        check(query);
    });

    $("#select").click(function() {
        console.log("select button clicked");
        $(cur_tag + "_preview").text($(cur_tag).text());
        $(cur_tag + "_run").text($("#run").text());
        query[cur_tag.split("#")[1] + "_info"] = info;
        query["sample"] = cur_sample;
        console.log(query);
        $("#run").text("No selection.");
        check_submission();
        check_selection();
        // Deselect file
        $('[id^=file_]').attr("class", "list-group-item");
    });

    $("#submit").click(function() {
        if ($("#data_preview").text() == "No data selected." || $("#ref_preview").text() == "No reference selected.") {
            $("#input_err").show();
        }
        else {
            query["user_id"] = Date.now();
            localStorage["external_query"] = JSON.stringify(query);
            document.location.href="./";
        }
    });

    $("#data_check").on("click", function(){
        $("#ref_check").removeAttr('checked');
        $("#data").text($("#ref").text());
        cur_tag = "#data";

        $("#data_well").show();
        $("#ref_well").hide();
        $("#run").attr("class", "alert alert-success");

        check_selection();
    });

    $("#ref_check").on("click", function(){
        $("#data_check").removeAttr('checked');
        $("#ref").text($("#data").text());
        cur_tag = "#ref";

        $("#ref_well").show();
        $("#data_well").hide();
        $("#run").attr("class", "alert alert-info");

        check_selection();
    });

    $("#toggle_submit").on("click", function(){
        if ($(this).is(":checked")) {
            $("#submit_form").show();
        }
        else {
            $("#submit_form").hide();
        }
    });

});
