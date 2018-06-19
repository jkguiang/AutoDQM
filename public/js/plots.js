// Map for storing result objects by their id
let result_map = {};

function main() {
    let query = getQuery();
    updateInfo(query);

    $("#load").show();
    $("#load_msg").text("Processing...").show();
    $("#err_msg").hide();

    initRunControls();
    process(query.subsystem,
            query.data_series, query.data_sample, query.data_run,
            query.ref_series, query.ref_sample, query.ref_run)
        .then(res => {
            console.log(res);
            $("#load").hide();
            $("#load_msg").hide();
            renderResults(res.data.items);
            searchChange();
        })
        .fail(res => {
            console.log("Error:", res);
            res.error.traceback && console.log(res.error.traceback);
            $("#load").hide();
            $("#load_msg").hide();
            $("#err_msg").text(res.error.message).show();
        });
}

function updateInfo(query) {
    $("#subsystem").text(query.subsystem);
    $("#data_series").text(query.data_series);
    $("#data_sample").text(query.data_sample);
    $("#data_run").text(query.data_run);
    $("#ref_series").text(query.ref_series);
    $("#ref_sample").text(query.ref_sample);
    $("#ref_run").text(query.ref_run);
}

function wrapApiCall(p) {
    let defer = $.Deferred();
    p.done(res => {
            if (res.error) {
                defer.reject(res);
            } else {
                defer.resolve(res);
            }
        })
        .fail(res => {
            defer.reject({
                error: {
                    message: res.statusText,
                    jqXHR: res
                }
            });
        })
    defer.abort = p.abort;
    return defer;
}

function process(subsystem,
    data_series, data_sample, data_run,
    ref_series, ref_sample, ref_run) {
    return wrapApiCall($.getJSON('cgi-bin/index.py', {
        type: 'process',
        subsystem: subsystem,
        data_series: data_series,
        data_sample: data_sample,
        data_run: data_run,
        ref_series: ref_series,
        ref_sample: ref_sample,
        ref_run: ref_run
    }));
}

function getRuns(series, sample) {
    return wrapApiCall($.getJSON('cgi-bin/index.py', {
        type: 'get_runs',
        series: series,
        sample: sample
    }));
}

function renderResults(results) {
    let container = $("#results");

    let blocks = [];
    for (let i = 0; i < results.length; i++) {
        blocks.push(resultHtml(results[i]));
    }
    container.append(...blocks);

    $('.result').mouseenter(hoverResult);
}

function resultHtml(result) {
    let classes = result.display ? 'result display' : 'result nodisplay';
    let id = `result_${result.id}`;
    result_map[id] = result;
    return `
    <div class="${classes}" id="result_${result.id}" style="display:inline-block">
        <a href=${result.pdf_path} target="_blank">
            <h4>${result.name}</h4>
            <img src=${result.png_path} width="300" />
        </a>
    </div>`
}

function updateDisplay(search = "", showAll = false) {
    let items = $('.result')
    items.hide();
    if (!showAll) {
        items = items.filter('.display');
    }
    if (search) {
        items = items.filter(`:contains(${search})`);
    }
    items.show();

    $(".result h4").unmark({
        done: search ? () => $(".result h4").mark(search) : null
    });
}

function searchChange() {
    let text = $('#search').val();
    let showAll = $('#showall').prop("checked");
    updateDisplay(text, showAll);
}

function hoverResult(e) {
    let id = e.currentTarget.id;
    let result = result_map[id];

    $('#preview').attr("src", result.png_path);
    $('#tooltip').html(resultInfoHtml(result));
}

function resultInfoHtml(result) {
    let rows = [
        `<tr><th scope="row">Name</th><td>${result.name}</td></tr>`,
        `<tr><th scope="row">Algo</th><td>${result.comparator}</td></tr>`,
        `<tr><th scope="row">Display</th><td>${result.display}</td></tr>`,
    ]
    for (let key in result.results) {
        let val = result.results[key];
        rows.push(`<tr><th scope="row">${key}</th><td>${val}</td></tr>`);
    }
    return `<tbody>
                ${rows.join('\n')}
            </tbody>`
}

// Fetch object pased from index
function parseQString() {
    let url = document.location.href.split("#")[0];
    let qString = url.split('?')[1];
    let params = qString.split('&');
    let query = {};
    for (let i = 0; i < params.length; i++) {
        let tmp = params[i].split('=');
        query[tmp[0]] = tmp[1];
    }
    return query;
}

function getQuery() {
    return parseQString();
}

// Pass query to main submit page
function submit(query) {
    localStorage["external_query"] = JSON.stringify(query);
    document.location.href = "./";
}

// Buttons for submitting same query with next or previous run
// Grab next and previous runs for button functionality
function initRunControls() {

    // Initialize buttons and selectize
    let query = getQuery();
    $("#next_run").click(function() {
        query.data_run = this.title.toString();
        submit(query);
    });
    $("#prev_run").click(function() {
        query.data_run = this.title.toString();
        submit(query);
    });

    $("#data-select-run").selectize({
        valueField: 'name',
        labelField: 'name',
        searchField: 'name',
        onChange: run => {
            query.data_run = run;
            submit(query);
        },
    });

    // Disable buttons/selectize until runs are loaded
    $("#next_run").attr('disabled', 'true');
    $("#prev_run").attr('disabled', 'true');
    $("#data-select-run")[0].selectize.disable();

    // Request runs based on local query
    var rReq;
    var run_list;
    rReq = getRuns(query.data_series, query.data_sample)
        .then(res => {
            let runs = res.data.items;
            let seen = {}
            // Filter entries with duplicate run number
            runs = runs.filter(r => {
                return seen.hasOwnProperty(r.name) ? false : (seen[r.name] = true);
            });
            
            let run_numbers = runs.map(r => Number(r.name)).sort();

            let current_runNum = Number(query.data_run);
            let next_runNum = run_numbers[run_numbers.indexOf(current_runNum) + 1];
            let prev_runNum = run_numbers[run_numbers.indexOf(current_runNum) - 1];

            $("#next_run").removeAttr('disabled').prop('title', next_runNum);
            $("#prev_run").removeAttr('disabled').prop('title', prev_runNum);
            $("#data-select-run")[0].selectize.enable();
            $("#data-select-run")[0].selectize.load(cb => cb(runs));
        })
        .fail(res => {
            console.log("Failed to retrieve data runs: ", res);
            res.error.traceback && console.log(res.error.traceback);
        });
}

$(main);
