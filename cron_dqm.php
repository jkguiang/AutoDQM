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
                
                <!-- PHP -->
                <?php

                    $cwd = getcwd();
                    $to_load = file_get_contents($cwd . "/" . "new_files.json");
                    $files_dict = json_decode($to_load, true);

                    $new_files = array();
                    $timestamp = $files_dict["timestamp"];

                    foreach($files_dict["files"] as $key => $val) {
                        $new_files[$key] = $val;
                    }

                ?>

                <!-- JQuery -->
                <script>
                    // Global variables
                    var query = {
                        "type": "retrieve",
                        "data_query": "", 
                        "ref_query": "", 
                        "sample": "", 
                        "data_info": "", 
                        "ref_info": "", 
                    }; // Stores query to be sent to index.php

                    var new_files = <?php echo json_encode($new_files);  ?> // New files dict {"run_number":"dataset_name", ...} from php
                    var timestamp = new Date(Number(<?php echo $timestamp ?>) * 1000);

                    // Form handlers
                    function display(new_files) {
                        $("#timestamp").text("Last Updated: " + timestamp.toString());

                        $("#file_list").html("");
                        var file_list = $("#file_list");
                        toappend = "";

                        var counter = 0;
                        for (var key in new_files) {
                            toappend+= "<a class='list-group-item' id='item_"+ counter +"'>"+ key +"</a>";
                            counter++;
                        }

                        file_list.append(toappend);

                        $('[id^=item_]').click(function() {
                            // Highlight ONLY selected item
                            $('[id^=item_]').attr("class", "list-group-item");
                            $(this).attr("class", 'list-group-item active');
                            // Update preview
                            $("#data_preview").text(new_files[$(this).text()]);
                            $("#data_run").text($(this).text());

                            // Update global query
                            query["data_query"] = new_files[$(this).text()];
                            query["data_info"] = $(this).text();
                        });
                    
                    }
                    // End form handlers

                    // Query handlers
                    function handle_respose() {
                    
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

                        display(new_files);

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
                        $("#refresh").click(function() {
                            var query = {
                                "type": "refresh",
                                "cron": "/SingleMuon/Run2017*PromptReco*/DQMIO",
                            };
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
                    
                    });

                </script>

        </head>

        <body>
            <ul class="nav nav-tabs" id="navbar" role="tablist">
                <li role="presentation"><a href="./">AutoDQM</a></li>
                <li role="presentation"><a href="search.php">Search</a></li>
                <li role="presentation" class="active"><a href="cron_dqm.php">New DQM Files</a></li>
                <li role="presentation"><a id="plots_url" href="plots.php">Plots</a></li>
            </ul><!-- end navbar -->

            <div class="container-wide">
                <p><br /><br /></p>
                <div class="row">
                    <div class="col-lg-2"></div><!-- end file list left padding -->
                    <div class="col-lg-8" id="file_list_div">
                        <div class="row text-center">
                            <small class="form-text text-muted" id="timestamp">Last updated: 0/00/00 00:00</small>
                        </div><!-- end file list timestamp row -->
                        <div class="row">
                            <div class="list-group" id="file_list"></div>
                        </div><!-- end file list row -->
                        <div class="row">
                            <div class="col-sm-5"></div>
                            <div class="col-sm-2 text-center"><button id="refresh" type="submit" class="btn btn-success">Refresh</div>
                            <div class="col-sm-5"></div>
                        </div><!-- end file list buttons row -->
                    </div><!-- end file list content col -->
                    <div class="col-lg-2"></div><!-- end file list right padding -->
                </div><!-- end file list div --> 
                <hr>
                <div class="row"><div class="col-lg-2"></div><div class="col-lg-8"><h3>Data</h3><hr></div><div class="col-lg-2"></div></div> <!-- end data header -->
                <div class="row" id="data_preview_div">
                    <div class="col-lg-2"></div><!-- end data preview right padding -->
                    <div class="col-lg-6">
                        <label for="data_preview">Dataset Name</label>
                        <div class="alert alert-success" id="data_preview">No selection.</div>
                    </div>
                    <div class="col-lg-2">
                        <label for="data_run">Run</label>
                        <div class="alert alert-success" id="data_run">None</div>
                    </div><!-- end data run div -->
                    <div class="col-lg-2"></div><!-- end data preview right padding -->
                </div><!-- end data preview div --> 
                <div class="row"><div class="col-lg-2"></div><div class="col-lg-8"><h3>Reference</h3><hr></div><div class="col-lg-2"></div></div> <!-- end ref header -->
                <div class="row" id="ref_preview_div">
                    <div class="col-lg-2"></div><!-- end ref preview right padding -->
                    <div class="col-lg-6">
                        <label for="ref_preview">Dataset Name</label>
                        <div class="alert alert-info" id="ref_preview">No selection.</div>
                    </div>
                    <div class="col-lg-2">
                        <label for="ref_run">Run</label>
                        <div class="alert alert-info" id="ref_run">None</div>
                    </div><!-- end ref run div -->
                    <div class="col-lg-2"></div><!-- end ref preview right padding -->
                </div><!-- end ref preview div --> 
                <div class="row">
                    <div class="col-lg-5"></div>
                    <div class="col-lg-2 text-center"><button id="submit" type="submit" class="btn btn-success" disabled>Submit</div>
                    <div class="col-lg-5"></div>
                </div><!-- end file list buttons row -->
            <p><br /><br /></p>
            </div> <!-- end container -->
        </body>
</html>
