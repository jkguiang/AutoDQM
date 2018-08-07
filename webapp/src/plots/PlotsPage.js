import React, {Component} from 'react';
import {css} from 'react-emotion';
import {
  Card,
  CardTitle,
  CardText,
  Button,
  Container,
  Row,
  Col,
  Progress,
} from 'reactstrap';
import Controls from './Controls.js';
import Preview from './Preview.js';
import ReportInfo from './ReportInfo.js';
import Plots from './Plots.js';
import {Link} from 'react-router-dom';
import axios from 'axios';

const fullHeight = css`
  height: 100%;
  overflow-y: auto;
`;

export default class PlotsPage extends Component {
  constructor(props) {
    super(props);
    this.state = {
      plots: [],
      error: null,
      refReq: null,
      dataReq: null,
      procReq: null,
      search: '',
      showAll: false,
      hoveredPlot: null,
    };
  }

  componentWillMount = () => {
    if (!this.validUrl()) {
      this.setState({
        error: {message: 'Invalid report parameters!'},
      });
    } else {
      this.loadReport();
    }
  };

  onShowAllChange = checked => {
    this.setState({showAll: checked});
  };

  onSearchChange = search => {
    this.setState({search});
  };

  handleHover = hoveredPlot => {
    this.setState({hoveredPlot});
  };

  loadRun = (series, sample, run) => {
    return cancellableQuery('/cgi-bin/index.py', {
      type: 'fetch_run',
      series,
      sample,
      run,
    });
  };

  process = params => {
    return cancellableQuery('/cgi-bin/index.py', {
      type: 'process',
      subsystem: params.subsystem,
      ref_series: params.refSeries,
      ref_sample: params.refSample,
      ref_run: params.refRun,
      data_series: params.dataSeries,
      data_sample: params.dataSample,
      data_run: params.dataRun,
    });
  };

  loadReport = () => {
    const ps = this.props.match.params;
    console.log(ps);
    const refReq = this.loadRun(ps.refSeries, ps.refSample, ps.refRun);
    const dataReq = this.loadRun(ps.dataSeries, ps.dataSample, ps.dataRun);
    this.setState({refReq, dataReq});
    refReq.then(res => {
      this.setState({refReq: null});
      return res;
    });
    dataReq.then(res => {
      this.setState({dataReq: null});
      return res;
    });

    Promise.all([refReq, dataReq])
      .then(res => {
        const procReq = this.process(ps);
        this.setState({refReq: null, dataReq: null, procReq});
        procReq
          .then(res => {
            const plots = res.data.items;
            this.setState({plots, procReq: null});
          })
          .catch(err => {
            if (!axios.isCancel(err))
              this.setState({procReq: null, error: err});
          });
      })
      .catch(err => {
        if (!axios.isCancel(err))
          this.setState({refReq: null, dataReq: null, error: err});
      });
  };

  validUrl = () => {
    const params = this.props.match.params;
    return (
      params.subsystem &&
      params.refSeries &&
      params.refSample &&
      params.refRun &&
      params.dataSeries &&
      params.dataSample &&
      params.dataRun
    );
  };

  render() {
    const {refReq, dataReq, procReq} = this.state;
    let body;
    if (this.state.error) {
      body = (
        <Card
          body
          outline
          color="danger"
          className="text-center mx-auto mt-3 col-lg-5">
          <CardTitle>Something went wrong...</CardTitle>
          <CardText>{this.state.error.message}</CardText>
          <Button color="primary" outline tag={Link} to="/">
            Return to input page.
          </Button>
        </Card>
      );
    } else if (refReq || dataReq || procReq) {
      body = <LoadingBox {...{refReq, dataReq, procReq}} />;
    } else {
      body = (
        <Plots
          plots={this.state.plots}
          search={this.state.search}
          showAll={this.state.showAll}
          onHover={this.handleHover}
        />
      );
    }
    
    return (
      <Container
        fluid
        className={css`
          flex-grow: 1;
          min-height: 0;
          height: 100%;
        `}>
        <Row
          className={css`
            padding: 0;
            height: 100%;
          `}>
          <Col
            md={4}
            xl={3}
            className={`${fullHeight} d-none d-md-block bg-light p-3`}>
            <Controls
              onShowAllChange={this.onShowAllChange}
              onSearchChange={this.onSearchChange}
              showAll={this.state.showAll}
              search={this.state.search}
              onHover={this.handleHover}
            />
            <Preview className="my-3" plot={this.state.hoveredPlot}/>
          </Col>
          <Col md={8} xl={9} className={fullHeight}>
            <ReportInfo
              {...this.props.match.params}
              timestamp={new Date().toUTCString()}
            />
            {body}
          </Col>
        </Row>
      </Container>
    );
  }
}

const LoadingBox = ({refReq, dataReq, procReq}) => {
  return (
    <Card body outline className="mx-auto mt-3 col-lg-5">
      <CardTitle className="text-center">Loading...</CardTitle>
      <Progress
        animated={refReq ? true : false}
        color={refReq ? 'info' : 'success'}
        value={100}
        className="mt-2">
        {refReq ? 'Reference loading...' : 'Reference loaded!'}
      </Progress>
      <Progress
        animated={dataReq ? true : false}
        color={dataReq ? 'info' : 'success'}
        value={100}
        className="mt-2">
        {dataReq ? 'Data loading...' : 'Data loaded!'}
      </Progress>
      <Progress
        animated={procReq ? true : false}
        color={procReq ? 'info' : refReq || dataReq ? 'secondary' : 'success'}
        value={100}
        className="mt-2">
        {procReq
          ? 'Processing...'
          : refReq || dataReq
            ? 'Waiting to process...'
            : 'Processed!'}
      </Progress>
    </Card>
  );
};

const cancellableQuery = (endpoint, query) => {
  const source = axios.CancelToken.source();
  const p = axios
    .get(endpoint, {params: query, cancelToken: source.token})
    .then(res => {
      if (res.data.error) throw res.data.error;
      return res.data;
    })
    .catch(err => {
      console.log(err);
      throw err;
    });
  p.cancel = () => source.cancel(`Cancelled request of type ${query.type}`);
  return p;
};
