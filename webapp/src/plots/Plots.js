import React, {Component} from 'react';
import {Card, CardHeader, CardImg} from 'reactstrap';
import {css, cx} from 'react-emotion';

export default class Plots extends Component {
  render() {
    let plotObjs = this.props.plots;

    const plots = plotObjs.map(p => {
      return (
        <Plot
          color={p.anomalous ? 'warning' : p.always_show ? 'info' : null}
          key={p.id}
          name={p.name}
          pngUri={p.paths.png}
          pdfUri={p.paths.pdf}
          search={this.props.search}
          display={shouldDisplay(p, this.props.showAll, this.props.search)}
          onHover={() => this.props.onHover(p)}
          onClick={() => this.props.onClick(p)}
        />
      );
    });
    return <div className={containerSty}>{plots}</div>;
  }
}

const Plot = ({
  color,
  name,
  pngUri,
  pdfUri,
  search,
  display,
  onHover,
  onClick,
}) => {
  return (
    <Card
      outline
      color={color}
      className={cx(plotSty, display ? null : hidden)}
      onMouseEnter={onHover}
      onClick={onClick}>
      <CardHeader>{hlSearch(name, search)}</CardHeader>
      <CardImg src={pngUri} />
    </Card>
  );
};

const containerSty = css`
  margin-top: 0.5em;
`;

const hidden = css`
  display: none;
`;

const mh = '0.5em';
const plotSty = css`
  width: calc(100% / 1 - 2 * ${mh});
  display: inline-block;
  margin: ${mh};
  @media (min-width: 576px) {
    width: calc(100% / 1 - 2 * ${mh});
  }

  @media (min-width: 768px) {
    width: calc(100% / 2 - 2 * ${mh});
  }

  @media (min-width: 992px) {
    width: calc(100% / 3 - 2 * ${mh});
  }

  @media (min-width: 1200px) {
    width: calc(100% / 4 - 2 * ${mh});
  }

  :hover {
    box-shadow: 0 .5rem 1rem rgba(0,0,0,.15) !important;
    text-decoration: underline;
  }
`;

const shouldDisplay = (plot, showAll, search) => {
  if (!plot.always_show && !plot.anomalous && !showAll) return false;
  if (search && plot.name.indexOf(search) === -1) return false;
  return true;
};

const hlSearch = (text, search) => {
  if (!search) return <span>{text}</span>;
  const len = search.length;
  const idx = text.indexOf(search);
  return (
    <span>
      {text.substring(0, idx)}
      <b>{text.substring(idx, idx + len)}</b>
      {text.substring(idx + len)}
    </span>
  );
};
