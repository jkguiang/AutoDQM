import React, {Component} from 'react';
import {Container, Row as BSRow, Col, Button} from 'reactstrap';
import Select from 'react-select';
import axios from 'axios';

export default class RunSelectForm extends Component {
  constructor(props) {
    super(props);
    this.state = {
      seriesReq: null,
      samplesReq: null,
      runsReq: null,
      seriesOpts: [],
      samplesOpts: [],
      refsOpts: [],
    };
  }

  componentDidMount = () => {
    this.loadSeries();
    if (this.props.series) this.loadSamples();
    if (this.props.sample) this.loadRuns();
  };

  componentWillUnmount = () => {
    const reqs = [
      this.state.seriesReq,
      this.state.sampleReq,
      this.state.runsReq,
    ];
    for (let req of reqs) {
      req && req.cancel();
    }
    this.setState({
      seriesReq: null,
      sampleReq: null,
      runsReq: null,
      seriesOpts: [],
      sampleOpts: [],
      runsOpts: [],
    });
  };

  componentDidUpdate = prevProps => {
    if (this.props.series !== prevProps.series) this.loadSamples();
    if (this.props.sample !== prevProps.sample) this.loadRuns();
  };

  handleChange = change => {
    const {series, sample, run} = this.props;
    const vals = Object.assign({series, sample, run}, change);
    this.props.onChange(vals);
  };

  loadSeries = () => {
    this.state.seriesReq && this.state.seriesReq.cancel();
    const p = this.loadOptions({type: 'get_series'});
    this.setState({seriesReq: p});

    p.then(res => {
      this.setState({seriesOpts: res, seriesReq: null});
    }).catch(err => {
      if (!axios.isCancel(err)) this.setState({runsOpts: [], runsReq: null});
    });
  };

  loadSamples = () => {
    this.state.samplesReq && this.state.samplesReq.cancel();
    const p = this.loadOptions({
      type: 'get_samples',
      series: this.props.series.value,
    });
    this.setState({samplesReq: p});

    p.then(res => {
      this.setState({samplesOpts: res, samplesReq: null});
    }).catch(err => {
      if (!axios.isCancel(err)) this.setState({runsOpts: [], runsReq: null});
    });
  };

  loadRuns = () => {
    this.state.runsReq && this.state.runsReq.cancel();
    const p = this.loadOptions({
      type: 'get_runs',
      series: this.props.series.value,
      sample: this.props.sample.value,
    });
    this.setState({runsReq: p});

    p.then(res => {
      const seen = {};
      const runs = res.filter(
        r => !seen.hasOwnProperty(r.value) && (seen[r.value] = true),
      );
      this.setState({runsOpts: runs, runsReq: null});
    }).catch(err => {
      if (!axios.isCancel(err)) this.setState({runsOpts: [], runsReq: null});
    });
  };

  loadOptions = query => {
    const source = axios.CancelToken.source();
    const p = axios
      .get('/cgi-bin/index.py', {params: query, cancelToken: source.token})
      .then(res => {
        if (res.data.error) throw res.data.error;
        return res.data.data.items.map(s => ({
          value: s.name,
          label: s.name,
        }));
      })
      .catch(err => {
        console.log(err);
        throw err;
      });
    p.cancel = () => source.cancel(`Cancelled request of type ${query.type}`);
    return p;
  };

  render() {
    return (
      <React.Fragment>
        <span>Series</span>
        <Select
          placeholder="Select series..."
          options={this.state.seriesOpts}
          value={this.props.series}
          onChange={series => this.handleChange({series})}
          isLoading={this.state.seriesReq}
        />
        <span>Sample</span>
        <Select
          placeholder="Select sample..."
          options={this.state.samplesOpts}
          value={this.props.sample}
          onChange={sample => this.handleChange({sample})}
          isLoading={this.state.samplesReq}
          isDisabled={!this.props.series}
        />
        <span>Run</span>
        <Select
          placeholder="Select run..."
          options={this.state.runsOpts}
          value={this.props.run}
          onChange={run => this.handleChange({run})}
          isLoading={this.state.runsReq}
          isDisabled={!this.props.sample}
        />
      </React.Fragment>
    );
  }
}
