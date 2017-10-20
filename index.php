<html>
        <head>
                <title>AutoDQM</title>

                <!-- Latest compiled and minified Boostrap CSS and Javascript -->
                <script src="https://ajax.googleapis.com/ajax/libs/jquery/1.11.3/jquery.min.js"></script>
                <script src="//code.jquery.com/ui/1.11.4/jquery-ui.js"></script>

                <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css">
                <script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/js/bootstrap.min.js"></script>

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
                                    <label for="sample_list">Name</label>
                                    <select class="form-control" id="sample_list">
                                        <option value="none">Select Sample</option>
                                        <option value="RelVal">RelVal</option>
                                        <option value="SingleMuon">SingleMuon</option>
                                    </select>
                                </div>
                            </div>
                            <div class="col-lg-6">
                                <!-- RelVal Sample Entry -->
                                <div class="form-group row">
                                    <form id="RelVal" action="/" method="post" role="form">
                                        <div class="form-group">
                                            <label for="RelVal_input">RelVal Sample</label>
                                            <input type="text" class="form-control" id="RelVal_input" onkeyup="updt_sample()" placeholder="e.g. ZMM_14">
                                        </div>
                                    </form>
                                <!-- SingleMuon Run Entry -->
                                    <form id="SingleMuon" action="/" method="post" role="form">
                                        <div class="form-group">
                                            <label for="SingleMuon_dataInput">Data Run Number</label>
                                            <input type="text" class="form-control" id="SingleMuon_dataInput" onkeyup="updt_sample()" placeholder="e.g. 300811">
                                            <hr style="margin:0px; height:10px; visibility:hidden;" />
                                            <label for="SingleMuon_refInput">Reference Run Number</label>
                                            <input type="text" class="form-control" id="SingleMuon_refInput" onkeyup="updt_sample()" placeholder="e.g. 301531">
                                        </div>
                                    </form>
                                </div>
                            </div>
                        </div>
                    </div> <!-- End top left column -->
                    <div class="col-lg-6">
                        <p><br /></p>
                        <div class="list-group">
                            <li class="list-group-item">Requirements</li>
                            <li class="list-group-item list-group-item-danger" id="sample_chk">Sample form filled</li>
                            <li class="list-group-item list-group-item-danger" id="slash_chk">One slash</li>
                            <li class="list-group-item list-group-item-danger" id="form_chk">Text on both sides of slash</li>
                            <li class="list-group-item list-group-item-danger" id="dqmio_chk">Ends with DQMIO</li>
                        </div>
                    </div>
                </div>
                <hr>
                <div class="row">
                    <div class="col-lg-6">
                        <h2>Data</h2>
                        <hr>
                        
                        <label for="path">Dataset Name</label>
                        <div class="alert alert-success"> 
                            <div class="input-group">
                                <span class="input-group-addon" id="data_sample">/sample/</span>
                                <form class="form-inline" id="full" action="./" method="post" role="form">
                                    <input type="text" class="form-control" id="path" onkeyup="updt_data()" name="path" placeholder="Please select a sample.">
                                </form>
                            </div>
                        </div>

                    </div > <!-- end right col -->

                    <div class="col-lg-6">
                        <h2>Reference</h2>
                        <hr>
                        
                        <label for="ref_path">Dataset Name</label>
                        <div class="alert alert-info">
                            <div class="input-group">
                                <span class="input-group-addon" id="ref_sample">/sample/</span>
                                <form class="form-inline" id="ref_full" action="./" method="post" role="form">
                                    <input type="text" class="form-control" id="ref_path" onkeyup="updt_ref()" name="ref_path" placeholder="Please select a sample.">
                                </form>
                            </div>
                        </div>

                    </div > <!-- end right col -->

                </div> <!-- end main row -->

                <p><br /></p>

                <hr>
                <div class="row">
                    <div class="col-lg-3">
                    </div> <!-- end secondary row left padding -->
                    <div class="col-lg-6">
                        <div class="row">
                            <div class="col-md-12">
                                <label for="preview_well">Data Preview</label>
                                <div class="alert alert-success" id="preview_well">
                                    <p id="preview">Please enter a data set name.</p>
                                </div>
                            </div>
                        </div> <!-- end preview row -->
                        <div class="row">
                            <div class="col-md-12">
                                <label for="ref_preview_well">Reference Preview</label>
                                <div class="alert alert-info" id="ref_preview_well">
                                    <p id="ref_preview">Please enter a reference data set name.</p>
                                </div>
                            </div>
                        </div> <!-- end ref_preview row -->
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
