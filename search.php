<html>
        <head>
                <title>AutoDQM</title>

                <!-- Latest compiled and minified Boostrap CSS and Javascript -->
                <script src="https://ajax.googleapis.com/ajax/libs/jquery/1.11.3/jquery.min.js"></script>
                <script src="//code.jquery.com/ui/1.11.4/jquery-ui.js"></script>

                <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css">
                <script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/js/bootstrap.min.js"></script>

                <!-- My Code -->
                <script src="src/js/search.js"></script>
                
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

        </head>

        <body>
            <ul class="nav nav-tabs" id="navbar" role="tablist">
                <li role="presentation"><a href="./">AutoDQM</a></li>
                <li role="presentation" class="active"><a href="search.php">Search</a></li>
                <li role="presentation"><a href="database.php">Database</a></li>
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
