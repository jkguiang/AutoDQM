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
                    var cur_tag = "#none";
                    var t0 = 0;

                    // Form functions: mostly for updating 'preview' wells
                    function check_search() {
                        // Ensure form is filled
                        if ( document.getElementById("search_txt").value == "" ) {
                            // TODO Add some check for correct input here
                            $("#search").attr('disabled', 'disabled');
                        }
                        else {
                            $("#search").removeAttr('disabled');
                        }
                    }

                    function check_selection() {
                        is_good = true;
                        if ($(cur_tag).text() == "No selection.") {
                            is_good = false;
                        }
                        if (!$("data_check").is(":checked") || !$("ref_check").is(":checked")) {
                            is_good = false;
                        }
                        if (is_good) {
                            $("#select").removeAttr('disabled');
                        }
                    }

                    function check_submission() {
                        is_good = true;
                        if ($("#data_select").text() == "No data selected.") {
                            is_good = false;
                        }
                        if ($("#ref_select").text() == "No reference selected.") {
                            is_good = false;
                        }
                        if (is_good) {
                            $("#submit").removeAttr('disabled');
                        }
                    }

                    // End form functions

                    // Query handlers
                    function display(new_list) {
                        var ul = $("#results");
                        var toappend = "";

                        for (var i = 0; i < new_list.length; i++) {
                            toappend += "<li>"+ new_list[i] +"</li>"
                        }

                        ul.append(toappend);
                    
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
                                $("#submit").show();
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

                            $("#submit").show();
                            $("#internal_err").show();
                        }
                        finally {
                            $("#search").show();
                            $("#load").hide();
                        }
                    }

                    function submit(query) {
                        console.log("submitting query");
                        console.log(query);
                        $("#load").show();
                        $("#submit").hide();
                        t0 = Math.floor(Date.now() / 1000);
                        console.log(t0);

                        $.ajaxSetup({timeout:300000}); // Set timeout to 5 minutes
                        $.get("search_handler.py", query)
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
                        $("#load").hide();
                        $("#data_well").hide();
                        $("#ref_well").hide();

                        // Error hides
                        $("#internal_err").hide();
                        $("#input_err").hide();

                        // Prevent 'enter' key from submitting forms (gives 404 error with full data set name form)
                        $(window).keydown(function(event) {
                            if (event.keyCode == 13) {
                                event.preventDefault();
                                return false;
                            }
                        });

                        // Main query handler
                        $("#search").click(function() {
                            $("#search").hide();
                            var query = {
                                "search": document.getElementById("search_txt").value,
                            }
                            check(query);
                        });

                        $("#select").click(function() {
                            $(cur_tag + "_preview").text($(cur_tag).text());
                            check_submission();
                        });

                        $("#submit").click(function() {
                            if ($("#data_select").text() == "No data selected." || $("#ref_select").text() == "No reference selected.") {
                                $("#input_err").show();
                            }
                            else {
                                localStorage["data"] = $("#data_select").text();
                                localStorage["ref"] = $("#ref_select").text();
                                document.location.href="./";
                            }
                        });

                        $("#data_check").on("click", function(){
                            if ( $(this).is(":checked") ) {
                                cur_tag = "#data";
                                $("#ref_check").attr('disabled', 'disabled');

                                $("#data_well").show();
                                $("#none_well").hide();
                                $("#ref_well").hide();

                                check_selection();
                            }
                            else {
                                cur_tag = "#none";
                                $("#ref_check").removeAttr('disabled');

                                $("#none_well").show();
                                $("#data_well").hide();
                                $("#ref_well").hide();
                            }
                        });

                        $("#ref_check").on("click", function(){
                            if ( $(this).is(":checked") ) {
                                cur_tag = "#ref";
                                $("#data_check").attr('disabled', 'disabled');

                                $("#ref_well").show();
                                $("#data_well").hide();
                                $("#none_well").hide();

                                check_selection();
                            }
                            else {
                                cur_tag = "#none";
                                $("#data_check").removeAttr('disabled');

                                $("#none_well").show();
                                $("#data_well").hide();
                                $("#ref_well").hide();
                            }
                        });
                    
                    });

                </script>

        </head>

        <body>
            <ul class="nav nav-tabs" id="navbar" role="tablist">
                <li role="presentation"><a href="./">AutoDQM</a></li>
                <li role="presentation" class="active"><a href="search.php">Search</a></li>
                <li role="presentation"><a href="plots.php">Plots</a></li>
            </ul>


            <div class="container-wide">
                <p><br /><br /></p>
                <div class="row">
                    <div class="col-sm-2"></div>
                    <div class="col-sm-8" style="padding: 0px">
                        <form id="modular" action="/" method="post" role="form">
                            <div class="form-group row">
                                <div class="col-sm-10">
                                    <input type="text" class="form-control" id="search_txt" onkeyup="check_search()" name="search_txt" placeholder="Dataset name">
                                </div>
                            </div>
                        </form>
                    </div>
                    <div class="col-sm-2" style="padding: 0px">
                        <div class="col-sm-1">
                            <button id="search" type="submit" class="btn btn-success" disabled>Search</button>
                        </div>
                        <div class="col-sm-1"><div class="loader" id="load"></div></div>
                    </div>
                </div>
                <hr>
                <div class="row">
                    <div class="well">
                        <ul id="results">
                        </ul>
                    </div>
                </div>
                <div class="row">
                    <div class="col-lg-6">
                        <div class="row">
                            <div class="col-sm-12" id="none_well"><label>Selection</label><div class="alert alert-warning"><p id="none">No selection.</p></div></div>
                            <div class="col-sm-12" id="data_well"><label>Selection</label><div class="alert alert-success"><p id="data">No selection.</p></div></div>
                            <div class="col-sm-12" id="ref_well"><label>Selection</label><div class="alert alert-info"><p id="ref">No selection.</p></div></div>
                        </div>

                        <div class="row">
                            <div class="col-sm-3"></div>
                            <div class="col-sm-2"><div class="checkbox"><label><input id="data_check" type="checkbox" value="data">Data</label></div></div>
                            <div class="col-sm-2"><div class="checkbox"><label><input id="ref_check" type="checkbox" value="ref">Reference</label></div></div>
                            <div class="col-sm-2"><button id="select" type="submit" class="btn btn-success" disabled>Select</button></div>
                            <div class="col-sm-3"></div>
                        </div>
                    </div> <!-- end slection preview -->
                    
                    <div class="col-lg-6">
                        <label for="data_select">Data</label>
                        <div class="alert alert-success" id="data_select" name="data_select">No data selected.</div>
                        <label for="ref_select">Reference</label>
                        <div class="alert alert-info" id="ref_select" name="ref_select">No reference selected.</div>
                        <div class="row">
                            <div class="col-sm-5"></div>
                            <div class="col-sm-2"><button id="submit" type="submit" class="btn btn-success" disabled>Submit</button></div>
                            <div class="col-sm-5"></div>
                        </div>
                    </div>
                </div> <!-- end secondary row -->
                <div class="row">
                    <p><br /></p>
                    <hr>
                    <div class="col-lg-3"></div>
                    <div class="col-lg-6"><div class="alert alert-danger" id="input_err">Error: Incomplete input.</div></div>
                    <div class="col-lg-6"><div class="alert alert-danger" id="internal_err">Error: Internal error.</div></div>
                    <div class="col-lg-3"></div>
                </div>
            </div> <!-- end container -->
        </body>
</html>
