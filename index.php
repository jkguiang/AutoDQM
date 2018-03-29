<html>
        <head>
            <title>AutoDQM</title>

            <!-- Latest compiled and minified Boostrap CSS and Javascript -->
            <script src="https://ajax.googleapis.com/ajax/libs/jquery/1.11.3/jquery.min.js"></script>
            <script src="//code.jquery.com/ui/1.11.4/jquery-ui.js"></script>

            <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css">
            <script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/js/bootstrap.min.js"></script>
            
            <!-- Selectize libraries -->
            <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/selectize.js/0.12.4/css/selectize.bootstrap3.min.css"></link>
            <script src="https://cdnjs.cloudflare.com/ajax/libs/selectize.js/0.12.4/js/standalone/selectize.min.js"></script>

            <!-- Tab Icon -->
            <link rel="shortcut icon" type="image/x-icon" href="favicon.ico" />

            <!-- My Code -->
            <script src="src/js/index.js"></script>                

            <!-- CSS -->
            <style>
                .container-wide {
                    padding: 0 50px !important;
                }
                .loader {
                    text-align: center;
                    margin: auto;
                    border: 6px solid #f3f3f3; /* Light grey */
                    border-top: 6px solid #3498db; /* Blue */
                    border-radius: 50%;
                    width: 60px;
                    height: 60px;
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
                <li role="presentation" class="active"><a href="./">AutoDQM</a></li>
                <li role="presentation"><a href="search.php">Search</a></li>
                <li role="presentation"><a href="database.php">Database</a></li>
                <li role="presentation"><a id="plots_url" href="plots.php">Plots</a></li>
            </ul>


            <div class="container-wide">

                <div class="row">
                    <div class="col-lg-6">
                        <div class="row"><h2>Sample</h2><hr></div>
                        <div class="row">
                            <div class="col-lg-6">
                                <div class="form-group">
                                    <label for="select-series">Series</label>
                                    <select class="form-control" id="select-series">
                                        <option value="Run2017">Run2017</option>
                                        <option value="Commissioning2018">Commissioning2018</option>
                                    </select>
                                    <label for="select-sample">Sample</label>
                                    <select class="form-control" id="select-sample">
                                        <option value="SingleMuon">SingleMuon</option>
                                        <option value="Cosmics">Cosmics</option>
                                    </select>
                                    <label for="select-subsystem">Subsystem</label>
                                    <select class="form-control" id="select-subsystem">
                                        <option value="CSC">CSC</option>
                                        <option value="EMTF">EMTF</option>
                                    </select>
                                </div>
                            </div>
                            <div class="col-lg-6">
                                <div class="form-group">
                                    <label for="select-data-run">Data Run</label>
                                    <select class="form-control" id="select-data-run">
                                        <option value="" disabled selected hidden>Input a data run...<option>
                                    </select>
                                    <label for="select-ref-run">Reference Run</label>
                                    <select class="form-control" id="select-ref-run">
                                        <option value="" disabled selected hidden>Input a reference run...<option>
                                    </select>
                                </div>
                            </div>
                        </div>
                    </div> <!-- End top left column -->
                    <div class="col-lg-6">
                        <p><br /></p>
                        <div class="list-group">
                            <li class="list-group-item">Requirements</li>
                            <li class="list-group-item list-group-item-danger" id="sample_chk">Sample form filled</li>
                        </div>
                    </div>
                </div>
                <hr>

                <p><br /></p>

                <div class="row">
                    <div class="col-lg-3">
                    </div> <!-- end secondary row left padding -->
                    <div class="col-lg-6">
                        <div class="text-center">
                            <button id="submit" type="submit" class="btn btn-lg btn-success">Submit</button>
                            <p><br /></p>
                            <a href="plots.php"><div class="alert alert-success" id="finished">Success! Please navigate to the 'Plots' page to view the results.</div></a>
                            <div class="alert alert-danger" id="input_err">Error: Incomplete input.</div>
                            <div class="alert alert-danger" id="internal_err">Error: Internal error.</div>
                        </div>
                        <div class="loader" id="load"></div>
                        <div class="text-center"><small class="form-text text-muted" id="load_msg">Loading...</small></div>
                    </div> <!-- end secondary row middle col -->
                    <div class="col-lg-3">
                    </div> <!-- end secondary row right padding -->
                </div> <!-- end secondary row -->

            </div> <!-- end container -->
        </body>
</html>
