
// Global variables
var query = {
    "type": "retrieve_data",
    "sample": "", 
    "data_info": "", 
    "ref_info": "", 
    "user_id": "",
}; // Stores query to be sent to index.php

var page_loads = 0;
var cur_tag = "#data";
var cur_sample = "none";
map = {};

// Form handlers
function updt_search() {

    page_loads += 1;
    filter(db_map);

}

function check_submission() {

    var passed = true;

    if ($("#data_run").text() == "None" || $("#ref_run").text() == "None") {
        passed = false;
    }

    if (passed) {
        $("#submit").removeAttr('disabled');
    }
    else {
        $("#submit").attr('disabled', 'disabled');
    }
}

function filter(db_map) {

    if (cur_sample == "none") {
        return;
    }

    var input = document.getElementById('search');
    if (page_loads == 1 && window.location.hash != "") {
        var search = window.location.hash.split("#")[1];
    }
    else{
        if (input == "") {
            window.location.hash = "";
        }
        var search = input.value;
        window.location.hash = search;
    }
    map["search"] = search;
    for (var i = 0; i < db_map[cur_sample].length; i++) {
        if (db_map[cur_sample][i]["run"].toString().indexOf(search) < 0) {
            db_map[cur_sample][i]["hidden"] = true;
        }
        else {
            db_map[cur_sample][i]["hidden"] = false;
        }
    }

    display(db_map);
}

function get_name(name, i) {

    var new_split = "";
    var html_name = "";

    if (map["search"] != "") {
        new_search = map["search"];
        new_split = name.split(new_search);
        new_name = "";

        for (var j = 0; j < new_split.length; j++) {
            new_name += new_split[j];
            html_name += new_split[j];
            if (name.indexOf(new_name + new_search) != -1) {
                new_name += new_search;
                html_name += "<font class='bg-info'>"+new_search+"</font>";
            }
        }
    }

    else {
        html_name = name;
    }

    return html_name;

}

function display(db_map) {

    if (cur_sample == "none") {
        return;
    }

    var ul = $("#file_list");
    ul.html("");
    toappend = "";

    toappend += "<div class='row' id='page_1'>";
    var counter = 1;

    var true_count = 0;
    for (var i = 0; i < db_map[cur_sample].length; i++) {
        if (db_map[cur_sample][i]["hidden"] == true) {
            continue;
        }
        html_name = get_name(db_map[cur_sample][i]["run"].toString(), i);
        toappend += "<a class='list-group-item' id='item_"+ i +"'>"+ html_name +"</a>";
        if ((true_count + 1) % 10 == 0 && i != 0) {
            toappend += "</div>";
            if (true_count == 9) {
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
        true_count++;
    }

    if (true_count % 10 != 0) {
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
    $('[id^=item_]').click(function() {
        // Store selected item
        map["selected"] = $(this);
        // Highlight ONLY selected item
        $('[id^=item_]').attr("class", "list-group-item");
        $(this).attr("class", 'list-group-item active');
        // Update preview
        $(cur_tag + "_run").text($(this).text());
        var last_mod = new Date(Number(db_map[cur_sample][Number(this.id.split("item_")[1])]["last_mod"]) * 1000);
        $(cur_tag + "_time").text(last_mod);

        // Check submission
        check_submission();
    });

    // Allows for navigation between lists of files
    $('[id^=nav_]').click(function() {
        show_value = $(this).attr('value');
        $('[id^=pagenavbar_]').hide();
        $('[id^=page_]').hide();
        $("#page_" + show_value).show();
        $("#pagenavbar_" + show_value).show();
    });

    // Update timestamps
    $("#newest").text("Newest file: " + newest);
    $("#timestamp").text("Last updated: " + timestamp);
    
}
// End form handlers


// Main function
$(function() {
    page_loads += 1;
    console.log(db_map)

    // Initial Hides
    $("#load").hide();
    $("#ref_well").hide();
    $("#SingleMuon_title").hide();
    $("#Cosmics_title").hide();
    $("#main_container").hide();
    
    // Ensure proper radio button selected
    $("#data_check").prop('checked', true);
    $("#ref_check").removeAttr('checked');
    check_submission();

    filter(db_map);

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

    // Radio menu
    $("#data_check").on("click", function(){
        $("#ref_check").removeAttr('checked');
        cur_tag = "#data";
    });
    $("#ref_check").on("click", function(){
        $("#data_check").removeAttr('checked');
        cur_tag = "#ref";
    });

    // Drop menu
    // Populate sample list with values from configs.json
    $.getJSON("data/configs.json", function(json) {
        samples = json["samples"];
        for ( var i = 0; i < samples.length; i++ ) {
            $("#sample_list").append($("<option>", {
                value: samples[i],
                text: samples[i]
            }));
        }
    });
    $("#sample_list").val("none");
    $("#sample_list").on('change', function() {
        // Store current sample (global variable)
        cur_sample = this.value;
        prefix = this.value;

        // Reset fields
        if (cur_sample != "none"){
            $("#main_container").show();
            filter(db_map);
        }
        else {
            $("#main_container").hide();
        }

        // Show proper input for selected sample
        var opts = document.getElementById("sample_list").options;
        for ( var i = 0; i < opts.length; i++ ) {
            if (opts[i].value == this.value) {
                $("#" + this.value + "_title").show();
            }
            else {
                $("#" + opts[i].value + "_title").hide();
            }
        }
    });

    // Main query handler
    $("#submit").click(function() {
        if ($("#data_preview").text() == "No data selected." || $("#ref_preview").text() == "No reference selected.") {
            $("#input_err").show();
        }
        else {
            query["sample"] = cur_sample;
            query["data_info"] = $("#data_run").text();
            query["ref_info"] = $("#ref_run").text();
            query["user_id"] = Date.now();
            localStorage["external_query"] = JSON.stringify(query);
            document.location.href="./";
        }
    });

});
