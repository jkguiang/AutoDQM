<html>
        <head>
                <title>AutoDQM</title>

                <!-- Latest compiled and minified Boostrap CSS and Javascript -->
                <script src="https://ajax.googleapis.com/ajax/libs/jquery/1.11.3/jquery.min.js"></script>
                <script src="//code.jquery.com/ui/1.11.4/jquery-ui.js"></script>

                <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css">
                <script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/js/bootstrap.min.js"></script>

                <!-- My Code -->
                
                <!-- CSS -->
                <style>
                    .alert-grey {
                        color: #727272;
                        background-color: #d6d6d6;
                        border-color: #cecece;
                    }
                    .container-wide {
                        padding: 0 50px !important;
                    }
                    .loader {
                        text-align: center;
                        margin: auto;
                        border: 8px solid #f3f3f3; /* Light grey */
                        border-top: 8px solid #3498db; /* Blue */
                        border-radius: 50%;
                        width: 40px;
                        height: 40px;
                        animation: spin 2s linear infinite;
                    }
                    @keyframes spin {
                        0% { transform: rotate(0deg); }
                        100% { transform: rotate(360deg); }
                    }
                </style>

                <!-- JQuery -->
                <script>
                    // Global variables
                    var cur_tag = "#data";
                    var cur_search = ""; // Stores most recent search (files or dsnames) type so script knows which div to fill
                    var cur_sample = ""; // Stores current sample (RelVal, SingleMuon) so script knows whether to require run selection
                    var info = ""; // Stores info for sample, passed to query when selection is completed
                    var query = {
                        "type": "retrieve_data",
                        "data_query": "", 
                        "ref_query": "", 
                        "sample": "", 
                        "data_info": "", 
                        "ref_info": "", 
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
                        $.get("handler.py", query)
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
                            $("#plots_url").attr('href', "plots.php?query=" + encodeURIComponent([localStorage["data"], localStorage["ref"]]));
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
                                "search": $(cur_tag).text(),
                            }
                            check(query);
                        });

                        $("#select").click(function() {
                            console.log("select button clicked");
                            $(cur_tag + "_preview").text($(cur_tag).text());
                            $(cur_tag + "_run").text($("#run").text());
                            query[cur_tag.split("#")[1] + "_info"] = info;
                            query[cur_tag.split("#")[1] + "_query"] = $(cur_tag).text();
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

                </script>

        </head>

        <body>
            <ul class="nav nav-tabs" id="navbar" role="tablist">
                <li role="presentation"><a href="./">AutoDQM</a></li>
                <li role="presentation" class="active"><a href="search.php">Search</a></li>
                <li role="presentation"><a href="cron_dqm.php">New DQM Files</a></li>
                <li role="presentation"><a id="plots_url" href="plots.php">Plots</a></li>
            </ul>


            <div class="container-wide">
                <p><br /><br /></p>
                <div class="row">
                    <div class="col-md-2"></div>
                    <div class="col-md-8">
                        <div class="row">
                            <div class="col-sm-10">
                                <form id="modular" action="/" method="post" role="form">
                                    <div class="form-group row">
                                        <input type="text" class="form-control" id="search_txt" onkeyup="check_search()" name="search_txt" placeholder="Dataset name">
                                    </div>
                                </form>
                            </div>
                            <div class="col-sm-2">
                                <button id="search" type="submit" class="btn btn-success" disabled>Search</button>
                                <div class="loader" id="dsnames_load"></div>
                            </div>
                        </div> <!-- End top row -->
                        <div class="row">
                            <div class="col-sm-10"><div class="alert alert-danger" id="input_err">Error: Incomplete input.</div></div>
                            <div class="col-sm-10"><div class="alert alert-danger" id="internal_err">Error: Internal error.</div></div>
                        </div> <!-- End bottom row -->
                    </div>
                    <div class="col-md-2">
                        <div class="checkbox"><label class="checkbox-inline"><input type="checkbox" id="toggle_submit" checked>Toggle Submit Form</label></div>
                    </div>
                </div>
                <hr>
                <div class="row">
                    <div class="col-lg-6">
                        <div class="list-group" id="dsnames"></div>
                    </div>
                    <div class="col-lg-6">
                        <div class="list-group" id="files"></div>
                    </div>
                </div>
                <div class="row">
                    <div class="col-lg-6">
                        <div class="row">
                            <div class="col-sm-12" id="data_well"><label>Selection</label><div class="alert alert-success"><p id="data">No selection.</p></div></div>
                            <div class="col-sm-12" id="ref_well"><label>Selection</label><div class="alert alert-info"><p id="ref">No selection.</p></div></div>
                            <div class="col-sm-12" id="run_well"><label>Run</label><div class="alert alert-success" id="run">No selection.</div></div>
                        </div><!-- pelection preview pane -->

                        <div class="row">
                            <div class="col-sm-2"></div>
                            <div class="col-sm-2"><label class="radio-inline"><input id="data_check" type="radio" value="data" checked>Data</label></div>
                            <div class="col-sm-2"><label class="radio-inline"><input id="ref_check" type="radio" value="ref">Reference</label></div>
                            <div class="col-sm-2"><button id="select" type="submit" class="btn btn-success" disabled>Select</button></div>
                            <div class="col-sm-2"><button id="get_files" type="submit" class="btn btn-success" disabled>Get File List</button><div class="loader" id="files_load"></div></div>
                            <!-- radio selection menu -->

                            <div class="col-sm-2"></div>
                        </div>
                    </div> <!-- end slection preview -->
                    
                    <div class="col-lg-6" id="submit_form">
                        <div class="row">
                            <div class="col-md-9">
                                <label for="data_preview">Data</label>
                                <div class="alert alert-success" id="data_preview">No data selected.</div>
                                <label for="ref_preview">Reference</label>
                                <div class="alert alert-info" id="ref_preview">No reference selected.</div>
                            </div>
                            <div class="col-md-3">
                                <label for="data_run">Run</label>
                                <div class="alert alert-grey" id="data_run">None.</div>
                                <label for="ref_run">Run</label>
                                <div class="alert alert-grey" id="ref_run">None.</div>
                            </div>
                        </div>
                        <div class="row">
                            <div class="col-sm-5"></div>
                            <div class="col-sm-2"><button id="submit" type="submit" class="btn btn-success" disabled>Submit</button></div>
                            <div class="col-sm-5"></div>
                        </div>
                    </div>
                </div> <!-- end secondary row -->
                <p><br /><br /></p>
            </div> <!-- end container -->
        </body>
</html>
