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
            <script src="js/index.js"></script>                

            <!-- CSS -->
            <link rel="stylesheet" href="styles/select-loading.css"></link>
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
                <li role="presentation"><a id="plots_url" href="plots.html">Plots</a></li>
            </ul>


            <div class="container-wide">

                <div class="row">
                    <div class="col-lg-6">
                        <div class="row">
                            <div class="col-lg-12">
                                <div class="form-group">
                                    <h3>Subsystem</h3>
                                    <select class="form-control" id="select-subsystem">
                                        <option value="" disabled selected hidden>Select a subsystem...<option>
                                    </select>
                                </div>
                            </div>
                        </div>
                        <div class="row">
                            <div class="col-lg-6">
                                <h3>Data Run</h3>
                                <div class="form-group">
                                    <label for="data-select-series">Series</label>
                                    <select class="form-control" id="data-select-series">
                                        <option value="" disabled selected hidden>Select a series...<option>
                                    </select>
                                    <label for="data-select-sample">Sample</label>
                                    <select class="form-control" id="data-select-sample">
                                        <option value="" disabled selected hidden>Select a sample...<option>
                                    </select>
                                    <label for="data-select-run">Data Run</label>
                                    <select class="form-control" id="data-select-run">
                                        <option value="" disabled selected hidden>Input a data run...<option>
                                    </select>
                                </div>
                            </div>
                            <div class="col-lg-6">
                                <h3>Reference Run</h3>
                                <div class="form-group">
                                    <label for="ref-select-series">Series</label>
                                    <select class="form-control" id="ref-select-series">
                                        <option value="" disabled selected hidden>Select a series...<option>
                                    </select>
                                    <label for="ref-select-sample">Sample</label>
                                    <select class="form-control" id="ref-select-sample">
                                        <option value="" disabled selected hidden>Select a sample...<option>
                                    </select>
                                    <label for="ref-select-run">Reference Run</label>
                                    <select class="form-control" id="ref-select-run">
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
                            <a href="plots.html"><div class="alert alert-success" id="finished">Success! Please navigate to the 'Plots' page to view the results.</div></a>
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
