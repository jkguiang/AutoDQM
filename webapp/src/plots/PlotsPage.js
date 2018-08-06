import React, {Component} from 'react';
import styled, {css} from 'react-emotion';
import {
  Container,
  Row,
  Col,
  Card,
  CardBody,
  CardTitle,
  CardText,
  ListGroup,
  Input,
  Button,
} from 'reactstrap';
import Controls from './Controls.js';
import Preview from './Preview.js';

const fullHeight = css`
  height: 100%;
  overflow-y: auto;
`;

export default class PlotsPage extends Component {
  render() {
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
            <Controls />
            <Preview className="mt-3" />
          </Col>
          <Col md={8} xl={9} className={fullHeight}>
            <ReportInfo />
            <Plots />
          </Col>
        </Row>
      </Container>
    );
  }
}



class ReportInfo extends Component {
  render() {
    return <React.Fragment />;
  }
}

class Plots extends Component {
  render() {
    return <React.Fragment />;
  }
}
