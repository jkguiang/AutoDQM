
// Global variables
var query = {
    "type": "retrieve_data",
    "data_query": "", 
    "ref_query": "", 
    "sample": "", 
    "data_info": "", 
    "ref_info": "", 
}; // Stores query to be sent to index.php

var page_loads = 0;
map = {};

// Form handlers
function updt_search() {

    page_loads += 1;
    filter(new_files);

}


function filter(new_files) {

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
    for (var i = 0; i < new_files.length; i++) {
        if (new_files[i]["run"].toString().indexOf(search) < 0) {
            new_files[i]["hidden"] = true;
        }
        else {
            new_files[i]["hidden"] = false;
        }
    }

    display(new_files);
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
                html_name += "<font class='bg-success'>"+new_search+"</font>";
            }
        }
    }

    else {
        html_name = name;
    }

    return html_name;

}

function display(new_files) {
    var ul = $("#file_list");
    ul.html("");
    toappend = "";

    toappend += "<div class='row' id='page_1'>";
    var counter = 1;

    true_count = 0;
    for (var i = 0; i < new_files.length; i++) {
        if (new_files[i]["hidden"] == true) {
            true_count++;
            continue;
        }
        html_name = get_name(new_files[i]["run"].toString(), i);
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

    if (new_files.length % 10 != 0) {
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
        $("#data_preview").text(new_files[Number(this.id.split("item_")[1])]["dsname"]);
        $("#data_run").text($(this).text());

        // Update global query
        query["data_query"] = new_files[$(this).text()];
        query["data_info"] = $(this).text();
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

    //Initial Hides
    $("#load").hide();

    filter(new_files);

    // Prevent 'enter' key from submitting forms (gives 404 error with full data set name form)
    $(window).keydown(function(event) {
        if (event.keyCode == 13) {
            event.preventDefault();
            return false;
        }
    });

    // Update plots link if query stored in local storage
    if (localStorage.hasOwnProperty("data")) {
        $("#plots_url").attr('href', "plots.php?query=" + encodeURIComponent([localStorage["data"], localStorage["ref"]]));
    }


    // Main query handler
    $("#submit").click(function() {
        if ($("#data_preview").text() == "No data selected." || $("#ref_preview").text() == "No reference selected.") {
            $("#input_err").show();
        }
        else {
            localStorage["external_query"] = JSON.stringify(query);
            document.location.href="./";
        }
    });

});
