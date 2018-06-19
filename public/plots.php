<html>
<head>
  <title>AutoPlotter</title>

  <script src="https://ajax.googleapis.com/ajax/libs/jquery/1.11.3/jquery.min.js"></script>
  <script src="https://code.jquery.com/ui/1.11.4/jquery-ui.js"></script>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/mark.js/8.11.1/jquery.mark.min.js"></script>

  <!-- Latest compiled and minified Boostrap CSS and Javascript -->
  <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css">
  <script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/js/bootstrap.min.js"></script>

  <!-- Selectize libraries -->
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/selectize.js/0.12.4/css/selectize.bootstrap3.min.css"></link>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/selectize.js/0.12.4/js/standalone/selectize.min.js"></script>

  <!-- My Code -->

  <!-- CSS -->
  <style>
    img:hover {
      border: 1px solid #cecece;
    }

    .well-image .bg {
      pointer-events: none;
      margin-bottom: 0px;
      opacity: 0.2;
      color: #fff;
      background: #fff url("") no-repeat center top;
      background-color: #ffffff !important;
      background-size: contain !important;

      -webkit-filter: blur(5px);
      -moz-filter: blur(5px);
      -o-filter: blur(5px);
      -ms-filter: blur(5px);
      filter: blur(5px);

      overflow: hidden;
      width: 115%;
      height: 100%;

      position: absolute;
      top: 0;
      left: 0;
      z-index: auto;
    }

    .well {
      overflow: hidden;
      width: 115%;
    }

    .tooltip-txt {
      white-space: pre;
    }
  </style>

  <!-- load jquery after php runs -->
  <script src="js/plots.js"></script>

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
    <li role="presentation"><a href="./">AutoDQM</a></li>
    <li role="presentation" class="active"><a href="plots.php">Plots</a></li>
  </ul>

  <p><br /><br /></p>

  <div class="container-fluid">
    <div class="row flex-xl">

      <!-- Side panel -->
      <div class="col-12 col-md-3 col-xl-3 bd-sidebar">
        <div class="panel panel-default affix" style="max-width:400px">

          <!-- Header -->
          <div class="panel-heading">AutoDQM</div>

          <!-- Controls -->
          <div class="panel-body text-center">
            <form>
              <div class="form-group">
                <input type="checkbox" id="showall" onchange="searchChange()">
                  <span>Show all plots</span>
                </input>
                <input type="text" id="search" onkeyup="searchChange()" placeholder="Search" class="form-control">
              </div>
            </form>
          </div>

          <!-- Preview -->
          <div class="panel-body text-center">
            <img id="preview" class="img-thumbnail" src="" alt="Hover over a thumbnail to get preview here" width=300 >
          </div>

          <!-- Information -->
          <table id="tooltip" class="table">
          </table>
        </div>
      </div>

      <div class="col-12 col-md-9 col-xl-9 bd-content">
        <div class="row">
          <div class="col-md-3"></div>
          <div id="info_table" class="col-md-6">
            <table class="table table-striped" id="info_table">
              <thead>
                <tr class="table-success">
                  <th scope="col" id="subsystem"></th>
                  <th scope="col">Data</th>
                  <th scope="col">Reference</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <th scope="row">Series</th>
                  <td><p id="data_series"></p></td>
                  <td><p id="ref_series"></p></td>
                </tr>
                <tr>
                  <th scope="row">Sample</th>
                  <td><p id="data_sample"></p></td>
                  <td><p id="ref_sample"></p></td>
                </tr>
                <tr>
                  <th scope="row">Run</th>
                  <td><p id="data_run"></p></td>
                  <td><p id="ref_run"></p></td>
                </tr>
              </tbody>
            </table>
          </div>
          <div class="col-md-3"></div>
        </div>

        <div class="row">
          <div class="col-sm-3"></div>
          <div class="col-md-6">
            <div class="col-sm-3 text-center">
              <button type="button" class="btn btn-primary" id="prev_run">&laquo Prev Run</button>
            </div>
            <div class="col-sm-6">
              <select class="form-control" id="data-select-run">
                <option value="" disabled selected hidden>Select a different data run...<option>
             </select>
            </div>
            <div class="col-sm-3 text-center">
              <button type="button" class="btn btn-primary" id="next_run">Next Run &raquo</button>
            </div>
          </div>
          <div class="col-sm-3"></div>
        </div>

        <!-- Images -->
        <div id="results" class="d-flex flex-wrap">
          <div class="loader" id="load"></div>
          <div class="text-center" id="load_msg"><small class="form-text text-muted"></small></div>
          <div class="alert alert-danger text-center"id="err_msg"><small class="form-text text-muted"></small></div>
        </div>
        <!-- /.container -->
      </div>
    </div>

    <!-- Footer -->
    <div class="container">
      <hr>
      <!-- thin, grey horizontal line -->
    </div>
  </div>
</body>

</html>
