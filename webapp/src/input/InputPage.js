import React, {Component} from 'react';
import {Container, Row, Col} from 'reactstrap';
import InputForm from './InputForm.js';
import RefSuggestions from './RefSuggestions.js';

export default class InputPage extends Component {
  constructor(props) {
    super(props);
    this.state = {
      refEqualsData: true,
      query: {
        subsystem: null,
        refSeries: null,
        refSample: null,
        refRun: null,
        dataSeries: null,
        dataSample: null,
        dataRun: null,
        ...props.recentQuery,
      },
    };
  }

  handleInputChange = change => {
    this.setState(prevState => {
      let refEqualsData = prevState.refEqualsData;
      if (change.refSeries || change.refSample || change.refRun)
        refEqualsData = false;

      let query = this.validatedQuery(
        {...prevState.query, ...change},
        refEqualsData,
      );
      return {query};
    });
  };

  handleSuggestionClick = ref => {
    this.setState(prevState => {
      let query = {
        ...prevState.query,
        refSeries: ref.series,
        refSample: ref.sample,
        refRun: ref.run,
      };
      return {query, refEqualsData: false};
    });
  };

  validatedQuery = (rawQuery, syncRefData) => {
    let q = {...rawQuery};
    if (syncRefData) {
      q.refSeries = q.dataSeries;
      q.refSample = q.dataSample;
      q.refRun = q.dataRun;
    }

    if (!rawQuery.dataSeries) q = {...q, dataSample: null, dataRun: null};
    else if (!rawQuery.dataSample) q = {...q, dataRun: null};

    if (!rawQuery.refSeries) q = {...q, refSample: null, refRun: null};
    else if (!rawQuery.refSample) q = {...q, refRun: null};

    return q;
  };

  render() {
    let query = this.state.query;
    return (
      <Container fluid>
        <Row>
          <Col md="6">
            <InputForm query={query} onChange={this.handleInputChange} />
          </Col>
          <Col md="6">
            <RefSuggestions
              subsystem={query.subsystem}
              series={query.dataSeries}
              sample={query.dataSample}
              run={query.dataRun}
              onChange={this.handleSuggestionClick}
            />
          </Col>
        </Row>
      </Container>
    );
  }
}
