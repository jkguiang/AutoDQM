import React, {Component} from 'react';
import {Link} from 'react-router-dom';
import {Card, CardHeader, CardImg} from 'reactstrap';
import {css, cx} from 'react-emotion';
import Fuse from 'fuse.js';

export default class Plots extends Component {
  render() {
    let plotObjs = this.props.plots;
    if (!this.props.showAll) plotObjs = plotObjs.filter(p => p.display);
    if (this.props.search) {
      let fuse = new Fuse(plotObjs, fuseOpts); // "list" is the item array
      plotObjs = fuse.search(this.props.search);
    } else {
      plotObjs = plotObjs.map(p => {
        return {item: p};
      });
    }

    const plots = plotObjs.map(p => {
      return (
        <Plot
          key={p.item.name}
          name={p.item.name}
          pngUri={p.item.png_path}
          pdfUri={p.item.pdf_path}
          matches={p.matches}
        />
      );
    });
    return <div className={containerSty}>{plots}</div>;
  }
}

const Plot = ({name, pngUri, pdfUri, matches}) => {
  return (
    <Card className={plotSty}>
      <Link to={pdfUri}>
        <CardHeader>{highlightedText(name, matches)}</CardHeader>
        <CardImg src={pngUri} />
      </Link>
    </Card>
  );
};

const fuseOpts = {
  shouldSort: true,
  includeScore: true,
  includeMatches: true,
  threshold: 0.6,
  location: 0,
  distance: 100,
  maxPatternLength: 32,
  minMatchCharLength: 1,
  keys: ['name'],
};

const containerSty = css`
  margin-top: 0.5em;
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
`;

const highlightedText = (text, matches) => {
  if (!matches) return <span>{text}</span>;
  let out = [];
  let prev = [-1, -1];
  for (let idx of matches[0].indices) {
    out.push(
      <span key={[prev[1] + 1, idx[0]]}>
        {text.substring(prev[1] + 1, idx[0])}
      </span>,
    );
    out.push(
      <b key={[idx[0], idx[1] + 1]}>{text.substring(idx[0], idx[1] + 1)}</b>,
    );
    prev = idx;
  }
  out.push(
    <span key={[prev[1] + 1, -1]}>
      {text.substring(prev[1] + 1)}
    </span>,
  );
  return out;
};
