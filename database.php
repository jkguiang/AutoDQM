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
                    $to_load = file_get_contents($cwd . "/src/" . "db_map.json");
                    $files_dict = json_decode($to_load, true);

                    $db_map = array();
                    $timestamp = $files_dict["timestamp"];
                    $newest = $files_dict["newest"];

                    foreach($files_dict["files"] as $key => $val) {
                        $new_entry = array(
                            "run" => $key,
                            "last_mod" => $val,
                            "hidden" => false,
                        );

                        $db_map[] = $new_entry;
                    }

                ?>

                <!-- pass php values to js vars -->
                <script>
                    var db_map = <?php echo json_encode($db_map);  ?> // New files dict {"run_number":"dataset_name", ...} from php
                    var timestamp = new Date(Number(<?php echo $timestamp ?>) * 1000);
                    var newest = new Date(Number(<?php echo $newest ?>) * 1000);
                </script>

                <!-- load jquery after php runs -->
                <script src="src/js/database.js"></script>

        </head>

        <body>
            <ul class="nav nav-tabs" id="navbar" role="tablist">
                <li role="presentation"><a href="./">AutoDQM</a></li>
                <li role="presentation"><a href="search.php">Search</a></li>
                <li role="presentation" class="active"><a href="database.php">Database</a></li>
                <li role="presentation"><a id="plots_url" href="plots.php">Plots</a></li>
            </ul><!-- end navbar -->

            <div class="container-wide">
                <p><br /><br /></p>
                <div class="row">
                    <div class="col-sm-3"></div>
                    <div class="col-sm-6">
                        <form id="modular" action="/" method="post" role="form">
                            <div class="form-group row">
                                <input type="text" class="form-control" id="search" onkeyup="updt_search()" name="search" placeholder="Search">
                            </div>
                        </form>
                    </div>
                    <div class="col-sm-3"></div>
                </div> <!-- End top row -->
                <div class="row">
                    <div class="col-lg-2"></div><!-- end file list left padding -->
                    <div class="col-lg-8" id="file_list_div">
                        <div class="row text-center">
                            <small class="form-text text-muted" id="timestamp">Last updated: 0/00/00 00:00</small>
                        </div><!-- end file list timestamp row -->
                        <div class="row">
                            <div class="list-group" id="file_list"></div>
                        </div><!-- end file list row -->
                        <div class="row text-center">
                            <small class="form-text text-muted" id="newest">Newest File: 0/00/00 00:00</small>
                        </div><!-- end file list newest timestamp row -->
                        <div class="row">
                            <div class="col-sm-5"></div>
                            <div class="col-sm-2 text-center"><div class="loader" id="load"></div></div>
                            <div class="col-sm-5"></div>
                        </div><!-- end file list buttons row -->
                    </div><!-- end file list content col -->
                    <div class="col-lg-2"></div><!-- end file list right padding -->
                </div><!-- end file list div --> 
                <hr>
                <div class="row"><div class="col-lg-2"></div><div class="col-lg-8"><h3>Selection</h3><hr></div><div class="col-lg-2"></div></div> <!-- end data header -->
                <div class="row" id="preview_div">
                    <div class="col-lg-2"></div><!-- end selection preview right padding -->
                    <div class="col-lg-3">
                        <label for="date">Last Modified</label>
                        <div class="alert alert-success" id="date">No selection.</div>
                    </div>
                    <div class="col-lg-2">
                        <label for="data_run">Run</label>
                        <div class="alert alert-success" id="run">None</div>
                    </div><!-- end selection run div -->
                    <div class="col-lg-5"></div><!-- end selection preview right padding -->
                </div><!-- end data preview div --> 

                <div class="row"><div class="col-lg-2"></div><div class="col-lg-8"><h3>Submission</h3><hr></div><div class="col-lg-2"></div></div> <!-- end ref header -->
                <div class="row" id="data_preview_div">
                    <div class="col-lg-2"></div><!-- end data preview right padding -->
                    <div class="col-lg-6">
                        <label for="data_preview">Dataset Name</label>
                        <div class="alert alert-success" id="data_preview">No selection.</div>
                    </div>
                    <div class="col-lg-2">
                        <label for="ref_run">Run</label>
                        <div class="alert alert-success" id="data_run">None</div>
                    </div><!-- end data run div -->
                    <div class="col-lg-2"></div><!-- end data preview right padding -->
                </div><!-- end data preview div --> 

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
